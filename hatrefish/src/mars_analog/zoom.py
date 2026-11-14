"""
放大（zoom）：把候選地從 0.1° 格（約 11 km）放大到約 1 km 子格重新計分，找出框內最像的 1 km 小區。

流程
1. 候選地：outputs/profiles/mars_{目標}_profile.json 的整體前 N 名（或某個面向的前 N 名，或手動座標）。
2. 以候選格為中心取一個方框（預設半寬 0.25°，約 55 km × 55 km），在 GEE 上把下列變數算到 0.01° 子格：
     坡度、粗糙度、海拔（Copernicus GLO-30 → 200 m）、地表溫度與日夜溫差、反照率、NDVI（250 m）、
     乾燥指數、陸地／冰雪／水體比例；另抓 HLS 真彩色當底圖（只畫圖）。
   方框下載結果跟目標無關，存在 data/interim/zoom/ 重複使用。
3. 岩性（GLiM 0.5°）、永凍土（ESA CCI 1 km 但本機只有 0.1° 版）、沙塵（MERRA-2 約 50 km）原生解析度比子格粗，
   直接沿用每個子格所在的 0.1° 格的值。
4. 百分位（熱慣量、冷、乾、日溫差）用全球 0.1° 的參考分布（earth_reference_pct.json）換算，
   然後用和全球版完全相同的 similarity_vector + 面向計分（profiles.score_table）。
5. 輸出 outputs/zoom/：每個候選一張圖（底圖＋子格分數＋面向比較）、zoom_{目標}.json、ZOOM_SUMMARY.md。

注意：子格的值和 0.1° 格的值不完全可比（地形資料不同、尺度不同），所以結果檔同時列出
「原本 0.1° 格的分數」和「同一個 0.1° 格內子格分數的中位數」，可以看出換資料、換尺度造成的差。
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import math
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from . import config, profiles
from .config import VARIABLES
from .novelty import distinct_sites, haversine_km, place_name
from .paths import DATA, OUTPUTS
from .similarity import ice_target, similarity_vector

CACHE = DATA / "interim" / "zoom"
OUT = OUTPUTS / "zoom"
HALF_DEG = 0.25          # 方框半寬（度）
SUB_DEG = 0.01           # 子格大小（度），約 1 km
RGB_DEG = 0.001          # 底圖像素（度），約 100 m
TOP_SUB = 3              # 每個框列出幾個最佳子格
SUB_SEP_KM = 5           # 最佳子格彼此至少相距
GRID_RES = 0.1
FINE_COLS = ["slope_deg", "roughness_m", "elev_m", "lst_day_c", "lst_night_c", "dtr_c", "lst_mean_c",
             "albedo", "ndvi_mean", "aridity_index", "land_frac", "ice_frac", "barren_frac", "water_frac"]
GROUPS = {  # 名稱: (gee_zoom 的函式名, 波段)
    "terrain": ("terrain", ["slope_deg", "roughness_m", "elev_m"]),
    "climate": ("climate", ["lst_day_c", "lst_night_c", "dtr_c", "lst_mean_c"]),
    "surface": ("surface", ["albedo", "ndvi_mean", "aridity_index"]),
    "masks": ("masks", ["land_frac", "ice_frac", "barren_frac", "water_frac"]),
}


# ---------------- 方框 ----------------
def box_for(lat: float, lon: float, half: float = HALF_DEG, sub: float = SUB_DEG) -> dict:
    """以 (lat, lon) 為中心、南北半寬 half 度的方框；東西方向放寬成 half / cos(緯度)，讓方框在公里上接近正方形
    （最多放寬 4 倍）。邊界對齊子格，不跨過 ±180° 經線與兩極。"""
    half_lon = min(half / max(math.cos(math.radians(lat)), 0.25), 4 * half)
    ny = int(round(2 * half / sub))
    nx = int(round(2 * half_lon / sub))
    half_lon = nx * sub / 2
    x0 = round((lon - half_lon) / sub) * sub
    y0 = round((lat + half) / sub) * sub
    x0 = min(max(x0, -180.0), 180.0 - 2 * half_lon)
    y0 = min(max(y0, -90.0 + 2 * half), 90.0)
    return {"x0": round(x0, 6), "y0": round(y0, 6), "half": half, "half_lon": round(half_lon, 6), "sub": sub,
            "nx": nx, "ny": ny, "center": [round(lat, 4), round(lon, 4)]}


def _key(box: dict, dem: str) -> str:
    return f"box_{box['y0']:+08.3f}_{box['x0']:+09.3f}_{box['nx']}x{box['ny']}_{box['sub']:.3f}_{dem}"


def fetch_box(box: dict, dem: str = "copernicus", with_rgb: bool = True, refresh: bool = False) -> dict:
    """下載一個方框的子格變數（和目標無關，存快取）。回傳 {波段: (n, n) 陣列, 'rgb': (m, m, 3) 或 None, 'meta': {...}}。"""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{_key(box, dem)}.npz"
    out = {}
    if path.exists() and not refresh:
        z = np.load(path, allow_pickle=False)
        out = {k: z[k] for k in z.files if k not in ("rgb", "meta")}
        out["rgb"] = z["rgb"] if z["rgb"].size else None
        out["meta"] = json.loads(str(z["meta"]))
        need_rgb = with_rgb and out["rgb"] is None and not out["meta"].get("rgb_tried")
        if not need_rgb:              # 之前用 --no-rgb 抓的才需要回去補底圖
            return out

    import ee
    from .adapters.earth import gee_zoom as G
    x0, y0, nx, ny, sub = box["x0"], box["y0"], box["nx"], box["ny"], box["sub"]
    lat_c, lon_c = y0 - box["half"], x0 + box["half_lon"]
    tf = G.transform(x0, y0, sub)
    t0 = time.time()
    meta = out.get("meta", {"box": box, "dem": dem})
    for name, (fn, bands) in GROUPS.items():
        if all(b in out for b in bands):
            continue
        img = G.terrain(lat_c, lon_c, tf, dem) if name == "terrain" else getattr(G, fn)(tf)
        out.update(G.fetch(img, bands, x0, y0, nx, ny, sub))
    rgb = out.get("rgb")
    if with_rgb and rgb is None:
        k = max(1, int(round(sub / RGB_DEG)))           # 底圖像素 = 子格的 1/k
        mx, my, res2 = nx * k, ny * k, sub / k
        while mx * my > 1_500_000:                       # 太大就降解析度（computePixels 單次上限約 48 MB）
            k = max(1, k // 2); mx, my, res2 = nx * k, ny * k, sub / k
        tf2 = G.transform(x0, y0, res2)
        region = ee.Geometry.Rectangle([x0, y0 - 2 * box["half"], x0 + 2 * box["half_lon"], y0], None, False)
        try:
            img, nimg = G.rgb(region, tf2)
            if img is not None:
                r = G.fetch(img, ["red", "green", "blue"], x0, y0, mx, my, res2)
                rgb = np.dstack([r["red"], r["green"], r["blue"]]).astype("float32")
                meta["rgb_source"] = f"NASA HLS S30+L30 median {G.HLS_DATES[0]}–{G.HLS_DATES[1]}, cloud < {G.HLS_MAX_CLOUD}% ({nimg} scenes)"
            else:
                h = G.fetch(G.hillshade(lat_c, lon_c, tf2), ["hillshade"], x0, y0, mx, my, res2)["hillshade"]
                rgb = np.dstack([h, h, h]).astype("float32") / 255.0
                meta["rgb_source"] = "Copernicus GLO-30 hillshade (no HLS scenes here)"
        except Exception as e:  # noqa: BLE001  底圖失敗不影響計分
            print(f"  ! 底圖失敗 {box['center']}: {str(e)[:120]}", flush=True)
            rgb = None
            meta["rgb_source"] = None
        meta["rgb_tried"] = True
    meta["seconds"] = round(time.time() - t0, 1)
    meta["fetched_at"] = datetime.now().isoformat(timespec="seconds")
    save = {k: out[k] for k in FINE_COLS}
    np.savez_compressed(path, **save, rgb=rgb if rgb is not None else np.zeros((0,), "float32"),
                        meta=json.dumps(meta))
    out["rgb"], out["meta"] = rgb, meta
    return out


# ---------------- 子格表 ----------------
def _pct(x: np.ndarray, qs: list[float]) -> np.ndarray:
    """用全球參考分布的 101 個分位數把數值換成百分位（0–1）。"""
    q = np.maximum.accumulate(np.asarray(qs, dtype="float64"))
    q = q + np.arange(len(q)) * 1e-9          # 去掉重複值，讓內插有定義
    p = np.interp(x, q, np.linspace(0, 1, len(q)))
    return np.where(np.isfinite(x), p, np.nan)


def subgrid_frame(arr: dict, box: dict) -> pd.DataFrame:
    """把方框陣列攤成表，欄位和 earth_grid.parquet 相同，讓 similarity_vector 可以直接用。"""
    nx, ny, sub, x0, y0 = box["nx"], box["ny"], box["sub"], box["x0"], box["y0"]
    iy, ix = np.mgrid[0:ny, 0:nx]
    lat = (y0 - (iy + 0.5) * sub).ravel()
    lon = (x0 + (ix + 0.5) * sub).ravel()
    df = pd.DataFrame({"sub_iy": iy.ravel().astype("int16"), "sub_ix": ix.ravel().astype("int16"),
                       "lat": lat.round(4), "lon": lon.round(4)})
    for c in FINE_COLS:
        df[c] = np.asarray(arr[c], dtype="float64").ravel()

    # 陸地遮罩（同 earth_grid.land_mask）
    land = (np.nan_to_num(df.land_frac) >= 0.5) & ((np.nan_to_num(df.ice_frac) < 0.5) |
                                                   (np.nan_to_num(df.barren_frac) >= 0.25))
    land &= ~((np.nan_to_num(df.water_frac) > 0.5) & (df.lat > -60))
    land &= ~((np.nan_to_num(df.slope_deg, nan=1) < 0.05) & (np.abs(np.nan_to_num(df.elev_m, nan=99)) <= 2))
    df["land"] = land.values

    # 熱慣量（ATI）與乾燥指數：同 earth_grid.build 的規則
    df.loc[df.lat < -60, "aridity_index"] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        ati = (1 - df.albedo) / df.dtr_c
    ati[(df.dtr_c < 5) | ~np.isfinite(ati) | ~(df.aridity_index < 0.65)] = np.nan
    df["ati"] = ati

    # 原生解析度比子格粗的變數：沿用所在 0.1° 格（那一格不在全球陸地表時，用框內最近的陸地格）
    g = profiles.grid()
    piy = np.floor((90 - df.lat.values) / GRID_RES).astype(int)
    pix = np.floor((df.lon.values + 180) / GRID_RES).astype(int) % 3600
    pkey = piy * 3600 + pix
    gk = g.iy.values.astype(int) * 3600 + g.ix.values.astype(int)
    pos = pd.Series(np.arange(len(g)), index=gk)
    hit = pd.Series(pkey).map(pos)
    in_box = g[(g.lat.between(y0 - 2 * box["half"] - GRID_RES, y0 + GRID_RES)) &
               (g.lon.between(x0 - GRID_RES, x0 + 2 * box["half_lon"] + GRID_RES))]
    if hit.isna().any() and len(in_box):
        miss = np.where(hit.isna().values)[0]
        bl, bo = in_box.lat.values, in_box.lon.values
        for i in miss:
            d = haversine_km(df.lat.values[i], df.lon.values[i], bl, bo)
            hit.iloc[i] = pos[int(in_box.iy.values[d.argmin()]) * 3600 + int(in_box.ix.values[d.argmin()])]
    df["parent_filled"] = pd.Series(pkey).map(pos).isna().values
    rows = hit.values
    ok = np.isfinite(rows)
    ridx = np.where(ok, rows, 0).astype(int)
    for c in ("glim_class", "permafrost_frac", "dust_aod", "dust_pct"):
        v = g[c].values[ridx]
        df[c] = pd.Series(v).where(ok, None if c == "glim_class" else np.nan).values
    df["glim_class"] = df.glim_class.fillna("nd").astype("string")
    df["parent_cell"] = np.where(ok, g.cell_id.astype(str).values[ridx], None)

    # 百分位：用全球參考分布換算
    ref = profiles.ref()
    df["ati_pct"] = _pct(df.ati.values, ref["ati"]["quantiles"])
    df["cold_pct"] = 1 - _pct(df.lst_mean_c.values, ref["lst_mean_c"]["quantiles"])
    df["dtr_pct"] = _pct(df.dtr_c.values, ref["dtr_c"]["quantiles"])
    df["arid_pct"] = 1 - _pct(df.aridity_index.values, ref["aridity_index"]["quantiles"])

    cov = {
        "cov_slope": df.slope_deg.notna(), "cov_roughness": df.roughness_m.notna(),
        "cov_thermal_inertia": df.ati.notna(), "cov_lithology": ~df.glim_class.isin(["nd", "wb"]),
        "cov_ice": df.permafrost_frac.notna(), "cov_temperature": df.lst_mean_c.notna(),
        "cov_diurnal_range": df.dtr_c.notna(), "cov_aridity": df.aridity_index.notna(),
        "cov_barrenness": df.ndvi_mean.notna(), "cov_dust": df.dust_aod.notna(),
    }
    for k, v in cov.items():
        df[k] = (v.values & df.land.values).astype(bool)
    return df


def score_box(target_id: str, sub_df: pd.DataFrame) -> pd.DataFrame:
    target = config.mars_targets()[target_id]
    sim = similarity_vector(target, sub_df, profiles.ref(), "B")
    tab = profiles.score_table(sim, sub_df.lat.values, sub_df.lon.values, sub_df.index)
    land = sub_df.land.values
    for c in [c for c in tab.columns if c.startswith("dim_")] + ["overall"]:
        tab.loc[~land, c] = np.nan
    return tab


# ---------------- 紀錄 ----------------
def _r(x, nd=3):
    return profiles._rnd(x, nd)


def worldview(lat, lon, half=0.1):
    return profiles.worldview_url(lat, lon, half)


def _sub_record(target_id: str, tab: pd.DataFrame, sdf: pd.DataFrame, i, rank: int) -> dict:
    target = config.mars_targets()[target_id]
    row, srow = tab.loc[i], sdf.loc[i]
    dims = {k: _r(row[f"dim_{k}"]) for k in profiles.evaluable()}
    have = {k: v for k, v in dims.items() if v is not None}
    breaks = []
    for v in VARIABLES:
        s = row[f"s_{v}"]
        if not np.isfinite(s) or s >= profiles.BREAK:
            continue
        col, key, unit = profiles.VALUE_KEYS[v]
        dim = next((k for k in profiles.evaluable() if v in profiles.dimensions()[k]["variables"]), None)
        mv = ice_target(target) if v == "ice" else target.get(v, {}).get(key)
        breaks.append({"variable": v, "dimension": dim or "reference_only", "score": _r(s),
                       "earth": _r(srow[col]) if col in srow.index else None, "mars": _r(mv), "unit": unit})
    return {
        "rank": rank, "lat": _r(row.lat, 3), "lon": _r(row.lon, 3),
        "overall": _r(row.overall, 1), "confidence": _r(row.confidence, 2),
        "variable_coverage": _r(row.var_coverage, 2),
        "dimension_scores": dims,
        "strongest_dimension": max(have, key=have.get) if have else None,
        "weakest_dimension": min(have, key=have.get) if have else None,
        "variable_scores": {v: _r(row[f"s_{v}"]) for v in VARIABLES},
        "breaks": breaks,
        "earth_values_1km": {c: _r(srow[c]) for c in ("slope_deg", "roughness_m", "elev_m", "lst_mean_c", "dtr_c",
                                                      "aridity_index", "ndvi_mean", "ati")},
        "earth_values_from_0p1_cell": {"glim_class": str(srow.glim_class), "permafrost_frac": _r(srow.permafrost_frac),
                                       "dust_aod": _r(srow.dust_aod)},
        "worldview_url": worldview(float(row.lat), float(row.lon)),
        "google_maps_url": f"https://www.google.com/maps/@{float(row.lat):.4f},{float(row.lon):.4f},12000m/data=!3m1!1e3",
    }


def zoom_one(target_id: str, cand: dict, arr: dict, box: dict, dimension: str | None = None) -> tuple[dict, pd.DataFrame]:
    sdf = subgrid_frame(arr, box)
    tab = score_box(target_id, sdf)
    pool = tab[(tab.confidence >= profiles.MIN_CONF) & (tab.var_coverage >= profiles.MIN_CONF) &
               np.isfinite(tab.overall)].copy()
    if dimension:
        pool = pool[np.isfinite(pool[f"dim_{dimension}"])]
        pool["_key"] = pool[f"dim_{dimension}"].round(3) * 1000 + pool.overall / 1000
    else:
        pool["_key"] = pool.overall
    sel = distinct_sites(pool, "_key", TOP_SUB, SUB_SEP_KM) if len(pool) else pool
    best = [_sub_record(target_id, tab, sdf, i, k + 1) for k, i in enumerate(sel.index)]
    if best:
        names = place_name([b["lat"] for b in best], [b["lon"] for b in best])
        for b, nm in zip(best, names):
            b["name"] = nm

    # 同一個 0.1° 格內子格的中位數：看「換資料＋換尺度」本身造成的差
    plat, plon = float(cand["lat"]), float(cand["lon"])
    inside = (np.abs(tab.lat - plat) < GRID_RES / 2) & (np.abs(tab.lon - plon) < GRID_RES / 2) & sdf.land.values
    land_n = int(sdf.land.sum())
    coarse_ov = cand.get("overall")
    rec = {
        "target": target_id,
        "mode": f"dimension:{dimension}" if dimension else "overall",
        "candidate": {k: cand.get(k) for k in ("rank", "name", "lat", "lon", "overall", "dimension_scores",
                                               "known_analog", "nearest_known", "nearest_known_km")},
        "box": {**{k: box[k] for k in ("x0", "y0", "half", "half_lon", "sub", "nx", "ny")},
                "dem": arr["meta"].get("dem"), "n_subcells": int(len(sdf)), "n_land": land_n,
                "n_ranked": int(len(pool)), "rgb_source": arr["meta"].get("rgb_source")},
        "parent_cell_1km_median": {
            "overall": _r(float(np.nanmedian(tab.overall[inside])) if inside.any() else None, 1),
            "dimension_scores": {k: _r(float(np.nanmedian(tab[f"dim_{k}"][inside])) if inside.any() else None)
                                 for k in profiles.evaluable()},
            "n_subcells": int(inside.sum())},
        "share_ge_coarse_overall": _r(float((tab.overall[sdf.land.values] >= coarse_ov).mean())
                                      if land_n and coarse_ov is not None else None, 3),
        "best_subsites": best,
    }
    return rec, tab.join(sdf[[c for c in sdf.columns if c not in tab.columns]])


# ---------------- 圖 ----------------
def _stretch(rgb: np.ndarray) -> np.ndarray:
    a = rgb.copy()
    ok = np.isfinite(a).all(2)
    if not ok.any():
        return np.ones_like(a)
    lo, hi = np.nanpercentile(a[ok], [2, 98])
    a = np.clip((a - lo) / max(hi - lo, 1e-6), 0, 1) ** (1 / 1.2)
    a[~ok] = 0.92
    return a


def figure(rec: dict, tab: pd.DataFrame, arr: dict, path: Path, target_name: str):
    plt = profiles._plt()
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Rectangle

    P = profiles
    box = rec["box"]
    nx, ny, x0, y0, half, hlon = box["nx"], box["ny"], box["x0"], box["y0"], box["half"], box["half_lon"]
    ext = [x0, x0 + 2 * hlon, y0 - 2 * half, y0]
    lat_c = y0 - half
    aspect = 1 / max(math.cos(math.radians(lat_c)), 0.2)
    cand = rec["candidate"]
    best = rec["best_subsites"]

    fig = plt.figure(figsize=(14.5, 6.0), dpi=150)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.9], height_ratios=[1, 0.035], wspace=0.3, hspace=0.22)
    ax1, ax2, ax3 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[:, 2])
    cax = fig.add_subplot(gs[1, 1])

    def marks(ax, color_text):
        ax.add_patch(Rectangle((cand["lon"] - GRID_RES / 2, cand["lat"] - GRID_RES / 2), GRID_RES, GRID_RES,
                               fill=False, ec=P.INK, lw=1.2, ls=(0, (4, 3)), zorder=4))
        for b in best:
            ax.scatter([b["lon"]], [b["lat"]], s=90, color=P.ACCENT, ec=P.SURFACE, lw=2, zorder=6)
            ax.annotate(str(b["rank"]), (b["lon"], b["lat"]), xytext=(7, 6), textcoords="offset points",
                        fontsize=9, fontweight="bold", color=color_text, zorder=7)
        ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(aspect)
        ax.tick_params(labelsize=7, colors=P.INK2)
        for s in ax.spines.values():
            s.set_color(P.GRID)

    # (a) 底圖
    if arr.get("rgb") is not None:
        ax1.imshow(_stretch(arr["rgb"]), extent=ext, origin="upper", interpolation="bilinear")
        src = rec["box"]["rgb_source"] or ""
    else:
        ax1.set_facecolor(P.GRID)
        src = "no basemap"
    marks(ax1, P.SURFACE)
    ax1.set_title("Surface (true color)", fontsize=9, loc="left", color=P.INK, pad=14)
    ax1.text(0, 1.012, src[:80], transform=ax1.transAxes, fontsize=6, color=P.INK2, va="bottom")

    # (b) 子格整體相似度
    ov = tab.overall.values.reshape(ny, nx)
    cmap = LinearSegmentedColormap.from_list("blue", P.BLUE_RAMP)
    cmap.set_bad(P.GRID)
    fin = ov[np.isfinite(ov)]
    vmin = float(np.nanpercentile(fin, 5)) if fin.size else 0
    vmax = float(np.nanmax(fin)) if fin.size else 100
    im = ax2.imshow(np.ma.masked_invalid(ov), extent=ext, origin="upper", cmap=cmap, vmin=vmin,
                    vmax=max(vmax, vmin + 1), interpolation="nearest")
    marks(ax2, P.INK)
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_label("overall similarity (0–100)", fontsize=7, color=P.INK2)
    cb.ax.tick_params(labelsize=7, colors=P.INK2); cb.outline.set_visible(False)
    ax2.set_title("Overall similarity, 1 km sub-cells", fontsize=9, loc="left", color=P.INK, pad=14)
    ax2.text(0, 1.012, "gray = water, ice or no data", transform=ax2.transAxes, fontsize=6, color=P.INK2,
             va="bottom")

    # (c) 面向分數：0.1° 格 vs 最佳 1 km 子格
    dims = P.evaluable()
    labels = [P.dimensions()[k].get("label_en", k) for k in dims]
    c0 = [(cand.get("dimension_scores") or {}).get(k) for k in dims]
    c1 = [(best[0]["dimension_scores"] if best else {}).get(k) for k in dims]
    y = np.arange(len(dims))
    hgt = 0.36
    ax3.barh(y - hgt / 2 - 0.01, [v or 0 for v in c0], height=hgt, color=P.MUTED, label="0.1° cell (global run)")
    ax3.barh(y + hgt / 2 + 0.01, [v or 0 for v in c1], height=hgt, color=P.ACCENT, label="best 1 km sub-cell (#1)")
    for yy, v in zip(y, c1):
        if v is not None:
            ax3.text(min(v, 1.0) + 0.015, yy + hgt / 2, f"{v:.2f}", va="center", fontsize=7, color=P.INK)
    ax3.set_yticks(y); ax3.set_yticklabels(labels, fontsize=8, color=P.INK)
    ax3.invert_yaxis(); ax3.set_xlim(0, 1.12); ax3.set_xticks([0, 0.5, 1.0])
    ax3.tick_params(axis="x", labelsize=7, colors=P.INK2)
    ax3.grid(axis="x", color=P.GRID, lw=0.6); ax3.set_axisbelow(True)
    for s in ("top", "right"):
        ax3.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax3.spines[s].set_color(P.GRID)
    ax3.legend(fontsize=7, frameon=False, loc="upper left", bbox_to_anchor=(0.0, -0.07), ncol=1)
    o0, o1 = cand.get("overall"), best[0]["overall"] if best else None
    ax3.set_title(f"Dimension scores — overall {o0:.0f} → {o1:.0f}" if (o0 is not None and o1 is not None)
                  else "Dimension scores", fontsize=9, loc="left", color=P.INK, pad=14)

    head = f"#{cand['rank']} " if cand.get("rank") else ""
    nm = cand.get("name") or f"{cand['lat']}, {cand['lon']}"
    b0 = f"   best 1 km: {best[0]['lat']:.3f}, {best[0]['lon']:.3f}" if best else ""
    fig.suptitle(f"Zoom — {target_name.split(' (')[0]} analog candidate {head}{nm}{b0}",
                 fontsize=11, x=0.01, ha="left", color=P.INK)
    fig.text(0.01, -0.02, "Dashed square = the 0.1° cell from the global run. Dots = best 1 km sub-cells "
             f"(at least {SUB_SEP_KM} km apart). Lithology, permafrost and dust come from the 0.1° cell.",
             fontsize=7, color=P.INK2)
    fig.savefig(path, bbox_inches="tight", facecolor=P.SURFACE)
    plt.close(fig)


# ---------------- 主流程 ----------------
def candidates(target_id: str, top: int = 5, dimension: str | None = None) -> list[dict]:
    pj = profiles.OUT / f"mars_{target_id}_profile.json"
    res = json.loads(pj.read_text(encoding="utf-8")) if pj.exists() else profiles.build_target(target_id)
    recs = res["top_by_dimension"][dimension] if dimension else res["top_overall"]
    return recs[:top]


def manual_candidate(target_id: str, lat: float, lon: float) -> dict:
    """手動座標：找出它所在的 0.1° 格，當成候選（rank = None）。"""
    df = profiles.profile_table(target_id)
    d = haversine_km(lat, lon, df.lat.values, df.lon.values)
    i = df.index[int(np.argmin(d))]
    rec = profiles._record(target_id, i, None)
    rec["name"] = place_name([rec["lat"]], [rec["lon"]])[0]
    return rec


def summary_md() -> str:
    """把 outputs/zoom/ 裡所有 zoom_*.json 整理成一張表（不同次執行的結果都會列進來）。"""
    dims = profiles.dimensions()
    files = sorted(OUT.glob("zoom_*.json"))
    L = ["# 放大結果（自動產生）", "",
         f"> 產生時間 {datetime.now(profiles.TZ):%Y-%m-%d %H:%M}，由 `scripts/zoom_candidates.py` 產生；數字以 `outputs/zoom/zoom_*.json` 為準。",
         "> 每個候選地以 0.1° 格為中心取方框，在約 1 km 子格重算坡度、粗糙度、溫度、乾燥度、NDVI、熱慣量；"
         "岩性、永凍土、沙塵沿用所在 0.1° 格。計分方法和全球版完全相同（面向等權重）。",
         "> 「0.1° 格內 1 km 中位數」和「0.1° 原分數」的差，是換資料（地形 GMTED → Copernicus）和換尺度本身造成的，"
         "不是找到更好的地點；看「最佳 1 km」要和這個中位數比。", ""]
    for fp in files:
        d = json.loads(fp.read_text(encoding="utf-8"))
        tid, recs, st = d["target"], d["results"], d.get("settings", {})
        if not recs:
            continue
        t = config.mars_targets().get(tid, {})
        m = st.get("mode") or ""
        mode = ({"overall": "整體前幾名", "point": "手動座標"}.get(m) or
                (f"{dims[m.split(':', 1)[1]]['label_zh']}面向前幾名" if m.startswith("dimension:") else m))
        L += [f"## {t.get('name', tid)}（{mode}；子格 {st.get('sub_deg')}°，方框半寬 {st.get('half_deg')}°，"
              f"地形 {st.get('dem')}）", "",
              "| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 連結 |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in recs:
            c, b = r["candidate"], (r["best_subsites"][0] if r["best_subsites"] else None)
            pm = r["parent_cell_1km_median"]["overall"]
            wk = dims[b["weakest_dimension"]]["label_zh"] if b and b["weakest_dimension"] else "—"
            share = r["share_ge_coarse_overall"]
            L.append(
                f"| #{c.get('rank') or '—'} {c.get('name') or ''} | {c['lat']}, {c['lon']} | "
                f"{c['overall'] if c.get('overall') is not None else '—'} | {pm if pm is not None else '—'} | "
                + (f"{b['lat']:.3f}, {b['lon']:.3f}（{b.get('name', '')}） | {b['overall']} | {wk} | " if b else "— | — | — | ")
                + (f"{share * 100:.0f}% | " if share is not None else "— | ")
                + (f"[Worldview]({b['worldview_url']}) · [衛星圖]({b['google_maps_url']}) · 圖 `{r.get('figure', '')}` |"
                   if b else "— |"))
        L.append("")
    return "\n".join(L)


def run(targets: list[str] | None = None, top: int = 5, dimension: str | None = None,
        point: tuple[float, float] | None = None, half: float = HALF_DEG, sub: float = SUB_DEG,
        dem: str = "copernicus", with_rgb: bool = True, workers: int = 4, refresh: bool = False,
        make_figures: bool = True) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    targets = targets or list(config.mars_targets())
    jobs = []   # (target, candidate, box)
    for tid in targets:
        cands = [manual_candidate(tid, *point)] if point else candidates(tid, top, dimension)
        for c in cands:
            jobs.append((tid, c, box_for(float(c["lat"]), float(c["lon"]), half, sub)))
    boxes = {}
    for _, _, b in jobs:
        boxes.setdefault(_key(b, dem), b)
    print(f"放大：{len(jobs)} 個候選、{len(boxes)} 個方框（已下載的會用快取）", flush=True)
    arrs = {}
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_box, b, dem, with_rgb, refresh): k for k, b in boxes.items()}
        for k, f in enumerate(cf.as_completed(futs), 1):
            key = futs[f]
            try:
                arrs[key] = f.result()
                print(f"  [{k}/{len(futs)}] {key}  {arrs[key]['meta'].get('seconds', 0)} s", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"  ! {key} 失敗：{str(e)[:160]}", flush=True)
    print(f"下載完成，{time.time() - t0:.0f} 秒", flush=True)

    all_recs: dict = {t: [] for t in targets}
    for tid, c, b in jobs:
        key = _key(b, dem)
        if key not in arrs:
            continue
        rec, tab = zoom_one(tid, c, arrs[key], b, dimension)
        tag = f"{tid}_{'dim-' + dimension + '_' if dimension else ''}{c.get('rank') or 'pt'}"
        if make_figures:
            fp = OUT / f"zoom_{tag}.png"
            figure(rec, tab, arrs[key], fp, config.mars_targets()[tid].get("name", tid))
            rec["figure"] = fp.name
        all_recs[tid].append(rec)
    mode = f"dimension:{dimension}" if dimension else ("point" if point else "overall")
    for tid, recs in all_recs.items():
        if recs:
            name = f"zoom_{tid}{'_dim-' + dimension if dimension else ''}{'_point' if point else ''}.json"
            (OUT / name).write_text(json.dumps({"target": tid, "generated_at": datetime.now(profiles.TZ).isoformat(
                timespec="seconds"), "settings": {"half_deg": half, "sub_deg": sub, "dem": dem, "mode": mode},
                "results": recs}, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "ZOOM_SUMMARY.md").write_text(summary_md(), encoding="utf-8")
    print("寫出", OUT, flush=True)
    return all_recs
