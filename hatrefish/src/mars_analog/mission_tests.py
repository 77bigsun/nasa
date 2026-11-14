"""
火星測試項目 R1–R6 的分數與排名（定義在 config/mission_tests.yaml，來自整合者 Harris 的規劃）。

- 每個火星目標 × 每項測試，算全球每個 0.1° 陸地格的測試分數（0–1）：
  測試內特徵的加權幾何平均（下限 0.01）。required 特徵缺資料 → 該格不評分；optional 有資料才納入。
- 特徵分數三類：類比剖面的單項相似度（和火星目標值比）、門檻型滿意度函數（梯形）、季節曲線與礦物指標。
  需要的地球補充資料（earth_monthly.parquet、earth_extra.parquet）還沒產生時，那些特徵列為「待補資料」。
- R3、R5 只對有冰的目標（clip(SWIM Ci, 0, 1) > 0）適用；R2 全球沒有資料，列為無法評估。
- 另外輸出：面向 × 測試交叉表、用面向分數組成的測試分數（交叉驗證）、參考用加權總分（ROC 權重）、
  已知類比地檢查、需求矩陣（給整合者）、候選池（給下一步的集合覆蓋）。

輸出在 outputs/mission_tests/。
"""
from __future__ import annotations

import json
import math
from datetime import datetime
from functools import lru_cache

import numpy as np
import pandas as pd
import yaml

from . import config, profiles
from .novelty import distinct_sites, flag_known, haversine_km, place_name
from .paths import CONFIG, OUTPUTS, PROCESSED
from .similarity import ice_target, similarity_vector

OUT = OUTPUTS / "mission_tests"
TZ = profiles.TZ
_rnd = profiles._rnd
# 地球每月月中的太陽黃經（近似，0° = 三月春分），用來和火星 Ls 依「當地季節」對齊
EARTH_MONTH_LAMBDA = ((np.array([15.5, 45, 74.5, 105, 135.5, 166, 196.5, 227.5, 258, 288.5, 319, 349.5]) - 79.3)
                      / 365.2422 * 360) % 360
ASTER_COLUMNS = {"carbonate": "aster_ci", "mafic": "aster_mi", "quartz": "aster_qi"}


# ---------------- 設定與資料 ----------------
@lru_cache
def spec() -> dict:
    return yaml.safe_load((CONFIG / "mission_tests.yaml").read_text(encoding="utf-8"))


def tests() -> dict:
    return spec()["tests"]


@lru_cache
def grid() -> pd.DataFrame:
    return profiles.grid()


@lru_cache
def extra() -> pd.DataFrame:
    """地球補充資料（月平均、冰河距離、礦物指標），依 cell_id 對齊全球網格；檔案不存在就是空表。"""
    g = grid()
    out = pd.DataFrame(index=g.index)
    for name in ("earth_monthly.parquet", "earth_extra.parquet"):
        p = PROCESSED / name
        if not p.exists():
            continue
        e = pd.read_parquet(p).drop_duplicates("cell_id").set_index("cell_id")
        cols = [c for c in e.columns if c not in ("lat", "lon", "iy", "ix")]
        j = e.reindex(g.cell_id.astype(str).values)[cols]
        j.index = g.index
        out = out.join(j)
    return out


@lru_cache(maxsize=4)
def _derived(name: str) -> np.ndarray | None:
    """衍生欄位。icy_frac = 冰雪覆蓋比例：MCD12Q1 冰雪、GLIMS 冰河比例（有補資料時）、
    以及「年均 NDVI < 0 且年均地表溫 < 0 °C」（土地覆蓋圖漏標的冰河、常年積雪）三者取最大。"""
    if name != "icy_frac":
        return None
    g = grid()
    icy = g.ice_frac.fillna(0).values.astype("float64")
    snow = (g.ndvi_mean.values < 0) & (g.lst_mean_c.values < 0)
    icy = np.maximum(icy, snow.astype("float64"))
    e = extra()
    if "glacier_frac" in e.columns:
        icy = np.maximum(icy, e.glacier_frac.fillna(0).values)
    return icy


def _col(name: str) -> np.ndarray | None:
    d = _derived(name)
    if d is not None:
        return d
    g = grid()
    if name in g.columns:
        return g[name].values.astype("float64")
    e = extra()
    if name in e.columns:
        return e[name].values.astype("float64")
    return None


def _monthly(prefix: str) -> np.ndarray | None:
    cols = [f"{prefix}{m:02d}" for m in range(1, 13)]
    e = extra()
    if not all(c in e.columns for c in cols):
        return None
    return e[cols].values.astype("float64")


@lru_cache
def mars_ti_quantiles() -> np.ndarray:
    d = json.loads((PROCESSED / "mars_reference_pct.json").read_text(encoding="utf-8"))
    return np.asarray(d["thermal_inertia"]["quantiles"], dtype="float64")


def mars_pct(value: float) -> float:
    q = np.maximum.accumulate(mars_ti_quantiles()) + np.arange(101) * 1e-9
    return float(np.interp(value, q, np.linspace(0, 1, 101)))


def target_attrs(target_id: str) -> dict:
    return (spec().get("target_attributes") or {}).get(target_id, {}) or {}


# ---------------- 特徵分數 ----------------
def desirability(x, rule: str, full_at: float, zero_at: float) -> np.ndarray:
    """門檻型滿意度函數（Derringer & Suich 1980 的梯形，線性）。NaN 進 → NaN 出。"""
    x = np.asarray(x, dtype="float64")
    if rule == "smaller_is_better":
        d = (zero_at - x) / (zero_at - full_at)
    elif rule == "larger_is_better":
        d = (x - zero_at) / (full_at - zero_at)
    else:
        raise ValueError(rule)
    return np.where(np.isfinite(x), np.clip(d, 0.0, 1.0), np.nan)


def _rowcorr(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    A = A - A.mean(1, keepdims=True)
    B = B - B.mean(1, keepdims=True)
    den = np.sqrt((A * A).sum(1) * (B * B).sum(1))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (A * B).sum(1) / den
    r[~np.isfinite(r)] = np.nan
    return r


def _mars_curve(target: dict, key: str, ls_angles: np.ndarray) -> np.ndarray:
    s = target["seasonal"]
    ls, v = np.asarray(s["ls"], float), np.asarray(s[key], float)
    return np.interp(np.mod(ls_angles, 360), np.r_[ls, 360.0], np.r_[v, v[0]])


def _mars_aligned(target: dict, key: str, lat: np.ndarray) -> np.ndarray:
    """火星曲線取在「和地球每個月同一個當地季節」的 Ls 上：北半球地點 = 太陽黃經，南半球 + 180°；
    火星目標在南半球時再減 180°。回傳 (N, 12)。"""
    off = 0.0 if float(target["lat"]) >= 0 else 180.0
    m_nh = _mars_curve(target, key, EARTH_MONTH_LAMBDA - off)
    m_sh = _mars_curve(target, key, EARTH_MONTH_LAMBDA + 180.0 - off)
    return np.where((lat >= 0)[:, None], m_nh[None, :], m_sh[None, :]).astype("float32")


def _amplitude(a: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        return (np.nanmax(a, -1) - np.nanmin(a, -1)) / np.nanmean(a, -1)


@lru_cache(maxsize=8)
def _global_pct(col: str) -> np.ndarray:
    v = _col(col)
    out = np.full(v.shape, np.nan)
    ok = np.isfinite(v)
    r = pd.Series(v[ok]).rank(pct=True).values
    out[ok] = r
    return out


def feature_status(target_id: str, f: dict) -> str:
    """scored / pending_data / not_applicable_for_target"""
    if f.get("attribute") and not target_attrs(target_id).get(f["attribute"]):
        return "not_applicable_for_target"
    k = f["kind"]
    if k in ("seasonal_shape", "seasonal_amplitude"):
        if _monthly(f["earth_prefix"]) is None:
            return "pending_data"
        if "seasonal" not in config.mars_targets()[target_id]:
            return "pending_data"
    if k == "threshold" and _col(f["column"]) is None:
        return "pending_data"
    if k == "index_rank":
        cols = [ASTER_COLUMNS[x] for x in target_attrs(target_id).get(f["attribute"], [])]
        if not cols or any(_col(c) is None for c in cols):
            return "pending_data"
    return "scored"


def feature_score(target_id: str, f: dict, sim: pd.DataFrame) -> np.ndarray:
    s = _feature_score(target_id, f, sim)
    fill = f.get("fill")
    if fill:
        s = s.copy()
        m = (grid().lat.values < float(fill["south_of"])) & ~np.isfinite(s)
        s[m] = float(fill["value"])
    return s


def _feature_score(target_id: str, f: dict, sim: pd.DataFrame) -> np.ndarray:
    target = config.mars_targets()[target_id]
    k = f["kind"]
    if k == "similarity":
        return sim[f"s_{f['var']}"].values.astype("float64")
    if k == "threshold":
        return desirability(_col(f["column"]), f["rule"], f["full_at"], f["zero_at"])
    if k == "mars_rank_threshold":
        return desirability(_col(f["column"]), "larger_is_better", mars_pct(f["mars_full_at"]),
                            mars_pct(f["mars_zero_at"]))
    if k == "seasonal_shape":
        E = _monthly(f["earth_prefix"])
        M = _mars_aligned(target, f["mars_key"], grid().lat.values)
        r = _rowcorr(E, M)
        r[~np.isfinite(E).all(1)] = np.nan
        return (1 + r) / 2
    if k == "seasonal_amplitude":
        E = _monthly(f["earth_prefix"])
        ae = _amplitude(E)
        am = float(_amplitude(np.asarray(target["seasonal"][f["mars_key"]], float)))
        with np.errstate(invalid="ignore", divide="ignore"):
            s = np.exp(-(np.log(ae / am)) ** 2 / (2 * math.log(2) ** 2))
        s[~(np.isfinite(E).all(1) & (ae > 0))] = np.nan
        return s
    if k == "index_rank":
        parts = [desirability(_global_pct(ASTER_COLUMNS[x]), "larger_is_better", f["full_at"], f["zero_at"])
                 for x in target_attrs(target_id)[f["attribute"]]]
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.exp(np.mean([np.log(np.maximum(p, spec()["eps"])) for p in parts], 0))
    raise ValueError(k)


# ---------------- 測試分數 ----------------
def applicable(target_id: str, test: dict) -> tuple[bool, str | None]:
    if test.get("status") == "not_evaluated":
        return False, "not_evaluated"
    if test.get("applies", "all") == "ice":
        ci = ice_target(config.mars_targets()[target_id])
        if not (ci is not None and ci >= float(spec().get("ice_min_ci", 0.0)) and ci > 0):
            return False, "not_applicable"
    return True, None


def weighted_gmean(feats: list[np.ndarray], weights: list[float], required: list[bool], eps: float) -> np.ndarray:
    n = len(feats[0])
    num, den = np.zeros(n), np.zeros(n)
    ok = np.ones(n, dtype=bool)
    for s, w, req in zip(feats, weights, required):
        fin = np.isfinite(s)
        if req:
            ok &= fin
        num += np.where(fin, w * np.log(np.maximum(np.where(fin, s, 1.0), eps)), 0.0)
        den += np.where(fin, w, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.exp(num / den)
    out[~ok | (den == 0)] = np.nan
    return out


def score_target(target_id: str) -> tuple[pd.DataFrame, dict]:
    """回傳 (每格的測試分數與特徵分數, 每項測試的狀態)。"""
    g = grid()
    target = config.mars_targets()[target_id]
    sim = similarity_vector(target, g, profiles.ref(), "B")
    eps = spec()["eps"]
    cols, status = {}, {}
    for tid, t in tests().items():
        ok, why = applicable(target_id, t)
        st = {"status": why or "scored", "features": {}}
        if ok:
            arrs, ws, reqs = [], [], []
            for f in t["features"]:
                fs = feature_status(target_id, f)
                st["features"][f["id"]] = fs
                if fs != "scored":
                    continue
                s = feature_score(target_id, f, sim)
                cols[f"f_{tid}_{f['id']}"] = s.astype("float32")
                arrs.append(s); ws.append(float(f.get("weight", 1.0))); reqs.append(bool(f.get("required", True)))
            if arrs:
                cols[f"T_{tid}"] = weighted_gmean(arrs, ws, reqs, eps).astype("float32")
            else:
                st["status"] = "not_evaluated"
        status[tid] = st
    df = pd.DataFrame(cols, index=g.index)
    df.insert(0, "lon", g.lon.values)
    df.insert(0, "lat", g.lat.values)
    return df, status


def dim_scores(target_id: str) -> pd.DataFrame:
    """類比剖面的面向分數與整體相似度（交叉驗證和參考用）。"""
    pt = profiles.profile_table(target_id)
    keep = [c for c in pt.columns if c.startswith("dim_")] + ["overall"]
    out = pt[keep].copy()
    profiles._CACHE.pop(target_id, None)      # 省記憶體
    return out


def dim_based(dims: pd.DataFrame, test: dict) -> np.ndarray | None:
    """用面向分數組成測試分數：主要面向（main）的等權重幾何平均；有任一主要面向沒分數 → NaN。"""
    main = [k for k, v in (test.get("dimensions") or {}).items() if v == "main" and f"dim_{k}" in dims.columns]
    if not main:
        return None
    A = np.vstack([dims[f"dim_{k}"].values for k in main])
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.exp(np.mean(np.log(np.maximum(A, spec()["eps"])), 0))
    out[~np.isfinite(A).all(0)] = np.nan
    return out


# ---------------- 排名與紀錄 ----------------
def _top(df: pd.DataFrame, col: str, n: int, sep: float, tiebreak: pd.Series | None = None) -> pd.DataFrame:
    p = df[np.isfinite(df[col])].copy()
    if not len(p):
        return p
    p["_key"] = p[col].round(3) * 1000 + (tiebreak.reindex(p.index).fillna(0) / 1000 if tiebreak is not None else 0)
    return distinct_sites(p, "_key", n, sep)


def _feature_values(target_id: str, f: dict, i, df: pd.DataFrame) -> dict:
    target = config.mars_targets()[target_id]
    g = grid()
    k = f["kind"]
    earth, mars = None, f.get("mars_requirement")
    if k == "similarity":
        col, key, _ = profiles.VALUE_KEYS[f["var"]]
        earth = g.at[i, col] if col in g.columns else None
        mars = ice_target(target) if f["var"] == "ice" else (target.get(f["var"]) or {}).get(key)
    elif k == "threshold":
        earth = _col(f["column"])[g.index.get_loc(i)]
        word = "≤" if f["rule"] == "smaller_is_better" else "≥"
        mars = f"{word}{f['full_at']} 滿分，{'≥' if word == '≤' else '≤'}{f['zero_at']} 為 0"
    elif k == "mars_rank_threshold":
        earth = g.at[i, f["column"]]
        mars = (f"火星熱慣量 {f['mars_zero_at']}→{f['mars_full_at']} = 火星第 "
                f"{mars_pct(f['mars_zero_at']) * 100:.0f}→{mars_pct(f['mars_full_at']) * 100:.0f} 百分位")
    elif k in ("seasonal_shape", "seasonal_amplitude"):
        E = _monthly(f["earth_prefix"])[g.index.get_loc(i)]
        mv = np.asarray(target["seasonal"][f["mars_key"]], float)
        if k == "seasonal_shape":
            earth = f"地球高峰在 {int(np.nanargmax(E)) + 1} 月"
            mars = f"火星高峰在 Ls {int(np.asarray(target['seasonal']['ls'])[int(np.argmax(mv))])}°"
        else:
            earth, mars = float(_amplitude(E)), float(_amplitude(mv))
    elif k == "index_rank":
        earth = {x: _rnd(_global_pct(ASTER_COLUMNS[x])[g.index.get_loc(i)]) for x in
                 target_attrs(target_id).get(f["attribute"], [])}
        mars = target_attrs(target_id).get(f["attribute"])
    if isinstance(earth, (float, np.floating)):
        earth = _rnd(float(earth))
    if isinstance(mars, (float, np.floating)):
        mars = _rnd(float(mars))
    return {"earth": earth, "mars": mars, "unit": f.get("unit")}


def _record(target_id: str, tid: str, i, rank: int, df: pd.DataFrame, dims: pd.DataFrame, status: dict) -> dict:
    t = tests()[tid]
    feats, values, missing, breaks = {}, {}, [], []
    for f in t["features"]:
        if status[tid]["features"].get(f["id"]) != "scored":
            continue
        s = df.at[i, f"f_{tid}_{f['id']}"]
        s = float(s) if np.isfinite(s) else None
        feats[f["id"]] = _rnd(s)
        if s is None:
            missing.append(f["id"])
            continue
        values[f["id"]] = _feature_values(target_id, f, i, df)
        if s < spec()["break_threshold"]:
            breaks.append({"feature": f["id"], "score": _rnd(s), **values[f["id"]]})
    have = {k: v for k, v in feats.items() if v is not None}
    return {
        "rank": rank, "cell_id": str(grid().at[i, "cell_id"]), "lat": _rnd(df.at[i, "lat"], 2), "lon": _rnd(df.at[i, "lon"], 2),
        "score": _rnd(float(df.at[i, f"T_{tid}"])), "features": feats, "optional_missing": missing,
        "weakest_feature": min(have, key=have.get) if have else None,
        "values": values, "breaks": breaks,
        "dimension_scores": {c[4:]: _rnd(float(dims.at[i, c])) for c in dims.columns if c.startswith("dim_")},
        "profile_overall": _rnd(float(dims.at[i, "overall"]), 1),
        "worldview_url": profiles.worldview_url(float(df.at[i, "lat"]), float(df.at[i, "lon"])),
    }


def _area_share(v: np.ndarray, lat: np.ndarray, thr: float) -> float | None:
    ok = np.isfinite(v)
    if not ok.any():
        return None
    w = np.cos(np.radians(lat))
    return _rnd(float((w * (ok & (v >= thr))).sum() / (w * ok).sum()), 4)


def known_check(df: pd.DataFrame, evaluated: list[str]) -> list[dict]:
    lat, lon = df.lat.values, df.lon.values
    w = np.cos(np.radians(lat))
    out = []
    for r in config.known_analogs().itertuples():
        d = haversine_km(r.lat, r.lon, lat, lon)
        idx = np.where(d <= float(r.radius_km))[0]
        if len(idx) == 0:
            j = int(np.argmin(d))
            if d[j] > 50:
                continue
            idx = np.array([j])
        rec = {"site_id": r.site_id, "name": r.name, "missions": r.mission_list, "tests": {}}
        for tid in evaluated:
            v = df[f"T_{tid}"].values
            sv = v[idx]
            if not np.isfinite(sv).any():
                rec["tests"][tid] = None
                continue
            med = float(np.nanmedian(sv))
            ok = np.isfinite(v)
            top = float((w * (ok & (v > med))).sum() / (w * ok).sum()) * 100
            rec["tests"][tid] = {"score": _rnd(med), "global_top_pct": _rnd(top, 1)}
        out.append(rec)
    return out


def mission_check(known: list[dict], evaluated: list[str]) -> dict:
    """標了某任務的已知類比地，在對應測試的全球前百分比中位數 vs 沒標的。"""
    out = {}
    for tid in evaluated:
        missions = [m for m, ts in spec()["mission_to_tests"].items() if tid in ts]
        tag, other = [], []
        for k in known:
            v = k["tests"].get(tid)
            if not v or v["global_top_pct"] is None:
                continue
            (tag if set(missions) & set(k["missions"]) else other).append(v["global_top_pct"])
        out[tid] = {"missions": missions, "n_tagged": len(tag), "n_other": len(other),
                    "median_top_pct_tagged": _rnd(float(np.median(tag)), 1) if tag else None,
                    "median_top_pct_other": _rnd(float(np.median(other)), 1) if other else None}
    return out


def build(target_id: str) -> tuple[dict, pd.DataFrame]:
    sp = spec()
    df, status = score_target(target_id)
    dims = dim_scores(target_id)
    evaluated = [k for k, v in status.items() if v["status"] == "scored"]
    tie = dims["overall"]
    res = {
        "target": {k: config.mars_targets()[target_id].get(k) for k in ("name", "lat", "lon", "radius_km", "missions")},
        "target_id": target_id, "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "ice_target": _rnd(ice_target(config.mars_targets()[target_id])),
        "status": status, "tests": {}, "cross_check": {},
    }
    lat = df.lat.values
    for tid in evaluated:
        sel = _top(df, f"T_{tid}", sp["top_n"], sp["min_sep_km"], tie)
        recs = profiles._annotate([_record(target_id, tid, i, k + 1, df, dims, status) for k, i in enumerate(sel.index)])
        v = df[f"T_{tid}"].values
        res["tests"][tid] = {
            "n_cells": int(np.isfinite(v).sum()),
            "share_ge": {str(t): _area_share(v, lat, t) for t in sp["strong"]},
            "optional_missing_in_top": {f["id"]: sum(1 for r in recs if f["id"] in r["optional_missing"])
                                        for f in tests()[tid]["features"] if not f.get("required", True)},
            "top": recs,
        }
        # 交叉驗證：用面向分數組成的測試分數
        db = dim_based(dims, tests()[tid])
        if db is not None:
            tmp = pd.DataFrame({"lat": df.lat, "lon": df.lon, "db": db}, index=df.index)
            sel2 = _top(tmp, "db", sp["cross_check"]["top"], sp["min_sep_km"], tie)
            a = sel.head(sp["cross_check"]["top"])
            hit = 0
            for la, lo in zip(a.lat.values, a.lon.values):
                if len(sel2) and (haversine_km(la, lo, sel2.lat.values, sel2.lon.values) <= sp["cross_check"]["match_km"]).any():
                    hit += 1
            ok = np.isfinite(v) & np.isfinite(db)
            rho = float(pd.Series(v[ok]).corr(pd.Series(db[ok]), method="spearman")) if ok.sum() > 100 else None
            res["cross_check"][tid] = {"dimensions": [k for k, x in tests()[tid]["dimensions"].items() if x == "main"],
                                       "top_overlap": _rnd(hit / max(len(a), 1), 2), "spearman_all_cells": _rnd(rho),
                                       "top_dim_based": [{"lat": _rnd(r.lat, 2), "lon": _rnd(r.lon, 2), "score": _rnd(r.db)}
                                                         for r in sel2.head(5).itertuples()]}
    # 參考用加權總分（ROC 權重；只用適用且已評分的測試，重新正規化；任一缺 → 不評分）
    w = {k: v for k, v in sp["test_weights"]["roc"].items() if k in evaluated}
    if w:
        tot = sum(w.values())
        A = np.vstack([df[f"T_{k}"].values for k in w])
        ww = np.array([w[k] / tot for k in w])[:, None]
        with np.errstate(invalid="ignore", divide="ignore"):
            wt = np.exp((ww * np.log(np.maximum(A, sp["eps"]))).sum(0))
        wt[~np.isfinite(A).all(0)] = np.nan
        df["W_roc"] = wt.astype("float32")
        sel = _top(df, "W_roc", 10, sp["min_sep_km"], tie)
        recs = []
        for k, i in enumerate(sel.index):
            recs.append({"rank": k + 1, "lat": _rnd(df.at[i, "lat"], 2), "lon": _rnd(df.at[i, "lon"], 2),
                         "score": _rnd(float(df.at[i, "W_roc"])),
                         "tests": {t: _rnd(float(df.at[i, f"T_{t}"])) for t in w}})
        res["weighted_reference"] = {"weights_used": {k: _rnd(v / tot) for k, v in w.items()},
                                     "top": profiles._annotate(recs)}
    known = known_check(df, evaluated)
    res["known_analogs"] = known
    res["mission_check"] = mission_check(known, evaluated)
    return res, df


# ---------------- 交叉表、需求矩陣、候選池 ----------------
def crosswalk() -> pd.DataFrame:
    dims = profiles.dimensions()
    rows = []
    for tid, t in tests().items():
        r = {"test": tid, "name": t["name_zh"]}
        for k in dims:
            v = (t.get("dimensions") or {}).get(k)
            r[k] = {"main": "●", "related": "○"}.get(v, "")
        rows.append(r)
    return pd.DataFrame(rows)


def requirement_matrix(all_status: dict) -> pd.DataFrame:
    rows = []
    for target_id, status in all_status.items():
        tname = config.mars_targets()[target_id].get("name", target_id)
        for tid, t in tests().items():
            st = status[tid]
            if not t["features"]:
                rows.append({"目標地點": tname, "測試代號": tid, "特徵": "—", "目標值或門檻": "—", "特徵類型": "—",
                             "行星端資料": "—", "地球端資料": "—", "特徵權重": "—", "狀態": st["status"],
                             "備註": t.get("reason", "")})
                continue
            active = [f for f in t["features"] if st["features"].get(f["id"]) == "scored"]
            wsum = sum(float(f.get("weight", 1.0)) for f in active) or 1.0
            for f in t["features"]:
                fs = st["features"].get(f["id"], st["status"])
                if st["status"] != "scored":
                    fs = st["status"]
                kind = {"similarity": "剖面（和目標比）", "threshold": "門檻", "mars_rank_threshold": "門檻（相對排名）",
                        "seasonal_shape": "時間序列（形狀）", "seasonal_amplitude": "時間序列（振幅）",
                        "index_rank": "類別（礦物指標）"}[f["kind"]]
                rows.append({"目標地點": tname, "測試代號": tid, "特徵": f["id"],
                             "目標值或門檻": f.get("mars_requirement", ""), "特徵類型": kind,
                             "行星端資料": f.get("mars_data", ""), "地球端資料": f.get("earth_data", ""),
                             "特徵權重": round(float(f.get("weight", 1.0)) / wsum, 3) if fs == "scored" else "—",
                             "狀態": fs + ("" if f.get("required", True) else "（optional）"), "備註": f.get("note", "")})
            for x in t.get("not_evaluated", []) or []:
                rows.append({"目標地點": tname, "測試代號": tid, "特徵": "—", "目標值或門檻": x, "特徵類型": "—",
                             "行星端資料": "—", "地球端資料": "—", "特徵權重": "—", "狀態": "not_evaluated", "備註": ""})
    return pd.DataFrame(rows)


def candidate_pool(frames: dict) -> pd.DataFrame:
    sp = spec()
    keep = set()
    for target_id, df in frames.items():
        for c in [c for c in df.columns if c.startswith("T_")]:
            sel = _top(df, c, sp["pool"]["top"], sp["pool"]["min_sep_km"])
            keep.update(sel.index.tolist())
    idx = sorted(keep)
    g = grid().loc[idx]
    out = pd.DataFrame({"cell_id": g.cell_id.astype(str).values, "lat": g.lat.values.round(2),
                        "lon": g.lon.values.round(2)}, index=idx)
    for target_id, df in frames.items():
        for c in [c for c in df.columns if c.startswith("T_")]:
            out[f"S_{target_id}_{c[2:]}"] = df.loc[idx, c].values.round(4)
    t = flag_known(out[["lat", "lon"]].copy())
    out["known_analog"] = t.known_analog.values
    out["nearest_known"] = t.nearest_known.values
    out["nearest_known_km"] = t.nearest_known_km.values
    out["place"] = place_name(out.lat.values, out.lon.values)
    return out.reset_index(drop=True)


# ---------------- 圖 ----------------
def figure(target_id: str, res: dict, df: pd.DataFrame, path):
    plt = profiles._plt()
    from matplotlib.colors import LinearSegmentedColormap
    P = profiles
    g = grid()
    panels = [(f"T_{t}", f"{t} {tests()[t]['name_en']}", res["tests"][t]["top"][:5]) for t in res["tests"]]
    if "W_roc" in df.columns:
        panels.append(("W_roc", "Weighted total (ROC weights, reference)", res["weighted_reference"]["top"][:5]))
    n = len(panels)
    if n == 0:
        return
    ncol = 3 if n > 2 else n
    nrow = math.ceil(n / ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(5.2 * ncol + 0.6, 2.75 * nrow + 0.5), dpi=130, squeeze=False)
    fig.subplots_adjust(left=0.01, right=0.93, bottom=0.02, top=0.90, wspace=0.04, hspace=0.16)
    cmap = LinearSegmentedColormap.from_list("blue", P.BLUE_RAMP)
    cmap.set_bad("#efeeea")
    ka = config.known_analogs()
    im = None
    for ax, (col, title, top) in zip(axes.ravel(), panels):
        arr = np.full((1800, 3600), np.nan, dtype="float32")
        arr[g.iy.values, g.ix.values] = df[col].values
        im = ax.imshow(arr, extent=[-180, 180, -90, 90], cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
        ax.scatter(ka.lon, ka.lat, s=6, marker="x", color=P.INK2, linewidth=0.6, zorder=2)
        if top:
            ax.scatter([r["lon"] for r in top], [r["lat"] for r in top], s=22, marker="o", facecolor="#eb6834",
                       edgecolor=P.SURFACE, linewidth=1.0, zorder=3)
        ax.set_xlim(-180, 180); ax.set_ylim(-90, 85)
        ax.set_xticks([]); ax.set_yticks([])
        for sp_ in ax.spines.values():
            sp_.set_visible(False)
        ax.set_title(title, loc="left", fontsize=9)
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    name = config.mars_targets()[target_id].get("name", target_id).split(" (")[0]
    fig.suptitle(f"Mission test scores — {name}  (orange = top 5 per test, x = known analog sites, "
                 "gray = not scored)", x=0.01, y=0.985, ha="left", fontsize=11)
    cax = fig.add_axes([0.945, 0.12, 0.012, 0.7])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("test score (0–1)", fontsize=8, color=P.INK2)
    cb.outline.set_visible(False)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


# ---------------- 總表 ----------------
STATUS_ZH = {"scored": "已評分", "not_applicable": "不適用（目標沒有可靠的冰訊號）", "not_evaluated": "無法評估",
             "pending_data": "待補資料", "not_applicable_for_target": "不適用此目標"}


def summary_md(results: list[dict], cw: pd.DataFrame) -> str:
    sp = spec()
    dims = profiles.dimensions()
    L = ["# 測試項目分數（自動產生）", "",
         f"> 產生時間 {datetime.now(TZ):%Y-%m-%d %H:%M}，由 `scripts/make_mission_tests.py` 產生；數字以 `outputs/mission_tests/*_tests.json` 為準。",
         "> 測試 R1–R6 的定義來自整合者的規劃（`nasa/docs/火星.pdf`），特徵、門檻、資料寫在 `config/mission_tests.yaml`。",
         "> 測試分數 = 測試內特徵的等權重幾何平均（下限 0.01）。必要特徵缺資料的格子不評分；可選特徵有資料才納入。"
         f"前 {sp['top_n']} 名彼此至少相距 {sp['min_sep_km']} km；已知類比地 = {sp['known_radius_km']} km 內。", "",
         "## 面向 × 測試交叉表", "", "● = 主要組成，○ = 相關但目前沒資料。", ""]
    head = ["測試"] + [dims[k].get("label_zh", k) for k in dims]
    L += ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in cw.itertuples(index=False):
        L.append(f"| {r.test} {r.name} | " + " | ".join(getattr(r, k) for k in dims) + " |")
    L += ["", "生物面向沒有對應到任何測試；R2 沒有任何面向能算。", ""]
    pend = sorted({f"{tid} {fid}" for r in results for tid, st in r["status"].items()
                   for fid, fs in st["features"].items() if fs == "pending_data"})
    if pend:
        L += [f"> 待補資料（跑 `scripts/fetch_earth_extra_gee.py` 後重跑本程式就會納入）：{'、'.join(pend)}", ""]
    for r in results:
        t = r["target"]
        L += [f"## {t['name']}（{t['lat']}, {t['lon']}）", ""]
        L.append("測試狀態：" + "；".join(f"{tid} {STATUS_ZH.get(st['status'], st['status'])}" for tid, st in r["status"].items())
                 + f"。冰訊號 clip(Ci, 0, 1) = {r['ice_target']}（R3、R5 需要 ≥ {spec().get('ice_min_ci')}）。")
        L.append("")
        for tid, tr in r["tests"].items():
            tt = tests()[tid]
            sh = tr["share_ge"]
            miss = {k: v for k, v in tr["optional_missing_in_top"].items() if v}
            L += [f"### {tid} {tt['name_zh']}", "",
                  f"可評分陸地格 {tr['n_cells']:,}；分數 ≥ 0.8 的陸地面積 {sh['0.8'] * 100:.1f}%、≥ 0.9 的 {sh['0.9'] * 100:.1f}%"
                  + (f"；前 {sp['top_n']} 名中可選特徵缺資料：" + "、".join(f"{k} {v} 筆" for k, v in miss.items()) if miss else "")
                  + "。", ""]
            feats = [f["id"] for f in tt["features"] if r["status"][tid]["features"].get(f["id"]) == "scored"]
            L += ["| # | 地點 | 座標 | 分數 | " + " | ".join(feats) + " | 最弱 | 已知類比地 |",
                  "|---|---|---|---|" + "---|" * len(feats) + "---|---|"]
            for x in tr["top"][:10]:
                kn = "是" if x.get("known_analog") else (f"否（{x.get('nearest_known')} {x.get('nearest_known_km'):.0f} km）"
                                                        if x.get("nearest_known_km") is not None else "否")
                L.append(f"| {x['rank']} | {x.get('name') or ''} | {x['lat']}, {x['lon']} | {x['score']} | "
                         + " | ".join("—" if x["features"].get(f) is None else f"{x['features'][f]:.2f}" for f in feats)
                         + f" | {x.get('weakest_feature') or '—'} | {kn} |")
            cc = r["cross_check"].get(tid)
            if cc:
                L += ["", f"交叉驗證（用面向 {'、'.join(dims[k]['label_zh'] for k in cc['dimensions'])} 組成）："
                          f"前 {sp['cross_check']['top']} 名在 {sp['cross_check']['match_km']} km 內重疊 "
                          f"{cc['top_overlap'] * 100:.0f}%，全部格子的等級相關 {cc['spearman_all_cells']}。"]
            L.append("")
        ev = [k for k in profiles.evaluable()]
        L += ["### 每項測試第 1 名的面向分數（面向 × 測試）", "",
              "| 測試 | 第 1 名 | 測試分數 | " + " | ".join(dims[k]["label_zh"] for k in ev) + " | 剖面整體 |",
              "|---|---|---|" + "---|" * len(ev) + "---|"]
        for tid, tr in r["tests"].items():
            if not tr["top"]:
                continue
            x = tr["top"][0]
            main = {k for k, v in (tests()[tid].get("dimensions") or {}).items() if v == "main"}
            cells = []
            for k in ev:
                v = x["dimension_scores"].get(k)
                txt = "—" if v is None else f"{v:.2f}"
                cells.append(f"**{txt}**" if k in main else txt)
            L.append(f"| {tid} | {x.get('name') or ''}（{x['lat']}, {x['lon']}） | {x['score']} | " + " | ".join(cells)
                     + f" | {x['profile_overall']} |")
        L += ["", "粗體 = 這項測試的主要面向。", ""]
        if r.get("weighted_reference"):
            wr = r["weighted_reference"]
            L += ["### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）", "",
                  "權重：" + "、".join(f"{k} {v}" for k, v in wr["weights_used"].items()), "",
                  "| # | 地點 | 座標 | 總分 | " + " | ".join(wr["weights_used"]) + " |",
                  "|---|---|---|---|" + "---|" * len(wr["weights_used"])]
            for x in wr["top"]:
                L.append(f"| {x['rank']} | {x.get('name') or ''} | {x['lat']}, {x['lon']} | {x['score']} | "
                         + " | ".join(f"{x['tests'][k]:.2f}" if x['tests'][k] is not None else "—" for k in wr["weights_used"]) + " |")
            L.append("")
        mc = r["mission_check"]
        L += ["### 已知類比地檢查", "",
              "標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：", "",
              "| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |", "|---|---|---|---|---|---|"]
        for tid, m in mc.items():
            L.append(f"| {tid} | {'、'.join(m['missions']) or '—'} | {m['n_tagged']} | {m['median_top_pct_tagged'] if m['median_top_pct_tagged'] is not None else '—'}% | "
                     f"{m['n_other']} | {m['median_top_pct_other'] if m['median_top_pct_other'] is not None else '—'}% |")
        L.append("")
    return "\n".join(L)


def _md_table(df: pd.DataFrame) -> str:
    esc = lambda x: str(x).replace("|", "／").replace("\n", " ")
    rows = ["| " + " | ".join(map(esc, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    rows += ["| " + " | ".join(esc(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows) + "\n"


# ---------------- 主流程 ----------------
def run(targets: list[str] | None = None, make_figures: bool = True) -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    targets = targets or list(config.mars_targets())
    results, frames, all_status = [], {}, {}
    for target_id in targets:
        print(f"測試項目：{target_id} …", flush=True)
        res, df = build(target_id)
        (OUT / f"{target_id}_tests.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str),
                                                     encoding="utf-8")
        if make_figures:
            figure(target_id, res, df, OUT / f"map_{target_id}_tests.png")
        results.append(res)
        all_status[target_id] = res["status"]
        frames[target_id] = df[["lat", "lon"] + [c for c in df.columns if c.startswith("T_")]]
    cw = crosswalk()
    cw.to_csv(OUT / "crosswalk_dimensions_tests.csv", index=False, encoding="utf-8-sig")
    rm = requirement_matrix(all_status)
    rm.to_csv(OUT / "requirement_matrix.csv", index=False, encoding="utf-8-sig")
    (OUT / "requirement_matrix.md").write_text(
        "# 需求矩陣（給整合者；自動產生自 config/mission_tests.yaml）\n\n" + _md_table(rm), encoding="utf-8")
    print("候選池 …", flush=True)
    candidate_pool(frames).to_csv(OUT / "candidate_pool.csv", index=False, encoding="utf-8-sig")
    (OUT / "TEST_SUMMARY.md").write_text(summary_md(results, cw), encoding="utf-8")
    print("寫出", OUT, flush=True)
    return results
