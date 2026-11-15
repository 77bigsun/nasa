"""Build the website hand-off package (2026-11-14). Presentation = per-task rankings + suitable tasks per lunar base site."""
import json, numpy as np, pandas as pd, datetime
g=pd.read_csv("global_by_task.csv"); m4=pd.read_csv("m4_global_by_moonsite.csv"); M=json.load(open("moon10_reference_sites.json"))
cells=pd.read_csv("m4_slope_global_cells.csv"); top=pd.read_csv("stage2_top_with_slope.csv"); v12=pd.read_csv("/home/claude/M4_slope_results.csv")
NAMES={ # approximate place names for 1-deg cells (checked against map coordinates; verify before publishing)
(74.5,96.5):("Taymyr Peninsula, Russia","俄羅斯 Taymyr 半島"),
(69.5,115.5):("Northern Yakutia (Olenyok basin), Russia","俄羅斯雅庫特北部（Olenyok 流域）"),
(82.5,-32.5):("Peary Land, North Greenland (ice-free)","格陵蘭北部 Peary Land（無冰區）"),
(-5.5,142.5):("Southern Highlands, Papua New Guinea","新幾內亞南部高地"),
(39.5,45.5):("Southern Armenia uplands","亞美尼亞南部山區"),
(59.5,-136.5):("Chilkat Range near Haines, Alaska/BC","阿拉斯加 Haines 附近 Chilkat 山脈"),
(-29.5,-70.5):("Elqui Valley Andes, Chile","智利 Elqui 谷地安地斯"),
(-29.5,-69.5):("High Andes, Chile–Argentina border","智利阿根廷邊界高安地斯"),
(-2.5,120.5):("Central Sulawesi highlands, Indonesia","印尼蘇拉威西中部山區"),
(36.5,51.5):("Alborz Mountains, Iran","伊朗 Alborz 山脈"),
(30.5,81.5):("Ngari near Mt Kailash, Tibet","西藏阿里（岡仁波齊一帶）"),
(19.5,-103.5):("Colima volcanic complex, Mexico","墨西哥 Colima 火山區"),
(-15.5,-74.5):("Southern coastal Andes, Peru","秘魯南部安地斯"),
(-0.5,-78.5):("Andes near Quito, Ecuador","厄瓜多 Quito 附近安地斯"),
(20.5,17.5):("Tibesti Mountains, Chad","查德 Tibesti 山脈"),
(74.5,105.5):("Eastern Taymyr Peninsula, Russia","俄羅斯 Taymyr 半島東部"),
(74.5,-19.5):("Wollaston Forland, NE Greenland","格陵蘭東北岸 Wollaston Forland"),
(74.5,98.5):("Taymyr Peninsula, Russia","俄羅斯 Taymyr 半島"),
(74.5,-113.5):("Northern Victoria Island, Canadian Arctic","加拿大 Victoria 島北端一帶"),
(75.5,138.5):("New Siberian Islands, Russia","俄羅斯新西伯利亞群島"),
(72.5,-55.5):("Upernavik coast, West Greenland","格陵蘭西岸 Upernavik"),
(71.5,-110.5):("Victoria Island, Canada","加拿大 Victoria 島"),
(72.5,-88.5):("NW Baffin Island, Canada","加拿大 Baffin 島西北"),
(72.5,97.5):("Southern Taymyr, Russia","俄羅斯 Taymyr 半島南部"),

(70.5,112.5):("Northern Yakutia, Russia","俄羅斯雅庫特北部"),
(67.5,135.5):("Verkhoyansk area, Yakutia, Russia","俄羅斯 Verkhoyansk 一帶"),
(71.5,-86.5):("Brodeur Peninsula, Baffin Island, Canada","加拿大 Baffin 島 Brodeur 半島"),
(71.5,99.5):("Khatanga area, Russia","俄羅斯 Khatanga 一帶"),
(69.5,-72.5):("Northern Baffin Island, Canada","加拿大 Baffin 島北部"),
(72.5,-87.5):("NW Baffin Island, Canada","加拿大 Baffin 島西北"),
(72.5,118.5):("Lower Olenyok, Yakutia, Russia","俄羅斯雅庫特 Olenyok 下游"),
(67.5,155.5):("Kolyma basin, Russia","俄羅斯 Kolyma 流域"),
(72.5,129.5):("Tiksi area, Lena coast, Russia","俄羅斯 Tiksi 一帶"),
(82.5,-69.5):("Northern Ellesmere Island (Lake Hazen area), Canada","加拿大 Ellesmere 島北部（Lake Hazen 一帶）"),
(70.5,-74.5):("North-central Baffin Island, Canada","加拿大 Baffin 島中北部"),
(71.5,-75.5):("Northern Baffin Island, Canada","加拿大 Baffin 島北部"),
(75.5,141.5):("New Siberian Islands, Russia","俄羅斯新西伯利亞群島"),
(73.5,-86.5):("Brodeur Peninsula, Baffin Island, Canada","加拿大 Baffin 島 Brodeur 半島"),
(81.5,-89.5):("Northern Axel Heiberg Island, Canada","加拿大 Axel Heiberg 島北部"),
(83.5,-35.5):("Peary Land, North Greenland","格陵蘭北部 Peary Land"),
(79.5,77.5):("Vize Island, Kara Sea, Russia","俄羅斯 Vize 島"),

(74.5,104.5):("Eastern Taymyr Peninsula, Russia","俄羅斯 Taymyr 半島東部"),
(74.5,58.5):("Novaya Zemlya, Russia","俄羅斯新地島"),
(74.5,-97.5):("Prince of Wales Island area, Canada","加拿大 Prince of Wales 島一帶"),
(74.5,-21.5):("Wollaston Forland, NE Greenland","格陵蘭東北岸 Wollaston Forland"),
(74.5,-121.5):("Banks Island, Canada","加拿大 Banks 島"),
(73.5,142.5):("Yana–Indigirka coast, Russia","俄羅斯 Yana–Indigirka 沿岸"),
(73.5,-25.5):("Kong Oscar Fjord, East Greenland","格陵蘭東岸 Kong Oscar 峽灣"),
(72.5,-54.5):("Upernavik coast, West Greenland","格陵蘭西岸 Upernavik"),
(71.5,-93.5):("Boothia Peninsula, Canada","加拿大 Boothia 半島"),
(72.5,117.5):("Lower Olenyok, Yakutia, Russia","俄羅斯雅庫特 Olenyok 下游"),
(70.5,125.5):("Lower Lena River, Yakutia, Russia","俄羅斯雅庫特 Lena 河下游"),
(73.5,87.5):("Central Taymyr, Russia","俄羅斯 Taymyr 半島中部"),
(72.5,125.5):("Lena Delta, Russia","俄羅斯 Lena 河三角洲"),
(67.5,151.5):("Kolyma basin, Russia","俄羅斯 Kolyma 流域"),
(67.5,81.5):("Gydan–Taz lowland, Russia","俄羅斯 Gydan–Taz 低地"),
(70.5,-83.5):("Melville Peninsula area, Canada","加拿大 Melville 半島一帶"),
(72.5,-115.5):("Victoria Island, Canada","加拿大 Victoria 島"),
(68.5,-69.5):("Central Baffin Island, Canada","加拿大 Baffin 島中部"),
(81.5,-21.5):("Kronprins Christian Land, NE Greenland","格陵蘭東北部 Kronprins Christian Land"),
(81.5,-84.5):("Northern Ellesmere Island, Canada","加拿大 Ellesmere 島北部"),
(77.5,-105.5):("Lougheed Island area, Canada","加拿大 Lougheed 島一帶"),
(76.5,-23.5):("Germania Land, NE Greenland","格陵蘭東北岸 Germania Land"),
(78.5,-67.5):("Inglefield Land, NW Greenland","格陵蘭西北 Inglefield Land"),
(79.5,-80.5):("Central Ellesmere Island, Canada","加拿大 Ellesmere 島中部"),
(78.5,100.5):("Severnaya Zemlya, Russia","俄羅斯北地群島"),
(35.5,77.5):("Aksai Chin / Karakoram high plateau","阿克賽欽／喀喇崑崙高原"),

}
def nm(la,lo,fallback):
    k=(round(la,1),round(lo,1)); return NAMES.get(k,(fallback,fallback))
TASKS={"M2":{"name":"Low-sun illumination & solar power","name_zh":"低太陽角光照與太陽能","weight":0.183,
  "features":[{"id":"noon_sun_elevation","w":.3,"c":1.0,"formula":"D(x=90-|lat|, b=90°, t=5°)"},{"id":"low_sun_fraction","w":.7,"c":1.0,"formula":"D(x=share of daylight with sun<10°, b=0, t=1)"}]},
 "M3":{"name":"Long darkness & extreme cold","name_zh":"長時間黑暗與極寒","weight":0.429,
  "features":[{"id":"longest_darkness_h","w":.5,"c":1.0,"formula":"D(b=12 h, t=120 h)"},{"id":"annual_min_temp_C","w":.35,"c":.6,"formula":"D(b=0, t=-89)"},{"id":"diurnal_range_C","w":.15,"c":.6,"formula":"D(b=10, t=40)"}]},
 "M4":{"name":"Steep-slope & extreme-terrain mobility","name_zh":"陡坡與極端地形移動","weight":0.280,"depends_on_moon_site":True,
  "features":[{"id":"slope_histogram_30m","w":.7,"c":1.0,"formula":"sum(min(p_earth,p_moon)) over bins 0-5,5-10,10-15,15-20,20-30,>30°"},{"id":"relief_16km_m","w":.3,"c":1.0,"formula":"exp(-[ln(R_E/R_M)]^2/(2 ln2^2))"}]},
 "M6":{"name":"Cold-trap ice / permafrost","name_zh":"冷陷冰資源探勘","weight":0.108,
  "features":[{"id":"annual_mean_temp_C","w":.25,"c":.6,"formula":"D(b=15, t=-55)"},{"id":"annual_max_temp_C","w":.25,"c":.6,"formula":"D(b=40, t=-20)"},{"id":"ice_permafrost_proxy","w":.5,"c":.3,"formula":"0.4·[Tmean<=-2]+0.3·[Tmean<=-8]"}]}}
FEATCOL={"M2":[("noon_sun_elevation","s_noon",None),("low_sun_fraction","s_low","lowsun")],
 "M3":[("longest_darkness_h","s_dark","dark_h"),("annual_min_temp_C","s_tmin","Tmin_used_C"),("diurnal_range_C","s_dtr","DTR_used_C")],
 "M6":[("annual_mean_temp_C","s_tmean","Tmean_used_C"),("annual_max_temp_C","s_tmax","Tmax_used_C"),("ice_permafrost_proxy","s_ice",None)]}
cls=lambda s: None if s is None or (isinstance(s,float) and np.isnan(s)) else ("similar" if s>=.6 else "different" if s<.3 else "partial")
def feats(row,t):
    out=[]
    for fid,sc,raw in FEATCOL[t]:
        s=row[sc]; s=None if pd.isna(s) else round(float(s),3)
        v=None if raw is None or pd.isna(row.get(raw,np.nan)) else round(float(row[raw]),2)
        out.append({"feature":fid,"value":v,"s":s,"classification":cls(s)})
    return out
def site_rec(row,t,rank):
    en,zh=nm(row.lat,row.lon,f"{row.lat:.1f}, {row.lon:.1f}")
    return {"rank":rank,"lat":float(row.lat),"lon":float(row.lon),"name_en":en,"name_zh":zh,"score":round(float(row[t]),1),
            "known_analog_region":row.known_region or None,"features":feats(row,t)}
rock=g[(~g.icesheet)&(g.temp_source=="MODIS_LST_2023")]
task_rankings={}
for t in ["M2","M3","M6"]:
    new=rock[rock.known_region.fillna("")==""].sort_values(t,ascending=False)
    # one cell per 3x3 deg block so one region does not fill the list
    seen=set(); picks=[]
    for r in new.itertuples():
        b=(int(r.lat//8),int(r.lon//25))
        if b in seen: continue
        seen.add(b); picks.append(r._asdict())
        if len(picks)==10: break
    kn=rock[rock.known_region.fillna("")!=""].sort_values(t,ascending=False).drop_duplicates("known_region").head(4)
    bot=rock.sort_values(t).head(3)
    task_rankings[t]={"new_candidates":[site_rec(pd.Series(p),t,i+1) for i,p in enumerate(picks)],
        "known_analogs_validation":[site_rec(r,t,i+1) for i,(_,r) in enumerate(kn.iterrows())],
        "least_similar":[site_rec(r,t,i+1) for i,(_,r) in enumerate(bot.iterrows())]}
# M4 per lunar site
cells["key"]=list(zip(cells.lat.round(1),cells.lon.round(1)))
F=["f0_5","f5_10","f10_15","f15_20","f20_30","f30p"]
def m4feat(name,lat,lon,k):
    mf=np.array(M[k]["slope_frac"]); mr=M[k]["relief_16km_m"]
    if name.startswith("GRID_"):
        c=cells[(cells.lat==lat)&(cells.lon==lon)].iloc[0]; frac=c[F].values.astype(float); rel=c.relief16km_m
    elif name in set(top.name):
        c=top[top.name==name].iloc[0]; frac=np.array([c["slope_"+b] for b in ["0-5","5-10","10-15","15-20","20-30",">30"]]); rel=c.relief16km_m
    else:
        c=v12[v12.site==name].iloc[0]; frac=np.array([c[x] for x in ["frac_0-5","5-10","10-15","15-20","20-30","gt30"]]); rel=c.relief_m_16km
    s1=float(np.minimum(frac,mf).sum()); s2=float(np.exp(-np.log(rel/mr)**2/(2*np.log(2)**2)))
    return [{"feature":"slope_histogram_30m","value":[round(float(x),3) for x in frac],"moon_value":mf.tolist(),"s":round(s1,3),"classification":cls(s1)},
            {"feature":"relief_16km_m","value":float(rel),"moon_value":mr,"s":round(s2,3),"classification":cls(s2)}]
PRETTY={"南極北維多利亞地（Terra Nova Bay 附近）":("Northern Victoria Land (Terra Nova Bay), Antarctica","南極北維多利亞地"),"南極乾谷（McMurdo Dry Valleys）":("McMurdo Dry Valleys, Antarctica","南極乾谷"),
 "HAWAII_MAUNAKEA":("Mauna Kea, Hawaii","夏威夷 Mauna Kea"),"格陵蘭西岸 Uummannaq 峽灣":("Uummannaq Fjord, West Greenland","格陵蘭西岸 Uummannaq 峽灣"),"格陵蘭北部 Peary Land":("Peary Land, North Greenland","格陵蘭北部 Peary Land")}
def m4rec(r,k,rank):
    if r["name"].startswith("GRID_"): en,zh=nm(r.lat,r.lon,f"{r.lat:.1f}, {r.lon:.1f}")
    else: en,zh=PRETTY.get(r["name"],(r["name"],r["name"]))
    return {"rank":rank,"lat":None if pd.isna(r.lat) else float(r.lat),"lon":None if pd.isna(r.lon) else float(r.lon),"name_en":en,"name_zh":zh,
            "score":float(r[k]),"known_analog_region":r.known_region if isinstance(r.known_region,str) and r.known_region else None,"features":m4feat(r["name"],r.lat,r.lon,k)}
task_rankings["M4"]={}
for k in M:
    new=m4[m4.known_region.fillna("")==""].sort_values(k,ascending=False).head(10)
    kn=m4[m4.known_region.fillna("")!=""].sort_values(k,ascending=False).head(4)
    bot=m4.sort_values(k).head(3)
    task_rankings["M4"][k]={"new_candidates":[m4rec(r,k,i+1) for i,(_,r) in enumerate(new.iterrows())],
        "known_analogs_validation":[m4rec(r,k,i+1) for i,(_,r) in enumerate(kn.iterrows())],
        "least_similar":[m4rec(r,k,i+1) for i,(_,r) in enumerate(bot.iterrows())]}
# lunar base candidate sites and suitable tasks (team judgement from the Canva table, 11/14) + terrain numbers
SUIT={"ConnectingRidge":(["M2","M4"],[],"Ridge illumination is well studied; sunlit crest and dark lowland should be scored separately."),
"PeakNearCabeusB":(["M2","M4"],[],"Do not assume cold-trap ice from the Cabeus B name; trap location and access must be checked."),
"Haworth":(["M3","M6"],[],"Colder, darker PSRs identified (ShadowCam/Diviner); crater-floor conditions do not apply to sunlit landing spots."),
"MalapertMassif":(["M4"],["M2"],"Peak-like massif with ridges; slope and trafficability computed here."),
"MonsMoutonPlateau":(["M2"],["M3","M6"],"Whole-mountain results must not be transferred to the plateau box."),
"MonsMouton":(["M2","M6"],[],"USGS water-ice prospectivity model exists (model, not confirmed ice)."),
"NobileRim1":(["M2","M4"],["M3","M6"],"M3/M6 need a chosen shadowed sub-area."),
"NobileRim2":(["M3","M6"],["M4"],"Colder, darker PSRs identified; worth detailed study."),
"deGerlacheRim2":(["M2","M4"],[],"Some PSRs show strong scattered light and temperature swings; permanent shadow does not guarantee surface ice."),
"SlaterPlain":(["M2"],[],"Official candidate; evidence insufficient for M3/M4/M6. Computed terrain: mostly gentle slopes.")}
def terrain_class(f):
    steep=f[4]+f[5]; gentle=f[0]+f[1]
    return "very steep" if steep>=.35 else "gentle" if gentle>=.5 else "moderate"
def best(t,k=None,n=3):
    lst=task_rankings[t][k]["new_candidates"] if t=="M4" else task_rankings[t]["new_candidates"]
    return [{"name_en":x["name_en"],"name_zh":x["name_zh"],"lat":x["lat"],"lon":x["lon"],"score":x["score"]} for x in lst[:n]]
moon_sites=[]
for k,v in M.items():
    pri,sec,note=SUIT[k]
    moon_sites.append({"id":k,"name":v["label"],"lat":v["lat"],"lon":v["lon"],"dem_source":v["source"],
        "terrain":{"relief_16km_m":v["relief_16km_m"],"slope_fraction_bins_deg":["0-5","5-10","10-15","15-20","20-30",">30"],"slope_fraction":v["slope_frac"],"class":terrain_class(v["slope_frac"])},
        "suitable_tasks":{"primary":pri,"secondary":sec,"basis":"team assessment (Canva, 2026-11-14) from published studies","note":note},
        "best_earth_analogs_by_task":{t:best(t,k if t=="M4" else None) for t in pri+sec}})
meta={"generated":datetime.datetime.now().isoformat(timespec="minutes"),"status":"preliminary - verify place names before publishing",
 "score_formula":"task score = 100·Σ(w·c·s)/Σ(w·c); total (optional) = Σ W_task·task over the tasks the user selects, W renormalised",
 "task_weights_roc":{t:TASKS[t]["weight"] for t in TASKS},"classification_cutoffs":{"similar":0.6,"different":0.3},
 "ice_mask":"NASA MODIS MCD12Q1 IGBP 'Permanent Snow and Ice' >=50% of 1-deg cell (GIBS layer, 2023)",
 "known_analog_regions_excluded_from_new_candidates":["Antarctica","Atacama","Iceland","Hawaii","Devon Island/Haughton","Death Valley"],
 "data_sources":["LRO LOLA 5 m (NASA GSFC PGDA)","LRO LOLA LDEM_80S_20M (NASA PDS)","LROC NAC ROI centres","NASA MODIS Terra monthly LST 2023 via NASA GIBS (temperatures)","MODIS MCD12Q1 via NASA GIBS","SRTM-based AWS Terrain Tiles","ERA5 via Open-Meteo (validation sites)"],
 "ai_disclosure":"Computation scripts and data assembly produced with Claude (Anthropic)."}
out={"meta":meta,"tasks":TASKS,"moon_sites":moon_sites,"task_rankings":task_rankings}
json.dump(out,open("moon_results.json","w"),ensure_ascii=False,indent=1)
# global heat-map grid (compact)
grid=g[["lat","lon","M2","M3","M6"]+[f"M4_{k}" for k in M]].copy(); grid["ice"]=g.icesheet.astype(int); grid["known"]=g.known_region.fillna("")
json.dump({"meta":{"grid":"1-deg land cells","columns":list(grid.columns),"note":"M4_* here = relief-only screen (no 30 m slope); use task_rankings.M4 for final M4"},
  "rows":grid.round(1).where(grid.notna(),None).values.tolist()},open("moon_global_grid.json","w"),separators=(",",":"))
print("ok", len(moon_sites), {t:len(task_rankings[t]["new_candidates"]) for t in ["M2","M3","M6"]})
for t in ["M2","M3","M6"]: print(t,[ (x["name_zh"],x["score"]) for x in task_rankings[t]["new_candidates"][:5]])
