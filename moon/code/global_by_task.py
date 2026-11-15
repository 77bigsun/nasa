"""Global per-task ranking (19,599 land cells, 1 deg). 11/14 feature weights, c data-fitness.
M2: noon .3 / low-sun .7 (astronomy, c=1)
M3: darkness .5 (c=1) / annual min T .35 (c=.6) / diurnal range .15 (c=.6; missing cells drop it)
M6: annual mean .25 / annual max .25 (c=.6) / ice-permafrost proxy .5 (c=.3)
M4: per lunar site: relief only on the full grid (c=.6); 30 m slope ranking in m4_global_by_moonsite.csv
Ice-sheet cells (annual max < -1 C) are listed separately: cold like the Moon but the surface is ice, not rock."""
import sys, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "/home/claude/global")
from global_screen import solar
D = lambda x, b, t: np.clip((x - b) / (t - b), 0, 1)
g = pd.read_csv(sys.argv[1])
sol = {la: solar(la) for la in sorted(g.lat.unique())}
g["lowsun"] = g.lat.map(lambda l: sol[l][0]); g["dark_h"] = g.lat.map(lambda l: sol[l][1])
s = pd.DataFrame(index=g.index)
s["noon"] = D(90 - g.lat.abs(), 90, 5); s["low"] = D(g.lowsun, 0, 1); s["dark"] = D(g.dark_h, 12, 120)
s["tmin"] = D(g.T2M_MIN_C, 0, -89); s["dtr"] = D(g.T2M_RANGE_C, 10, 40)
s["tmean"] = D(g.T2M_ann_C, 15, -55); s["tmax"] = D(g.T2M_MAX_C, 40, -20)
s["ice"] = 0.4 * (g.T2M_ann_C <= -2) + 0.3 * (g.T2M_ann_C <= -8)
def comb(cols):
    num = sum(s[k].fillna(0) * w * c for k, w, c in cols)
    den = sum(s[k].notna() * w * c for k, w, c in cols)
    return (100 * num / den).where(den > 0)
T = pd.DataFrame({
    "M2": comb([("noon", .3, 1), ("low", .7, 1)]),
    "M3": comb([("dark", .5, 1), ("tmin", .35, .6), ("dtr", .15, .6)]),
    "M6": comb([("tmean", .25, .6), ("tmax", .25, .6), ("ice", .5, .3)]),
})
M = json.load(open("/home/claude/global/moon10_reference_sites.json"))
rel = g.relief16km_m.where(g.relief16km_m > 0)
for k, v in M.items():
    T["M4_" + k] = (100 * np.exp(-np.log(rel / v["relief_16km_m"]) ** 2 / (2 * np.log(2) ** 2))).where(rel.notna())
out = pd.concat([g, s.add_prefix("s_").round(3), T.round(1)], axis=1)
out["icesheet"] = g.T2M_MAX_C < -1
out.to_csv("/home/claude/global/global_by_task.csv", index=False)
rock = out[~out.icesheet]
res = {}
for t in ["M2", "M3", "M6"]:
    r = rock.sort_values(t, ascending=False)
    res[t] = {"top": r.head(10)[["lat", "lon", t, "T2M_ann_C", "T2M_MIN_C", "T2M_MAX_C"]].values.tolist(),
              "bottom": r.tail(5)[["lat", "lon", t]].values.tolist()}
json.dump(res, open("/home/claude/global/global_by_task_top.json", "w"))
fig, ax = plt.subplots(3, 1, figsize=(11, 15), dpi=110)
for a, t, title in zip(ax, ["M2", "M3", "M6"], ["M2 Low-sun illumination", "M3 Long darkness & extreme cold", "M6 Cold-trap ice / permafrost"]):
    sc = a.scatter(rock.lon, rock.lat, c=rock[t], s=2.4, marker="s", cmap="viridis", vmin=0, vmax=100, linewidths=0)
    i = out[out.icesheet]; a.scatter(i.lon, i.lat, c="#cfd3d8", s=2.4, marker="s", linewidths=0)
    a.set_xlim(-180, 180); a.set_ylim(-90, 90); a.set_title(title + "  (grey = ice sheet, ranked separately)"); a.grid(alpha=.25)
    plt.colorbar(sc, ax=a, fraction=0.02, pad=0.01)
plt.tight_layout(); plt.savefig("/home/claude/global/global_by_task_maps.png")
for t in res: print(t, "TOP", [(a, b, round(c, 1)) for a, b, c, *_ in res[t]["top"][:5]], "BOTTOM", res[t]["bottom"][-3:])
