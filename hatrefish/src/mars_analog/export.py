"""
B10：輸出結果檔 outputs/mars_{target}_{mission}.json（PROJECT_CONTEXT 7.1 格式）＋ 全球熱度圖 PNG。
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from . import config, training
from .config import GAPS, MISSIONS, VARIABLES
from .novelty import distinct_sites, flag_known, place_name
from .paths import OUTPUTS
from .scoring import aggregate

UNITS = {"slope": "deg", "roughness": "m", "thermal_inertia": "percentile", "ice": "fraction",
         "temperature": "C", "diurnal_range": "C", "aridity": "aridity_index", "barrenness": "NDVI",
         "dust": "percentile", "lithology": "class"}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
MIN_SEP_KM = 150   # 前 N 名彼此至少相距 150 km（50 km 時前 20 名全擠在西藏西部同一區）
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def worldview_url(lat, lon, half=1.0):
    return ("https://worldview.earthdata.nasa.gov/?v="
            f"{lon - half:.2f},{lat - half:.2f},{lon + half:.2f},{lat + half:.2f}"
            "&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01")


def _breaks(row, sim_row, target, thr, weights):
    out = []
    for v in VARIABLES:
        s = sim_row[f"s_{v}"]
        if weights.get(v, 0) < 0.01:   # 這個任務幾乎不計分的變數不列
            continue
        if not sim_row[f"cov_{v}"] or not np.isfinite(s) or s >= thr:
            continue
        t = target.get(v, {})
        if v == "temperature":
            e, mv = float(row.lst_mean_c), t.get("value")
        elif v == "slope":
            e, mv = float(row.slope_deg), t.get("value")
        elif v == "roughness":
            e, mv = float(row.roughness_m), t.get("value")
        elif v == "thermal_inertia":
            e, mv = float(row.ati_pct), t.get("pct")
        elif v == "dust":
            e, mv = float(row.dust_pct), t.get("pct")
        elif v == "ice":
            from .similarity import ice_target
            e, mv = float(row.permafrost_frac), ice_target(target)
        elif v == "aridity":
            e, mv = float(row.aridity_index), "hyper-arid (Mars)"
        elif v == "barrenness":
            e, mv = float(row.ndvi_mean), 0.0
        elif v == "diurnal_range":
            e, mv = float(row.dtr_c), t.get("value") or "larger than any Earth site (Mars)"
        else:
            e, mv = str(row.glim_class), t.get("group")
        rnd = (lambda x: round(x, 3) if isinstance(x, float) else x)
        out.append({"variable": v, "score": round(float(s), 3), "earth": rnd(e), "mars": rnd(mv), "unit": UNITS[v]})
    return out


def heatmap(target_id, mission, total: np.ndarray, top: pd.DataFrame, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    g = training.grid()
    arr = np.full((1800, 3600), np.nan, dtype="float32")
    arr[g.iy.values, g.ix.values] = total
    cmap = LinearSegmentedColormap.from_list("blue", BLUE_RAMP)
    cmap.set_bad("#efeeea")
    fig, ax = plt.subplots(figsize=(12, 5.6), dpi=160, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    vmin, vmax = np.nanpercentile(total, [50, 99.9])
    im = ax.imshow(arr, extent=[-180, 180, -90, 90], cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
    kn, nw = top[top.known_analog], top[~top.known_analog]
    ax.scatter(nw.lon, nw.lat, s=46, marker="o", facecolor="#eb6834", edgecolor=SURFACE, linewidth=1.5,
               label=f"new candidate ({len(nw)} of top {len(top)})", zorder=3)
    if len(kn):
        ax.scatter(kn.lon, kn.lat, s=52, marker="D", facecolor=INK, edgecolor=SURFACE, linewidth=1.5,
                   label=f"known analog ({len(kn)} of top {len(top)})", zorder=3)
    ka = config.known_analogs()
    ax.scatter(ka.lon, ka.lat, s=14, marker="x", color=INK2, linewidth=0.8, label="known analog sites (training labels)", zorder=2)
    for r in top.head(3).itertuples():
        ax.annotate(f"#{r.rank}", (r.lon, r.lat), xytext=(6, 6), textcoords="offset points", fontsize=9,
                    color=INK, fontweight="bold")
    ax.set_ylim(-60, 85)
    ax.set_xticks(range(-180, 181, 60)); ax.set_yticks(range(-60, 81, 30))
    ax.tick_params(colors=INK2, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    t = config.mars_targets()[target_id]
    ax.set_title(f"Earth similarity to {t['name']} — mission: {mission}", loc="left", fontsize=12, color=INK)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("total score (0–100)", color=INK2, fontsize=8); cb.ax.tick_params(colors=INK2, labelsize=7)
    cb.outline.set_visible(False)
    ax.legend(loc="lower left", fontsize=8, frameon=False, labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def export_one(target_id: str, mission: str, top_n: int = 20, weights: dict | None = None,
               method: str = "B", save: bool = True) -> dict:
    g = training.grid()
    target = config.mars_targets()[target_id]
    w = weights or config.weights_for(mission)
    sim = training.sim_for(target_id, method)
    agg = aggregate(sim, w)
    df = pd.concat([g[["cell_id", "lat", "lon"]], agg], axis=1)
    top = distinct_sites(df.dropna(subset=["total"]), top_n=top_n, min_sep_km=MIN_SEP_KM)
    top = flag_known(top)
    names = place_name(top.lat.values, top.lon.values)
    top["name"] = [n if k else p for n, k, p in zip(top.name, top.known_analog, names)]
    top["rank"] = np.arange(1, len(top) + 1)
    thr = config.features()["defaults"]["breaks_threshold"]
    results = []
    for idx, r in top.iterrows():
        sr, gr = sim.loc[idx], g.loc[idx]
        results.append({
            "rank": int(r["rank"]), "cell_id": r.cell_id, "lat": float(r.lat), "lon": float(r.lon),
            "name": r["name"], "total": round(float(r.total), 1), "confidence": round(float(r.confidence), 3),
            "scores": {v: (None if not sr[f"cov_{v}"] else round(float(sr[f's_{v}']), 3)) for v in VARIABLES},
            "coverage": {v: bool(sr[f"cov_{v}"]) for v in VARIABLES},
            "known_analog": bool(r.known_analog),
            "nearest_known": r.nearest_known, "nearest_known_km": float(r.nearest_known_km),
            "breaks": _breaks(gr, sr, target, thr, w), "gaps": GAPS, "worldview_url": worldview_url(r.lat, r.lon),
            # 11/14：南極極點附近 7 格沒有地形資料（elev/slope/roughness 為 NaN），進前 20 名時 round(NaN) 會當掉 → 輸出 null
            "earth_values": {"slope_deg": None if pd.isna(gr.slope_deg) else round(float(gr.slope_deg), 2),
                             "roughness_m": None if pd.isna(gr.roughness_m) else round(float(gr.roughness_m), 1),
                             "lst_mean_c": None if pd.isna(gr.lst_mean_c) else round(float(gr.lst_mean_c), 1),
                             "dtr_c": None if pd.isna(gr.dtr_c) else round(float(gr.dtr_c), 1),
                             "aridity_index": None if pd.isna(gr.aridity_index) else round(float(gr.aridity_index), 4),
                             "ndvi_mean": round(float(gr.ndvi_mean), 3) if pd.notna(gr.ndvi_mean) else None,
                             "permafrost_frac": None if pd.isna(gr.permafrost_frac) else round(float(gr.permafrost_frac), 2),
                             "glim_class": str(gr.glim_class),
                             "elev_m": None if pd.isna(gr.elev_m) else round(float(gr.elev_m))},
        })
    out = {"body": "mars", "version": "v1", "generated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
           "target": {"id": target_id, "name": target["name"], "lat": target["lat"], "lon": target["lon"]},
           "mission": mission, "method": method, "variables": VARIABLES,
           "weights": {v: round(w[v], 4) for v in VARIABLES}, "results": results,
           "heatmap": f"mars_{target_id}_{mission}.png",
           "provenance": {"mars_targets": config.mars_targets_source(),
                          "labels": config.known_analogs().attrs.get("source")}}
    if save:
        (OUTPUTS / f"mars_{target_id}_{mission}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                                                  encoding="utf-8")
        heatmap(target_id, mission, agg.total.values, top, OUTPUTS / f"mars_{target_id}_{mission}.png")
    return out


def run():
    for t in config.mars_targets():
        for m in MISSIONS:
            o = export_one(t, m)
            r = o["results"]
            print(f"{t}/{m}: #1 {r[0]['name']} {r[0]['total']}  known in top20: {sum(x['known_analog'] for x in r)}",
                  flush=True)


if __name__ == "__main__":
    run()
