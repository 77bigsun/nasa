import numpy as np, pandas as pd
D=lambda x,b,t: abs(round(float(np.clip((x-b)/(t-b),0,1)),3))
base=pd.read_csv("new_features_results.csv")[["site","M6_annual_mean_C","M6_annual_max_C"]]
cat={"ATACAMA_YUNGAY":"known","DEATHVALLEY_UBEHEBE":"known","HAWAII_MAUNAKEA":"known","HAWAII_KAU_DESERT":"known","AZ_BLACK_POINT_LAVA":"known","NV_LUNAR_CRATER":"known","ID_CRATERS_OF_MOON":"known","BOLIVIA_UYUNI_SALT":"control","NM_WHITE_SANDS":"control","NV_CUPRITE_CLAY":"control","ALGERIA_GRAND_ERG":"control","CA_IMPERIAL_CROPS":"control"}
base["group"]=base.site.map(cat)
polar=pd.DataFrame([["DEVON_HAUGHTON",-14.55,16.10,"polar"],["SVALBARD_ADVENTDALEN",-3.78,14.24,"polar"],["ANTARCTICA_DRY_VALLEYS",-18.99,0.28,"polar"]],columns=["site","M6_annual_mean_C","M6_annual_max_C","group"])
df=pd.concat([base,polar],ignore_index=True)
# ice checklist (literature, c=0.3): permafrost 0.4, ground ice 0.3, cold-trap-like ice 0.3
ice={"DEVON_HAUGHTON":(1,1,0),"SVALBARD_ADVENTDALEN":(1,1,0),"ANTARCTICA_DRY_VALLEYS":(1,1,0),
     "HAWAII_MAUNAKEA":(1,1,0),"ID_CRATERS_OF_MOON":(0,0,1)}
df["s_mean"]=[D(x,15,-55) for x in df.M6_annual_mean_C]
df["s_max"]=[D(x,40,-20) for x in df.M6_annual_max_C]
df["s_ice"]=[round(0.4*a+0.3*b+0.3*c,2) for a,b,c in (ice.get(s,(0,0,0)) for s in df.site)]
# 11/11 combine with c: temps from ERA5 = proxy (0.6), checklist = literature (0.3); equal w
w={"s_mean":1,"s_max":1,"s_ice":1}; c={"s_mean":0.6,"s_max":0.6,"s_ice":0.3}
num=sum(w[k]*c[k]*df[k] for k in w); den=sum(w[k]*c[k] for k in w)
df["M6_score"]=(100*num/den).round(1)
df=df.sort_values("M6_score",ascending=False); df.to_csv("M6_suitability_test.csv",index=False)
print(df.to_string(index=False))
print(df.groupby("group")[["s_mean","s_max","s_ice","M6_score"]].mean().round(3))
def auc(a,b): return np.mean([1 if x>y else .5 if x==y else 0 for x in a for y in b])
g=lambda n:df[df.group==n].M6_score.values
print("AUC polar>known",auc(g("polar"),g("known")),"polar>control",auc(g("polar"),g("control")),"known>control",auc(g("known"),g("control")))
print("corr mean/max",np.corrcoef(df.s_mean,df.s_max)[0,1].round(3))
