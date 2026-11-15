import numpy as np, pandas as pd
sites = {"ATACAMA_YUNGAY":-24.09,"DEATHVALLEY_UBEHEBE":37.010,"HAWAII_MAUNAKEA":19.82,"HAWAII_KAU_DESERT":19.35,
"AZ_BLACK_POINT_LAVA":35.67,"NV_LUNAR_CRATER":38.38,"ID_CRATERS_OF_MOON":43.42,"BOLIVIA_UYUNI_SALT":-20.20,
"NM_WHITE_SANDS":32.78,"NV_CUPRITE_CLAY":37.54,"ALGERIA_GRAND_ERG":30.50,"CA_IMPERIAL_CROPS":33.00}
clip=lambda v:float(np.clip(v,0,1))
D=lambda x,b,t:clip((x-b)/(t-b))
def decl(doy): # Spencer formula, radians
    g=2*np.pi*(doy-1)/365
    return (0.006918-0.399912*np.cos(g)+0.070257*np.sin(g)-0.006758*np.cos(2*g)+0.000907*np.sin(2*g)-0.002697*np.cos(3*g)+0.00148*np.sin(3*g))
def solar(lat):
    phi=np.radians(lat); t=np.arange(0,365*24,1/6)  # 10-min steps, 1 year
    doy=t/24+1; H=np.radians(15*((t%24)-12))
    el=np.degrees(np.arcsin(np.sin(phi)*np.sin(decl(doy))+np.cos(phi)*np.cos(decl(doy))*np.cos(H)))
    day=el>-0.833
    f_low=((el>-0.833)&(el<10)).sum()/day.sum()
    # longest continuous dark run (hours)
    d=(~day).astype(int); runs=[];c=0
    for v in np.r_[d,d]:  # wrap year
        c=c+1 if v else 0; runs.append(c)
    return f_low, max(runs)/6
relief = pd.read_csv("M4_slope_results.csv").set_index("site")["relief_m_16km"]
R_M=relief["MOON_Site01_ConnectingRidge_30m"]
rows=[]
for s,lat in sites.items():
    f,L=solar(lat); R=relief[s]
    rows.append(dict(site=s,lat=lat,
      M4_relief_m=R, s_M4_relief=round(float(np.exp(-np.log(R/R_M)**2/(2*np.log(2)**2))),3),
      M2_lowsun_frac=round(f,3), s_M2_lowsun=round(D(f,0,1),3),
      M3_longest_dark_h=round(L,1), s_M3_dark=round(D(L,12,120),3)))
df=pd.DataFrame(rows); df.to_csv("new_features_results.csv",index=False)
print(df.to_string())
