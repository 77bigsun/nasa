"""Import reviewed team CSVs; preserve provenance and recompute astronomy.

No scripts from the downloaded branch are executed. Reported reanalysis/terrain
summaries retain their verification limits; PDF-only polar values stay labelled.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import numpy as np

COMMIT='2eb163e0d7ad92ddb565a9c249193e7f3924e955'
SITES=[
 ('ATACAMA_YUNGAY','Atacama - Yungay','known',-24.09,-69.92),
 ('DEATHVALLEY_UBEHEBE','Death Valley - Ubehebe','known',37.01,-117.45),
 ('HAWAII_MAUNAKEA','Mauna Kea','known',19.82,-155.47),
 ('HAWAII_KAU_DESERT','Hawaii - Kau Desert','known',19.35,-155.36),
 ('AZ_BLACK_POINT_LAVA','Black Point Lava Flow','known',35.67,-111.47),
 ('NV_LUNAR_CRATER','Nevada Lunar Crater','known',38.38,-116.07),
 ('ID_CRATERS_OF_MOON','Craters of the Moon','known',43.42,-113.52),
 ('BOLIVIA_UYUNI_SALT','Uyuni Salt Flat','control',-20.20,-67.60),
 ('NM_WHITE_SANDS','White Sands','control',32.78,-106.30),
 ('NV_CUPRITE_CLAY','Cuprite','control',37.54,-117.18),
 ('ALGERIA_GRAND_ERG','Algerian Grand Erg','control',30.50,7.50),
 ('CA_IMPERIAL_CROPS','Imperial Valley Cropland','control',33,-115.50),
]
POLAR=[
 ('CA_HAUGHTON','Haughton Crater',75.38,-89.67,-15,16,46.8,'https://ntrs.nasa.gov/citations/20050169531'),
 ('SJ_ADVENTDALEN','Adventdalen',78.20,15.8,-4,14,41.9,'https://egusphere.copernicus.org/preprints/2024/egusphere-2024-2972/'),
 ('AQ_DRY_VALLEYS','McMurdo Dry Valleys',-77.53,161.7,-19,0,59.9,'https://science.nasa.gov/earth/earth-observatory/martian-landscape-antarctica-4420/'),
]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def solar(latitude):
    hours=np.arange(365*24*6)/6
    day=hours/24+1;g=2*np.pi*(day-1)/365
    decl=(.006918-.399912*np.cos(g)+.070257*np.sin(g)-.006758*np.cos(2*g)
          +.000907*np.sin(2*g)-.002697*np.cos(3*g)+.00148*np.sin(3*g))
    phi=math.radians(latitude);angle=np.radians(15*((hours%24)-12))
    elevation=np.degrees(np.arcsin(np.clip(np.sin(phi)*np.sin(decl)+np.cos(phi)*np.cos(decl)*np.cos(angle),-1,1)))
    daylight=elevation>-.833
    low=float(np.sum(daylight&(elevation<10))/np.sum(daylight))
    dark=~daylight
    if dark.all():longest=len(dark)/6
    else:
        indices=np.flatnonzero(~np.concatenate([dark,dark]))
        longest=min(len(dark),max(0,int(np.diff(indices).max(initial=1))-1))/6
    return {'noon_elevation':90-abs(latitude),'low_sun_fraction':low,'longest_dark':longest}


def record(value,fitness,kind,source,notes=None):
    return {'value':value,'fitness':fitness,'kind':kind,'source':source,'notes':notes or []}


def build(source,root,pdf):
    out=root/'data/lunar';archive=out/'team-source';archive.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for relative in ['results/M4_slope_results.csv','results/new_features_results.csv','results/M5_site_ranges.csv']:
        p=source/relative
        if not p.exists():p=source/Path(relative).name
        target=archive/p.name
        if p.resolve()!=target.resolve():shutil.copyfile(p,target)
        manifest.append({'path':'team-source/'+p.name,'sha256':sha(p),'upstream_path':'moon/'+relative})
    with (archive/'new_features_results.csv').open(encoding='utf-8-sig',newline='') as stream:
        climates={r['site']:r for r in csv.DictReader(stream)}
    with (archive/'M4_slope_results.csv').open(encoding='utf-8-sig',newline='') as stream:
        terrain={r['site']:r for r in csv.DictReader(stream)}
    if set(climates)!={s[0] for s in SITES}:raise ValueError('Unexpected validation-site inventory')
    sites=[];pdf_source={'title':'Team lunar method PDF, pages 3-4','url':'/docs/lunar-method-2026-11-14.pdf'}
    csv_source={'title':'Team CSV results at imported commit','url':f'https://github.com/77bigsun/nasa/blob/{COMMIT}/moon_branch_2026-11-14.zip'}
    astro_source={'title':'Reviewed team astronomical calculation','url':csv_source['url']}
    for sid,name,group,lat,lon in SITES:
        c=climates[sid];t=terrain[sid];features={}
        for fid,value in solar(lat).items():features[fid]=record(value,1,'astronomical_model',astro_source,['365-day year; ten-minute step; no terrain obstruction.'])
        hist=[float(t[k]) for k in ['frac_0-5','5-10','10-15','15-20','20-30','gt30']]
        if any(v<0 for v in hist) or abs(sum(hist)-1)>.005:raise ValueError('Invalid rounded slope histogram')
        features['slope_histogram']=record(hist,1,'team_derived_terrain',csv_source,['Rounded team CSV histogram; raw DEM windows and processing metadata were not included.'])
        features['relief']=record(float(t['relief_m_16km']),1,'team_derived_terrain',csv_source,['Team-reported 16 km elevation range, not the older 2 km pilot metric.'])
        for fid,key in [('annual_mean','M6_annual_mean_C'),('annual_max','M6_annual_max_C'),('annual_min','M3_annual_min_C'),('diurnal_range','M3_diurnal_range_C')]:
            features[fid]=record(float(c[key]),.6,'team_reported_reanalysis',csv_source,['Reported ERA5/Open-Meteo 2014-2023 summary; original API responses/model settings absent.','2 m air temperature is a proxy for the surface thermal environment.'])
        # These aggregate judgements are explicitly reported in PDF table 5.2.
        # They are not inferred for the other validation points.
        ice=.7 if sid=='HAWAII_MAUNAKEA' else 0 if sid in ['BOLIVIA_UYUNI_SALT','DEATHVALLEY_UBEHEBE','NM_WHITE_SANDS','ALGERIA_GRAND_ERG','CA_IMPERIAL_CROPS'] else None
        features['ice_checklist']=record(ice,.3 if ice is not None else 0,'team_reported_assessment',pdf_source,['PDF aggregate judgement only; component evidence and site-specific literature need verification.'])
        sites.append({'id':sid,'name':name,'lat':lat,'lon':lon,'group':group,'coordinate_status':'document_study_point',
            'coordinate_source':pdf_source,'features':features,'ice_cover_status':'not_verified'})
    for sid,name,lat,lon,mean,maximum,reported,coordinate_url in POLAR:
        features={fid:record(value,1,'astronomical_model',astro_source,['365-day year; ten-minute step; no terrain obstruction.']) for fid,value in solar(lat).items()}
        for fid,value in [('annual_mean',mean),('annual_max',maximum)]:
            features[fid]=record(value,.6,'pdf_reported_rounded',pdf_source,['Rounded regional climate summary from the PDF; source period, raw records and exact pixel support were not supplied.'])
        features['ice_checklist']=record(.7,.3,'team_reported_assessment',pdf_source,['PDF aggregate judgement; site-specific supporting references need verification.'])
        sites.append({'id':sid,'name':name,'lat':lat,'lon':lon,'group':'polar','coordinate_status':'approximate_regional_point',
            'coordinate_source':{'title':'Regional coordinate reference','url':coordinate_url},'features':features,
            'ice_cover_status':'not_verified','reported_m6_score':reported})
    for site in sites:
        for entry in site['features'].values():
            if isinstance(entry['value'],(int,float)) and not math.isfinite(entry['value']):raise ValueError('Nonfinite imported value')
    result={'version':'lunar-study-2026-11-14','reference_id':'moon-scr','sites':sites,
        'provenance':{'branch':'moon','commit':COMMIT,'artifacts':manifest,
            'document_sha256':sha(pdf),'document_pages':6,
            'scope':'12 team CSV validation points plus 3 PDF-reported polar regional examples. No global overall-score grid was supplied.',
            'verification':'Astronomy recomputed from coordinates; reported climate/terrain summaries retain their original source-verification limits.'},
        'global_scan':{'status':'not_imported','cells':[],'reported_land_cells':19599,'imported_land_cells':0}}
    (out/'study.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    target=root/'frontend/public/docs/lunar-method-2026-11-14.pdf';target.parent.mkdir(parents=True,exist_ok=True)
    if pdf.resolve()!=target.resolve():shutil.copyfile(pdf,target)
    print('Imported',len(sites),'lunar validation locations; recomputed astronomy; global grid remains unimported.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--pdf',type=Path,required=True)
    args=parser.parse_args();build(args.source,Path(__file__).resolve().parents[1],args.pdf)
