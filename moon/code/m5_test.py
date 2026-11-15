import json, numpy as np, pandas as pd
d=json.load(open('earth_gsd_sg.json'))
by={}
for k,(b,s) in d.items(): by.setdefault(k.split('|')[0],[]).append(s)
def cls(sites):
    v=np.concatenate([by[s] for s in sites]); return len(v),v.min(),v.max(),np.percentile(v,[10,50,90])
classes={"arid_desert_soil":["Nev","CCS","KLM"],"aeolian_sand":["Ord","Hor"],"cultivated_alluvial":["CD","KOY"],
         "periglacial_glacial":["KLM","MDG","LLR"]}
for c,s in classes.items():
    n,lo,hi,p=cls(s); print(f"{c:20s} n={n:3d} min={lo:.2f} max={hi:.2f}  p10/50/90={p.round(2)}")
for s in ["KLM","MDG","LLR"]: print(s,len(by[s]),np.round([min(by[s]),np.median(by[s]),max(by[s])],2))
