import json,numpy as np,pandas as pd
T=json.loads('''{"ATACAMA_YUNGAY":{"elev":960,"mean":20.39,"annmax":35.3,"annmin":3.33,"dtr":16.7},"DEATHVALLEY_UBEHEBE":{"elev":656,"mean":21.13,"annmax":43.37,"annmin":-2.5,"dtr":9.81},"HAWAII_MAUNAKEA":{"elev":4169,"mean":1.23,"annmax":11.68,"annmin":-9.82,"dtr":8.66},"HAWAII_KAU_DESERT":{"elev":886,"mean":19.25,"annmax":29.08,"annmin":10.06,"dtr":6.97},"AZ_BLACK_POINT_LAVA":{"elev":1607,"mean":14.3,"annmax":38.47,"annmin":-11.55,"dtr":13.28},"NV_LUNAR_CRATER":{"elev":1779,"mean":11.83,"annmax":36.27,"annmin":-17.05,"dtr":11.64},"ID_CRATERS_OF_MOON":{"elev":1740,"mean":6.95,"annmax":35.15,"annmin":-23.06,"dtr":10.35},"BOLIVIA_UYUNI_SALT":{"elev":3654,"mean":7,"annmax":22.5,"annmin":-9.07,"dtr":15.79},"NM_WHITE_SANDS":{"elev":1214,"mean":17.85,"annmax":40,"annmin":-7,"dtr":13.12},"NV_CUPRITE_CLAY":{"elev":1580,"mean":14.03,"annmax":37.82,"annmin":-12.46,"dtr":11.94},"ALGERIA_GRAND_ERG":{"elev":205,"mean":23.61,"annmax":46.7,"annmin":-1.76,"dtr":13.65},"CA_IMPERIAL_CROPS":{"elev":-42,"mean":24.75,"annmax":49.12,"annmin":0.47,"dtr":15.77}}''')
D=lambda x,b,t:round(float(np.clip((x-b)/(t-b),0,1)),3)
df=pd.read_csv("new_features_results.csv").set_index("site")
for s,v in T.items():
    df.loc[s,"era5_elev_m"]=v["elev"]
    df.loc[s,"M6_annual_mean_C"]=v["mean"];   df.loc[s,"s_M6_mean"]=D(v["mean"],15,-55)
    df.loc[s,"M6_annual_max_C"]=v["annmax"];  df.loc[s,"s_M6_max"]=D(v["annmax"],40,-20)
    df.loc[s,"M3_annual_min_C"]=v["annmin"];  df.loc[s,"s_M3_min"]=D(v["annmin"],0,-89)
    df.loc[s,"M3_diurnal_range_C"]=v["dtr"];  df.loc[s,"s_M3_dtr"]=D(v["dtr"],10,40)
df.to_csv("new_features_results.csv")
print(df[["s_M4_relief","s_M2_lowsun","s_M3_dark","s_M6_mean","s_M6_max","s_M3_min","s_M3_dtr"]].to_string())
