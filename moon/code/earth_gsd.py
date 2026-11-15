import openpyxl, numpy as np, json, re
wb=openpyxl.load_workbook('/mnt/user-data/uploads/a61151cb-S1_GSD_data_from_Earth.xlsx',read_only=True,data_only=True)
edges=[(1,1e9),(0.5,1),(0.25,0.5),(0.075,0.25),(0.02,0.075),(0,0.02)]
moon=np.array(json.load(open('moon_references_M5.json'))['S_G_grain_size']['mass_fraction_mean'])
def num(x):
    try: return float(x)
    except: return None
out={}
for ws in wb.worksheets:
    rows=[list(r) for r in ws.iter_rows(values_only=True)]
    for i,r in enumerate(rows):
        for c,v in enumerate(r):
            if isinstance(v,str) and re.match(r'D\s*\(\s*[>≥.]*\s*mm',v.replace(' ','')):
                # diameters down column c from row i+1; samples in columns c+1.. while header non-empty
                Ds=[]; rr=i+1
                while rr<len(rows) and num(rows[rr][c]) is not None: Ds.append(num(rows[rr][c])); rr+=1
                if len(Ds)<4: continue
                for cc in range(c+1,len(r)):
                    name=r[cc]
                    if name is None or (isinstance(name,str) and name.startswith('D(')): break
                    vals=[num(rows[i+1+k][cc]) if cc<len(rows[i+1+k]) else None for k in range(len(Ds))]
                    if any(v is None for v in vals): continue
                    tot=sum(vals)
                    if not (90<=tot<=110) or min(Ds)>0.02: continue   # need full range incl. fines
                    b=np.zeros(6)
                    for D,m in zip(Ds,vals):
                        for k,(lo,hi) in enumerate(edges):
                            if lo<=D<hi: b[k]+=m; break
                    b/=b.sum()
                    out[f'{ws.title.split(",")[0].strip()}|{name}']=(b, float(np.minimum(b,moon).sum()))
sites={}
for k,(b,s) in out.items(): sites.setdefault(k.split('|')[0],[]).append(s)
for s,v in sorted(sites.items(), key=lambda kv:-np.median(kv[1])):
    print(f'{s:10s} n={len(v):3d}  S_G min={min(v):.2f} median={np.median(v):.2f} max={max(v):.2f}')
json.dump({k:[v[0].tolist(),v[1]] for k,v in out.items()},open('earth_gsd_sg.json','w'))
