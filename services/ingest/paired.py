"""Build the only runtime measurement snapshot from downloaded scientific products.

Missing, unsupported and unmatched quantities stay missing. Reference datasets
can be shown as context without being used as interchangeable measurements.
"""
import argparse
import copy
import json
from pathlib import Path
import shutil
import numpy as np
import rasterio
import yaml
from .run import extract_terrain, save_json


BLOCKERS = {
    'm1_rock_proxy':'Lunar rock abundance is not imported; Earth thermal contrast is not calibrated to a rock fraction.',
    'm1_radar_rough':'No matched and calibrated Mini-RF / Sentinel-1 / PALSAR radar pair; wavelengths and viewing geometries differ.',
    'm4_radar_rough':'No matched and calibrated radar roughness pair at the selected footprints.',
    'm3_diurnal_range':'Actual thermal samples are present, but a multi-year lunar cycle and sparse Earth overpasses do not measure the same diurnal extrema.',
    'm3_cold_hours':'Sparse MODIS overpasses cannot establish continuous hours below a temperature threshold; no duration is filled in.',
    'm3_abs_temp':'Observed temperatures are shown, but the lunar extreme is outside the Earth-reproducible test range and is excluded.',
    'm4_looseness':'Thermal contrast is imported as context; no validated cross-planet soil-looseness calibration is available.',
    'm5_tir_mineral':'A matched Diviner Christiansen / Earth thermal-emissivity product pair and spectral-response calibration are not imported.',
    'm5_vswir_mineral':'No site-matched M3 / EMIT spectra on a common calibrated wavelength grid are imported.',
    'm5_grain_proxy':'Thermal contrast does not directly measure grain size; a calibrated paired grain-size proxy is missing.',
    'm6_ice_depth':'The lunar PRP value is a thermophysical stable-ice model; neither it nor Earth active-layer thickness is a direct paired ice-depth measurement.',
    'm6_annual_temp':'The lunar model is annual mean at 2 cm depth; Earth MODIS here samples January surface temperature. Depth and temporal support differ.',
    'm6_permafrost':'No comparable validated categorical ice/permafrost pair at these footprints is available.',
    'm6_hydrogen':'No matched LEND/Mini-RF hydrogen signal and calibrated terrestrial counterpart are imported.',
    'm6_cold_trap':'A finite near-field horizon is imported as context; one local cycle does not establish permanent shadow or buried ice.',
    'r1_slope_1_5m':'Earth GLO-30 cannot resolve 1-5 m slopes. A colocated terrestrial lidar/DTM product is required.',
    'r1_rock':'No calibrated numeric rock-fraction pair at centimetre landing-hazard scales is available.',
    'r1_thermal_inertia':'TES thermal inertia and Earth sampled LST contrast have different units and physics; percentile defaults are not invented.',
    'r2_texture':'Actual Sentinel-2 texture context is imported; no matched calibrated Mars image texture at common support is imported.',
    'r2_dune_fraction':'No validated dune segmentation or annotation pair is imported; a brightness texture is not a dune fraction.',
    'r3_ground_ice':'Actual SWIM ice consistency is imported; it is not comparable to Earth soil moisture, ice fraction or active-layer thickness.',
    'r3_polygons':'No validated polygon-presence annotations at comparable spatial resolution are imported.',
    'r3_subsurface_radar':'No calibrated SHARAD / terrestrial radar profile pair with compatible depth sensitivity is available.',
    'r4_hydrated_spectra':'No site-matched CRISM/OMEGA and Earth hydrated-mineral spectra with a common wavelength grid are imported.',
    'r5_landform':'No validated paired landform classes are imported; DEM roughness does not identify a glacial landform.',
    'r5_polygon_size':'No paired high-resolution polygon annotations are imported; Sentinel-2 pixels alone do not establish polygon size.',
    'r6_dust':'One REMS sol is not dust seasonality; no matched seasonal aerosol/dust product pair is imported.',
    'r6_wind_speed':'Gale wind samples do not pass the selected quality filter; Earth POWER 10 m winds cannot fill missing rover wind.',
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def source(title, url):
    return {'title':title, 'url':url}


def evidence(value, unit, quantity, method, spatial, temporal, sources, key='', hashes=(), notes=()):
    return {
        'value':value, 'unit':unit, 'quantity':quantity,
        'status':'usable' if key else 'context_only', 'comparison_key':key,
        'method':method, 'spatial_support':spatial, 'temporal_support':temporal,
        'sources':sources, 'hashes':list(hashes), 'notes':list(notes),
    }


def blank():
    return {'is_placeholder':False,'values':{},'categories':{},'spectra':{},'series':{},
            'planet_values':{},'evidence':{},'distributions':{}}


def put(item, fid, record, series=None, distribution=None):
    item['evidence'][fid] = record
    if record['status'] == 'usable' and isinstance(record['value'], (float,int)):
        item['values'][fid] = record['value']
    if series is not None:
        item['series'][fid] = series
    if distribution is not None:
        item['distributions'][fid] = distribution


def longest_dark(series):
    mask = np.asarray(series['values']) < .5
    if mask.all():
        return float(len(mask)*series['step_hours'])
    best = current = 0
    for dark in np.concatenate([mask,mask]):
        current = current+1 if dark else 0
        best = max(best,current)
    return float(min(best,len(mask))*series['step_hours'])


def rms_height(path, spacing=100):
    with rasterio.open(path) as src:
        z = src.read(1, masked=True).astype(float).filled(np.nan)[1:-1,1:-1]
    y,x = np.indices(z.shape)
    good = np.isfinite(z)
    design = np.column_stack([x[good]*spacing,y[good]*spacing,np.ones(good.sum())])
    plane = np.linalg.lstsq(design,z[good],rcond=None)[0]
    return float(np.sqrt(np.mean((z[good]-design@plane)**2)))


def terrain_records(item, record, sources, sha, roughness=None, slope100=None):
    support = '2 km window; 100 m area-averaged grid; 200 m central-difference slope support'
    notes = ['Common analysis scale does not remove source error or interpolation uncertainty.',
             'Three manually selected Earth windows; not a global analog search.']
    for fid in ['m1_slope','m4_slope_dist']:
        e = evidence(record['statistics']['mean_slope_deg'],'deg','Terrain slope distribution',
                     'Native DEM pixels area-averaged, then central-difference slope',support,
                     'Source DEM acquisition epochs differ; static-terrain comparison',sources,
                     key='slope_distribution_grid100_support200_window2000',
                     hashes=[sha],notes=notes)
        put(item,fid,e,distribution=record['slope_samples_deg'])
    if roughness is not None:
        put(item,'r5_roughness',evidence(roughness,'m','Detrended terrain RMS height',
            'RMS height after least-squares removal of a best-fit plane',support,
            'Static-terrain comparison',sources,key='detrended_rms_grid100_window2000',
            hashes=[sha],notes=notes+['This is topographic roughness, not radar roughness or a landform classification.']))
    if slope100 is not None:
        put(item,'r1_slope_100m',evidence(slope100['statistics']['mean_slope_deg'],'deg',
            'Mean slope at 100 m gradient support','Area-average to 50 m grid; central differences over 100 m',
            '2 km window; 50 m grid; 100 m gradient support','Static-terrain comparison',sources,
            key='mean_slope_grid50_support100_window2000',hashes=[sha],notes=notes))


def solar_records(item, model, sources, scope):
    common = dict(spatial='2 m observer; 100 m DEM grid; terrain horizon truncated at 1 km',
                  temporal='2025-01-01 start; one physical local solar cycle',
                  sources=sources, notes=[scope,'Model-derived from actual ephemerides and DEM; not a measured power output.'])
    illum = dict(model['illumination'],value_unit='fraction',quantity='Finite-horizon solar visibility')
    elevation = dict(model['elevation'],value_unit='deg',quantity='Solar elevation')
    put(item,'m2_illum_fraction',evidence(float(np.mean(illum['values'])),'fraction','Finite-horizon solar visibility',
        'SPICE Sun position and local terrain obstruction',key='spice_nearfield1km_illumination_fraction',**common),series=illum)
    put(item,'m2_sun_elevation',evidence(float(np.mean(elevation['values'])),'deg','Mean solar elevation over a local cycle',
        'SPICE Sun vector in documented body-fixed frame',key='spice_cycle_mean_solar_elevation',**common),series=elevation)
    put(item,'m2_horizon',evidence(float(np.mean(model['horizon_deg'])),'deg','Mean near-field horizon elevation',
        '24 geographic-azimuth sectors, 1 km maximum radius',key='nearfield_horizon_1km_grid100_observer2m',**common))
    put(item,'m3_max_dark',evidence(longest_dark(illum),'h','Longest modelled continuous darkness',
        'Circular run length of finite-horizon visibility samples, in physical Earth hours',
        key='spice_nearfield1km_longest_dark_hours',**common),series=illum)
    put(item,'m6_cold_trap',evidence(float(np.mean(model['horizon_deg'])),'deg','Local terrain enclosure proxy',
        'Near-field horizon summary only',**common))


def build(data_dir, source_dir):
    data_dir, source_dir = Path(data_dir), Path(source_dir)
    pilot = read(data_dir/'observed/pilot.json')
    solar = read(data_dir/'observed/solar.json')
    mars = read(source_dir/'mars/ready.json')
    moon = source_dir/'moon';earth = source_dir/'earth'
    target = blank(); candidates = []
    solar_sources = [source('NASA NAIF '+s['url'].split('/')[-1],s['url']) for s in solar['sources']]
    lunar = pilot['target']
    terrain_records(target,lunar,[source('LOLA adjusted Site01 DEM',lunar['raw_url'])],lunar['sha256'])
    solar_records(target,solar['sites'][lunar['id']],solar_sources+[source('LOLA Site01',lunar['source_url'])],solar['scope'])
    for site in pilot['candidates']:
        item = dict(blank(),id=site['id'],name=site['name'],name_en=site['name'],
                    lat=site['lat'],lon=site['lon'],known_analog=site['id']=='earth-pilot-nevada')
        if site['id']=='earth-pilot-nevada':item.update(name='Death Valley study window',name_en='Death Valley study window')
        raw = data_dir/'raw'/(site['id']+'-glo30.tif')
        fine = extract_terrain(raw,(site['lat'],site['lon']),'earth',50,2000,
                               data_dir/'processed'/(site['id']+'-50m.tif'))
        terrain_records(item,site,[source('Copernicus GLO-30 DSM',site['raw_url'])],site['sha256'],
                        rms_height(data_dir/'processed'/site['derived_file']),fine)
        solar_records(item,solar['sites'][site['id']],solar_sources+[source('Copernicus DSM',site['source_url'])],solar['scope'])
        modis = read(earth/(site['id']+'-modis.json'))
        sentinel = read(earth/(site['id']+'-sentinel.json'))
        msources = [source('Terra MOD11A1 v061 on Microsoft Planetary Computer',modis['source_url'])]
        valid = [r for r in modis['records'] if r.get('paired_pixels',0)>0]
        if valid:
            msources += [source(valid[0]['item_id'],valid[0]['assets']['LST_Day_1km']['href'])]
        note = ('MODIS day/night overpasses do not determine an hourly thermal waveform or cold-duration hours. '
                'A January Earth sample and a multi-year lunar cumulative cell have different temporal and spatial support.')
        context = dict(method='QA-filtered paired day/night native pixels; no gap interpolation',
            spatial='3 x 3 native MODIS pixels, approximately 2.78 km square',temporal=modis['period'],
            sources=msources,notes=[note,f"Valid paired days: {modis['valid_paired_days']}; best-QA days: {modis['best_qa_days']}."])
        for fid in ['m3_diurnal_range','r1_thermal_inertia','m1_rock_proxy','m4_looseness','m5_grain_proxy']:
            put(item,fid,evidence(modis['day_night_difference_kelvin'],'K','Observed paired day/night LST contrast',**context))
        put(item,'m3_abs_temp',evidence(modis['observed_min_kelvin']-273.15,'C','Minimum sampled land-surface temperature',**context))
        put(item,'m6_annual_temp',evidence((modis['day_kelvin']+modis['night_kelvin'])/2,'K',
            'January day/night sampled surface temperature, not annual ground temperature',**context))
        # Actual MODIS local view times are optional; nominal overpass times are never invented.
        samples = modis.get('overpass_samples',[])
        if samples:
            samples = sorted(samples,key=lambda r:r['phase'])
            item['series']['m3_diurnal_range'] = {'phase':[s['phase'] for s in samples],
                'values':[s['temperature_kelvin'] for s in samples],'step_hours':None,
                'value_unit':'K','quantity':'Land-surface temperature',
                'period':'Actual MODIS local view-time samples, January 2025; irregular observations, not an hourly cycle'}
        put(item,'r2_texture',evidence(sentinel['surface_reflectance_sd'],'reflectance',
            'Sentinel-2 B04 reflectance spatial standard deviation',
            'Scaled BOA reflectance; SCL land-only mask; native 10 m pixels','2 km window; 10 m B04; SCL nearest-neighbour mask',
            sentinel['datetime'],[source('Sentinel-2 L2A '+sentinel['item_id'],sentinel['assets']['B04']['href'])],
            hashes=[sentinel['assets']['B04']['sha256']],notes=[
                'No matched calibrated Mars image texture is imported. Different cameras and illumination require validation.',
                'Crop SHA-256 identifies the derived native-window GeoTIFF, not the entire remote tile.']))
        power = next(x for x in pilot['meteorology'] if x['id']==site['id'])
        for fid, parameter, unit, quantity in [
            ('r6_air_temp','T2M','C','Near-surface air-temperature cycle'),
            ('r6_wind_speed','WS10M','m/s','Wind-speed cycle')]:
            values = power['parameters'][parameter]
            key = 'near_surface_air_temperature_cycle_range' if parameter=='T2M' else ''
            notes = ['Earth January 2025 monthly mean local-solar cycle versus one Gale sol in May 2015; no matched-season or annual claim.',
                     'POWER is coarse-grid meteorology, not a colocated field instrument.']
            if parameter=='WS10M':
                notes += ['POWER wind is at 10 m; Gale has no reliable paired wind samples.']
            series = {'phase':values['phase'],'values':values['mean_cycle'],'step_hours':1,'value_unit':unit,'quantity':quantity,'period':'NASA POWER January 2025 hourly local-solar bin means'}
            put(item,fid,evidence(float(np.ptp(values['mean_cycle'])),unit,quantity,
                'Range of observed/reanalysis local-solar bin means','POWER 2 m air temperature / 10 m wind; coarse grid',
                '2025-01-01/2025-01-31',[source('NASA POWER hourly',power['raw_url'])],key=key,
                hashes=[power['sha256']],notes=notes),series=series)
        candidates.append(item)
    gcp = read(moon/'gcp_target.json');prp = read(moon/'prp_target.json')
    rows = np.asarray(gcp['rows'])
    kelvin = rows[:,-1]
    phase = rows[:,2]/24
    good = np.isfinite(kelvin)&(kelvin>0)&(kelvin!=-9999)
    cycle = {'phase':phase[good].tolist(),'values':kelvin[good].tolist(),
             'step_hours':29.530588853*.25,'value_unit':'K','quantity':'Bolometric temperature','period':'Diviner GCP 2009-2015 cumulative local-time bins; coarse 0.5 degree cell'}
    thermal = dict(method='Positive valid bolometric temperatures from PDS GCP fixed-width table; no gap filling',
        spatial=f"0.5 degree cell centered at {gcp['grid_lat']}, {gcp['grid_lon']}; not the 2 km DEM window",
        temporal='Cumulative 2009-2015; 96 local-time bins',sources=[source('Diviner GCP numeric table',gcp['url'])])
    # Keep the cumulative orbital cycle separate from the finer PRP model triangle.
    put(target,'m3_diurnal_range',evidence(float(np.ptp(kelvin[good])),'K','Range of cumulative bolometric thermal cycle',
        method=thermal['method'],spatial=thermal['spatial'],
        temporal=thermal['temporal'],sources=thermal['sources'],hashes=[gcp['sha256']],
        notes=['The cumulative lunar cycle and sparse Earth overpasses are displayed as evidence, not scored as equivalent thermal sampling.']),series=cycle)
    put(target,'m3_abs_temp',evidence(float(kelvin[good].min()-273.15),'C','Minimum cumulative bolometric temperature',
        thermal['method'],thermal['spatial'],thermal['temporal'],thermal['sources'],hashes=[gcp['sha256']]))
    for fid,value,unit,quantity in [
        ('m6_ice_depth',prp['model_stable_ice_depth_m'],'m','Modelled stable-ice depth, not detected ice'),
        ('m6_annual_temp',prp['annual_mean_2cm_K'],'K','Modelled annual-mean temperature at 2 cm depth')]:
        put(target,fid,evidence(value,unit,quantity,'PDS PRP containing-triangle model value; no interpolation',
            f"Containing triangle near {prp['centroid_lat']}, {prp['centroid_lon']}",'Long-term thermophysical model',
            [source('Diviner PRP numeric model table',prp['url'])],hashes=[prp['range_sha256']],
            notes=['Stable-ice model depth is not measured ice or terrestrial active-layer thickness.']))
    for name in ['gale-dtm.tif','gale-dtm-100m.tif']:
        shutil.copyfile(source_dir/'mars'/name,data_dir/'processed'/name)
    targets = {'moon-scr':target}
    gale = blank();terrain = mars['terrain'];weather = mars['weather']
    terrain_records(gale,terrain['metrics']['100'],[source('HiRISE Gale DTM',terrain['raw_url'])],terrain['raw_sha256'],
        terrain['metrics']['100']['statistics']['detrended_rms_height_m'],terrain['metrics']['50'])
    air = weather['air_temperature']
    gseries = {key:air[key] for key in ['phase','values','step_hours','period']}
    put(gale,'r6_air_temp',evidence(float(np.ptp(air['values'])),'C','Near-surface air-temperature cycle',
        'Quality-filtered calibrated REMS samples, hourly LMST bin means','Gale regional REMS record, approximately 1.6 m above the surface; rover trajectory not registered to the selected DTM pixel',
        f"Curiosity sol 1000; {weather['start']}/{weather['end']}",
        [source('Certified REMS PDS4 '+str(weather['sol']),v['url']) for v in weather['provenance']],
        key='near_surface_air_temperature_cycle_range',hashes=[v['sha256'] for v in weather['provenance']],
        notes=weather['caveats']),series=gseries)
    gseries.update(value_unit='C',quantity='Near-surface air temperature')
    gale['series']['r6_air_temp']=gseries
    gale['evidence']={k:v for k,v in gale['evidence'].items() if k.startswith('r')}
    gale['values']={k:v for k,v in gale['values'].items() if k.startswith('r')}
    gale['distributions']={k:v for k,v in gale['distributions'].items() if k.startswith('r')}
    targets['mars-gale'] = gale
    ap = blank();tes = mars['tes']
    put(ap,'r1_thermal_inertia',evidence(tes['ap105']['value'],tes['units'],'TES nighttime thermal inertia',
        'Big-endian int16 native pixel; quality mask 1 (not interpolated)','Native approximately 2.96 km TES pixel',
        'Observations February 1999-April 2004; 2007 derived release',[source('TES numeric thermal inertia',tes['data_url']),
        source('TES quality mask',tes['mask_url'])],notes=tes['caveats']))
    if mars.get('swim'):
        swim = mars['swim']
        put(ap,'r3_ground_ice',evidence(swim['ap105']['value'],'consistency index','SWIM 1-5 m ice consistency',
            'Native SWIM composite sample; not an ice fraction or probability','Approximately 2.96 km native pixel',
            'SWIM2 multi-instrument composite',[source('SWIM2 numeric ice consistency',swim['raw_url'])],
            notes=['A unitless multi-instrument consistency index cannot be scored against Earth soil moisture or permafrost temperature.']))
    targets['mars-ap105'] = ap
    snapshot = {'mode':'observed','candidates':candidates,'targets':targets}
    from services.shared.contracts import MeasurementSnapshot
    MeasurementSnapshot.model_validate(snapshot)
    save_json(data_dir/'observed/mission-measurements.json',snapshot)
    # Every task/feature is mapped, including those with unavailable measurements.
    pairings = []
    for mission in ['moon','mars']:
        tasks = yaml.safe_load((data_dir/f'seed/tasks_{mission}.yaml').read_text(encoding='utf-8'))
        for task in tasks:
            for f in task['features']:
                actual = [(sid,t['evidence'][f['id']]) for sid,t in targets.items() if sid.startswith(mission+'-') and f['id'] in t['evidence']]
                ready = [sid for sid,e in actual if e['status']=='usable' and any(c['evidence'].get(f['id'],{}).get('status')=='usable' for c in candidates)]
                pairings.append({'mission':mission,'task_id':task['id'],'feature_id':f['id'],'name':f['name'],
                    'planet_sources':f['planet_data'],'earth_sources':f['earth_data'],
                    'planet_products':list({x['url']:x for _,e in actual for x in e['sources']}.values()),
                    'earth_products':list({x['url']:x for c in candidates for x in c['evidence'].get(f['id'],{}).get('sources',[])}.values()),
                    'status':'paired' if ready else 'context_only' if actual or any(f['id'] in c['evidence'] for c in candidates) else 'missing',
                    'ready_sites':ready,'observed_sites':[sid for sid,e in actual],
                    'reason':'Comparable source quantities imported; see each feature for support and limitations.' if ready else
                        'Some source values are imported, but quantity, sampling or coverage is not comparable; no score is invented.' if actual or any(f['id'] in c['evidence'] for c in candidates) else
                        'No validated pair of numeric products at the selected footprints; calibration, access or high-resolution coverage is still required.'})
    for row in pairings:
        if row['status']!='paired':row['reason']=BLOCKERS.get(row['feature_id'],row['reason'])
    save_json(data_dir/'observed/task-pairings.json',pairings)
    print(f"Observed runtime snapshot: {len(candidates)} Earth windows, {len(targets)} planetary targets, "
          f"{sum(p['status']=='paired' for p in pairings)}/{len(pairings)} comparable features.",flush=True)
    return snapshot


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir',type=Path,default=root/'data')
    parser.add_argument('--source-dir',type=Path,default=root/'data/raw/missions')
    args = parser.parse_args()
    build(args.data_dir,args.source_dir)


if __name__ == '__main__':
    main()
