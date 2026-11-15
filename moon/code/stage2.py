"""Stage 2: full M2/M3/M4/M6 scores for 60 spaced top grid cells + 15 named sites (NASA POWER point climatology)."""
import numpy as np, pandas as pd
from global_screen import solar, D   # reuse
p=pd.read_csv("stage2_power_points.csv"); g=pd.read_csv("global_scores_1deg.csv")
m4=pd.read_csv("/home/claude/M4_slope_results.csv").set_index("site")
def grid_rel(la,lo):
    d=(g.lat-la)**2+(((g.lon-lo+180)%360)-180)**2; r=g.loc[d.idxmin()]; return r.relief16km_m, r.elev_m
rows=[]
for _,r in p.iterrows():
    f,L=solar(r.lat)
    if r.id in m4.index: rel,rc,slope=m4.loc[r.id,"relief_m_16km"],1.0,m4.loc[r.id,"S_slope_hist"]
    else: rel,_e=grid_rel(r.lat,r.lon); rc,slope=0.6,np.nan
    s=dict(noon=float(D(90-abs(r.lat),90,5)),low=float(D(f,0,1)),dark=float(D(L,12,120)),
           tmin=float(D(r.Tmin,0,-89)),dtr=float(D(r.dtr,10,40)),
           relief=float(np.exp(-np.log(max(rel,1)/2477)**2/(2*np.log(2)**2))) if rel>0 else 0.0, slope=slope,
           tmean=float(D(r['T'],15,-55)),tmax=float(D(r.Tmax,40,-20)),ice=0.4*(r['T']<=-2)+0.3*(r['T']<=-8))
    def comb(cols):
        n=d=0
        for k,c in cols:
            if s[k] is None or (isinstance(s[k],float) and np.isnan(s[k])): continue
            n+=c*s[k]; d+=c
        return 100*n/d if d else np.nan
    t=dict(M2=comb([("noon",1),("low",1)]),M3=comb([("dark",1),("tmin",.6),("dtr",.6)]),
           M4=comb([("slope",1),("relief",rc)]),M6=comb([("tmean",.6),("tmax",.6),("ice",.3)]))
    W=dict(M2=.183,M3=.429,M4=.280,M6=.108)
    total=sum(W[k]*t[k] for k in W)/sum(W.values())
    surface="likely ice-covered" if r.Tmax< -1 else "exposed ground in summer (Tmax>=-1C)"
    if r.id=="ANTARCTICA_DRY_VALLEYS": surface="ice-free (known; grid too coarse)"
    rows.append(dict(id=r.id,lat=r.lat,lon=r.lon,relief_m=rel,T_mean=r['T'],T_max=r.Tmax,T_min=r.Tmin,DTR=r.dtr,
        longest_dark_h=round(L,1),**{"s_"+k:(round(v,3) if not (isinstance(v,float) and np.isnan(v)) else None) for k,v in s.items()},
        **{"test_"+k:round(v,1) for k,v in t.items()},total=round(total,1),surface=surface))
out=pd.DataFrame(rows).sort_values("total",ascending=False); out.to_csv("stage2_scores.csv",index=False)
pd.set_option("display.width",250)
print(out[["id","T_max","surface","test_M2","test_M3","test_M4","test_M6","total"]].to_string(index=False))
