"""
B4：單項相似度。對每一格、每個變數算出和火星目標「有多像」（0–1），沒資料就是 NaN、coverage = False。

方法（method）：
- "B"（預設，PROJECT_CONTEXT 3.1）：
    slope / roughness → gaussian；thermal_inertia / dust → abs_pct_diff；
    temperature / diurnal_range / aridity → earth_extreme_pct；lithology → lookup；ice → abs_prob_diff（目標 = clip(SWIM Ci, 0, 1)）；barrenness → ndvi_linear
- "A"：能直接比數值的全部用 gaussian 比原始數值（溫度、乾燥度、沙塵也直接比；熱慣量單位不同，只能比百分位）
- "C"：先把火星目標值「拉回」地球範圍（例如溫度設成地球最冷的值），再 gaussian
選項：dust_mode = "pct" | "gaussian"（B6 要求另外試）
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config
from .config import VARIABLES


def ice_target(target: dict) -> float | None:
    """火星端「冰」的目標值（2026-11-14 修正）。
    SWIM 的 Ci 是冰跡象的一致性（−1～+1），不是冰的比例。Ci ≤ 0 = 沒有一致的冰跡象 → 目標 0（找無冰的地方）；
    Ci > 0 → 目標 = Ci（越確定有冰，越要找永凍土比例高的地方）。舊版 (Ci+1)/2 會把 Jezero 的 −0.21 變成 0.40，
    讓「部分永凍土」的地方在水冰面向拿滿分。
    """
    x = target.get("ice", {})
    if not x.get("coverage", False):
        return None
    ci = x.get("value")
    if ci is None and x.get("p") is not None:      # 只有舊版 p 的檔案：反推 Ci
        ci = 2 * float(x["p"]) - 1
    return None if ci is None else float(np.clip(float(ci), 0.0, 1.0))


def _gauss(x, t, sigma):
    return np.exp(-((x - t) ** 2) / (2 * sigma ** 2))


def _q(ref, var, q):
    return float(np.interp(q, np.linspace(0, 1, 101), ref[var]["quantiles"]))


def similarity_vector(target: dict, grid: pd.DataFrame, ref: dict, method: str = "B",
                      dust_mode: str | None = None) -> pd.DataFrame:
    """回傳 DataFrame[s_<var>..., cov_<var>..., d_<var>...]（d_ = 給「哪裡不像」用的實際差距）。"""
    feat = config.features()["variables"]
    n = len(grid)
    S, C, D = {}, {}, {}
    dust_mode = dust_mode or ("gaussian" if method in ("A", "C") else "pct")

    def tval(v, key="value"):
        x = target.get(v, {})
        return x.get(key) if x.get("coverage", False) else None

    # --- 坡度、粗糙度：直接比數值 ---
    for v, col in (("slope", "slope_deg"), ("roughness", "roughness_m")):
        t = tval(v)
        sigma = feat[v]["sigma"]
        if sigma == "auto":
            sigma = 0.5 * ref[col]["area_weighted_std"]
        x = grid[col].values
        if t is None:
            S[v] = np.full(n, np.nan)
        else:
            S[v] = _gauss(x, float(t), float(sigma))
            D[v] = x - float(t)
        C[v] = grid[f"cov_{v}"].values & (t is not None)

    # --- 熱慣量：兩個星球量法不同，只能比「在自己星球排第幾」---
    p = tval("thermal_inertia", "pct")
    S["thermal_inertia"] = (1 - np.abs(grid.ati_pct.values - p)) if p is not None else np.full(n, np.nan)
    if p is not None:
        D["thermal_inertia"] = grid.ati_pct.values - p
    C["thermal_inertia"] = grid.cov_thermal_inertia.values & (p is not None)

    # --- 岩性：查表 ---
    grp = target.get("lithology", {}).get("group")
    table = config.lithology_table().get(grp, {}) if grp else {}
    default = float(feat["lithology"].get("default_score", 0.1))
    S["lithology"] = grid.glim_class.astype(str).map(lambda c: table.get(c, default)).values.astype(float) \
        if grp else np.full(n, np.nan)
    C["lithology"] = grid.cov_lithology.values & (grp is not None)

    # --- 冰：比例 ---
    pm = ice_target(target)
    S["ice"] = (1 - np.abs(grid.permafrost_frac.values - pm)) if pm is not None else np.full(n, np.nan)
    if pm is not None:
        D["ice"] = grid.permafrost_frac.values - pm
    C["ice"] = grid.cov_ice.values & (pm is not None)

    # --- 溫度、日溫差、乾燥度 ---
    T = grid.lst_mean_c.values
    t_mars = tval("temperature")
    if method == "B":
        S["temperature"] = grid.cold_pct.values
        S["diurnal_range"] = grid.dtr_pct.values
        S["aridity"] = grid.arid_pct.values
    else:
        sT = 0.5 * ref["lst_mean_c"]["area_weighted_std"]
        tgtT = float(t_mars) if (method == "A" and t_mars is not None) else _q(ref, "lst_mean_c", 0.0)
        S["temperature"] = _gauss(T, tgtT, sT)
        S["diurnal_range"] = grid.dtr_pct.values  # 火星日溫差值暫缺，A/C 也用極端百分位
        sA = 0.05  # 乾燥指數 < 0.05 = 極乾（UNEP 定義）
        tgtA = 0.0 if method == "A" else _q(ref, "aridity_index", 0.0)
        S["aridity"] = _gauss(grid.aridity_index.values, tgtA, sA)
    if t_mars is not None:
        D["temperature"] = T - float(t_mars)
    D["aridity"] = grid.aridity_index.values
    D["diurnal_range"] = grid.dtr_c.values
    C["temperature"] = grid.cov_temperature.values
    C["diurnal_range"] = grid.cov_diurnal_range.values
    C["aridity"] = grid.cov_aridity.values

    # --- 荒蕪度 ---
    ndvi_max = float(feat["barrenness"].get("ndvi_max", 0.3))
    S["barrenness"] = np.clip(1 - grid.ndvi_mean.values / ndvi_max, 0, 1)
    D["barrenness"] = grid.ndvi_mean.values
    C["barrenness"] = grid.cov_barrenness.values

    # --- 沙塵 ---
    dp, dv = tval("dust", "pct"), tval("dust")
    if dust_mode == "pct":
        S["dust"] = (1 - np.abs(grid.dust_pct.values - dp)) if dp is not None else np.full(n, np.nan)
        ok = dp is not None
    else:  # 直接比光學厚度（A）或先夾到地球範圍（C）
        tgt = dv
        if tgt is not None and method == "C":
            tgt = min(max(float(dv), _q(ref, "dust_aod", 0.0)), _q(ref, "dust_aod", 1.0))
        sD = 0.5 * ref["dust_aod"]["area_weighted_std"]
        S["dust"] = _gauss(grid.dust_aod.values, float(tgt), sD) if tgt is not None else np.full(n, np.nan)
        ok = tgt is not None
    if dp is not None:
        D["dust"] = grid.dust_pct.values - dp
    C["dust"] = grid.cov_dust.values & ok

    out = {}
    for v in VARIABLES:
        s = np.asarray(S[v], dtype="float64")
        c = np.asarray(C[v], dtype=bool) & np.isfinite(s)
        out[f"s_{v}"] = np.where(c, s, np.nan).astype("float32")
        out[f"cov_{v}"] = c
        if v in D:
            out[f"d_{v}"] = np.asarray(D[v], dtype="float32")
    return pd.DataFrame(out, index=grid.index)
