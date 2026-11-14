"""Reproducible public-data pilot. It never overwrites demonstration fixtures.

Download only named public products, preserve hashes, read native raster pixels,
resample to one metric grid, and export explicitly scoped observation records.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import tarfile
import time
from urllib.parse import urlparse
import httpx
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject, transform, transform_bounds
from rasterio.windows import Window, from_bounds
import shapefile
import yaml

ALLOWED_HOSTS={'pgda.gsfc.nasa.gov','copernicus-dem-30m.s3.amazonaws.com','power.larc.nasa.gov'}

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def save_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    temporary.replace(path)

def download(client,url,path,limit_mb=90):
    parsed=urlparse(url)
    if parsed.scheme!='https' or parsed.hostname not in ALLOWED_HOSTS:raise ValueError('Download host is not allowed')
    metadata=path.with_suffix(path.suffix+'.metadata.json')
    if path.exists() and metadata.exists():
        cached=json.loads(metadata.read_text(encoding='utf-8'))
        if cached['url']==url and cached['sha256']==digest(path):return cached
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.part')
    print(f'Downloading {path.name}',flush=True)
    count=0
    with client.stream('GET',url) as response:
        response.raise_for_status()
        if urlparse(str(response.url)).hostname not in ALLOWED_HOSTS:raise ValueError('Unexpected redirect host')
        if int(response.headers.get('content-length',0))>limit_mb*1024**2:raise ValueError('Product exceeds configured download limit')
        with temporary.open('wb') as stream:
            for chunk in response.iter_bytes(1024*1024):
                count+=len(chunk)
                if count>limit_mb*1024**2:raise ValueError('Download exceeded configured limit')
                stream.write(chunk)
    temporary.replace(path)
    result={'url':url,'bytes':count,'sha256':digest(path),'retrieved_at':datetime.now(timezone.utc).isoformat()}
    save_json(metadata,result)
    return result

def roi_center(archive,index):
    # Read archive members in memory; never extract untrusted paths to disk.
    with tarfile.open(archive,'r:gz') as tar:
        members={Path(m.name).suffix.lower():m for m in tar.getmembers() if m.isfile() and Path(m.name).suffix.lower() in {'.shp','.shx','.dbf'}}
        if '.shp' not in members:raise ValueError('ROI archive has no shapefile')
        args={ext[1:]:io.BytesIO(tar.extractfile(member).read()) for ext,member in members.items()}
        reader=shapefile.Reader(**args)
        shape=reader.shape(index)
        xmin,ymin,xmax,ymax=shape.bbox
        return (xmin+xmax)/2,(ymin+ymax)/2

def terrain_statistics(elevation,grid_m):
    values=np.asarray(elevation,dtype=float)
    if values.ndim!=2 or min(values.shape)<5:raise ValueError('Terrain grid must be at least 5 x 5')
    dy,dx=np.gradient(values,grid_m,grid_m,edge_order=2)
    slopes=np.degrees(np.arctan(np.hypot(dx,dy)))[1:-1,1:-1]
    core=values[1:-1,1:-1]
    valid=np.isfinite(slopes)&np.isfinite(core)
    if valid.mean()<.9:raise ValueError('Less than 90% valid terrain coverage')
    s=slopes[valid];z=core[valid]
    return {'mean_slope_deg':float(s.mean()),'median_slope_deg':float(np.median(s)),'p90_slope_deg':float(np.percentile(s,90)),'relief_p95_p05_m':float(np.percentile(z,95)-np.percentile(z,5)),'sample_count':int(len(s)),'valid_fraction':float(valid.mean())},s.tolist()

def extract_terrain(path,center,planet,grid_m,window_m,processed):
    cells=int(window_m/grid_m)
    if cells<5 or cells*grid_m!=window_m:raise ValueError('Window must be an integral number of grid cells')
    with rasterio.open(path) as src:
        if planet=='moon':
            dst_crs=src.crs;x,y=center
            lon,lat=transform(src.crs,CRS.from_proj4('+proj=longlat +R=1737400 +no_defs'),[x],[y])
            lon,lat=float(lon[0]),float(lat[0])
        else:
            lat,lon=center
            zone=int((lon+180)//6)+1
            dst_crs=CRS.from_epsg((32600 if lat>=0 else 32700)+zone)
            xx,yy=transform(CRS.from_epsg(4326),dst_crs,[lon],[lat]);x,y=xx[0],yy[0]
        half=window_m/2+grid_m
        bounds=(x-half,y-half,x+half,y+half)
        native_bounds=transform_bounds(dst_crs,src.crs,*bounds,densify_pts=21)
        requested=from_bounds(*native_bounds,transform=src.transform)
        col=max(0,math.floor(requested.col_off)-2);row=max(0,math.floor(requested.row_off)-2)
        width=min(src.width-col,math.ceil(requested.width)+4);height=min(src.height-row,math.ceil(requested.height)+4)
        window=Window(col,row,width,height)
        # Native read has no out_shape: quantitative work never uses COG overviews.
        original=src.read(1,window=window,masked=True).astype('float64')
        original=original.filled(np.nan)*src.scales[0]+src.offsets[0]
        affine=from_origin(bounds[0],bounds[3],grid_m,grid_m)
        grid=np.full((cells+2,cells+2),np.nan,dtype='float64')
        reproject(original,grid,src_transform=src.window_transform(window),src_crs=src.crs,src_nodata=np.nan,dst_transform=affine,dst_crs=dst_crs,dst_nodata=np.nan,resampling=Resampling.average,num_threads=1)
        stats,slopes=terrain_statistics(grid,grid_m)
        processed.parent.mkdir(parents=True,exist_ok=True)
        with rasterio.open(processed,'w',driver='GTiff',width=cells+2,height=cells+2,count=1,dtype='float32',crs=dst_crs,transform=affine,nodata=np.nan,compress='deflate') as dst:dst.write(grid.astype('float32'),1)
        return {'planet':planet,'lat':lat,'lon':lon,'native_crs':src.crs.to_wkt(),'native_pixel_size':list(src.res),'analysis_crs':dst_crs.to_wkt(),'grid_m':grid_m,'window_m':window_m,'gradient_support_m':2*grid_m,'statistics':stats,'slope_samples_deg':slopes,'is_placeholder':False,'derived_file':str(processed.name)}

def copernicus_url(lat,lon):
    y=math.floor(lat);x=math.floor(lon)
    tile=f'Copernicus_DSM_COG_10_{"N" if y>=0 else "S"}{abs(y):02}_00_{"E" if x>=0 else "W"}{abs(x):03}_00_DEM'
    return f'https://copernicus-dem-30m.s3.amazonaws.com/{tile}/{tile}.tif'

def power_summary(data):
    fill=data.get('header',{}).get('fill_value',-999)
    params=data['properties']['parameter']
    output={}
    for name,series in params.items():
        rows=[(key,float(value)) for key,value in series.items() if value!=fill and np.isfinite(value)]
        if len(rows)<24:raise ValueError('POWER response has insufficient valid hours')
        cycle=[float(np.mean([value for key,value in rows if int(key[-2:])==hour])) for hour in range(24)]
        output[name]={'mean':float(np.mean([v for _,v in rows])),'sample_count':len(rows),'phase':[h/24 for h in range(24)],'mean_cycle':cycle,'units':data.get('parameters',{}).get(name,{}).get('units','')}
    return output

def run(config_path,data_dir):
    config=yaml.safe_load(config_path.read_text(encoding='utf-8'))
    raw=data_dir/'raw';processed=data_dir/'processed';observed=data_dir/'observed'
    now=datetime.now(timezone.utc).isoformat()
    provenance=[]
    with httpx.Client(timeout=httpx.Timeout(180,connect=30),follow_redirects=True,headers={'User-Agent':'EarthAnalogFinder-research-pilot/0.3'}) as client:
        moon=config['moon']
        dem=raw/'pgda-site01-surface.tif';rois=raw/'pgda-site01-rois.tgz'
        md=download(client,moon['dem_url'],dem,config['max_download_mb']);provenance.append(md)
        rm=download(client,moon['roi_url'],rois,config['max_download_mb']);provenance.append(rm)
        center=roi_center(rois,moon['roi_index'])
        target={**extract_terrain(dem,center,'moon',config['grid_m'],config['window_m'],processed/(moon['id']+'.tif')),'id':moon['id'],'name':moon['name'],'source_id':moon['source_id'],'source_url':moon['product_page'],'raw_url':moon['dem_url'],'sha256':md['sha256'],'roi_index':moon['roi_index'],'selection':'Study window centered on the first published ROI bounding-box center; not a final base coordinate.'}
        candidates=[];meteorology=[]
        for site in config['earth']:
            path=raw/(site['id']+'-glo30.tif')
            md=download(client,copernicus_url(site['lat'],site['lon']),path,config['max_download_mb']);provenance.append(md)
            candidate={**extract_terrain(path,(site['lat'],site['lon']),'earth',config['grid_m'],config['window_m'],processed/(site['id']+'.tif')),**site,'source_id':'copernicus-glo30','source_url':'https://registry.opendata.aws/copernicus-dem/','raw_url':md['url'],'sha256':md['sha256'],'selection':'Manually selected pipeline validation window; not a newly discovered analog.'}
            candidates.append(candidate)
            request=config['power']
            params={'parameters':','.join(request['parameters']),'community':'RE','longitude':site['lon'],'latitude':site['lat'],'start':request['start'],'end':request['end'],'format':'JSON','time-standard':request['time_standard']}
            url=str(httpx.URL('https://power.larc.nasa.gov/api/temporal/hourly/point',params=params))
            weather=raw/(site['id']+'-power.json')
            try:
                item=download(client,url,weather,config['max_download_mb']);provenance.append(item)
                data=json.loads(weather.read_text(encoding='utf-8'))
                meteorology.append({'id':site['id'],'name':site['name'],'lat':site['lat'],'lon':site['lon'],'start':request['start'],'end':request['end'],'time_standard':request['time_standard'],'source_id':'nasa-power-hourly','source_url':'https://power.larc.nasa.gov/docs/services/api/temporal/hourly/','raw_url':url,'sha256':item['sha256'],'parameters':power_summary(data),'is_placeholder':False})
            except (httpx.HTTPError,ValueError,KeyError) as error:
                print(f'POWER not imported for {site["id"]}: {error}',flush=True)
            time.sleep(1)
    result={'status':'available','created_at':now,'scope':'Observed terrain pilot only. Three manual Earth windows are not a global analog search or complete mission validation.','grid_m':config['grid_m'],'window_m':config['window_m'],'target':target,'candidates':candidates,'meteorology':meteorology,'downloads':provenance,'uses_placeholder':False,'caveats':['Copernicus is a surface model and can include vegetation and infrastructure.','LOLA Site01 is an interpolated product; uncertainty clones have not been propagated.','Slopes use native-pixel area averaging to a 100 m grid with 200 m central-difference support.','POWER air temperature is not MODIS land-surface temperature. Meteorology is shown as context, not a lunar temperature or illumination score.','The demonstration mission rankings remain separate and still use placeholder measurements.']}
    save_json(observed/'pilot.json',result)
    print(f'Imported {len(candidates)+1} terrain windows, {len(meteorology)} meteorology records, {len(provenance)} source files.',flush=True)
    return result

def main():
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,default=root/'data/ingest/pilot.yaml');parser.add_argument('--data-dir',type=Path,default=Path(os.getenv('DATA_DIR',root/'data')))
    args=parser.parse_args();run(args.config,args.data_dir)

if __name__=='__main__':main()
