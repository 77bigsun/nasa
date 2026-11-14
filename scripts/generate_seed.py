"""Rebuild deterministic English placeholder fixtures from SPEC tables.

Run only to intentionally reset data/seed. Scientific values remain synthetic.
"""
from pathlib import Path
import json
import math
import random
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data' / 'seed'
SPEC = (ROOT / 'docs' / 'SPEC.md').read_text(encoding='utf-8-sig')
RNG = random.Random(42)

def write(name, data):
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / name).write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')

def rows(section, prefix):
    text = SPEC.split(section, 1)[1]
    return [[x.strip() for x in line.strip().strip('|').split('|')] for line in text.splitlines() if line.startswith(prefix)]

SOURCES = [
 ('earthdata','NASA Earthdata Search',True,'https://search.earthdata.nasa.gov/'),
 ('worldview','NASA Worldview',True,'https://worldview.earthdata.nasa.gov/'),
 ('pds','NASA Planetary Data System (PDS)',True,'https://pds.nasa.gov/'),
 ('lro','NASA LRO',True,'https://science.nasa.gov/mission/lro/'),
 ('diviner','NASA LRO Diviner Lunar Data',True,'https://pds-geosciences.wustl.edu/missions/lro/diviner.htm'),
 ('copernicus','Copernicus Data Space Ecosystem',True,'https://dataspace.copernicus.eu/'),
 ('esa','ESA Open Science Catalog',True,'https://opensciencedata.esa.int/'),
 ('jaxa','JAXA G-Portal',True,'https://gportal.jaxa.jp/gpr/'),
 ('rcm','CSA RADARSAT Constellation Mission (RCM)',True,'https://www.asc-csa.gc.ca/eng/satellites/radarsat/'),
 ('radarsat','CSA RADARSAT-1',True,'https://www.asc-csa.gc.ca/eng/satellites/radarsat1/'),
 ('sar','CSA SAR Python Tutorial',True,'https://github.com/asc-csa/Synthetic_Aperture_Radar_Tutorial'),
 ('pgda','NASA PGDA',False,'https://pgda.gsfc.nasa.gov/'),
 ('trek','Moon Trek / Mars Trek',False,'https://trek.nasa.gov/'),
 ('ctx','Caltech CTX Global Mosaic',False,'https://murray-lab.caltech.edu/CTX/'),
 ('themis','ASU THEMIS Thermal Inertia',False,'https://themis.asu.edu/'),
 ('swim','SWIM Subsurface Ice Maps',False,'https://swim.psi.edu/'),
 ('mcd','Mars Climate Database (LMD)',False,'https://www-mars.lmd.jussieu.fr/'),
 ('power','NASA POWER',False,'https://power.larc.nasa.gov/'),
 ('cci','ESA CCI Permafrost',False,'https://climate.esa.int/en/projects/permafrost/'),
 ('shadowcam','ShadowCam',False,'https://www.shadowcam.asu.edu/'),
 ('dunes','USGS Mars Global Dune Database',False,'https://astrogeology.usgs.gov/'),
 ('rgi','Randolph Glacier Inventory',False,'https://www.glims.org/RGI/')
]
NASA_MOON='https://www.nasa.gov/moonbase-phases/'
NASA_MARS='https://science.nasa.gov/mission/skyfall/'
TASK_EN=['Precision landing','Low-angle illumination & power','Darkness & extreme cold','Extreme terrain mobility','Regolith operations','Cold-trap ice prospecting','Landing surface conditions','Visual navigation','Shallow subsurface ice','Hydrated minerals','Glacial & periglacial terrain','Dust & near-surface weather']
ORDERS={'moon':[6,4,2,3,1,5],'mars':[1,4,2,5,6,3]}
RANKS={'moon':[(27,3),(13,2),(2,1),(8,2),(1,1),(55,6)],'mars':[(10,2),None,(52,6),None,None,(35,4)]}
FEATURE_EN=['Multiscale slope','Rock coverage proxy','Radar roughness','Illumination fraction','Solar elevation','Horizon obstruction','Diurnal temperature range','Cold exposure hours','Longest darkness','Absolute surface temperature','Slope distribution','Surface looseness','Radar roughness','Thermal infrared mineral signature','Visible / SWIR mineral spectrum','Grain size proxy','Ice depth','Annual temperature','Permafrost','Hydrogen / ice signal','Cold-trap terrain','100 m slope','1–5 m slope','Rock fraction','Thermal inertia','Image texture','Dune fraction','Ground ice','Polygonal terrain','Subsurface radar','Hydrated mineral spectrum','Landform class','Polygon size','Surface roughness','Dust seasonality','Wind / temperature cycle']
FEATURE_NAMES={}
SOURCE_USE={x[0]:[] for x in SOURCES}

def source_entries(raw, side):
    # Resources denotes the competition list, not institutional ownership.
    out=[]
    for part in raw.split(';'):
        label=part.replace('✅','').replace('➕','').strip()
        if not label: continue
        key = ('cci' if 'CCI' in label else 'mcd' if 'MCD' in label else 'swim' if 'SWIM' in label else 'ctx' if '➕' in part and 'CTX' in part else 'pgda' if 'PGDA' in label else 'dunes' if 'dune database' in label.lower() else 'rgi' if 'RGI' in label else 'diviner' if 'Diviner' in label else 'lro' if any(t in label for t in ['LOLA','Mini-RF','LEND','SPICE']) else 'pds' if side=='planet' else 'copernicus' if any(t in label for t in ['Copernicus','Sentinel']) else 'jaxa' if 'PALSAR' in label else 'radarsat' if 'RADARSAT' in label else 'earthdata')
        entry=next(s for s in SOURCES if s[0]==key)
        out.append({'name':label,'official':'➕' not in part,'source_id':key,'url':entry[3]})
    return out

all_tasks=[]
findex=0
for mission, section in [('moon','### 4.2'),('mars','### 4.3')]:
    block=SPEC.split(section,1)[1].split('### 4.',1)[0]
    taskrows=[[x.strip() for x in line.strip('|').split('|')] for line in block.splitlines() if re.match(r'^\| [MR]\d \|',line)]
    tasks=[]
    for idx,row in enumerate(taskrows[:6]):
        tid,name,verify,basis,rank,order,manual=row
        n=RANKS[mission][idx]
        task={'id':tid,'mission':mission,'name':name,'name_en':TASK_EN[(0 if mission=='moon' else 6)+idx], 'verify':verify,'nasa_basis':basis,'nasa_url':NASA_MOON if mission=='moon' else NASA_MARS,'tech_gap':{'rank':n[0],'bin':n[1],'label':rank} if n else None,'order':ORDERS[mission][idx], 'manual_adjust':None if manual=='—' else {'reason':manual},'notes':[],'features':[]}
        task['notes']=[('Align local solar phase; a lunar solar day is about 29.5 Earth days.' if mission=='moon' else 'Align local time and solar longitude Ls; a Martian year is about 687 Earth days.'),'Use Copernicus DEM for terrain. All demo values are synthetic, not observations.']
        if tid in ['M1','M4']:task['notes'].append('Quantitative slope and rock thresholds need literature review; use profile comparisons for now.')
        if tid in ['M4','M6']:task['notes'].append('M4 and M6 can share a site; integration bonuses apply after fixing minimum site count.')
        if mission=='mars':task['notes'].append('The five SkyFall regions lack lander measurements. Engineering constraints and gap ranks follow the team brief and require source review.')
        tasks.append(task)
    frows=[[x.strip() for x in line.strip('|').split('|')] for line in block.splitlines() if re.match(r'^\| [MR]\d \| [mr]\d_',line)]
    for tid,fid,name,kind,mode,pdata,edata,note in frows:
        threshold={'r1_slope_100m':{'ideal_max':5,'zero_at':15},'r1_slope_1_5m':{'ideal_max':12,'zero_at':15},'r2_dune_fraction':{'ideal_max':.05,'zero_at':.3}}.get(fid)
        stat={'m2_illum_fraction':'fraction_above','m2_sun_elevation':'mean','m3_diurnal_range':'range','m3_cold_hours':'hours_below','m3_max_dark':'longest_below','r6_dust':'mean','r6_wind_temp':'range'}.get(fid,'mean')
        f={'id':fid,'name':name,'name_en':FEATURE_EN[findex],'type':kind,'compare_mode':mode,'unit':'deg' if any(x in fid for x in ['slope','elevation','horizon']) else 'h' if fid in ['m3_cold_hours','m3_max_dark'] else '°C' if fid=='m3_abs_temp' else 'm' if fid in ['m6_ice_depth','r5_polygon_size'] else '', 'weight':1.,'threshold':threshold,'planet_threshold':{'max':.05} if fid=='r1_rock' else {'zero_at':100,'ideal_min':150} if fid=='r1_thermal_inertia' else None,'out_of_earth_range':fid=='m3_abs_temp','earth_proxy':'earth_proxy' in note or fid in ['m1_rock_proxy','m4_looseness','m5_grain_proxy','r1_rock','r1_slope_1_5m'],'planet_data':source_entries(pdata,'planet'),'earth_data':source_entries(edata,'earth'),'notes':[note] if note else [],'stat':stat,'stat_threshold':0,'rank_stat_threshold':5 if fid=='m3_cold_hours' else None}
        if mode=='relative_rank':f['notes'].append('Cross-planet units differ: compare percentiles only; planetary thresholds do not score Earth candidates.')
        for source in f['planet_data']+f['earth_data']:SOURCE_USE[source['source_id']].append(fid)
        FEATURE_NAMES[fid]=f
        next(task for task in tasks if task['id']==tid)['features'].append(f)
        findex+=1
    write(f'tasks_{mission}.yaml',tasks)
    all_tasks+=tasks

write('missions.yaml',[
 {'id':'moon','name':'Moon: Permanent Base Candidates','name_en':'Moon: Permanent Base Candidates','goal':'Find a compact network of Earth sites for six lunar south-polar base tests.','goal_en':'Find a compact network of Earth sites for six lunar south-polar base tests.','summary':'South-polar illumination, long darkness, and cold-trap resources create linked engineering tests. The 5 kW and 120-hour targets and gap ordering follow the team brief and require original-source review.','summary_en':'South-polar illumination, long darkness, and cold-trap resources create linked engineering tests. The 5 kW and 120-hour targets and gap ordering follow the team brief and require original-source review.','nasa_sources':[{'title':"Moon Base User's Guide",'url':NASA_MOON},{'title':'Moon to Mars Architecture','url':'https://www.nasa.gov/moontomarsarchitecture/'}]},
 {'id':'mars','name':'Mars: Landing & Exploration','name_en':'Mars: Landing & Exploration','goal':'Connect landing, navigation, and subsurface ice requirements to complementary Earth sites.','goal_en':'Connect landing, navigation, and subsurface ice requirements to complementary Earth sites.','summary':'SkyFall links three-helicopter exploration to geology, climate, and subsurface ice. AP-105 coordinates and engineering constraints are team-supplied design cases, not a confirmed landing selection.','summary_en':'SkyFall links three-helicopter exploration to geology, climate, and subsurface ice. AP-105 coordinates and engineering constraints are team-supplied design cases, not a confirmed landing selection.','nasa_sources':[{'title':'NASA SkyFall','url':NASA_MARS},{'title':'SR-1 Freedom','url':'https://www.nasa.gov/mission/space-reactor-1-freedom/'}]}
])
sites=[]
for mission in ['moon','mars']:
    section='### 4.2' if mission=='moon' else '### 4.3'
    for row in rows(section,'| '+mission+'-'):
        sid,name,*rest=row
        lat,lon,status=None,None,'todo'
        if sid=='mars-ap105':lat,lon,status=43.3295,198.5228,'exact'
        if sid=='mars-jezero':lat,lon,status=18.4,77.5,'approx'
        if sid=='mars-gale':lat,lon,status=-5.4,137.8,'approx'
        description='Team-supplied target. Feature values currently use deterministic placeholders.'
        sites.append({'id':sid,'mission':mission,'name':name,'name_en':name,'source':rest[-1],'description':description,'description_en':description,'lat':lat,'lon':lon,'coords_status':status})
write('target_sites.yaml',sites)
limits={}
for mission in ['moon','mars']:
    block=SPEC.split(f'**Earth limitations (earth_limits, mission: {mission})**',1)[1].split('### ',1)[0]
    limits[mission]=[dict(zip(['condition','planet','reproducible','handling'],[x.strip() for x in line.strip('|').split('|')])) for line in block.splitlines() if line.startswith('| ') and not line.startswith('| Condition')]
block=SPEC.split('**SkyFall landing engineering constraints**',1)[1].split('| id |',1)[0]
constraints=[dict(zip(['condition','requirement','earth_analog'],[x.strip() for x in line.strip('|').split('|')])) for line in block.splitlines() if line.startswith('| ') and not line.startswith('| Condition')]
write('earth_limits.yaml',limits)
write('constraints.yaml',{'moon':[],'mars':constraints})
write('data_sources.yaml',[{'id':key,'name':name,'portal':name,'official':official,'url':url,'status':'TODO' if url is None else 'portal','used_by':sorted(set(SOURCE_USE[key])),'notes':'Official denotes the competition Resources list. Product links, versions, coverage, and licensing require team review.'} for key,name,official,url in SOURCES])
write('earth_facts.yaml',{'source':{'title':'NASA Planetary Fact Sheet','url':'https://nssdc.gsfc.nasa.gov/planetary/factsheet/'},'notes':'Day length is the solar day, not sidereal rotation. Lunar shadow temperatures are local extremes, not global averages.','rows':[
 {'name':'Surface gravity','name_en':'Surface gravity','earth':'1 g','moon':'0.166 g','mars':'0.38 g'},
 {'name':'Solar day','name_en':'Solar day','earth':'24 h','moon':'29.5 Earth days','mars':'24 h 39 min'},
 {'name':'Surface pressure','name_en':'Surface pressure','earth':'1013 hPa','moon':'≈ 0 hPa','mars':'≈ 6 hPa'},
 {'name':'Surface temperature','name_en':'Surface temperature','earth':'≈ 15°C','moon':'< −230°C / > 100°C','mars':'≈ −60°C'},
 {'name':'Global intrinsic magnetic field','name_en':'Global intrinsic magnetic field','earth':'Yes','moon':'No','mars':'No'}]})
write('categorical_tables.yaml',{'m6_permafrost':{'yes':{'yes':1.,'no':0.,'unknown':.5},'no':{'yes':0.,'no':1.,'unknown':.5}},'r3_polygons':{'present':{'present':1.,'absent':0.},'absent':{'present':0.,'absent':1.}},'r5_landform':{a:{b:(1. if a==b else .7 if {a,b}=={'polygonal_terrain','patterned_ground'} else .4 if 'debris_apron' in [a,b] else .3) for b in ['polygonal_terrain','patterned_ground','debris_apron','plain']} for a in ['polygonal_terrain','patterned_ground','debris_apron','plain']}})
write('method.yaml',{'tau':.7,'sigma':1.,'sigma_rank':.15,'epsilon':1e-6,'similar_cutoff':.7,'different_cutoff':.4,'weight_scheme':'roc','sensitivity':{'n_samples':500,'alpha':1.,'seed':42},'integration_bonus':[{'tasks':['M4','M6'],'bonus':.05}],'map':{'gibs_url':'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg','max_zoom':8,'fallback_url':'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'}})

# Coordinates are illustrative land locations; names deliberately avoid discovery claims.
COORDS=[(36,-116),(64,-147),(68,20),(-24,135),(31,-7),(43,104),(38,29),(46,93),(40,-4),(-32,24),(60,25),(56,99),(-22,25),(47,69),(35,70),(62,130),(-15,133),(51,-106),(39,-111),(69,88)]
def fixture(quality=0., target=False):
    item={'is_placeholder':True,'values':{},'categories':{},'spectra':{},'series':{},'planet_values':{'r1_rock':.03,'r1_thermal_inertia':160.} if target else {}}
    for fid,f in FEATURE_NAMES.items():
        if f['type']=='categorical':
            options={'m6_permafrost':['yes','no'],'r3_polygons':['present','absent'],'r5_landform':['polygonal_terrain','patterned_ground','debris_apron','plain']}[fid]
            item['categories'][fid]=options[0] if target or RNG.random()<quality else RNG.choice(options)
        elif f['type']=='spectral':
            item['spectra'][fid]=[max(.01, .4+.2*math.sin(j*.55)+(0 if target else RNG.gauss(0,.4*(1-quality)))) for j in range(24)]
        elif f['type']=='timeseries':
            if target and f['compare_mode']=='relative_rank':item['values'][fid]=.6
            base=12 if fid=='m3_diurnal_range' else 5 if fid=='m3_cold_hours' else .25 if fid=='r6_dust' else 4
            amplitude=8 if fid!='r6_dust' else .2
            shift=0 if target else (1-quality)*RNG.uniform(-1.5,1.5)
            item['series'][fid]={'phase':[round(j/48,6) for j in range(48)],'values':[round(base+amplitude*math.sin(2*math.pi*j/48+shift)+(0 if target else RNG.gauss(0,(1-quality)*amplitude*.4)),5) for j in range(48)],'step_hours':1.,'period':'normalized_demo_cycle'}
        else:
            base=.6 if f['compare_mode']=='relative_rank' else 3 if f['type']=='threshold' else 8.2 if fid=='m5_tir_mineral' else .5 if fid=='m6_ice_depth' else 20 if fid=='r5_polygon_size' else -230 if fid=='m3_abs_temp' else 7
            if fid=='r2_dune_fraction':base=.04
            item['values'][fid]=base if target else round(max(0,base+RNG.gauss(0,(1-quality)*(.45 if f['compare_mode']=='relative_rank' else .15 if fid=='r2_dune_fraction' else .4 if fid=='m6_ice_depth' else 5))),5)
    return item
write('target_values.demo.yaml',{s['id']:fixture(target=True) for s in sites})
candidates=[dict(fixture(quality=.92 if idx<2 else .7 if idx<6 else .35),id=f'demo-{idx+1:02}',name=f'Demo-{idx+1:02}',name_en=f'Demo-{idx+1:02}',lat=lat,lon=lon,known_analog=idx in [0,4,9,14]) for idx,(lat,lon) in enumerate(COORDS)]
(DEST/'earth_candidates.demo.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Generated {len(all_tasks)} tasks, {len(FEATURE_NAMES)} features, {len(sites)} targets, {len(candidates)} placeholder candidates (seed=42).')

