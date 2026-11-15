"""Swap temperature source to NASA MODIS Terra monthly LST (2023, via NASA GIBS / Worldview), the competition-listed source.
Annual mean = mean of monthly (day+night)/2; annual max = max monthly daytime; annual min = min monthly night-time;
diurnal range = mean monthly (day - night). Colour-map floor: values < 200 K are reported as 199 K (-74 C).
Anchors are unchanged from the 11/14 model (b,t). Usage: python3 apply_lst.py modis_lst_2023_1deg.csv"""
import sys, numpy as np, pandas as pd
D = lambda x, b, t: np.clip((x - b) / (t - b), 0, 1)
g = pd.read_csv("/home/claude/global/global_by_task.csv")
l = pd.read_csv(sys.argv[1])
g = g.drop(columns=[c for c in g.columns if c.startswith("LST_") or c == "n_months"], errors="ignore").merge(l, on=["lat", "lon"], how="left")
g["temp_source"] = np.where(g.LST_mean_C.notna(), "MODIS_LST_2023", "NASA_POWER")
tmean = g.LST_mean_C.fillna(g.T2M_ann_C); tmax = g.LST_max_C.fillna(g.T2M_MAX_C)
tmin = g.LST_min_C.fillna(g.T2M_MIN_C); # polar day/night months have no diurnal cycle: LST present but no month with both day & night -> DTR 0
dtr = g.LST_dtr_C.where(g.LST_dtr_C.notna() | g.LST_mean_C.isna(), 0.0).fillna(g.T2M_RANGE_C)
g["DTR_used_C"] = dtr; g["Tmin_used_C"] = tmin; g["Tmean_used_C"] = tmean; g["Tmax_used_C"] = tmax
g["s_tmin"] = D(tmin, 0, -89); g["s_dtr"] = D(dtr, 10, 40)
g["s_tmean"] = D(tmean, 15, -55); g["s_tmax"] = D(tmax, 40, -20)
g["s_ice"] = 0.4 * (tmean <= -2) + 0.3 * (tmean <= -8)
def comb(cols):
    num = sum(g[k].fillna(0) * w * c for k, w, c in cols); den = sum(g[k].notna() * w * c for k, w, c in cols)
    return (100 * num / den).where(den > 0)
g["M3"] = comb([("s_dark", .5, 1), ("s_tmin", .35, .6), ("s_dtr", .15, .6)]).round(1)
g["M6"] = comb([("s_tmean", .25, .6), ("s_tmax", .25, .6), ("s_ice", .5, .3)]).round(1)
g.to_csv("/home/claude/global/global_by_task.csv", index=False)
print(g.temp_source.value_counts().to_dict())
