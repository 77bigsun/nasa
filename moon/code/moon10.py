"""10 lunar reference sites. Connecting Ridge: PGDA LOLA 5 m (Site01) resampled to 30 m. Nine Artemis III regions (Oct 2024):
PDS LOLA LDEM_80S_20M, 16 km window centred on the LROC NAC ROI centre (NobileRim1, SlaterPlain: literature centres), bilinear to 30 m.
Cross-check: Malapert 20 m vs 5 m Site23 slope histograms agree within 0.03 per bin."""
import numpy as np, pandas as pd, json
from reweight import FW, score
M={
"ConnectingRidge":("Shackleton 連接脊 Connecting Ridge",-89.45,None,2477,[0.098,0.2757,0.3035,0.2206,0.1023,0],"LOLA 5 m PGDA Site01"),
"PeakNearCabeusB":("Peak near Cabeus B",-83.6,-68.8,3628,[0.0202,0.0815,0.1873,0.2826,0.4174,0.0111],"LOLA 20 m, LROC ROI centre"),
"Haworth":("Haworth",-86.7,-23.7,2127,[0.1964,0.4104,0.244,0.109,0.04,0.0003],"LOLA 20 m, LROC ROI centre"),
"MalapertMassif":("Malapert Massif",-86.0,0.3,3186,[0.0422,0.1193,0.1929,0.2736,0.3599,0.0121],"LOLA 20 m, LROC ROI centre"),
"MonsMoutonPlateau":("Mons Mouton Plateau",-84.3,30.6,1526,[0.2799,0.4513,0.1855,0.062,0.0203,0.001],"LOLA 20 m, LROC ROI centre"),
"MonsMouton":("Mons Mouton",-85.4,35.3,3454,[0.0979,0.2242,0.283,0.2311,0.1581,0.0058],"LOLA 20 m, LROC ROI centre (shared with Nobile Rim 1)"),
"NobileRim1":("Nobile Rim 1",-85.28,37.01,4447,[0.1293,0.2211,0.2072,0.1536,0.2705,0.0183],"LOLA 20 m, literature centre"),
"NobileRim2":("Nobile Rim 2",-83.9,58.7,2738,[0.1835,0.3138,0.2607,0.1685,0.0731,0.0003],"LOLA 20 m, LROC ROI centre"),
"deGerlacheRim2":("de Gerlache Rim 2",-88.5,-66.7,2725,[0.038,0.1503,0.3273,0.3229,0.1606,0.0009],"LOLA 20 m, LROC ROI centre"),
"SlaterPlain":("Slater Plain",-86.96,126.82,2077,[0.1988,0.3527,0.2443,0.1515,0.0514,0.0013],"LOLA 20 m, literature centre"),
}
s2=pd.read_csv("stage2_scores.csv"); top=pd.read_csv("stage2_top_with_slope.csv"); m4=pd.read_csv("/home/claude/M4_slope_results.csv").set_index("site")
gmap={"C1_VictoriaLand":"GRID_-73.5_166.5","C2_AlexanderIsland":"GRID_-70.5_-69.5","C3_EllesmereN":"GRID_82.5_-76.5","C4_ScoresbySund":"GRID_70.5_-27.5","C5_BaffinN":"GRID_73.5_-77.5","C6_Uummannaq":"GRID_71.5_-52.5","C7_AxelHeiberg":"GRID_79.5_-90.5","C8_DryValleys":"ANTARCTICA_DRY_VALLEYS","C9_PearyLand":"GRID_83.5_-32.5","C10_NEGreenland":"GRID_80.5_-19.5","DEVON_HAUGHTON":"DEVON_HAUGHTON","SVALBARD_ADVENTDALEN":"SVALBARD_ADVENTDALEN"}
inv={v:k for k,v in gmap.items()}; bins=["0-5","5-10","10-15","15-20","20-30",">30"]
rows=[]
for r in s2.itertuples():
    if r.surface=="likely ice-covered": continue
    name=r.id; frac=None; rel=r.relief_m; rc=0.6
    if r.id in inv:
        f=top[top.id==inv[r.id]].iloc[0]; name=f["name"]; frac=[f["slope_"+b] for b in bins]; rel=f.relief16km_m; rc=1.0
    elif r.id in m4.index:
        frac=[m4.loc[r.id,c] for c in ["frac_0-5","5-10","10-15","15-20","20-30","gt30"]]; rel=m4.loc[r.id,"relief_m_16km"]; rc=1.0
    base=dict(noon=r.s_noon,low=r.s_low,dark=r.s_dark,tmin=r.s_tmin,dtr=r.s_dtr,tmean=r.s_tmean,tmax=r.s_tmax,ice=r.s_ice)
    row=dict(id=r.id,name=name,lat=r.lat,lon=r.lon,has_30m_slope=frac is not None)
    for k,(lab,la,lo,mrel,mfrac,src) in M.items():
        s=dict(base); s["slope"]=float(np.minimum(frac,mfrac).sum()) if frac is not None else np.nan
        s["relief"]=float(np.exp(-np.log(max(rel,1)/mrel)**2/(2*np.log(2)**2))) if rel>0 else 0.0
        T,tot=score(s,rc,FW); row[f"{k}__M2"]=round(T["M2"],1);row[f"{k}__M3"]=round(T["M3"],1);row[f"{k}__M4"]=round(T["M4"],1);row[f"{k}__M6"]=round(T["M6"],1);row[f"{k}__total"]=round(tot,1)
    rows.append(row)
o=pd.DataFrame(rows)
for k in M: o[f"{k}__rank"]=o[f"{k}__total"].rank(ascending=False,method="min").astype(int)
o.to_csv("moon10_matrix.csv",index=False)
json.dump({k:dict(label=v[0],lat=v[1],lon=v[2],relief_16km_m=v[3],slope_frac=v[4],source=v[5]) for k,v in M.items()},open("moon10_reference_sites.json","w"),ensure_ascii=False,indent=1)
summ=[]
for k,(lab,*_) in M.items():
    t=o.sort_values(f"{k}__total",ascending=False)
    summ.append([lab]+[f"{n}({v})" for n,v in zip(t.name[:3],t[f"{k}__total"][:3])])
for s in summ: print(" | ".join(s))
