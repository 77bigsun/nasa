"""Import independently located study windows for every catalog target.

Lunar points are named records in the authors' published geospatial archive.
Mars points use the current Gazetteer footprint centres, not landing ellipses.
Remote DEMs are cropped at native resolution; the crop hash is not a full-file hash.
"""
import argparse
from datetime import datetime, timezone
import io
import json
import math
from pathlib import Path
import re
import zipfile

import httpx
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject, transform, transform_bounds
from rasterio.windows import Window, from_bounds
import shapefile
import spiceypy as spice
import yaml

from .run import save_json, terrain_statistics, digest, extract_terrain
from . import moon_products, mars_products, solar

ARCHIVE='https://zenodo.org/api/records/17084058/files/Landing_Sites.zip/content'
LUNAR_SOURCE='https://doi.org/10.5281/zenodo.17084058'
MOON_DEM='https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF'
MARS_DEM='https://planetarymaps.usgs.gov/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif'
MARS_PAGE='https://astrogeology.usgs.gov/search/map/mars_mgs_mola_mex_hrsc_blended_dem_global_200m'
MOON_POINTS={
    'moon-cabeus-b-peak':'PCB01','moon-haworth':'HW01','moon-malapert':'MMA01',
    'moon-mouton-plateau':'MMP01','moon-mouton':'MMO01','moon-nobile-1':'NR101',
    'moon-nobile-2':'NR201','moon-degerlache-2':'dGR201','moon-slater':'SP01',
}
MARS_NAMES={
    'mars-deuteronilus':(1509,'Deuteronilus Mensae',45.11,23.92),
    'mars-utopia':(6260,'Utopia Planitia',46.74,117.52),
    'mars-phlegra':(4701,'Phlegra Montes',40.40,163.71),
    'mars-erebus':(1821,'Erebus Montes',35.66,185.02),
}
ENV={'GDAL_DISABLE_READDIR_ON_OPEN':'EMPTY_DIR','CPL_VSIL_CURL_ALLOWED_EXTENSIONS':'.TIF,.tif',
     'GDAL_HTTP_CONNECTTIMEOUT':'30','GDAL_HTTP_TIMEOUT':'90','GDAL_HTTP_MAX_RETRY':'2',
     'GDAL_HTTP_RETRY_DELAY':'1','VSI_CACHE':False}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def same_location(a,b):
    # Projection libraries can differ in the last decimal of a derived geometry
    # check. Source identity, coordinates and the requested support must agree.
    return all(a.get(key)==b.get(key) for key in [
        'lat','lon','window_m','source_point','source_url','coordinate_source_sha256'])


def fetch(client,url,path):
    path=Path(path);meta=path.with_suffix(path.suffix+'.metadata.json')
    if path.exists() and meta.exists():
        saved=read(meta)
        if saved['url']==url and saved['sha256']==digest(path):return saved
    path.parent.mkdir(parents=True,exist_ok=True)
    response=client.get(url);response.raise_for_status()
    if len(response.content)>40*1024**2:raise ValueError('Unexpectedly large coordinate source')
    path.write_bytes(response.content)
    result={'url':url,'sha256':digest(path),'bytes':len(response.content),
            'hash_kind':'full_product','retrieved_at':datetime.now(timezone.utc).isoformat()}
    save_json(meta,result)
    return result


def lunar_locations(archive):
    """Read just named shapefile members in memory, never extract archive paths."""
    with zipfile.ZipFile(archive) as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read('Landing_Sites.zip'))) as inner:
            reader=shapefile.Reader(**{ext:io.BytesIO(inner.read('LandingSites.'+ext)) for ext in ['shp','shx','dbf']})
            crs=CRS.from_wkt(inner.read('LandingSites.prj').decode('ascii'))
            lookup={record.record['Name']:record for record in reader.iterShapeRecords()}
    result={}
    for sid,name in MOON_POINTS.items():
        row=lookup[name];lat=float(row.record['Latitude']);lon=float(row.record['Longitude'])
        x,y=row.shape.points[0]
        ll=transform(crs,CRS.from_proj4('+proj=longlat +R=1737400'),[x],[y])
        discrepancy=math.hypot((ll[0][0]-lon)*math.cos(math.radians(lat)),ll[1][0]-lat)*30323.35
        if discrepancy>25:raise ValueError(f'{name}: geometry and coordinate columns disagree by {discrepancy} m')
        result[sid]={'lat':lat,'lon':lon%360,'source_point':name,'region_code':row.record['Landing_Re'],
                     'source_url':LUNAR_SOURCE,'coordinate_method':'Published named study point; checked against shapefile geometry',
                     'geometry_discrepancy_m':discrepancy,'window_m':2000}
    return result


def coordinates(data,client,cached_only=False):
    raw=data/'raw/regions';raw.mkdir(parents=True,exist_ok=True)
    archive=raw/'Landing_Sites.zip'
    if not cached_only:fetch(client,ARCHIVE,archive)
    locations=lunar_locations(archive)
    for sid,(fid,name,lat,lon) in MARS_NAMES.items():
        url=f'https://planetarynames.wr.usgs.gov/Feature/{fid}'
        path=raw/(sid+'-gazetteer.html')
        if not cached_only:fetch(client,url,path)
        text=path.read_text(encoding='utf-8')
        # The page includes historical networks too. Require the current values
        # reviewed from the last footprint entry, not a guessed planet coordinate.
        numbers=re.findall(r'Center (?:Latitude|Longitude).*?([-+]?\d+\.\d+)',text,re.S)
        if name not in text or len(numbers)<4 or not np.allclose(np.asarray(numbers[-4:-2],float),[lat,lon],atol=.005,rtol=0):
            raise ValueError(f'{sid}: Gazetteer centre changed; review the current control network')
        locations[sid]={'lat':lat,'lon':lon,'source_point':str(fid),'source_url':url,
            'coordinate_method':'Current Gazetteer named-feature centre; a regional study sample, not a SkyFall landing site',
            'window_m':20000,'outside_skyfall_latitude_band':not 30<=lat<=45,'coordinate_source_sha256':digest(path)}
    existing=yaml.safe_load((data/'seed/target_sites.yaml').read_text(encoding='utf-8'))
    for site in existing:
        if site['id'].startswith('mars-') and site['id'] not in locations:
            references={'mars-gale':'https://hirise.lpl.arizona.edu/dtm/dtm.php?ID=ESP_040770_1755',
                'mars-ap105':'https://science.nasa.gov/wp-content/uploads/2026/09/skyfall-mission-information-package-final.pdf',
                'mars-jezero':'https://mars.nasa.gov/files/m2020/SDT_Appendices_Final_v6.pdf'}
            locations[site['id']]={'lat':site['lat'],'lon':site['lon'],'source_url':references[site['id']],
                'source_point':site['id'],'coordinate_method':'Existing reviewed study point','window_m':20000}
    for site in locations.values():
        if site['source_url']==LUNAR_SOURCE:site['coordinate_source_sha256']=digest(archive)
    save_json(data/'observed/target-locations.json',{'locations':locations,
        'scope':'Representative published study points. A local window is not an entire candidate region or certified landing site.',
        'lunar_citation':'Wueller et al. (2026), JGR Planets, doi:10.1029/2025JE009434; Zenodo doi:10.5281/zenodo.17084058'})
    return locations


def native_crop(url,site,planet,path,window_m):
    """Persist native source pixels before any regridding; cache by source/point."""
    sidecar=path.with_suffix('.metadata.json')
    if path.exists() and sidecar.exists():
        old=read(sidecar)
        if all(old.get(k)==v for k,v in {'url':url,'lat':site['lat'],'lon':site['lon'],'window_m':window_m}.items()) and old['sha256']==digest(path):return old
    radius=1737400 if planet=='moon' else 3396190
    local=CRS.from_proj4(f'+proj=aeqd +lat_0={site["lat"]} +lon_0={site["lon"]} +R={radius} +units=m')
    half=window_m/2+(150 if planet=='moon' else 750)
    with rasterio.Env(**ENV),rasterio.open('/vsicurl/'+url) as src:
        bounds=transform_bounds(local,src.crs,-half,-half,half,half,densify_pts=21)
        requested=from_bounds(*bounds,src.transform)
        col=math.floor(requested.col_off)-2;row=math.floor(requested.row_off)-2
        width=math.ceil(requested.width)+4;height=math.ceil(requested.height)+4
        if min(col,row)<0 or col+width>src.width or row+height>src.height:raise ValueError('Study window outside source DEM')
        window=Window(col,row,width,height)
        array=src.read(1,window=window)
        profile=src.profile.copy();profile.update(width=width,height=height,transform=src.window_transform(window),compress='deflate',tiled=False)
        profile.pop('blockxsize',None);profile.pop('blockysize',None)
        path.parent.mkdir(parents=True,exist_ok=True)
        with rasterio.open(path,'w',**profile) as dst:dst.write(array,1)
        metadata={'url':url,'lat':site['lat'],'lon':site['lon'],'window_m':window_m,
            'source_window':[col,row,width,height],'source_crs':src.crs.to_wkt(),
            'native_resolution':list(src.res),'native_shape':list(src.shape),
            'sha256':digest(path),'hash_kind':'derived native-resolution crop, not full remote product',
            'retrieved_at':datetime.now(timezone.utc).isoformat()}
    save_json(sidecar,metadata)
    return metadata


def mars_grid(path,site,output,spacing=500,window_m=20000):
    radius=3396190;cells=window_m//spacing
    dst_crs=CRS.from_proj4(f'+proj=aeqd +lat_0={site["lat"]} +lon_0={site["lon"]} +R={radius} +units=m')
    affine=from_origin(-window_m/2-spacing,window_m/2+spacing,spacing,spacing)
    grid=np.full((cells+2,cells+2),np.nan)
    with rasterio.open(path) as src:
        original=src.read(1,masked=True).astype(float).filled(np.nan)
        reproject(original,grid,src_transform=src.transform,src_crs=src.crs,src_nodata=np.nan,
                  dst_transform=affine,dst_crs=dst_crs,dst_nodata=np.nan,resampling=Resampling.average)
    stats,slopes=terrain_statistics(grid,spacing)
    output.parent.mkdir(parents=True,exist_ok=True)
    with rasterio.open(output,'w',driver='GTiff',width=cells+2,height=cells+2,count=1,dtype='float32',
                       crs=dst_crs,transform=affine,nodata=np.nan,compress='deflate') as dst:dst.write(grid.astype('float32'),1)
    return {'statistics':stats,'slope_samples_deg':slopes,'grid_m':spacing,'window_m':window_m,'derived_file':output.name}


def thermal(out,site,client):
    lon=(site['lon']+180)%360-180;lat=site['lat']
    url=moon_products.PDS+'data_derived_gcp/global_cumul_avg_cyl_90s80s_002.tab'
    col=int(math.floor((lon+180)*2));row=int(math.floor((lat+90)*2))
    first=(1+(col*20+row)*96)*113
    raw,metadata=moon_products.fetch_range(client,url,out/'gcp.csv',first,first+96*113-1,156211313)
    rows=np.array([[float(v) for v in line.split(',')] for line in raw.decode('ascii').splitlines()])
    if rows.shape!=(96,11) or not np.allclose(rows[:,0],-180+(col+.5)/2) or not np.allclose(rows[:,1],-90+(row+.5)/2):
        raise ValueError('Diviner cell coordinates disagree with requested target')
    good=np.isfinite(rows[:,-1])&(rows[:,-1]>0)&(rows[:,-1]!=-9999)
    result={**metadata,'grid_lat':float(rows[0,1]),'grid_lon':float(rows[0,0]),'requested_lat':lat,'requested_lon':lon,
            'valid_tbol_count':int(good.sum()),'phase':(rows[good,2]/24).tolist(),'kelvin':rows[good,-1].tolist()}
    save_json(out/'thermal.json',result)
    return result


def acquire(data,locations,client,cached_only=False):
    root=data/'raw/regions';records={}
    if not cached_only:
        for sid,site in locations.items():
            output=root/sid;output.mkdir(parents=True,exist_ok=True)
            result_path=output/'ready.json'
            if result_path.exists():
                previous=read(result_path)
                expected=data/'processed'/(sid+('-100m.tif' if sid.startswith('moon-') else '-500m.tif'))
                if (same_location(previous['location'],site) and (output/'native.tif').exists() and expected.exists()
                        and previous['dem']['sha256']==digest(output/'native.tif')
                        and previous['terrain'].get('derived_sha256')==digest(expected)):
                    records[sid]=previous;print(sid,'verified cached study window',flush=True);continue
            print(sid,'reading native source pixels',flush=True)
            planet='moon' if sid.startswith('moon-') else 'mars'
            crop=output/'native.tif'
            metadata=native_crop(MOON_DEM if planet=='moon' else MARS_DEM,site,planet,crop,site['window_m'])
            processed=data/'processed'/(sid+('-100m.tif' if planet=='moon' else '-500m.tif'))
            if planet=='moon':
                with rasterio.open(crop) as src:
                    xy=transform(CRS.from_proj4('+proj=longlat +R=1737400'),src.crs,[site['lon']],[site['lat']])
                terrain=extract_terrain(crop,(xy[0][0],xy[1][0]),'moon',100,2000,processed)
                horizon=solar.local_horizon(processed,site['lat'],site['lon'],'moon')
                light=dict(solar.solar_cycle(site['lat'],site['lon'],'moon',horizon),horizon_deg=horizon)
                result={'location':site,'terrain':terrain,'solar':light,'thermal':thermal(output,site,client),'dem':metadata}
            else:
                result={'location':site,'terrain':mars_grid(crop,site,processed),'dem':metadata}
            result['terrain']['derived_sha256']=digest(processed)
            save_json(result_path,result);records[sid]=result
            print(sid,'imported',result['terrain']['statistics']['sample_count'],'terrain cells',flush=True)
    else:
        for sid,site in locations.items():
            record=read(root/sid/'ready.json')
            if not same_location(record['location'],site):raise ValueError('Cached location changed')
            processed=data/'processed'/(sid+('-100m.tif' if sid.startswith('moon-') else '-500m.tif'))
            if record['dem']['sha256']!=digest(root/sid/'native.tif') or record['terrain']['derived_sha256']!=digest(processed):
                raise ValueError('Cached terrain checksum mismatch')
            if sid.startswith('moon-') and record['thermal']['sha256']!=digest(root/sid/'gcp.csv'):
                raise ValueError('Cached thermal checksum mismatch')
            records[sid]=record
    # Reuse the same real Earth windows, resampled at the Mars regional scale.
    earth={}
    pilot=read(data/'observed/pilot.json')
    from .paired import rms_height
    for site in pilot['candidates']:
        path=data/'processed'/(site['id']+'-500m.tif')
        record=extract_terrain(data/'raw'/(site['id']+'-glo30.tif'),(site['lat'],site['lon']),'earth',500,20000,path)
        earth[site['id']]={'rms_height_m':rms_height(path,500),'grid_m':500,'window_m':20000,
            'source_url':site['raw_url'],'derived_sha256':digest(path)}
    for sid,record in records.items():
        if sid.startswith('mars-'):record['regional_rms_m']=rms_height(data/'processed'/(sid+'-500m.tif'),500)
    context_path=root/'mars-context.json'
    if not cached_only:
        sites={sid.removeprefix('mars-'):(s['lat'],(s['lon']+180)%360-180) for sid,s in locations.items() if sid.startswith('mars-')}
        context={'tes':mars_products.read_tes(data/'raw/missions/mars',client,sites),
                 'swim':mars_products.read_swim(data/'raw/missions/mars',client,sites)}
        save_json(context_path,context)
    else:context=read(context_path)
    save_json(data/'observed/regional-evidence.json',{'targets':records,'earth_regional':earth,'mars_context':context,
        'scope':'Lunar 2 km windows; Mars/Earth regional 20 km windows with 500 m grids. Fine landing slopes, rocks, ice and seasonal weather remain separate requirements.'})
    return records


def enrich(snapshot,data):
    """Attach only successfully acquired, independently scoped measurements."""
    from .paired import blank, terrain_records, solar_records, evidence, put, source
    regional=read(data/'observed/regional-evidence.json')
    targets=snapshot['targets'];models=read(data/'observed/solar.json')
    ephemerides=[source('NASA NAIF '+p['url'].split('/')[-1],p['url']) for p in models['sources']]
    for sid,record in regional['targets'].items():
        site=record['location'];dem=record['dem'];item=targets.setdefault(sid,blank())
        if sid.startswith('moon-'):
            refs=[source('Adjusted LOLA south-polar 20 m DEM',MOON_DEM),source('Published study point '+site['source_point'],LUNAR_SOURCE)]
            terrain_records(item,record['terrain'],refs,dem['sha256'])
            solar_records(item,record['solar'],ephemerides+refs,models['scope'])
            thermal=record['thermal'];kelvin=np.asarray(thermal['kelvin'])
            if len(kelvin):
                notes=['Cumulative lunar orbital sampling and sparse Earth MODIS overpasses have different support; shown as context.',
                       'Native 0.5 degree cell is much larger than this 2 km terrain window.']
                common=dict(method='Positive valid PDS Diviner bolometric temperatures; no missing bins interpolated',
                    spatial=f"0.5 degree cell centered at {thermal['grid_lat']}, {thermal['grid_lon']}",
                    temporal='Diviner GCP cumulative 2009-2015 local-time bins',
                    sources=[source('Diviner GCP numeric table',thermal['url'])],hashes=[thermal['sha256']],notes=notes)
                series={'phase':thermal['phase'],'values':thermal['kelvin'],'step_hours':29.530588853*.25 if len(kelvin)==96 else None,
                        'period':'Diviner GCP cumulative 2009-2015; 96 possible local-time bins','value_unit':'K','quantity':'Bolometric temperature'}
                put(item,'m3_diurnal_range',evidence(float(np.ptp(kelvin)),'K','Range of cumulative bolometric thermal cycle',**common),series=series)
                put(item,'m3_abs_temp',evidence(float(kelvin.min()-273.15),'C','Minimum cumulative bolometric temperature',**common))
        else:
            notes=['Regional 20 km study window, 500 m grid. Not centimetre rocks, radar roughness or a glacial-landform identification.',
                   'The 200 m blended product includes MOLA interpolation; native grid spacing does not guarantee effective resolution.',
                   'A representative point does not characterize the entire named region or establish landing suitability.']
            put(item,'r5_roughness',evidence(record['regional_rms_m'],'m','Regional detrended terrain RMS height',
                'Native HRSC/MOLA DEM area-averaged; least-squares planar detrending',
                '20 km window; 500 m grid','Static regional terrain; source epochs differ',
                [source('USGS HRSC/MOLA 200 m blend',MARS_PAGE),source('Numeric elevation raster',MARS_DEM)],
                key='detrended_rms_grid500_window20000',hashes=[dem['sha256']],notes=notes))
            if 'r1_slope_100m' not in item['evidence']:
                put(item,'r1_slope_100m',evidence(record['terrain']['statistics']['mean_slope_deg'],'deg',
                    'Regional slope at 1 km gradient support, not a 100 m landing slope',
                    'Central differences on 500 m grid','20 km window; 1 km gradient support','Static regional terrain',
                    [source('USGS HRSC/MOLA elevation raster',MARS_DEM)],hashes=[dem['sha256']],notes=notes+[
                        'Too coarse for the required 100 m gradient support; this value cannot score the landing slope feature.']))
            name=sid.removeprefix('mars-');tes=regional['mars_context']['tes'];ts=tes['samples'][name]
            put(item,'r1_thermal_inertia',evidence(ts['value'],tes['units'],'TES nighttime thermal inertia',
                'Native int16 pixel, excluding interpolated mask 0','Approximately 2.96 km native TES pixel',
                'Observations 1999-2004; derived release 2007',[source('TES numeric thermal inertia',tes['data_url']),source('TES quality mask',tes['mask_url'])],
                notes=tes['caveats']+[f"Native quality mask: {ts['mask']}; interpolated or invalid pixels remain unavailable."]))
            swim=regional['mars_context']['swim'];sample=swim['samples'][name]
            put(item,'r3_ground_ice',evidence(sample['value'],'consistency index','SWIM 1-5 m ice consistency',
                'Native composite pixel; no interpolation','Approximately 2.96 km native pixel','SWIM2 multi-instrument composite',
                [source('SWIM2 numeric ice consistency',swim['raw_url'])],hashes=[swim['sha256']],notes=swim['caveats']))
    for candidate in snapshot['candidates']:
        record=regional['earth_regional'][candidate['id']]
        put(candidate,'r5_roughness',evidence(record['rms_height_m'],'m','Regional detrended terrain RMS height',
            'Copernicus GLO-30 area-averaged; least-squares planar detrending','20 km window; 500 m grid',
            'Static regional terrain; source epochs differ',[source('Copernicus GLO-30 DSM',record['source_url'])],
            key='detrended_rms_grid500_window20000',hashes=[record['derived_sha256']],notes=[
                'Common regional grid and window with Mars; not a fine-scale rock, radar or landform comparison.',
                'DSM and planetary DEM source error and interpolation uncertainty remain.']))
    return snapshot


def publish_catalog(data):
    """Publish coordinates only after every corresponding study window succeeded."""
    regional=read(data/'observed/regional-evidence.json')
    sites=yaml.safe_load((data/'seed/target_sites.yaml').read_text(encoding='utf-8'))
    locales=read(data/'locales/zh-TW.json')
    translations=read(data/'locales/regional.zh-TW.json')
    for site in sites:
        sid=site['id']
        if sid=='moon-scr':
            site['coordinate_reference']={'title':'Published LOLA Site01 ROI','url':'https://pgda.gsfc.nasa.gov/products/78'}
            site['study_window_m']=2000
            continue
        row=regional['targets'][sid];location=row['location']
        site.update(lat=location['lat'],lon=location['lon'],coords_status='approx' if sid!='mars-ap105' else 'exact',
            coordinate_reference={'title':('Wueller et al. published point '+location['source_point']) if sid.startswith('moon-') else 'Study-point reference',
                                  'url':location['source_url']},study_window_m=location['window_m'])
        if sid.startswith('moon-'):
            description=f"Published study point {location['source_point']}; 2 km terrain and finite-horizon solar models imported, with native-cell Diviner temperatures. This is a study window, not a finalized landing site."
            translated=translations['moon'].format(point=location['source_point'])
            site['source']='Wueller et al. (2026), doi:10.1029/2025JE009434; Zenodo 10.5281/zenodo.17084058'
        else:
            description='Regional study window: 20 km terrain with a 500 m comparison grid, plus native TES/SWIM context where valid. Regional roughness is comparable; it does not resolve 100 m landing slopes, rocks or polygonal landforms.'
            translated=translations['mars']
            if sid in MARS_NAMES:
                site['source']='USGS Gazetteer current named-feature centre; regional sample only'
                description+=' The point is a Gazetteer feature centre, not a selected SkyFall landing site.'
                translated+=translations['gazetteer']
                if location.get('outside_skyfall_latitude_band'):
                    description+=' This centre lies outside the provisional 30-45 N landing band.'
                    translated+=translations['outside_band']
            if sid=='mars-gale':
                description+=' Gale also retains its own finer HiRISE slope and regional REMS air-temperature evidence.'
                translated+=translations['gale']
        site.update(description=description,description_en=description)
        locales[description]=translated
    (data/'seed/target_sites.yaml').write_text(yaml.safe_dump(sites,sort_keys=False,allow_unicode=True,width=110),encoding='utf-8')
    save_json(data/'locales/zh-TW.json',locales)


def build(data,cached_only=False):
    data=Path(data)
    with httpx.Client(timeout=httpx.Timeout(180,connect=30),follow_redirects=True) as client:
        locations=coordinates(data,client,cached_only)
        spice.kclear()
        try:
            for kernel in solar.KERNELS:spice.furnsh(str(data/'raw/spice'/kernel))
            acquire(data,locations,client,cached_only)
        finally:spice.kclear()
    publish_catalog(data)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-dir',type=Path,default=Path(__file__).resolve().parents[2]/'data')
    parser.add_argument('--stage',choices=['coordinates','acquire','all'],default='all')
    parser.add_argument('--cached-only',action='store_true')
    parser.add_argument('--publish-catalog',action='store_true')
    args=parser.parse_args();data=args.data_dir
    with httpx.Client(timeout=httpx.Timeout(180,connect=30),follow_redirects=True) as client:
        locations=coordinates(data,client,args.cached_only)
        if args.stage=='coordinates':return
        spice.kclear()
        try:
            for kernel in solar.KERNELS:spice.furnsh(str(data/'raw/spice'/kernel))
            acquire(data,locations,client,args.cached_only)
        finally:spice.kclear()
    if args.publish_catalog:publish_catalog(data)


if __name__=='__main__':main()
