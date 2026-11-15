"""Final per-task rankings, split into judge-flagged known analog regions (validation) vs new candidates.
Known regions (challenge brief): Antarctica, Atacama, Iceland, Hawaii; plus Haughton/Devon Island and Death Valley."""
import pandas as pd, numpy as np, json
KNOWN={"Antarctica":lambda la,lo:la< -60,"Hawaii":lambda la,lo:(18<=la<=23)&(-161<=lo<=-154),
 "Atacama":lambda la,lo:(-28<=la<=-18)&(-72<=lo<=-67),"Iceland":lambda la,lo:(63<=la<=67)&(-25<=lo<=-13),
 "Devon/Haughton":lambda la,lo:(74.5<=la<=77)&(-96<=lo<=-80),"Death Valley":lambda la,lo:(35.5<=la<=37.5)&(-118<=lo<=-116)}
def known(la,lo):
    for k,f in KNOWN.items():
        if f(la,lo): return k
    return ""
g=pd.read_csv("global_by_task.csv"); g["known_region"]=[known(a,b) for a,b in zip(g.lat,g.lon)]
g.to_csv("global_by_task.csv",index=False)
rock=g[(~g.icesheet)&(g.get("temp_source","MODIS_LST_2023")=="MODIS_LST_2023")]
res={}
for t in ["M2","M3","M6"]:
    new=rock[rock.known_region==""].sort_values(t,ascending=False); kn=rock[rock.known_region!=""].sort_values(t,ascending=False)
    res[t]={"new_top":new.head(8)[["lat","lon",t,"T2M_ann_C","T2M_MIN_C","T2M_MAX_C"]].round(2).values.tolist(),
            "known_top":kn.head(4)[["lat","lon",t,"known_region"]].values.tolist(),
            "bottom":rock.sort_values(t).head(3)[["lat","lon",t]].values.tolist()}
m4=pd.read_csv("m4_global_by_moonsite.csv")
m4["known_region"]=[known(a,b) if not pd.isna(a) else ("Hawaii" if "HAWAII" in n else "Atacama" if "ATACAMA" in n else "Death Valley" if "DEATHVALLEY" in n else "Antarctica" if "南極" in n else "Devon/Haughton" if "Haughton" in n else "") for a,b,n in zip(m4.lat,m4.lon,m4.name)]
M=json.load(open("moon10_reference_sites.json")); res["M4"]={}
for k,v in M.items():
    new=m4[m4.known_region==""].sort_values(k,ascending=False); kn=m4[m4.known_region!=""].sort_values(k,ascending=False)
    res["M4"][k]={"label":v["label"],"new_top":new.head(3)[["name","lat","lon",k]].values.tolist(),"known_top":kn.head(2)[["name",k]].values.tolist()}
m4.to_csv("m4_global_by_moonsite.csv",index=False)
json.dump(res,open("final_rankings.json","w"),ensure_ascii=False,indent=1,default=float)
for t in ["M2","M3","M6"]:
    print("==",t); print(" NEW:",res[t]["new_top"][:6]); print(" KNOWN:",res[t]["known_top"]); print(" BOTTOM:",res[t]["bottom"])
for k,v in res["M4"].items(): print("M4",v["label"],"NEW:",[(a,c,d,e) for a,c,d,e in v["new_top"]],"KNOWN:",v["known_top"])
