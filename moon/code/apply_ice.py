"""Replace the temperature-based ice-sheet guess with NASA MODIS MCD12Q1 (GIBS layer MODIS_Combined_L3_IGBP_Land_Cover_Type_Annual, 2023):
a 1-deg cell with >=50% 'Permanent Snow and Ice' pixels (0.1 deg sampling) is an ice sheet; cells poleward of 58 deg only (elsewhere none)."""
import pandas as pd, numpy as np
rle="3738.2.250.1.274.7.1.202.1.216.3.54.1.234.5.237.7.239.1.10.9.264.10.5.1.262.11.263.1.6.15.252.2.4.17.238.15.215.1.4.21.163.1.1.1.5.21.144.24.113.2.2.26.90.29.56.28.3.2.50.32.3.5.52.1.3.39.1.1.1.3.25.5.1.27.4.2.9.1.5.3.7.7.4.20.1.2.1.4.1.1.1.4.2.5.9.47.1.6.2.2.4.11.2.1.3.33.2.16.6.12.7.8.1.27.1.19.3.1.4.11.13.5.7.2"
bits=[];cur=1
for n in map(int,rle.split(".")): bits+= [cur]*n; cur=1-cur
g=pd.read_csv("global_by_task.csv")
m=(g.lat>58)|(g.lat< -58)
print("subset",m.sum(),"bits",len(bits))
assert m.sum()==len(bits)
g["modis_ice"]=False; g.loc[m,"modis_ice"]=np.array(bits,bool)
g["icesheet"]=g.modis_ice
g.to_csv("global_by_task.csv",index=False)
print("ice cells",g.icesheet.sum(),"| Antarctica ice-free cells",((g.lat< -60)&~g.icesheet).sum(),"| Greenland-ish ice-free",((g.lat>59.5)&(g.lon>-73)&(g.lon<-11)&~g.icesheet).sum())
