"""M4 global ranking per lunar site. Pool = 145 cells chosen globally as best relief matches for any of the 10 lunar sites
(+12 polar candidates +12 validation sites), each with 30 m slope histogram (Terrarium, 16 km box). M4 = .7 slope + .3 relief."""
import numpy as np, pandas as pd, json
M=json.load(open("moon10_reference_sites.json"))
a=pd.read_csv("m4_slope_global_cells.csv"); a["name"]=a.apply(lambda r:f"GRID_{r.lat}_{r.lon}",axis=1)
F=["f0_5","f5_10","f10_15","f15_20","f20_30","f30p"]
top=pd.read_csv("stage2_top_with_slope.csv")
b=pd.DataFrame({"name":top["name"],"lat":top.lat,"lon":top.lon,"relief16km_m":top.relief16km_m,**{f:top["slope_"+s] for f,s in zip(F,["0-5","5-10","10-15","15-20","20-30",">30"])}})
m4=pd.read_csv("/home/claude/M4_slope_results.csv"); m4=m4[m4.category!="reference"]
c=pd.DataFrame({"name":m4.site,"lat":np.nan,"lon":np.nan,"relief16km_m":m4.relief_m_16km,**{f:m4[s] for f,s in zip(F,["frac_0-5","5-10","10-15","15-20","20-30","gt30"])}})
pool=pd.concat([b,c,a],ignore_index=True).drop_duplicates(subset=["lat","lon"],keep="first")
pool=pool[pool.get("land_frac",pd.Series(1,index=pool.index)).fillna(1)>=0.5]
out=pool[["name","lat","lon","relief16km_m"]].copy()
for k,v in M.items():
    sl=np.minimum(pool[F].values,np.array(v["slope_frac"])).sum(1)
    rl=np.exp(-np.log(pool.relief16km_m.clip(lower=1)/v["relief_16km_m"])**2/(2*np.log(2)**2))
    out[k]=(100*(.7*sl+.3*rl)).round(1)
out.to_csv("m4_global_by_moonsite.csv",index=False)
print("pool",len(out))
for k,v in M.items():
    s=out.sort_values(k,ascending=False)
    print(v["label"],"|",[(n,x) for n,x in zip(s.name[:3],s[k][:3])])
