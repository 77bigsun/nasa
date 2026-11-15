"""M4 against 4 lunar reference sites with LOLA 5 m DEMs (resampled to 30 m), then totals with 11/14 feature weights."""
import numpy as np, pandas as pd, json
from reweight import FW, W_TEST, score
MOON={ # PGDA LOLA_5mpp site: (Artemis region label, tile km, relief m, slope fractions 0-5,5-10,10-15,15-20,20-30,>30)
 "Site01":("Shackleton 連接脊 Connecting Ridge（Moon Base I 目的地）",16,2477,[0.098,0.2757,0.3035,0.2206,0.1023,0]),
 "Site11":("de Gerlache 撞擊坑邊緣（de Gerlache Rim）",16,2619,[0.0468,0.173,0.326,0.3121,0.142,0.0002]),
 "Site20":("Mons Mouton Plateau（舊名 Leibnitz Beta Plateau）",16,3664,[0.1076,0.3109,0.2404,0.1423,0.1988,0.0001]),
 "Site23":("Malapert Massif",21,4267,[0.0427,0.1238,0.1998,0.2478,0.3833,0.0026]),
}
s2=pd.read_csv("stage2_scores.csv"); top=pd.read_csv("stage2_top_with_slope.csv"); m4=pd.read_csv("/home/claude/M4_slope_results.csv").set_index("site")
gmap={"C1_VictoriaLand":"GRID_-73.5_166.5","C2_AlexanderIsland":"GRID_-70.5_-69.5","C3_EllesmereN":"GRID_82.5_-76.5","C4_ScoresbySund":"GRID_70.5_-27.5","C5_BaffinN":"GRID_73.5_-77.5","C6_Uummannaq":"GRID_71.5_-52.5","C7_AxelHeiberg":"GRID_79.5_-90.5","C8_DryValleys":"ANTARCTICA_DRY_VALLEYS","C9_PearyLand":"GRID_83.5_-32.5","C10_NEGreenland":"GRID_80.5_-19.5","DEVON_HAUGHTON":"DEVON_HAUGHTON","SVALBARD_ADVENTDALEN":"SVALBARD_ADVENTDALEN"}
fine={gmap[r.id]:r for r in top.itertuples()}
bins=["0-5","5-10","10-15","15-20","20-30",">30"]
rows=[]
for r in s2.itertuples():
    if r.surface=="likely ice-covered": continue
    name=r.id; frac=None; rel=r.relief_m; rc=0.6
    if r.id in fine:
        f=fine[r.id]; name=f.name; frac=[getattr(f,"_%d"%0)] if False else [top.loc[top.id==f.id,"slope_"+b].item() for b in bins]; rel=f.relief16km_m; rc=1.0
    elif r.id in m4.index:
        frac=[m4.loc[r.id,c] for c in ["frac_0-5","5-10","10-15","15-20","20-30","gt30"]]; rel=m4.loc[r.id,"relief_m_16km"]; rc=1.0
    base=dict(noon=r.s_noon,low=r.s_low,dark=r.s_dark,tmin=r.s_tmin,dtr=r.s_dtr,tmean=r.s_tmean,tmax=r.s_tmax,ice=r.s_ice)
    row=dict(id=r.id,name=name,lat=r.lat,lon=r.lon)
    for k,(lab,km,mrel,mfrac) in MOON.items():
        s=dict(base); s["slope"]=float(np.minimum(frac,mfrac).sum()) if frac is not None else np.nan
        s["relief"]=float(np.exp(-np.log(max(rel,1)/mrel)**2/(2*np.log(2)**2))) if rel>0 else 0.0
        T,tot=score(s,rc,FW); row[f"{k}_M4"]=round(T["M4"],1); row[f"{k}_total"]=round(tot,1)
    rows.append(row)
o=pd.DataFrame(rows)
for k in MOON: o[f"{k}_rank"]=o[f"{k}_total"].rank(ascending=False,method="min").astype(int)
o=o.sort_values("Site01_rank"); o.to_csv("moon_site_matrix.csv",index=False)
pd.set_option("display.width",250)
print(o[["name"]+[f"{k}_total" for k in MOON]+[f"{k}_rank" for k in MOON]].head(10).to_string(index=False))
for k,(lab,*_) in MOON.items(): print(k,lab,"top3:",list(o.sort_values(f"{k}_rank").name[:3]))
json.dump({k:dict(label=v[0],tile_km=v[1],relief_m=v[2],slope_frac=v[3]) for k,v in MOON.items()},open("moon_reference_sites.json","w"),ensure_ascii=False,indent=1)
