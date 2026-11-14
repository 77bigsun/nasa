"""
類比剖面（analog profile）：把 10 個單項相似度整理成 7 個類比面向，不依任務加權。

- 面向分數 = 面向內「有資料的變數」等權重幾何平均（下限 0.01，同 PROJECT_CONTEXT 第 4 節）
- 整體相似度 = 有分數的面向等權重幾何平均 × 100
- 信心度 = 這一格有分數的面向數 ÷ 目前可評估的面向數
- 生物、洞穴目前沒有變數 → 結果檔標成 not_evaluated（之後補資料只要改 config/dimensions.yaml）
- 排名：整體相似度前 N 名；每個面向各自的前幾名（面向分數相同時，用整體相似度決定先後）
- 已知類比地也算剖面，顯示它們在哪些面向像、哪些不像

輸出（outputs/profiles/）：
  mars_{目標}_profile.json      整體前 20、每面向前 5、已知類比地剖面、各面向「很像」的陸地比例
  map_{目標}_{面向}.png          每個面向＋整體的全球地圖
  radar_{目標}_top.png           整體前 6 名的雷達圖
  radar_{目標}_known.png         標給這個目標的已知類比地的雷達圖
  PROFILE_SUMMARY.md             人看的總表
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import numpy as np
import pandas as pd
import yaml

from . import config, earth_grid
from .config import VARIABLES
from .novelty import distinct_sites, flag_known, haversine_km, place_name
from .paths import CONFIG, OUTPUTS
from .similarity import ice_target, similarity_vector

EPS = 0.01
MIN_SEP_KM = 150          # 前 N 名彼此至少相距 150 km（同 export.py）
MIN_CONF = 0.8            # 排名只用「至少 80% 可評估面向有資料」的格子，避免缺資料的格子靠少數面向衝高分
TOP_OVERALL = 20
TOP_PER_DIM = 5
STRONG = 0.9              # 「很像」的門檻，用來算各面向很像的陸地比例
BREAK = 0.3               # 單項分數低於此值 → 寫進 breaks（哪裡不像）
OUT = OUTPUTS / "profiles"
TZ = timezone(timedelta(hours=8))

# 變數 → (地球網格欄位, 火星目標的鍵, 單位)
VALUE_KEYS = {
    "slope": ("slope_deg", "value", "deg"),
    "roughness": ("roughness_m", "value", "m"),
    "thermal_inertia": ("ati_pct", "pct", "percentile on own planet"),
    "lithology": ("glim_class", "group", "class"),
    "ice": ("permafrost_frac", "p", "Earth permafrost fraction vs Mars target clip(SWIM Ci,0,1)"),
    "temperature": ("lst_mean_c", "value", "C"),
    "diurnal_range": ("dtr_c", "value", "C"),
    "aridity": ("aridity_index", "value", "aridity index"),
    "barrenness": ("ndvi_mean", "value", "NDVI"),
    "dust": ("dust_pct", "pct", "percentile on own planet"),
}

BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
SURFACE, INK, INK2, GRID, ACCENT, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6", "#a8a7a2"


# ---------------- 設定與資料 ----------------
@lru_cache
def dimensions() -> dict:
    d = yaml.safe_load((CONFIG / "dimensions.yaml").read_text(encoding="utf-8"))["dimensions"]
    for v in d.values():
        v["variables"] = [x for x in (v.get("variables") or []) if x in VARIABLES]
    return d


def evaluable() -> list[str]:
    return [k for k, v in dimensions().items() if v["variables"]]


def not_evaluated() -> list[str]:
    return [k for k, v in dimensions().items() if not v["variables"]]


@lru_cache
def grid() -> pd.DataFrame:
    return earth_grid.load()


@lru_cache
def ref() -> dict:
    return earth_grid.reference()


def _gmean(S: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """每列等權重幾何平均，只用有限值。回傳 (平均, 有值的個數)；全部缺值 → NaN。"""
    L = np.log(np.maximum(S, EPS))          # NaN 會保留成 NaN
    ok = np.isfinite(L)
    n = ok.sum(1)
    m = np.where(ok, L, 0.0).sum(1) / np.maximum(n, 1)
    return np.where(n > 0, np.exp(m), np.nan), n


_CACHE: dict = {}


def profile_table(target_id: str) -> pd.DataFrame:
    """全球每一格：各面向分數、整體相似度、信心度、10 個單項分數。"""
    if target_id in _CACHE:
        return _CACHE[target_id]
    g = grid()
    sim = similarity_vector(config.mars_targets()[target_id], g, ref(), "B")
    df = score_table(sim, g.lat.values, g.lon.values, g.index)
    _CACHE[target_id] = df
    return df


def score_table(sim: pd.DataFrame, lat, lon, index=None) -> pd.DataFrame:
    """單項相似度（similarity_vector 的輸出）→ 各面向分數、整體相似度、信心度、變數覆蓋率。
    全球 0.1° 格（profile_table）和放大後的子格（zoom.py）共用同一套算法。"""
    out = {"lat": np.asarray(lat), "lon": np.asarray(lon)}
    for k in evaluable():
        S = np.column_stack([sim[f"s_{v}"].values.astype("float64") for v in dimensions()[k]["variables"]])
        d, n = _gmean(S)
        out[f"dim_{k}"] = d.astype("float32")
        out[f"ncov_{k}"] = n.astype("int8")
    D = np.column_stack([out[f"dim_{k}"] for k in evaluable()]).astype("float64")
    o, nd = _gmean(D)
    out["overall"] = (o * 100).astype("float32")
    out["confidence"] = (nd / len(evaluable())).astype("float32")
    nv = sum(len(dimensions()[k]["variables"]) for k in evaluable())
    out["var_coverage"] = (sum(out[f"ncov_{k}"].astype("int16") for k in evaluable()) / nv).astype("float32")
    df = pd.DataFrame(out, index=sim.index if index is None else index)
    for v in VARIABLES:
        df[f"s_{v}"] = sim[f"s_{v}"].values
    return df


# ---------------- 單一地點的紀錄 ----------------
def _rnd(x, nd=3):
    if x is None:
        return None
    if isinstance(x, (float, np.floating)):
        return None if not np.isfinite(x) else round(float(x), nd)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def worldview_url(lat, lon, half=1.0):
    return ("https://worldview.earthdata.nasa.gov/?v="
            f"{lon - half:.2f},{lat - half:.2f},{lon + half:.2f},{lat + half:.2f}"
            "&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01")


def _dims_of(row) -> dict:
    out = {k: None for k in dimensions()}
    for k in evaluable():
        out[k] = _rnd(row[f"dim_{k}"])
    return out


def _breaks(target: dict, row, grow) -> list[dict]:
    out = []
    for v in VARIABLES:
        s = row[f"s_{v}"]
        if not np.isfinite(s) or s >= BREAK:
            continue
        col, key, unit = VALUE_KEYS[v]
        dim = next((k for k in evaluable() if v in dimensions()[k]["variables"]), None)
        mv = ice_target(target) if v == "ice" else target.get(v, {}).get(key)
        out.append({"variable": v, "dimension": dim or "reference_only", "score": _rnd(s),
                    "earth": _rnd(grow[col]) if col in grow.index else None,
                    "mars": _rnd(mv), "unit": unit})
    return out


def _record(target_id: str, idx, rank: int | None = None) -> dict:
    df, g = profile_table(target_id), grid()
    row, grow = df.loc[idx], g.loc[idx]
    target = config.mars_targets()[target_id]
    dims = _dims_of(row)
    have = {k: v for k, v in dims.items() if v is not None}
    rec = {
        "rank": rank, "cell_id": str(grow["cell_id"]) if "cell_id" in grow.index else f"row_{int(idx)}",
        "lat": _rnd(row.lat, 2), "lon": _rnd(row.lon, 2),
        "overall": _rnd(row.overall, 1), "confidence": _rnd(row.confidence, 2),
        "variable_coverage": _rnd(row.var_coverage, 2),
        "dimension_scores": dims,
        "strongest_dimension": max(have, key=have.get) if have else None,
        "weakest_dimension": min(have, key=have.get) if have else None,
        "variable_scores": {v: _rnd(row[f"s_{v}"]) for v in VARIABLES},
        "breaks": _breaks(target, row, grow),
        "earth_values": {c: _rnd(grow[c]) for c in ("slope_deg", "roughness_m", "lst_mean_c", "dtr_c",
                                                     "aridity_index", "ndvi_mean", "permafrost_frac",
                                                     "glim_class", "elev_m") if c in grow.index},
        "gaps": list(config.GAPS),
        "worldview_url": worldview_url(float(row.lat), float(row.lon)),
    }
    return rec


def _annotate(recs: list[dict]) -> list[dict]:
    """已知類比地判斷（50 km）與新候選地的地名。"""
    if not recs:
        return recs
    t = pd.DataFrame({"lat": [r["lat"] for r in recs], "lon": [r["lon"] for r in recs]})
    t = flag_known(t)
    names = place_name(t.lat.values, t.lon.values)
    for r, kn, nk, nkm, nm, pn in zip(recs, t.known_analog, t.nearest_known, t.nearest_known_km, t.name, names):
        r["known_analog"] = bool(kn)
        r["nearest_known"] = nk
        r["nearest_known_km"] = _rnd(float(nkm), 0)
        r["name"] = nm if kn else pn
    return recs


# ---------------- 排名 ----------------
def _pool(target_id: str) -> pd.DataFrame:
    """排名用的格子：至少 80% 的面向有分數，而且至少 80% 的變數有資料（避免缺資料的格子靠較少變數衝高分）。"""
    df = profile_table(target_id)
    return df[(df.confidence >= MIN_CONF) & (df.var_coverage >= MIN_CONF) & np.isfinite(df.overall)]


def top_overall(target_id: str, n: int = TOP_OVERALL) -> list[dict]:
    sel = distinct_sites(_pool(target_id), "overall", n, MIN_SEP_KM)
    return _annotate([_record(target_id, i, k + 1) for k, i in enumerate(sel.index)])


def top_dimension(target_id: str, dim: str, n: int = TOP_PER_DIM) -> list[dict]:
    """只用「這個面向的變數全部有資料」的格子。面向分數取到小數第 2 位排序；同分時整體相似度高的優先。"""
    p = _pool(target_id)
    p = p[np.isfinite(p[f"dim_{dim}"]) & (p[f"ncov_{dim}"] == len(dimensions()[dim]["variables"]))].copy()
    p["_key"] = p[f"dim_{dim}"].round(2) * 1000 + p.overall / 1000
    sel = distinct_sites(p, "_key", n, MIN_SEP_KM)
    return _annotate([_record(target_id, i, k + 1) for k, i in enumerate(sel.index)])


def strong_share(target_id: str) -> dict:
    """各面向「分數 ≥ 0.9」的陸地面積比例（cos 緯度加權）：看出「只在某一面向像」的地方有多常見。"""
    df = profile_table(target_id)
    w = np.cos(np.radians(df.lat.values))
    out = {}
    for k in evaluable():
        d = df[f"dim_{k}"].values
        ok = np.isfinite(d)
        out[k] = _rnd(float((w * (ok & (d >= STRONG))).sum() / max((w * ok).sum(), 1e-9)), 4)
    o = df.overall.values
    ok = np.isfinite(o)
    out["overall_ge_90"] = _rnd(float((w * (ok & (o >= 90))).sum() / max((w * ok).sum(), 1e-9)), 4)
    return out


def known_profiles(target_id: str) -> list[dict]:
    """每個已知類比地：半徑內陸地格的面向分數中位數，以及在全球的排名百分位。"""
    df = profile_table(target_id)
    lat, lon = df.lat.values, df.lon.values
    w = np.cos(np.radians(lat))
    o_all = df.overall.values
    ok_all = np.isfinite(o_all)
    out = []
    for r in config.known_analogs().itertuples():
        d = haversine_km(r.lat, r.lon, lat, lon)
        idx = np.where(d <= float(r.radius_km))[0]
        if len(idx) == 0:
            j = int(np.argmin(d))
            if d[j] > 50:
                continue
            idx = np.array([j])
        sub = df.iloc[idx]
        dims = {k: None for k in dimensions()}
        for k in evaluable():
            dims[k] = _rnd(float(np.nanmedian(sub[f"dim_{k}"].values))) if np.isfinite(sub[f"dim_{k}"].values).any() else None
        ov = float(np.nanmedian(sub.overall.values)) if np.isfinite(sub.overall.values).any() else np.nan
        have = {k: v for k, v in dims.items() if v is not None}
        out.append({
            "site_id": r.site_id, "name": r.name, "lat": r.lat, "lon": r.lon,
            "tagged_for_this_target": target_id in r.targets, "missions": r.mission_list,
            "n_cells": int(len(idx)), "overall": _rnd(ov, 1),
            "global_top_pct": _rnd(float((w * (ok_all & (o_all > ov))).sum() / (w * ok_all).sum()) * 100, 1)
            if np.isfinite(ov) else None,
            "dimension_scores": dims,
            "strongest_dimension": max(have, key=have.get) if have else None,
            "weakest_dimension": min(have, key=have.get) if have else None,
        })
    return sorted(out, key=lambda x: -(x["overall"] or -1))


def build_target(target_id: str) -> dict:
    t = config.mars_targets()[target_id]
    return {
        "body": "mars", "version": "profile-v1", "method": "B",
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "target": {"id": target_id, "name": t.get("name"), "lat": t.get("lat"), "lon": t.get("lon"),
                   "radius_km": t.get("radius_km"),
                   "lithology_group": (t.get("lithology") or {}).get("group"),
                   "lithology_group_source": (t.get("lithology") or {}).get("group_source", "sim3292_map"),
                   "lithology_group_note": (t.get("lithology") or {}).get("group_note")},
        "dimensions": {k: {"label_zh": v.get("label_zh"), "label_en": v.get("label_en"),
                           "variables": v["variables"]} for k, v in dimensions().items()},
        "not_evaluated": not_evaluated(),
        "scoring": {"dimension": "equal-weight geometric mean of variables with data (floor 0.01)",
                    "overall": "equal-weight geometric mean of dimensions with data x 100",
                    "confidence": "dimensions with data / evaluable dimensions",
                    "ranking_filter": f"confidence >= {MIN_CONF} and variable coverage >= {MIN_CONF}; "
                                      "per-dimension top lists use only cells with all variables of that dimension",
                    "ice_target": "clip(SWIM Ci, 0, 1)", "min_separation_km": MIN_SEP_KM},
        "strong_share": strong_share(target_id),
        "top_overall": top_overall(target_id),
        "top_by_dimension": {k: top_dimension(target_id, k) for k in evaluable()},
        "known_analogs": known_profiles(target_id),
        "provenance": {"mars_targets": config.mars_targets_source(),
                       "labels": config.known_analogs().attrs.get("source")},
    }


# ---------------- 圖 ----------------
def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                         "savefig.facecolor": SURFACE})
    return plt


def dim_map(target_id: str, col: str, title: str, path, top: list[dict] | None = None, vmin=0.0, vmax=1.0):
    plt = _plt()
    from matplotlib.colors import LinearSegmentedColormap
    g, df = grid(), profile_table(target_id)
    arr = np.full((1800, 3600), np.nan, dtype="float32")
    arr[g.iy.values, g.ix.values] = df[col].values
    cmap = LinearSegmentedColormap.from_list("blue", BLUE_RAMP)
    cmap.set_bad("#efeeea")
    fig, ax = plt.subplots(figsize=(11, 5), dpi=130)
    im = ax.imshow(arr, extent=[-180, 180, -90, 90], cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
    ka = config.known_analogs()
    ax.scatter(ka.lon, ka.lat, s=12, marker="x", color=INK2, linewidth=0.8, label="known analog sites", zorder=2)
    if top:
        ax.scatter([r["lon"] for r in top], [r["lat"] for r in top], s=40, marker="o", facecolor="#eb6834",
                   edgecolor=SURFACE, linewidth=1.2, label=f"top {len(top)}", zorder=3)
        for r in top[:3]:
            ax.annotate(f"#{r['rank']}", (r["lon"], r["lat"]), xytext=(5, 5), textcoords="offset points",
                        fontsize=8, color=INK, fontweight="bold")
    ax.set_ylim(-60, 85)
    ax.set_xticks(range(-180, 181, 60)); ax.set_yticks(range(-60, 81, 30))
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(title, loc="left", fontsize=11)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.outline.set_visible(False)
    ax.legend(loc="lower left", fontsize=7, frameon=False, labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def radar_grid(entries: list[dict], title: str, path, name_key="name"):
    """只畫「可評估」的面向；沒有變數的面向（生物、洞穴）寫在標題，不畫成 0 分以免誤導。"""
    if not entries:
        return
    plt = _plt()
    order = evaluable()
    labels = [dimensions()[k].get("label_en", k) for k in order]
    ang = np.linspace(0, 2 * np.pi, len(order), endpoint=False)
    ncol = 3
    nrow = math.ceil(len(entries) / ncol)
    fig, axes = plt.subplots(nrow, ncol, subplot_kw={"projection": "polar"}, figsize=(ncol * 3.4, nrow * 3.9), dpi=140)
    axes = np.atleast_1d(axes).ravel()
    for ax, e in zip(axes, entries):
        vals = [e["dimension_scores"].get(k) for k in order]
        idx = [i for i, v in enumerate(vals) if v is not None]
        if idx:
            a = np.r_[ang[idx], ang[idx][0]]
            v = np.r_[[vals[i] for i in idx], vals[idx[0]]]
            ax.plot(a, v, color=ACCENT, lw=1.6)
            ax.fill(a, v, color=ACCENT, alpha=0.18)
            ax.scatter(ang[idx], [vals[i] for i in idx], s=10, color=ACCENT, zorder=3)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels([])
        ax.set_xticks(ang)
        ax.set_xticklabels([lab if vals[i] is not None else f"{lab}\n(no data)" for i, lab in enumerate(labels)],
                           fontsize=7)
        for i, tl in enumerate(ax.get_xticklabels()):
            if vals[i] is None:
                tl.set_color(MUTED)
        ax.tick_params(axis="x", pad=2)
        ax.grid(color=GRID, linewidth=0.6)
        ax.spines["polar"].set_color(GRID)
        nm = str(e.get(name_key) or f"{e['lat']}, {e['lon']}")
        nm = nm if len(nm) <= 34 else nm[:32] + "…"
        head = f"#{e['rank']} " if e.get("rank") else ""
        ov = e.get("overall")
        ax.set_title(f"{head}{nm}\noverall {ov:.0f}" if ov is not None else f"{head}{nm}", fontsize=8, pad=16)
    for ax in axes[len(entries):]:
        ax.axis("off")
    ne = [dimensions()[k].get("label_en", k) for k in not_evaluated()]
    sub = f"\n(not evaluated yet: {', '.join(ne)})" if ne else ""
    fig.suptitle(title + sub, fontsize=10, x=0.02, ha="left")
    fig.tight_layout(h_pad=3.0, w_pad=2.0)
    fig.savefig(path)
    plt.close(fig)


def figures(target_id: str, res: dict):
    name = res["target"]["name"]
    for k in evaluable():
        lab = dimensions()[k].get("label_en", k)
        dim_map(target_id, f"dim_{k}", f"{lab} analog to {name} (0–1)", OUT / f"map_{target_id}_{k}.png",
                res["top_by_dimension"][k])
    o = profile_table(target_id).overall.values
    lo, hi = np.nanpercentile(o, [50, 99.9])
    dim_map(target_id, "overall", f"Overall similarity to {name} (equal-weight dimensions, 0–100)",
            OUT / f"map_{target_id}_overall.png", res["top_overall"], vmin=lo, vmax=hi)
    radar_grid(res["top_overall"][:6], f"Analog profiles — top 6 overall for {name.split(' (')[0]}", OUT / f"radar_{target_id}_top.png")
    kn, tagged = known_for_display(res, 9)
    short = name.split(" (")[0]
    title = (f"Analog profiles — known analog sites tagged for {short}" if tagged else
             f"Analog profiles — best-ranked known analog sites for {short} (none tagged for this target)")
    radar_grid([dict(e, rank=None) for e in kn], title, OUT / f"radar_{target_id}_known.png")


def known_for_display(res: dict, n: int) -> tuple[list[dict], bool]:
    """標給這個目標的已知類比地；一個都沒有時（例如新目標），改列全部已知類比地中全球排名最前的 n 個。"""
    tagged = [e for e in res["known_analogs"] if e["tagged_for_this_target"]]
    if tagged:
        return tagged[:n], True
    ranked = sorted((e for e in res["known_analogs"] if e.get("global_top_pct") is not None),
                    key=lambda e: e["global_top_pct"])
    return ranked[:n], False


# ---------------- 人看的總表 ----------------
def _fmt(v, nd=2):
    return "—" if v is None else f"{v:.{nd}f}"


def summary_md(results: list[dict]) -> str:
    dims = dimensions()
    ev = evaluable()
    head = " | ".join(dims[k]["label_zh"] for k in ev)
    L = ["# 類比剖面總表（自動產生）", "",
         f"> 產生時間 {datetime.now(TZ):%Y-%m-%d %H:%M}。由 `scripts/make_profiles.py` 產生，數字以 `outputs/profiles/*.json` 為準。",
         "> 面向分數 = 面向內變數的等權重幾何平均；整體 = 面向的等權重幾何平均 × 100；不依任務加權。",
         f"> 尚未評估的面向：{'、'.join(dims[k]['label_zh'] for k in not_evaluated()) or '無'}（沒有變數）。",
         f"> 排名只用「面向」和「變數」都至少 {MIN_CONF:.0%} 有資料的格子；每個面向的前 5 名只用該面向變數全部有資料的格子；地點彼此至少相距 {MIN_SEP_KM} km。",
         "> 日溫差不計入任何面向（火星日溫差主要來自稀薄大氣，地球無法模擬），只在 breaks 裡當參考。",
         "> 冰的目標值 = clip(SWIM Ci, 0, 1)：Ci ≤ 0 視為沒有冰。", ""]
    for res in results:
        t = res["target"]
        L += [f"## {t['name']}（{t['lat']}, {t['lon']}）", ""]
        if t.get("lithology_group_source") == "literature_override":
            L += [f"> 岩性類別用文獻覆寫為 `{t['lithology_group']}`（全球地質圖 1:20M 分不出這裡的礦物）：{t.get('lithology_group_note') or ''}", ""]
        ss = res["strong_share"]
        L += ["**各面向「分數 ≥ 0.9」的陸地比例**：" + "、".join(
            f"{dims[k]['label_zh']} {ss[k] * 100:.1f}%" for k in ev) + f"；整體 ≥ 90 分：{ss['overall_ge_90'] * 100:.2f}%", ""]
        L += ["### 整體相似度前 10 名", "",
              f"| # | 地點 | 座標 | 整體 | {head} | 最弱面向 | 已知類比地 |",
              "|---|---|---|---|" + "---|" * len(ev) + "---|---|"]
        for r in res["top_overall"][:10]:
            ds = " | ".join(_fmt(r["dimension_scores"][k]) for k in ev)
            wk = dims[r["weakest_dimension"]]["label_zh"] if r["weakest_dimension"] else "—"
            L.append(f"| {r['rank']} | {r['name'] or '—'} | {r['lat']}, {r['lon']} | {r['overall']:.1f} | {ds} | {wk} | "
                     f"{'是' if r['known_analog'] else '否（新候選）'} |")
        L += ["", "### 每個面向最像的前 5 名", ""]
        for k in ev:
            items = res["top_by_dimension"][k]
            L.append(f"- **{dims[k]['label_zh']}**：" + "；".join(
                f"{r['name'] or (str(r['lat']) + ', ' + str(r['lon']))}（{_fmt(r['dimension_scores'][k])}，整體 {r['overall']:.0f}）"
                for r in items))
        rows, tagged = known_for_display(res, len(res["known_analogs"]) if any(
            e["tagged_for_this_target"] for e in res["known_analogs"]) else 8)
        L += ["", "### 已知類比地的剖面（標給這個目標的）" if tagged else
              "### 已知類比地的剖面（沒有標給這個目標的；列出全部已知類比地中全球排名最前的 8 個，供參考）", "",
              f"| 類比地 | 整體 | 全球前 % | {head} | 最強 | 最弱 |",
              "|---|---|---|" + "---|" * len(ev) + "---|---|"]
        for r in rows:
            ds = " | ".join(_fmt(r["dimension_scores"][k]) for k in ev)
            st = dims[r["strongest_dimension"]]["label_zh"] if r["strongest_dimension"] else "—"
            wk = dims[r["weakest_dimension"]]["label_zh"] if r["weakest_dimension"] else "—"
            L.append(f"| {r['name']} | {_fmt(r['overall'], 1)} | {_fmt(r['global_top_pct'], 1)} | {ds} | {st} | {wk} |")
        L.append("")
    return "\n".join(L)


def run(targets: list[str] | None = None, make_figures: bool = True) -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for tid in targets or list(config.mars_targets()):
        print(f"類比剖面：{tid} …", flush=True)
        res = build_target(tid)
        (OUT / f"mars_{tid}_profile.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        if make_figures:
            figures(tid, res)
        results.append(res)
    (OUT / "PROFILE_SUMMARY.md").write_text(summary_md(results), encoding="utf-8")
    print("寫出", OUT, flush=True)
    return results
