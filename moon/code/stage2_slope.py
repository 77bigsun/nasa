"""Add 30 m slope histogram (Terrarium, 16 km box) + fine relief to top-10 candidates; recompute M4 and total."""
import numpy as np, pandas as pd
SL={ # id: (grid_id, z, pix_m, relief_m, frac[6], S_slope)
"C1_VictoriaLand":("GRID_-73.5_166.5",11,21.7,2237,[0.326,0.3279,0.1688,0.1222,0.0456,0.0094],0.710),
"C2_AlexanderIsland":("GRID_-70.5_-69.5",11,25.5,1002,[0.6446,0.3064,0.0377,0.0111,0.0002,0],0.423),
"C3_EllesmereN":("GRID_82.5_-76.5",9,39.9,1848,[0.2338,0.2611,0.1325,0.0965,0.1613,0.1147],0.690),
"C4_ScoresbySund":("GRID_70.5_-27.5",11,25.5,1963,[0.2769,0.1744,0.138,0.0992,0.1457,0.1658],0.612),
"C5_BaffinN":("GRID_73.5_-77.5",11,21.7,1168,[0.3162,0.1534,0.136,0.1347,0.1966,0.0631],0.624),
"C6_Uummannaq":("GRID_71.5_-52.5",11,24.3,2275,[0.2381,0.2999,0.161,0.0922,0.062,0.1468],0.689),
"C7_AxelHeiberg":("GRID_79.5_-90.5",10,27.9,1418,[0.306,0.1867,0.1321,0.1013,0.1749,0.099],0.620),
"C8_DryValleys":("ANTARCTICA_DRY_VALLEYS",10,33.0,1409,[0.1558,0.3334,0.3408,0.1473,0.0227,0],0.847),
"C9_PearyLand":("GRID_83.5_-32.5",9,34.6,1304,[0.5283,0.3632,0.0942,0.0143,0,0],0.482),
"C10_NEGreenland":("GRID_80.5_-19.5",10,25.2,1246,[0.6356,0.2577,0.0844,0.0168,0.0027,0.0027],0.460),
"DEVON_HAUGHTON":("DEVON_HAUGHTON",10,38.6,266,[0.6709,0.2334,0.0676,0.0225,0.0055,0],0.427),
"SVALBARD_ADVENTDALEN":("SVALBARD_ADVENTDALEN",10,31.3,990,[0.2699,0.1689,0.1649,0.1421,0.1983,0.0559],0.676),
}
names={"C1_VictoriaLand":"南極北維多利亞地（Terra Nova Bay 附近）","C2_AlexanderIsland":"南極半島 Alexander Island 附近","C3_EllesmereN":"加拿大 Ellesmere Island 北部",
"C4_ScoresbySund":"格陵蘭東岸 Scoresby Sund","C5_BaffinN":"加拿大 Baffin Island 北部（Bylot Island 附近）","C6_Uummannaq":"格陵蘭西岸 Uummannaq 峽灣",
"C7_AxelHeiberg":"加拿大 Axel Heiberg Island","C8_DryValleys":"南極乾谷（McMurdo Dry Valleys）","C9_PearyLand":"格陵蘭北部 Peary Land","C10_NEGreenland":"格陵蘭東北部",
"DEVON_HAUGHTON":"加拿大 Devon Island Haughton 隕石坑","SVALBARD_ADVENTDALEN":"挪威斯瓦巴 Adventdalen"}
s2=pd.read_csv("stage2_scores.csv").set_index("id")
W=dict(M2=.183,M3=.429,M4=.280,M6=.108); rows=[]
for k,(gid,z,pix,rel,frac,S) in SL.items():
    r=s2.loc[gid]; s_rel=float(np.exp(-np.log(rel/2477)**2/(2*np.log(2)**2)))
    M4=100*(S*1+s_rel*1)/2
    tot=(W["M2"]*r.test_M2+W["M3"]*r.test_M3+W["M4"]*M4+W["M6"]*r.test_M6)/sum(W.values())
    rows.append(dict(id=k,name=names[k],lat=r.lat,lon=r.lon,dem_zoom=z,pixel_m=pix,relief16km_m=rel,
        **{f"slope_{b}":v for b,v in zip(["0-5","5-10","10-15","15-20","20-30",">30"],frac)},
        s_slope=S,s_relief=round(s_rel,3),test_M2=r.test_M2,test_M3=r.test_M3,test_M4_old=r.test_M4,test_M4=round(M4,1),test_M6=r.test_M6,
        total_old=r.total,total=round(tot,1),T_mean=r.T_mean,T_max=r.T_max,T_min=r.T_min,surface=r.surface))
o=pd.DataFrame(rows).sort_values("total",ascending=False); o.to_csv("stage2_top_with_slope.csv",index=False)
print(o[["name","s_slope","s_relief","test_M4_old","test_M4","total_old","total"]].to_string(index=False))
