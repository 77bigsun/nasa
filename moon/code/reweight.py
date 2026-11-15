"""11/14 22:00 feature-weight update. M2 noon .3/low .7; M3 dark .5/tmin .35/dtr .15; M4 slope .7/relief .3;
M6 temperature .5 (annual mean & max, .25 each) / ice .5. c (data fitness) still multiplies w. Test weights ROC renormalized."""
import numpy as np, pandas as pd
W_TEST=dict(M2=.183,M3=.429,M4=.280,M6=.108)
FW={"M2":{"noon":(.3,1),"low":(.7,1)},
    "M3":{"dark":(.5,1),"tmin":(.35,.6),"dtr":(.15,.6)},
    "M4":{"slope":(.7,1),"relief":(.3,None)},          # relief c: 1.0 fine DEM, 0.6 grid
    "M6":{"tmean":(.25,.6),"tmax":(.25,.6),"ice":(.5,.3)}}
OLD={"M2":{"noon":(1,1),"low":(1,1)},"M3":{"dark":(1,1),"tmin":(1,.6),"dtr":(1,.6)},
     "M4":{"slope":(1,1),"relief":(1,None)},"M6":{"tmean":(1,.6),"tmax":(1,.6),"ice":(1,.3)}}
def score(s,rel_c,FWx):
    T={}
    for t,fs in FWx.items():
        n=d=0
        for k,(w,c) in fs.items():
            v=s.get(k); c=rel_c if c is None else c
            if v is None or pd.isna(v): continue
            n+=w*c*v; d+=w*c
        T[t]=100*n/d if d else np.nan
    tot=sum(W_TEST[k]*T[k] for k in T if not pd.isna(T[k]))/sum(W_TEST[k] for k in T if not pd.isna(T[k]))
    return T,tot
s2=pd.read_csv("stage2_scores.csv"); top=pd.read_csv("stage2_top_with_slope.csv")
gmap={"C1_VictoriaLand":"GRID_-73.5_166.5","C2_AlexanderIsland":"GRID_-70.5_-69.5","C3_EllesmereN":"GRID_82.5_-76.5","C4_ScoresbySund":"GRID_70.5_-27.5","C5_BaffinN":"GRID_73.5_-77.5","C6_Uummannaq":"GRID_71.5_-52.5","C7_AxelHeiberg":"GRID_79.5_-90.5","C8_DryValleys":"ANTARCTICA_DRY_VALLEYS","C9_PearyLand":"GRID_83.5_-32.5","C10_NEGreenland":"GRID_80.5_-19.5","DEVON_HAUGHTON":"DEVON_HAUGHTON","SVALBARD_ADVENTDALEN":"SVALBARD_ADVENTDALEN"}
fine={gmap[r.id]:r for r in top.itertuples()}
named={"ATACAMA_YUNGAY","DEATHVALLEY_UBEHEBE","HAWAII_MAUNAKEA","HAWAII_KAU_DESERT","AZ_BLACK_POINT_LAVA","NV_LUNAR_CRATER","ID_CRATERS_OF_MOON","BOLIVIA_UYUNI_SALT","NM_WHITE_SANDS","NV_CUPRITE_CLAY","ALGERIA_GRAND_ERG","CA_IMPERIAL_CROPS"}
rows=[]
for r in s2.itertuples():
    s=dict(noon=r.s_noon,low=r.s_low,dark=r.s_dark,tmin=r.s_tmin,dtr=r.s_dtr,tmean=r.s_tmean,tmax=r.s_tmax,ice=r.s_ice,slope=r.s_slope,relief=r.s_relief)
    rc=1.0 if r.id in named else 0.6
    name=r.id
    if r.id in fine:
        f=fine[r.id]; s["slope"]=f.s_slope; s["relief"]=f.s_relief; rc=1.0; name=f.name
    if r.surface=="likely ice-covered": continue
    To,old=score(s,rc,OLD); Tn,new=score(s,rc,FW)
    rows.append(dict(id=r.id,name=name,lat=r.lat,lon=r.lon,has_slope=not pd.isna(s["slope"]),
        **{f"old_{k}":round(v,1) for k,v in To.items()},old_total=round(old,1),
        **{f"new_{k}":round(v,1) for k,v in Tn.items()},new_total=round(new,1)))
o=pd.DataFrame(rows)
o["old_rank"]=o.old_total.rank(ascending=False,method="min").astype(int); o["new_rank"]=o.new_total.rank(ascending=False,method="min").astype(int)
o=o.sort_values("new_rank"); o.to_csv("reweight_comparison.csv",index=False)
pd.set_option("display.width",260)
print(o[["name","has_slope","old_total","new_total","old_rank","new_rank","new_M2","new_M3","new_M4","new_M6"]].head(14).to_string(index=False))
print(o[["name","old_total","new_total","old_rank","new_rank"]].tail(6).to_string(index=False))
from scipy.stats import spearmanr; print("spearman",round(spearmanr(o.old_rank,o.new_rank).correlation,3), "n",len(o))
