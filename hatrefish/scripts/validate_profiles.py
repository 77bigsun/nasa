r"""
類比剖面的驗證（11/15 加）：沒有「正確答案清單」，所以用四種證據互相印證。

    conda activate nasa_hackathon
    cd hatrefish
    python scripts\validate_profiles.py              # 7 個目標，約 5–10 分鐘
    python scripts\validate_profiles.py --target jezero --draws 20   # 快速試跑

輸出 outputs/validation/VALIDATION.md、validation.json。只讀 data/processed 和 config，不改任何結果。

1. 分面向找回已知類比地：每個已知類比地只看「它被選上的原因」對應的面向（對照表 SITE_DIMS，是本隊的判斷，
   報告會列出來），算它在該面向的全球排名百分位（面積加權，同分取中間）。比較：同一批地點用總體分數的排名。
   只對 known_analogs.csv 標給它的火星目標算（mars_target_ids）。
2. 負對照：明顯不像火星的地方（雨林、三角洲、農地），總體分數應該排在後段。
3. 穩健性：和等權重的前 20 名比，有幾個地點仍在（150 km 內算同一處），等權重第 1 名還在不在前 5。
   情境分五類：(a) 每個面向權重 ×0.5、×1.5；(b) 隨機權重（Dirichlet α = 1）；(c) 合成方式：算術平均、
   取最小值、幾何平均但最低分 0.05（原本 0.01）；(d) 排名池門檻：資料覆蓋 60%、100%（原本 80%）；
   (e) 地點最小間距 100、300 km（原本 150）。另外單獨列「拿掉一個面向」，不算進穩定度（那是在問另一個問題）。
   穩定度：等權重前 20 名的每個地點，在每一類情境裡留在前 20 的比例；總穩定度 = 五類的平均（每類權重相同）。
3b. 方法變體（不算進穩定度，是在問「如果方法這樣改，結果差多少」）：
   - 植被獨立：地表物質只用岩性＋熱慣量，「無植被」另成一個面向（共 6 個面向）。
   - 沒冰的目標不算冰：和 R3、R5 同一條標準（SWIM Ci < ice_min_ci = 0.1）的火星目標，總分不含「水與冰」
     （有冰的目標不變，標「—」）。
   - 溫度冷到一定程度就滿分：溫度單項分數 ÷ 0.9 後上限 1（地球最冷的 10% 都滿分）。
   - 三者一起。
   另外算：植被獨立後第 1 節的「分面向找回」、溫度飽和後「環境面向」前 3 名。
4. 區域層級的找回：前 20 名有幾成落在任一已知類比地 300 km 內，和「排名池裡隨機一格」的比例（面積加權）相比。

百分位 = 全球排名池中分數比它高的面積比例 + 同分面積比例的一半（0% = 最像、100% = 最不像）。
排名池和剖面相同：面向、變數都至少 80% 有資料（profiles._pool）。
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mars_analog import config, profiles  # noqa: E402
from mars_analog.novelty import distinct_sites, haversine_km, place_name  # noqa: E402
from mars_analog.similarity import ice_target  # noqa: E402

TEMP_SAT = 0.9   # 溫度單項分數 ≥ 0.9（地球最冷的 10%）就算滿分


def ice_min_ci() -> float:
    """和 R3、R5 測試同一條標準：SWIM Ci ≥ ice_min_ci 才算有冰（config/mission_tests.yaml）。"""
    import yaml
    return float(yaml.safe_load((ROOT / "config" / "mission_tests.yaml").read_text(encoding="utf-8")).get("ice_min_ci", 0.0))


def no_ice(t: str) -> bool:
    it = ice_target(config.mars_targets()[t])
    return it is not None and it < ice_min_ci()

OUT = ROOT / "outputs" / "validation"
TZ = timezone(timedelta(hours=8))
TOP = 20
SEP = profiles.MIN_SEP_KM
NEAR_KM = 300

# 已知類比地 → 它被選上的原因對應到哪些面向（依 known_analogs.csv 的 analog_for 判斷；空 = 我們量不到的特徵）
SITE_DIMS = {
    "atacama_yungay": ["environment", "surface"],          # 極乾、氧化土壤
    "mcmurdo_dry_valleys": ["environment", "water_ice"],   # 寒冷極地荒漠、地下冰
    "beacon_valley": ["water_ice", "environment"],         # 乾土下的埋藏冰
    "haughton_crater": ["environment", "water_ice"],       # 極地荒漠、永凍土（隕石坑形態量不到）
    "axel_heiberg_lost_hammer": ["environment", "water_ice"],  # 永凍土中的鹽泉
    "svalbard_bockfjorden": ["surface", "water_ice"],      # 火山岩中的碳酸鹽、永凍土地形
    "mdrs_hanksville": ["surface", "terrain"],             # 倒置河道、氾濫平原黏土
    "utah_navajo_concretions": ["surface"],                # 赤鐵礦結核
    "pilot_valley_utah": ["surface"],                      # 高鹽古湖鹽類
    "black_point_lava_flow": ["surface", "terrain"],       # 沉積層上的玄武岩流、地表作業
    "death_valley_badwater": ["surface", "environment"],   # 乾鹽湖蒸發岩
    "mojave_lavic_lake": ["terrain", "surface"],           # 乾鹽湖與玄武岩上的探測車路線
    "white_sands_lake_lucero": ["surface"],                # 石膏沙丘與乾鹽湖
    "pavilion_lake": [],                                   # 淡水湖微生物岩（生物面向，沒有全球資料）
    "lake_salda": ["surface"],                             # 湖相碳酸鹽、三角洲
    "rio_tinto": ["surface"],                              # 酸性硫酸鹽礦物
    "ries_crater": [],                                     # 隕石坑噴出物（形態量不到）
    "askja_vikrahraun": ["surface", "terrain"],            # 玄武岩流形態、風成波紋
    "lanzarote": ["surface", "terrain"],                   # 玄武岩火山地形（熔岩管量不到）
    "mauna_kea_palagonite": ["surface"],                   # 橙玄玻璃質土壤光譜
    "hiseas_mauna_loa": ["terrain", "surface"],            # 火山地形上的模擬棲地（作業面）
    "kau_desert_kilauea": ["surface"],                     # 玄武岩酸性硫酸鹽蝕變
    "lonar_crater": ["surface"],                           # 玄武岩中的熱液黏土
    "kachchh_matanumadh": ["surface"],                     # 蝕變玄武岩中的黃鉀鐵礬與黏土
    "qaidam_dalangtan": ["surface", "environment"],        # 極乾鹽湖、硫酸鹽與氯化物
    "dallol": ["surface"],                                 # 熱液酸性硫酸鹽
    "dhofar_amadee18": ["terrain", "surface", "environment"],  # 沙漠沉積地形、鹽丘
    "pilbara_dresser": [],                                 # 古熱液潟湖疊層石（生物面向）
}

NEGATIVE = [  # 明顯不像火星的地方
    ("Amazon rainforest, Brazil", -5.0, -62.0),
    ("Congo Basin rainforest, DR Congo", 0.5, 22.0),
    ("Borneo rainforest, Indonesia", 0.8, 114.0),
    ("Ganges–Brahmaputra delta, Bangladesh", 23.8, 89.5),
    ("Mekong Delta, Vietnam", 10.0, 105.8),
    ("Paris Basin farmland, France", 48.6, 2.4),
    ("Corn Belt, Iowa, USA", 42.0, -93.5),
    ("Pasture, central Ireland", 53.0, -8.0),
]


def pct_of(values: np.ndarray, w: np.ndarray, x: float) -> float:
    """x 在 values（面積權重 w）裡的「由高到低」百分位：比 x 高的比例 + 同分比例的一半。"""
    tot = w.sum()
    hi = w[values > x].sum()
    eq = w[values == x].sum()
    return float((hi + 0.5 * eq) / tot * 100)


def site_cells(df: pd.DataFrame, lat: float, lon: float, radius: float) -> np.ndarray:
    d = haversine_km(lat, lon, df.lat.values, df.lon.values)
    idx = np.where(d <= radius)[0]
    if len(idx) == 0:
        j = int(np.argmin(d))
        idx = np.array([j]) if d[j] <= 50 else idx
    return idx


def weighted_overall(pool: pd.DataFrame, dims: list[str], w: dict, floor: float = profiles.EPS) -> np.ndarray:
    D = np.column_stack([pool[f"dim_{k}"].values.astype("float64") for k in dims])
    W = np.array([w[k] for k in dims], dtype="float64")[None, :] * np.isfinite(D)
    L = np.log(np.maximum(np.nan_to_num(D, nan=1.0), floor))
    s = W.sum(1)
    return np.where(s > 0, np.exp((W * L).sum(1) / np.where(s > 0, s, 1)), np.nan) * 100


def other_overall(pool: pd.DataFrame, dims: list[str], how: str) -> np.ndarray:
    D = np.column_stack([pool[f"dim_{k}"].values.astype("float64") for k in dims])
    ok = np.isfinite(D).any(1)
    with np.errstate(all="ignore"):
        v = np.nanmean(D, 1) if how == "mean" else np.nanmin(D, 1)
    return np.where(ok, v * 100, np.nan)


def top_sites(pool: pd.DataFrame, score: np.ndarray, n: int = TOP, sep: float = SEP) -> pd.DataFrame:
    p = pool[["lat", "lon"]].copy()
    p["_s"] = score
    p = p[np.isfinite(p._s)]
    return distinct_sites(p, "_s", n, sep)


def hits(base: pd.DataFrame, s: pd.DataFrame) -> np.ndarray:
    """base 的每個地點，在 s 裡有沒有 SEP km 內的地點。"""
    if not len(s):
        return np.zeros(len(base), dtype=bool)
    return np.array([(haversine_km(la, lo, s.lat.values, s.lon.values) <= SEP).any()
                     for la, lo in zip(base.lat.values, base.lon.values)])


def overlap(a: pd.DataFrame, b: pd.DataFrame) -> int:
    """a 的地點有幾個在 b 的某個地點 SEP km 內。"""
    if not len(a) or not len(b):
        return 0
    return int(sum((haversine_km(la, lo, b.lat.values, b.lon.values) <= SEP).any()
                   for la, lo in zip(a.lat.values, a.lon.values)))


def variant_dims(frame: pd.DataFrame, t: str, split=False, noice=False, tempsat=False) -> dict:
    """依方法變體重算各面向分數（和 profiles.score_table 同一種幾何平均與最低分）。"""
    dims = {k: frame[f"dim_{k}"].values.astype("float64") for k in profiles.evaluable()}
    sv = lambda v: frame[f"s_{v}"].values.astype("float64")  # noqa: E731
    if split:
        surf = [v for v in profiles.dimensions()["surface"]["variables"] if v != "barrenness"]
        dims["surface"] = profiles._gmean(np.column_stack([sv(v) for v in surf]))[0]
        dims["bareness"] = sv("barrenness")
    if tempsat:
        env = []
        for v in profiles.dimensions()["environment"]["variables"]:
            x = sv(v)
            env.append(np.minimum(1.0, x / TEMP_SAT) if v == "temperature" else x)
        dims["environment"] = profiles._gmean(np.column_stack(env))[0]
    if noice and no_ice(t):
        dims.pop("water_ice", None)
    return dims


def overall_of(dims: dict) -> np.ndarray:
    o, _ = profiles._gmean(np.column_stack(list(dims.values())))
    return o * 100


def dim_top(frame: pd.DataFrame, dim: np.ndarray, overall: np.ndarray, n: int = 3) -> pd.DataFrame:
    """某面向的前 n 名（面向分數取到小數第 2 位，同分整體高的優先；同 profiles.top_dimension）。"""
    p = frame[["lat", "lon"]].copy()
    p["_k"] = np.round(dim, 2) * 1000 + overall / 1000
    p = p[np.isfinite(p._k)]
    return distinct_sites(p, "_k", n, SEP)


def validate_target(t: str, draws: int, rng: np.random.Generator) -> dict:
    df = profiles.profile_table(t)
    dims = profiles.evaluable()
    pool = profiles._pool(t)
    w_pool = np.cos(np.radians(pool.lat.values))
    ov_pool = pool.overall.values.astype("float64")
    ka = config.known_analogs()
    res = {"target": t, "pool_cells": int(len(pool))}

    # 1. 分面向找回
    split_surf_pool = variant_dims(pool, t, split=True)["surface"]
    split_surf_df = variant_dims(df, t, split=True)["surface"]
    rows = []
    for r in ka.itertuples():
        if t not in r.targets:
            continue
        idx = site_cells(df, r.lat, r.lon, float(r.radius_km))
        if not len(idx):
            continue
        sub = df.iloc[idx]
        ov = float(np.nanmedian(sub.overall.values)) if np.isfinite(sub.overall.values).any() else np.nan
        rec = {"site_id": r.site_id, "name": r.name, "dims": SITE_DIMS.get(r.site_id, []),
               "overall_pct": pct_of(ov_pool, w_pool, ov) if np.isfinite(ov) else None, "dim_pct": {}}
        for k in rec["dims"]:
            v = sub[f"dim_{k}"].values
            if not np.isfinite(v).any():
                continue
            x = float(np.nanmedian(v))
            col = pool[f"dim_{k}"].values.astype("float64")
            ok = np.isfinite(col)
            rec["dim_pct"][k] = pct_of(col[ok], w_pool[ok], x)
        rec["best_dim_pct"] = min(rec["dim_pct"].values()) if rec["dim_pct"] else None
        if "surface" in rec["dim_pct"]:          # 植被獨立後的地表物質（只有岩性＋熱慣量）
            col = split_surf_pool
            ok = np.isfinite(col)
            vs = split_surf_df[idx]
            if np.isfinite(vs).any():
                rec["surface_rock_pct"] = pct_of(col[ok], w_pool[ok], float(np.nanmedian(vs)))
        dp2 = dict(rec["dim_pct"])
        if "surface_rock_pct" in rec:
            dp2["surface"] = rec["surface_rock_pct"]
        rec["best_dim_pct_split"] = min(dp2.values()) if dp2 else None
        rows.append(rec)
    res["known"] = rows

    # 2. 負對照
    neg = []
    for name, la, lo in NEGATIVE:
        idx = site_cells(df, la, lo, 30)
        sub = df.iloc[idx] if len(idx) else df.iloc[[]]
        v = sub.overall.values
        if not len(v) or not np.isfinite(v).any():
            neg.append({"name": name, "lat": la, "lon": lo, "overall": None, "pct": None})
            continue
        x = float(np.nanmedian(v))
        neg.append({"name": name, "lat": la, "lon": lo, "overall": round(x, 1), "pct": pct_of(ov_pool, w_pool, x)})
    res["negative"] = neg

    # 3. 穩健性
    base_w = {k: 1.0 for k in dims}
    base_score = weighted_overall(pool, dims, base_w)
    base = top_sites(pool, base_score)
    first = base.head(1)
    res["top_scores"] = {"first": float(np.nanmax(base_score)),
                         "twentieth": float(pd.Series(base_score, index=pool.index).loc[base.index].min()) if len(base) else None}
    fam_hits: dict[str, list] = {k: [] for k in ("weights", "random", "aggregation", "filter", "separation")}
    scen = []

    def run(family: str, label: str, p: pd.DataFrame, score: np.ndarray, sep: float = SEP):
        s = top_sites(p, score, TOP, sep)
        h = hits(base, s)
        rec = {"family": family, "label": label, "overlap": int(h.sum()), "first_in_top5": bool(overlap(first, s.head(5)))}
        scen.append(rec)
        if family in fam_hits:
            fam_hits[family].append(h)
        return rec

    for k in dims:
        for f in (0.5, 1.5):
            w = dict(base_w)
            w[k] = f
            run("weights", f"{k} ×{f:g}", pool, weighted_overall(pool, dims, w))
        w = dict(base_w)
        w[k] = 0.0
        run("drop", f"{k} 拿掉", pool, weighted_overall(pool, dims, w))
    rnd = [run("random", "隨機權重", pool, weighted_overall(pool, dims, dict(zip(dims, rng.dirichlet(np.ones(len(dims))) * len(dims)))))
           for _ in range(draws)]
    run("aggregation", "算術平均", pool, other_overall(pool, dims, "mean"))
    run("aggregation", "取最小值", pool, other_overall(pool, dims, "min"))
    run("aggregation", "幾何平均，最低分 0.05", pool, weighted_overall(pool, dims, base_w, floor=0.05))
    for c in (0.6, 1.0):
        p = df[(df.confidence >= c) & (df.var_coverage >= c) & np.isfinite(df.overall)]
        run("filter", f"資料覆蓋 ≥ {c:.0%}", p, weighted_overall(p, dims, base_w))
    for sep in (100, 300):
        run("separation", f"最小間距 {sep} km", pool, base_score, sep)

    has_noice = no_ice(t)
    for lab, kw in (("植被獨立成一個面向", dict(split=True)), ("沒冰的目標不算冰", dict(noice=True)),
                    ("溫度冷到最冷 10% 就滿分", dict(tempsat=True)), ("三者一起", dict(split=True, noice=True, tempsat=True))):
        if kw == {"noice": True} and not has_noice:
            scen.append({"family": "variant", "label": lab, "overlap": None, "first_in_top5": None})
            continue
        run("variant", lab, pool, overall_of(variant_dims(pool, t, **kw)))
    base_env = pool["dim_environment"].values.astype("float64")
    sat = variant_dims(pool, t, tempsat=True)
    env_base = dim_top(pool, base_env, base_score)
    env_sat = dim_top(pool, sat["environment"], overall_of(sat))
    res["env_top"] = {"base": place_name(env_base.lat.values, env_base.lon.values),
                      "base_ll": [[round(float(a), 2), round(float(b), 2)] for a, b in zip(env_base.lat, env_base.lon)],
                      "tempsat": place_name(env_sat.lat.values, env_sat.lon.values),
                      "tempsat_ll": [[round(float(a), 2), round(float(b), 2)] for a, b in zip(env_sat.lat, env_sat.lon)]}
    res["noice_applies"] = bool(has_noice)

    names = place_name(base.lat.values, base.lon.values)
    stab = []
    for i, (la, lo) in enumerate(zip(base.lat.values, base.lon.values)):
        fam = {k: float(np.mean([h[i] for h in v])) for k, v in fam_hits.items() if v}
        stab.append({"rank": i + 1, "lat": round(float(la), 2), "lon": round(float(lo), 2), "name": names[i],
                     "overall": round(float(base_score[pool.index.get_indexer([base.index[i]])[0]]), 1),
                     "by_family": fam, "stability": float(np.mean(list(fam.values()))) if fam else None})
    res["robust"] = {"scenarios": [x for x in scen if x["family"] != "random"],
                     "random": {"draws": draws,
                                "overlap_median": float(np.median([x["overlap"] for x in rnd])) if rnd else None,
                                "overlap_p10": float(np.percentile([x["overlap"] for x in rnd], 10)) if rnd else None,
                                "first_in_top5_share": float(np.mean([x["first_in_top5"] for x in rnd])) if rnd else None},
                     "stability": stab}

    # 4. 區域層級的找回
    near_pool = np.zeros(len(pool), dtype=bool)
    near_top = np.zeros(len(base), dtype=bool)
    for r in ka.itertuples():
        near_pool |= haversine_km(r.lat, r.lon, pool.lat.values, pool.lon.values) <= NEAR_KM
        near_top |= haversine_km(r.lat, r.lon, base.lat.values, base.lon.values) <= NEAR_KM
    baseline = float(w_pool[near_pool].sum() / w_pool.sum())
    share = float(near_top.mean()) if len(base) else None
    res["region"] = {"top_n": int(len(base)), "near_known_share": share, "baseline_share": baseline,
                     "enrichment": (share / baseline) if share is not None and baseline > 0 else None}
    return res


def _f(x, nd=0, pct=False):
    if x is None:
        return "—"
    return f"{x:.{nd}f}%" if pct else f"{x:.{nd}f}"


def report(results: list[dict], draws: int) -> str:
    L = ["# 類比剖面驗證", "",
         f"> 產生時間 {datetime.now(TZ).isoformat(timespec='seconds')}，`scripts/validate_profiles.py`。"
         "百分位：0% = 全球最像，50% = 隨機，100% = 最不像（面積加權，排名池同剖面）。", ""]

    # 1
    allk = [k for r in results for k in r["known"]]
    dimk = [k for k in allk if k["best_dim_pct"] is not None]
    L += ["## 1. 分面向找回已知類比地", "",
          "每個已知類比地只看它被選上的原因對應的面向（對照表在第 5 節），只對標給它的火星目標算。", ""]
    if dimk:
        bd = np.array([k["best_dim_pct"] for k in dimk])
        ovp = np.array([k["overall_pct"] for k in dimk if k["overall_pct"] is not None])
        L += ["| 指標 | 用對應面向 | 用總體分數 |", "|---|---|---|",
              f"| 地點 × 目標組數 | {len(bd)} | {len(ovp)} |",
              f"| 百分位中位數 | {np.median(bd):.1f}% | {np.median(ovp):.1f}% |",
              f"| 前 10% 的比例（隨機 = 10%） | {np.mean(bd <= 10) * 100:.0f}% | {np.mean(ovp <= 10) * 100:.0f}% |",
              f"| 前 25% 的比例（隨機 = 25%） | {np.mean(bd <= 25) * 100:.0f}% | {np.mean(ovp <= 25) * 100:.0f}% |", "",
              "「用對應面向」取該地點對應面向中最好的那個百分位（一個地點被選上，通常只要一個面向像就夠）。", ""]
    skipped = sorted({k["site_id"] for k in allk if not k["dims"]})
    if skipped:
        L += [f"沒算的（被選上的原因我們量不到，例如生物、隕石坑形態）：{', '.join(skipped)}。", ""]
    L += ["| 目標 | 已知類比地 | 對應面向：百分位 | 總體百分位 |", "|---|---|---|---|"]
    for r in results:
        for k in sorted(r["known"], key=lambda k: (k["best_dim_pct"] is None, k["best_dim_pct"] or 0)):
            dp = "、".join(f"{d} {v:.0f}%" for d, v in k["dim_pct"].items()) or "—"
            L.append(f"| {r['target']} | {k['name']} | {dp} | {_f(k['overall_pct'], 0, True)} |")
    L.append("")

    # 2
    L += ["## 2. 負對照（明顯不像火星的地方）", "",
          "判準：不能進全球前 25%，總體分數也要遠低於前 20 名。格子裡是百分位（總體分數）。", "",
          "| 地點 | " + " | ".join(r["target"] for r in results) + " |",
          "|---|" + "---|" * len(results)]
    for i, (name, _, _) in enumerate(NEGATIVE):
        L.append(f"| {name} | " + " | ".join(
            f"{_f(r['negative'][i]['pct'], 0, True)}（{_f(r['negative'][i]['overall'])}）" for r in results) + " |")
    L.append("| **對照：前 20 名的最低分** | " + " | ".join(_f(r["top_scores"]["twentieth"], 1) for r in results) + " |")
    allneg = [n["pct"] for r in results for n in r["negative"] if n["pct"] is not None]
    if allneg:
        a = np.array(allneg)
        L += ["", f"全部 {len(a)} 組：進入前 25% 的 {int((a < 25).sum())} 組，百分位最低 {a.min():.0f}%，中位數 {np.median(a):.0f}%。",
              "負對照多半落在中段而不是最後：例如對沒有冰訊號的目標，溫帶農地在「水與冰」拿滿分、在「地形」接近滿分，"
              "五個面向的幾何平均會被撐到中段。所以排名只有最前面一段有意義，中段的先後不代表像不像。"]
    L.append("")

    # 3
    L += ["## 3. 穩健性（和等權重前 20 名比）", "",
          f"數字 = 前 20 名裡有幾個地點仍在（{SEP} km 內算同一處）；★ = 等權重第 1 名仍在前 5。", ""]
    L += ["| 情境 | " + " | ".join(r["target"] for r in results) + " |", "|---|" + "---|" * len(results)]
    order = [("weights", "權重"), ("drop", "拿掉面向（不算進穩定度）"), ("aggregation", "合成方式"),
             ("filter", "排名池門檻"), ("separation", "最小間距"), ("variant", "方法變體（不算進穩定度）")]
    labels = [(fam, x["label"]) for fam, _ in order for x in results[0]["robust"]["scenarios"] if x["family"] == fam]
    for fam, lab in labels:
        cells = []
        for r in results:
            x = next(o for o in r["robust"]["scenarios"] if o["family"] == fam and o["label"] == lab)
            cells.append("—" if x["overlap"] is None else f"{x['overlap']}{' ★' if x['first_in_top5'] else ''}")
        L.append(f"| {dict(order)[fam]}：{lab} | " + " | ".join(cells) + " |")
    L.append(f"| 隨機權重 {draws} 組：重疊中位數（第 10 百分位） | " + " | ".join(
        f"{_f(r['robust']['random']['overlap_median'])}（{_f(r['robust']['random']['overlap_p10'])}）" for r in results) + " |")
    L.append("| 隨機權重：第 1 名仍在前 5 的比例 | " + " | ".join(
        _f((r['robust']['random']['first_in_top5_share'] or 0) * 100, 0, True) for r in results) + " |")
    L += ["", "### 3.1 每個地點的穩定度", "",
          "等權重前 10 名，在各類情境裡留在前 20 名的比例。總穩定度 = 五類的平均；"
          "≥ 80% 可以說「換假設也穩」，< 50% 表示這個地點的名次靠特定假設。", ""]
    fams = [("weights", "權重 ±50%"), ("random", "隨機權重"), ("aggregation", "合成方式"),
            ("filter", "排名池門檻"), ("separation", "最小間距")]
    for r in results:
        L += [f"**{r['target']}**", "", "| # | 地點 | 總體 | " + " | ".join(n for _, n in fams) + " | 總穩定度 |",
              "|---|---|---|" + "---|" * len(fams) + "---|"]
        for x in r["robust"]["stability"][:10]:
            L.append(f"| {x['rank']} | {x['name'] or ''}（{x['lat']}, {x['lon']}） | {x['overall']} | " + " | ".join(
                _f(x['by_family'].get(k, 0) * 100, 0, True) for k, _ in fams) + f" | **{_f((x['stability'] or 0) * 100, 0, True)}** |")
        L.append("")
    allst = [x["stability"] for r in results for x in r["robust"]["stability"][:10] if x["stability"] is not None]
    if allst:
        a = np.array(allst)
        L += [f"全部目標的前 10 名（{len(a)} 個）：總穩定度 ≥ 80% 的 {int((a >= 0.8).sum())} 個，"
              f"50–80% 的 {int(((a >= 0.5) & (a < 0.8)).sum())} 個，< 50% 的 {int((a < 0.5).sum())} 個。", ""]

    # 3.2 方法變體細節
    L += ["### 3.2 方法變體的細節", ""]
    allk2 = [k for r in results for k in r["known"] if k.get("best_dim_pct_split") is not None]
    if allk2:
        a0 = np.array([k["best_dim_pct"] for k in allk2])
        a1 = np.array([k["best_dim_pct_split"] for k in allk2])
        L += ["**植被獨立後，第 1 節的分面向找回**（地表物質只看岩性＋熱慣量）", "",
              "| 指標 | 現在 | 植被獨立 |", "|---|---|---|",
              f"| 百分位中位數 | {np.median(a0):.1f}% | {np.median(a1):.1f}% |",
              f"| 前 10% 的比例 | {np.mean(a0 <= 10) * 100:.0f}% | {np.mean(a1 <= 10) * 100:.0f}% |",
              f"| 前 25% 的比例 | {np.mean(a0 <= 25) * 100:.0f}% | {np.mean(a1 <= 25) * 100:.0f}% |", "",
              "| 目標 | 已知類比地 | 地表物質：現在 → 只看岩石 |", "|---|---|---|"]
        for r in results:
            for k in r["known"]:
                if "surface" in k["dim_pct"] and "surface_rock_pct" in k:
                    d = k["surface_rock_pct"] - k["dim_pct"]["surface"]
                    if abs(d) >= 15:
                        L.append(f"| {r['target']} | {k['name']} | {k['dim_pct']['surface']:.0f}% → {k['surface_rock_pct']:.0f}% |")
        L += ["", "（只列變動 ≥ 15 個百分點的。）", ""]
    L += ["**溫度飽和後，環境面向的前 3 名**", "", "| 目標 | 現在 | 冷到最冷 10% 就滿分 |", "|---|---|---|"]
    for r in results:
        e = r["env_top"]
        L.append(f"| {r['target']} | {'；'.join(n or '' for n in e['base'])} | {'；'.join(n or '' for n in e['tempsat'])} |")
    L += ["", "注意：環境面向的兩個變數（溫度、乾燥度）都是「越極端越像」，和火星目標無關，所以每個目標的環境前幾名都一樣；"
          "溫度飽和只會換掉被極端值獨佔的地點，不會讓它隨目標改變。", "",
          f"「沒冰的目標不算冰」適用 SWIM Ci < {ice_min_ci():g} 的目標（同 R3、R5 的標準）："
          + "、".join(r["target"] for r in results if r.get("noice_applies")) + "；其他目標標「—」。", ""]

    # 4
    L += ["## 4. 區域層級的找回", "",
          f"前 {TOP} 名落在任一已知類比地 {NEAR_KM} km 內的比例，和排名池裡隨機一格的比例（面積加權）相比。", "",
          "| 目標 | 前 20 名 | 隨機 | 倍數 |", "|---|---|---|---|"]
    for r in results:
        g = r["region"]
        L.append(f"| {r['target']} | {_f((g['near_known_share'] or 0) * 100, 0, True)} | "
                 f"{_f(g['baseline_share'] * 100, 1, True)} | {_f(g['enrichment'], 1)} |")
    L += ["", "已知類比地本身偏向容易到達、研究多的地方，所以這是區域層級的佐證，不是準確率。", ""]

    # 5
    L += ["## 5. 已知類比地 → 面向對照（本隊判斷）", "", "| 地點 | 面向 |", "|---|---|"]
    for s, d in SITE_DIMS.items():
        L.append(f"| {s} | {'、'.join(d) or '（量不到，不算）'} |")
    L += ["", "## 6. 限制", "",
          "- 沒有「正確答案」：已知類比地多半因為單一特徵被選上，也偏向容易到達的地方。",
          "- 已知類比地只有 28 個，而且 4 個目標（ap105、oxia、meridiani、protonilus）沒有標給它們的已知類比地，第 1 節只涵蓋 jezero、gale、arcadia。",
          "- 面向對照是人工判斷；改 `SITE_DIMS` 就能重算。",
          "- 負對照只有 8 個點，用來排除「算法亂來」，不能證明排在前面的就是好的類比地。",
          "- 穩健性只改了「怎麼合成、怎麼篩選」，沒有改輸入資料本身（例如溫度 ±1–2 K 的誤差）、單一變數的比較參數，"
          "也沒有改火星端的目標值；這些列為之後的工作。", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", action="append")
    ap.add_argument("--draws", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    targets = a.target or list(config.mars_targets())
    rng = np.random.default_rng(a.seed)
    results = []
    for t in targets:
        print(f"[{t}] ...", flush=True)
        results.append(validate_target(t, a.draws, rng))
        profiles._CACHE.clear()          # 一次只留一個目標的全球表，省記憶體
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "validation.json").write_text(json.dumps(results, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    (OUT / "VALIDATION.md").write_text(report(results, a.draws), encoding="utf-8")
    print(f"written to {OUT}")


if __name__ == "__main__":
    main()
