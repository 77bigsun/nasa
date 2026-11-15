"""Stage 1 global screen: 1-deg land grid, features computable globally (M2, M3 dark, M4 relief, M6 mean+ice proxy)."""
import numpy as np, pandas as pd, sys
sys.path.insert(0,'/home/claude'); 
clip=lambda v:np.clip(v,0,1); D=lambda x,b,t:clip((x-b)/(t-b))
def decl(doy):
    g=2*np.pi*(doy-1)/365
    return 0.006918-0.399912*np.cos(g)+0.070257*np.sin(g)-0.006758*np.cos(2*g)+0.000907*np.sin(2*g)-0.002697*np.cos(3*g)+0.00148*np.sin(3*g)
t=np.arange(0,365*24,1/6); dd=decl(t/24+1); H=np.radians(15*((t%24)-12))
def solar(lat):
    phi=np.radians(lat); el=np.degrees(np.arcsin(np.sin(phi)*np.sin(dd)+np.cos(phi)*np.cos(dd)*np.cos(H)))
    day=el>-0.833; f=((el<10)&day).sum()/max(day.sum(),1) if day.any() else 1.0
    dk=np.r_[~day,~day].astype(int); best=run=0
    for v in dk:
        run=run+1 if v else 0; best=max(best,run)
    return f, min(best,len(t))/6
g=pd.read_csv("global_screen_1deg.csv")
sol={la:solar(la) for la in sorted(g.lat.unique())}
g["lowsun_frac"]=g.lat.map(lambda l:sol[l][0]); g["longest_dark_h"]=g.lat.map(lambda l:sol[l][1])
s=pd.DataFrame(index=g.index)
s["noon"]=D(90-g.lat.abs(),90,5); s["low"]=D(g.lowsun_frac,0,1); s["dark"]=D(g.longest_dark_h,12,120)
rel=g.relief16km_m.where(g.relief16km_m>=0)
s["relief"]=np.where(rel>0,np.exp(-np.log(rel.clip(lower=1)/2477)**2/(2*np.log(2)**2)),np.where(rel==0,0,np.nan))
s["mean"]=D(g.T2M_ann_C,15,-55); s["ice"]=0.4*(g.T2M_ann_C<=-2)+0.3*(g.T2M_ann_C<=-8)
def comb(cols):
    num=sum(s[k].fillna(0)*c*s[k].notna() for k,c in cols); den=sum(c*s[k].notna() for k,c in cols)
    return (100*num/den).where(den>0)
T=pd.DataFrame({"M2":comb([("noon",1),("low",1)]),"M3":comb([("dark",1)]),"M4":comb([("relief",0.6)]),"M6":comb([("mean",0.6),("ice",0.3)])})
W={"M2":0.183,"M3":0.429,"M4":0.280,"M6":0.108}
num=sum(T[k].fillna(0)*w for k,w in W.items()); den=sum(T[k].notna()*w for k,w in W.items())
out=pd.concat([g,s.add_prefix("s_").round(3),T.add_prefix("test_").round(1)],axis=1)
out["total"]=(num/den).round(1)
out["icesheet_flag"]=(g.lat.abs()>58)&(g.elev_m>1000)&(g.T2M_ann_C<=-15)
out.to_csv("global_scores_1deg.csv",index=False)
print(out.total.describe().round(1)); print("icesheet",out.icesheet_flag.sum())
r=out[~out.icesheet_flag].sort_values("total",ascending=False)
print(r.head(10)[["lat","lon","elev_m","relief16km_m","T2M_ann_C","test_M2","test_M3","test_M4","test_M6","total"]].to_string(index=False))
