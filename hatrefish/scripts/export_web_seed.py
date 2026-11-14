r"""
把本隊（hatrefish）的資料轉成網頁整合的資料契約（github.com/77bigsun/nasa，main 分支 data/seed/）。

    conda activate nasa_hackathon
    cd hatrefish
    python scripts\export_web_seed.py                                        # 用 config/web_contract/ 的契約快照
    python scripts\export_web_seed.py --web-seed ..\..\nasa-main\data\seed   # 讀 main 最新的定義，另外輸出可直接替換的合併檔
    python scripts\export_web_seed.py --web-seed ..\..\nasa-main\data\seed --check   # 再用網頁自己的評分程式跑一次

輸出 outputs/web/：
  current/    照網頁現在的 tasks_mars.yaml 填值（網頁不用改程式或定義）
  proposed/   套用本隊建議（PROPOSALS）後的 tasks_mars.yaml、categorical_tables.yaml、data_sources.yaml 和對應的值
      兩個資料夾都有 earth_candidates.mars.json（只含火星用的地球候選）與 target_values.mars.yaml（mars-ap105／jezero／gale）；
      有 --web-seed 時另有 merged/：和網頁現有檔合併後的 earth_candidates.demo.json、target_values.demo.yaml
      （月球的 placeholder 保留；placeholder 候選身上的火星特徵值移除，避免假數字混進火星排名）
  earth_population.json   每個特徵的全球地球分位數（建議網頁用它算百分位，見 WEB_EXPORT.md 第 4 節）
  WEB_EXPORT.md           特徵對照、候選清單、缺什麼、給整合者的建議

讀：data/processed/earth_grid.parquet、earth_monthly.parquet、earth_extra.parquet、mars_targets.json、
    outputs/mission_tests/candidate_pool.csv（先跑 scripts/make_mission_tests.py）、data/labels/known_analogs.csv
"""
import argparse
import copy
import json
import math
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mars_analog import config, mission_tests as mt  # noqa: E402
from mars_analog.novelty import haversine_km, place_name  # noqa: E402
from mars_analog.paths import PROCESSED  # noqa: E402

CONTRACT = ROOT / "config" / "web_contract"      # main 分支 c875ba6 的 tasks_mars.yaml、categorical_tables.yaml、data_sources.yaml
CONTRACT_COMMIT = "c875ba6"
OUT = ROOT / "outputs" / "web"
POOL = ROOT / "outputs" / "mission_tests" / "candidate_pool.csv"

TARGETS = {"mars-ap105": "ap105", "mars-jezero": "jezero", "mars-gale": "gale"}   # 網頁目標 id → 本隊目標 id
MAX_PICKS = 22             # 依分數挑的候選上限（3 個目標共 11 個測試 × 2）
MAX_CANDIDATES = 28        # 再補已知類比地後的總上限：網頁的邊際效益曲線用窮舉組合 C(n, 6)，候選太多會跑不動
PER_TEST = 2               # 每個（目標 × 測試）取前幾名
MIN_SEP_KM = 150           # 候選之間至少相隔
KNOWN = ["mcmurdo_dry_valleys", "haughton_crater", "atacama_yungay", "lake_salda", "mdrs_hanksville", "askja_vikrahraun"]
ICE_TASKS = ("R3", "R5")   # mission_tests.yaml 的 applies: ice（SWIM Ci 太低的目標不評這兩項）
SOUTH_FILL = -60.0         # 南緯 60° 以南沒有 NDVI、乾燥指數：當作無植被、極乾（同 mission_tests.yaml 的 fill）
EARTH_YEAR_H = 365.2422 * 24
MARS_YEAR_H = 686.98 * 24

# ---------------------------------------------------------------------------------------------------------------
# 地球端：網頁特徵 id → 本隊欄位
# ---------------------------------------------------------------------------------------------------------------
EARTH = {
    "r1_slope_100m": {"col": "slope_deg"},
    "r1_thermal_inertia": {"col": "ati"},
    "r3_ground_ice": {"col": "permafrost_frac"},
    "r5_roughness": {"col": "roughness_m"},
    "r6_dust": {"series": "dust"},
    "r6_wind_temp": {"series": "day_night"},
    # 以下是建議新增的特徵（proposed/ 才會用到）
    "r1_barren": {"col": "ndvi_mean", "south_fill": 0.0},
    "r1_ice_free": {"col": "icy_frac"},
    "r3_cold": {"col": "lst_mean_c"},
    "r3_dryness": {"col": "aridity_index", "south_fill": 0.0},
    "r4_lithology": {"category": "glim_class"},
    "r4_barren": {"col": "ndvi_mean", "south_fill": 0.0},
    "r5_ground_ice": {"col": "permafrost_frac"},
    "r5_cold": {"col": "lst_mean_c"},
    "r6_temperature": {"col": "lst_mean_c"},
}

# 全球分位數（earth_reference_pct.json：無冰陸地 0.1° 格，cos 緯度加權）對應的變數
POPULATION_VAR = {
    "r1_slope_100m": "slope_deg", "r1_thermal_inertia": "ati", "r3_ground_ice": "permafrost_frac",
    "r5_ground_ice": "permafrost_frac", "r5_roughness": "roughness_m", "r6_dust": "dust_aod", "r6_wind_temp": "dtr_c",
    "r1_barren": "ndvi_mean", "r4_barren": "ndvi_mean", "r3_cold": "lst_mean_c", "r5_cold": "lst_mean_c",
    "r6_temperature": "lst_mean_c", "r3_dryness": "aridity_index",
}

# ---------------------------------------------------------------------------------------------------------------
# 建議改動（proposed/）：讓網頁評分程式能用到本隊已經有的資料，規則同 config/mission_tests.yaml
# ---------------------------------------------------------------------------------------------------------------
NEW_SOURCES = [
    {"id": "gmted", "name": "USGS GMTED2010", "portal": "USGS EROS", "official": False,
     "url": "https://doi.org/10.3133/ofr20111073", "status": "used",
     "notes": "Danielson & Gesch (2011)。本隊用 230 m 坡度與 5×5 視窗高程標準差，取 0.1° 格內中位數（Google Earth Engine）。"},
    {"id": "hrsc_mola", "name": "Mars HRSC MOLA Blended DEM Global 200 m v2", "portal": "USGS Astrogeology", "official": False,
     "url": "https://astrogeology.usgs.gov/search/map/mars_mgs_mola_mex_hrsc_blended_dem_global_200m",
     "status": "used", "notes": "Fergason et al. (2018)。火星端坡度與粗糙度，和地球端同為約 200 m 尺度。"},
    {"id": "glim", "name": "GLiM Global Lithological Map", "portal": "Universität Hamburg", "official": False,
     "url": "https://doi.org/10.1029/2012GC004370", "status": "used",
     "notes": "Hartmann & Moosdorf (2012)，0.5° 版。只是岩性大類代理。"},
    {"id": "sim3292", "name": "USGS SIM 3292 Geologic Map of Mars", "portal": "USGS", "official": False,
     "url": "https://doi.org/10.3133/sim3292", "status": "used",
     "notes": "Tanaka et al. (2014)。地質單元依本隊對照表歸成岩性大類；Oxia、Meridiani 用文獻覆寫。"},
    {"id": "aridity", "name": "Global Aridity Index and PET Database v3", "portal": "figshare", "official": False,
     "url": "https://doi.org/10.1038/s41597-022-01493-1", "status": "used", "notes": "Zomer et al. (2022)。南緯 60° 以南沒有資料，補成極乾。"},
    {"id": "tes", "name": "TES nighttime thermal inertia (Putzig & Mellon 2007)", "portal": "PDS", "official": True,
     "url": "https://doi.org/10.1016/j.icarus.2007.05.013", "status": "used", "notes": "火星熱慣量與全球百分位。"},
]


def _src(sid, name):
    return {"name": name, "official": sid in ("earthdata", "pds", "copernicus", "tes"), "source_id": sid,
            "url": None}


def _feature(fid, name, name_en, ftype, mode, unit, earth, planet, notes, threshold=None, stat="mean"):
    return {"id": fid, "name": name, "name_en": name_en, "type": ftype, "compare_mode": mode, "unit": unit,
            "weight": 1.0, "threshold": threshold, "planet_threshold": None, "out_of_earth_range": False,
            "earth_proxy": False, "planet_data": planet, "earth_data": earth, "notes": notes, "stat": stat,
            "stat_threshold": 0, "rank_stat_threshold": None}


MODIS_LST = ("earthdata", "MODIS MOD11A2＋MYD11A2 地表溫 2015–2024")
MODIS_NDVI = ("earthdata", "MODIS NDVI 2015–2024")
MCD = ("mcd", "火星氣候資料庫 MCD v6")
PROPOSALS = {
    "modify": {
        "r3_ground_ice": {"type": "threshold", "compare_mode": "absolute", "unit": "fraction",
                          "threshold": {"zero_at": 0.1, "ideal_min": 0.9},
                          "earth_data": [_src("cci", "ESA CCI 永凍土 v5.0（0.1° 格內永凍土比例）")],
                          "planet_data": [_src("swim", "SWIM4MIM 冰一致性 Ci")],
                          "notes+": ["本隊建議：測「有沒有冰可以偵測」，地球永凍土比例 0.1 → 0 分、0.9 → 1 分；"
                                     "SWIM Ci < 0.1 的目標（Jezero、Gale）不評 R3／R5（目標值留空）。"]},
        "r5_roughness": {"compare_mode": "absolute", "unit": "m",
                         "earth_data": [_src("gmted", "GMTED2010 230 m，5×5 視窗高程標準差")],
                         "planet_data": [_src("hrsc_mola", "HRSC＋MOLA 200 m，5×5 視窗高程標準差")],
                         "notes+": ["本隊建議改 absolute：兩邊都在約 200 m 尺度、同一算法，單位都是公尺，可以直接比。"]},
        "r1_slope_100m": {"earth_data": [_src("gmted", "GMTED2010 230 m 坡度（0.1° 格內中位數）")],
                          "planet_data": [_src("hrsc_mola", "HRSC＋MOLA 200 m 坡度")],
                          "notes+": ["本隊資料是 200 m 尺度，不是 100 m。"]},
        "r1_thermal_inertia": {"earth_data": [_src("earthdata", "MODIS 表觀熱慣量 ATI =（1 − 反照率）／ 日夜溫差")],
                               "planet_data": [_src("tes", "TES 夜間熱慣量（Putzig & Mellon 2007）")]},
        "r6_dust": {"earth_data": [_src("earthdata", "MERRA-2 DUEXTTAU 月平均 2019–2023")],
                    "planet_data": [_src(*MCD)],
                    "notes+": ["序列的 phase = 當地季節的太陽黃經 ／ 360（0 = 當地春分）；地球南半球、火星南半球各加半年。"]},
        "r6_wind_temp": {"earth_data": [_src(*MODIS_LST)], "planet_data": [_src(*MCD)],
                         "notes+": ["本隊只有溫度日夜差，沒有風。地球序列是 MODIS 日間、夜間兩點（約 12:00、00:00），range = 日夜溫差。",
                                    "火星日夜溫差（約 75–95 °C）超出地球範圍，目標百分位填 1.0（取地球最極端，同本隊 earth_extreme_pct）。"]},
    },
    "add": {
        "R1": [
            _feature("r1_barren", "無植被", "Bare ground", "threshold", "absolute", "NDVI",
                     [_src(*MODIS_NDVI)], [], ["NDVI ≤ 0 得 1、≥ 0.3 得 0；南緯 60° 以南沒有 NDVI，補 0（無植被）。"],
                     threshold={"ideal_max": 0.0, "zero_at": 0.3}),
            _feature("r1_ice_free", "不是冰面", "Ice-free surface", "threshold", "absolute", "fraction",
                     [_src("earthdata", "MCD12Q1 冰雪比例；年均 NDVI < 0 且年均溫 < 0 °C")], [],
                     ["降落面是岩石與風化層，不是冰：冰雪比例 ≤ 0.1 得 1、≥ 0.5 得 0。"],
                     threshold={"ideal_max": 0.1, "zero_at": 0.5}),
        ],
        "R3": [
            _feature("r3_cold", "年均地表溫低於 0 °C", "Below-freezing mean temperature", "threshold", "absolute", "°C",
                     [_src(*MODIS_LST)], [_src(*MCD)], ["年均地表溫 ≤ −2 °C 得 1、≥ 2 °C 得 0（地球能維持永凍土）。"],
                     threshold={"ideal_max": -2.0, "zero_at": 2.0}),
            _feature("r3_dryness", "乾燥程度", "Aridity", "profile", "relative_rank", "",
                     [_src("aridity", "Global Aridity Index v3")], [],
                     ["目標百分位 0（地球最乾）；南緯 60° 以南沒有資料，補 0（極乾）。"]),
        ],
        "R4": [
            _feature("r4_lithology", "岩性大類", "Lithology class", "categorical", "absolute", "",
                     [_src("glim", "GLiM 0.5°")], [_src("sim3292", "USGS SIM 3292＋文獻覆寫")],
                     ["只是岩性大類代理，很粗；對照表見 categorical_tables.yaml。"]),
            _feature("r4_barren", "岩石裸露", "Exposed rock", "threshold", "absolute", "NDVI",
                     [_src(*MODIS_NDVI)], [], ["植被會遮住光譜。NDVI ≤ 0 得 1、≥ 0.3 得 0。"],
                     threshold={"ideal_max": 0.0, "zero_at": 0.3}),
        ],
        "R5": [
            _feature("r5_ground_ice", "永凍土", "Permafrost", "threshold", "absolute", "fraction",
                     [_src("cci", "ESA CCI 永凍土 v5.0")], [_src("swim", "SWIM4MIM Ci")],
                     ["永凍土比例 0.1 → 0、0.9 → 1；SWIM Ci < 0.1 的目標不評。"],
                     threshold={"zero_at": 0.1, "ideal_min": 0.9}),
            _feature("r5_cold", "年均地表溫低於 0 °C", "Below-freezing mean temperature", "threshold", "absolute", "°C",
                     [_src(*MODIS_LST)], [_src(*MCD)], ["同 r3_cold。"], threshold={"ideal_max": -2.0, "zero_at": 2.0}),
        ],
        "R6": [
            _feature("r6_temperature", "年均地表溫（越冷越好）", "Mean surface temperature", "profile", "relative_rank", "°C",
                     [_src(*MODIS_LST)], [_src(*MCD)], ["火星比地球任何地方都冷，目標百分位填 0（取地球最冷）。"]),
        ],
    },
}


# ---------------------------------------------------------------------------------------------------------------
# 讀資料
# ---------------------------------------------------------------------------------------------------------------
def _num(x, nd=4):
    if x is None:
        return None
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(x):
        return None
    return float(f"{x:.{nd}g}") if abs(x) >= 1 else round(x, nd)


def earth_frame() -> pd.DataFrame:
    g = mt.grid()
    df = g[["cell_id", "lat", "lon", "slope_deg", "ati", "permafrost_frac", "roughness_m", "lst_mean_c", "lst_day_c",
            "lst_night_c", "dtr_c", "aridity_index", "ndvi_mean", "glim_class"]].copy()
    df["icy_frac"] = mt._col("icy_frac")
    dust = mt._monthly("dust_m")
    df[[f"dust_m{m:02d}" for m in range(1, 13)]] = dust if dust is not None else np.nan
    return df


def earth_season_phase(lat: float) -> np.ndarray:
    """地球 12 個月的當地季節相位（太陽黃經 / 360，南半球加半年），同 mission_tests 的季節對齊。"""
    lam = mt.EARTH_MONTH_LAMBDA + (0.0 if lat >= 0 else 180.0)
    return (lam % 360) / 360


def _series(phase, values, step_hours, period):
    phase = np.asarray(phase, float)
    values = np.asarray(values, float)
    if not len(values) or not np.isfinite(values).all():
        return None
    o = np.argsort(phase)
    return {"phase": [round(float(p), 6) for p in phase[o]], "values": [_num(v) for v in values[o]],
            "step_hours": round(step_hours, 2), "period": period}


def earth_measurements(row, feature_ids) -> dict:
    out = {"values": {}, "categories": {}, "spectra": {}, "series": {}, "planet_values": {}}
    for fid in feature_ids:
        spec = EARTH.get(fid)
        if spec is None:
            continue
        if "col" in spec:
            v = row[spec["col"]]
            if (v is None or not np.isfinite(v)) and "south_fill" in spec and row["lat"] < SOUTH_FILL:
                v = spec["south_fill"]
            v = _num(v)
            if v is not None:
                out["values"][fid] = v
        elif "category" in spec:
            c = row[spec["category"]]
            if isinstance(c, str) and c not in ("nd", ""):
                out["categories"][fid] = c
        elif spec["series"] == "dust":
            s = _series(earth_season_phase(row["lat"]), [row[f"dust_m{m:02d}"] for m in range(1, 13)],
                        EARTH_YEAR_H / 12, "season_ls: 當地季節的太陽黃經/360（MERRA-2 DUEXTTAU 月平均）")
            if s:
                out["series"][fid] = s
        elif spec["series"] == "day_night":
            s = _series([0.0, 0.5], [row["lst_night_c"], row["lst_day_c"]], 12.0,
                        "local_solar_day: MODIS 夜間（≈00:00）與日間（≈12:00）兩點，Terra＋Aqua 2015–2024")
            if s:
                out["series"][fid] = s
    return out


def mars_measurements(tid: str, features: dict) -> tuple[dict, list[str]]:
    """features: {fid: feature dict（網頁格式）}。依每個特徵的 compare_mode 填值。"""
    t = config.mars_targets()[tid]       # 變數已經攤平在目標底下（config._normalize_targets）
    f = t

    def val(k):
        return (f.get(k) or {}).get("value")

    ci = val("ice")
    has_ice = ci is not None and ci >= float(mt.spec().get("ice_min_ci", 0.1))
    ice01 = None if ci is None else float(np.clip(ci, 0, 1))
    sea = t.get("seasonal") or {}
    dust_series = None
    if sea.get("ls") and sea.get("dust_tau"):
        off = 0.0 if float(t["lat"]) >= 0 else 0.5
        dust_series = _series((np.asarray(sea["ls"], float) / 360 + off) % 1, sea["dust_tau"], MARS_YEAR_H / len(sea["ls"]),
                              "season_ls: 火星太陽黃經 Ls/360（當地季節；MCD tauref）")
    m = {
        "r1_slope_100m": {"raw": val("slope")},
        "r1_thermal_inertia": {"raw": val("thermal_inertia"), "pct": (f.get("thermal_inertia") or {}).get("pct")},
        "r3_ground_ice": {"raw": ice01, "planet": ci},
        "r5_ground_ice": {"raw": ice01, "planet": ci},
        "r5_roughness": {"raw": val("roughness")},
        "r6_dust": {"raw": val("dust"), "pct": (f.get("dust") or {}).get("pct"), "series": dust_series},
        "r6_wind_temp": {"raw": val("diurnal_range"), "pct": 1.0},
        "r1_barren": {"raw": 0.0}, "r4_barren": {"raw": 0.0}, "r1_ice_free": {"raw": 0.0},
        "r3_cold": {"raw": val("temperature")}, "r5_cold": {"raw": val("temperature")},
        "r3_dryness": {"pct": 0.0},
        "r6_temperature": {"raw": val("temperature"), "pct": 0.0},
        "r4_lithology": {"category": (f.get("lithology") or {}).get("group")},
    }
    out = {"is_placeholder": False, "values": {}, "categories": {}, "spectra": {}, "series": {}, "planet_values": {}}
    notes = []
    for fid, feat in features.items():
        task = feat["_task"]
        d = m.get(fid)
        if d is None:
            continue
        if task in ICE_TASKS and not has_ice:
            continue
        if feat["type"] == "categorical":
            if d.get("category"):
                out["categories"][fid] = d["category"]
            continue
        v = d.get("pct") if feat["compare_mode"] == "relative_rank" else d.get("raw")
        if feat["compare_mode"] == "relative_rank" and v is None and d.get("raw") is not None:
            notes.append(f"{fid}：relative_rank 需要火星百分位，本隊沒有 → 目標值留空（原始值 {d['raw']} 放在 planet_values）")
        v = _num(v)
        if v is not None:
            out["values"][fid] = v
        raw = _num(d.get("planet", d.get("raw")))
        if raw is not None and fid in ("r1_slope_100m", "r1_thermal_inertia", "r3_ground_ice", "r5_ground_ice",
                                       "r5_roughness", "r6_dust", "r6_wind_temp", "r6_temperature", "r3_cold", "r5_cold"):
            out["planet_values"][fid] = raw
        if feat["type"] == "timeseries" and d.get("series"):
            out["series"][fid] = d["series"]
    if not has_ice:
        notes.append(f"SWIM Ci = {ci}（< {mt.spec().get('ice_min_ci', 0.1)}）：R3、R5 不適用，這兩項的目標值全部留空")
    return out, notes


# ---------------------------------------------------------------------------------------------------------------
# 任務定義
# ---------------------------------------------------------------------------------------------------------------
def load_contract(web_seed: Path | None) -> tuple[list, dict, list, str]:
    base = web_seed if web_seed else CONTRACT
    rd = lambda n: yaml.safe_load((base / n).read_text(encoding="utf-8"))  # noqa: E731
    origin = str(web_seed) if web_seed else f"config/web_contract/（main {CONTRACT_COMMIT} 的快照）"
    return rd("tasks_mars.yaml"), rd("categorical_tables.yaml"), rd("data_sources.yaml"), origin


def apply_proposals(tasks, tables, sources):
    tasks, tables, sources = copy.deepcopy(tasks), copy.deepcopy(tables), copy.deepcopy(sources)
    for t in tasks:
        for f in t["features"]:
            p = PROPOSALS["modify"].get(f["id"])
            if p:
                for k, v in p.items():
                    if k == "notes+":
                        f["notes"] = list(f.get("notes") or []) + v
                    else:
                        f[k] = v
        have = {f["id"] for f in t["features"]}
        t["features"] += [copy.deepcopy(f) for f in PROPOSALS["add"].get(t["id"], []) if f["id"] not in have]
    # 岩性對照表：本隊 lithology_mars_to_glim.csv，沒列的 GLiM 類別用預設 0.1（同 features.yaml default_score），水體 0
    lt = config.lithology_table()
    default = float(config.features()["variables"]["lithology"].get("default_score", 0.1))
    glim = ["su", "ss", "sm", "mt", "sc", "pa", "vb", "vi", "va", "pb", "py", "pi", "wb", "ev", "ig"]
    tables["r4_lithology"] = {g: {c: (0.0 if c == "wb" else float(lt[g].get(c, default))) for c in glim} for g in sorted(lt)}
    ids = {s["id"] for s in sources}
    sources += [copy.deepcopy(s) | {"used_by": []} for s in NEW_SOURCES if s["id"] not in ids]
    fids = {f["id"]: f for t in tasks for f in t["features"]}
    for s in sources:
        used = set(s.get("used_by") or [])
        used |= {fid for fid, f in fids.items() if any(r["source_id"] == s["id"] for r in f["planet_data"] + f["earth_data"])}
        s["used_by"] = sorted(i for i in used if not i.startswith("r") or i in fids)   # m* 是月球組的，不動
    return tasks, tables, sources


def feature_index(tasks) -> dict:
    return {f["id"]: f | {"_task": t["id"]} for t in tasks for f in t["features"]}


# ---------------------------------------------------------------------------------------------------------------
# 候選
# ---------------------------------------------------------------------------------------------------------------
def select_candidates(earth: pd.DataFrame) -> pd.DataFrame:
    if not POOL.exists():
        raise SystemExit(f"沒有 {POOL}：先跑 python scripts\\make_mission_tests.py")
    pool = pd.read_csv(POOL)
    chosen = []          # dict(cell_id, lat, lon, reasons)

    def near(la, lo):
        if not chosen:
            return None, 1e9
        d = haversine_km(la, lo, np.array([c["lat"] for c in chosen]), np.array([c["lon"] for c in chosen]))
        j = int(np.argmin(d))
        return j, float(d[j])

    for wid, tid in TARGETS.items():
        cols = sorted([c for c in pool.columns if c.startswith(f"S_{tid}_R")], key=lambda c: c[-2:])
        for col in cols:
            ranked = pool.dropna(subset=[col]).sort_values(col, ascending=False)
            n = 0
            for r in ranked.itertuples():
                if len(chosen) >= MAX_PICKS:
                    break
                j, d = near(r.lat, r.lon)
                reason = f"{tid} {col[-2:]} 第 {n + 1} 名（本隊分數 {getattr(r, col):.2f}）"
                if d < 1:
                    chosen[j]["reasons"].append(reason)
                    n += 1
                elif d >= MIN_SEP_KM:
                    chosen.append({"cell_id": r.cell_id, "lat": r.lat, "lon": r.lon, "reasons": [reason], "known": None})
                    n += 1
                if n >= PER_TEST:
                    break
    ka = config.known_analogs().set_index("site_id")
    cov = earth[["slope_deg", "ati", "lst_mean_c", "roughness_m", "dust_m01"]].notna().sum(axis=1).values
    for sid in KNOWN:
        if sid not in ka.index:
            continue
        k = ka.loc[sid]
        j, d = near(k.lat, k.lon)
        if d <= 50:
            chosen[j]["known"] = sid
            continue
        if len(chosen) >= MAX_CANDIDATES:
            continue
        dd = haversine_km(k.lat, k.lon, earth.lat.values, earth.lon.values)
        ok = np.where(dd <= float(k.radius_km) + 10)[0]
        if not len(ok):
            continue
        best = ok[np.lexsort((dd[ok], -cov[ok]))[0]]
        chosen.append({"cell_id": earth.cell_id.iloc[best], "lat": round(float(earth.lat.iloc[best]), 2),
                       "lon": round(float(earth.lon.iloc[best]), 2), "reasons": ["已知類比地（對照用）"], "known": sid})
    out = pd.DataFrame(chosen)
    out["place"] = place_name(out.lat.values, out.lon.values)
    return out


def _ll(lat, lon) -> str:
    return f"{abs(lat):.1f}°{'N' if lat >= 0 else 'S'} {abs(lon):.1f}°{'E' if lon >= 0 else 'W'}"


def _names(row, ka):
    if isinstance(row["known"], str):
        n = str(ka.loc[row["known"], "name"])
        return n, n
    ll = _ll(row["lat"], row["lon"])
    if row["lat"] < SOUTH_FILL:
        return f"南極 {ll}", f"Antarctica {ll}"
    p = row["place"] or ""
    if p.startswith("near "):
        town = p[5:]
        return f"{town} 附近", p
    if " km from " in p:
        d, town = p.split(" km from ", 1)
        if float(d) <= 300:
            return f"距 {town} {d} km", p
        return f"{ll}（最近城鎮 {town}，{d} km）", f"{ll} ({p})"
    return ll, ll


def candidate_records(sel: pd.DataFrame, earth: pd.DataFrame, feature_ids) -> list[dict]:
    ka = config.known_analogs().set_index("site_id")
    e = earth.set_index("cell_id")
    recs = []
    for _, r in sel.iterrows():
        row = e.loc[r.cell_id]
        zh, en = _names(r, ka)
        m = earth_measurements(row, feature_ids)
        recs.append({"id": f"hf-{r.cell_id}", "name": zh, "name_en": en, "lat": round(float(r.lat), 3),
                     "lon": round(float(r.lon), 3), "known_analog": isinstance(r.known, str), "is_placeholder": False, **m})
    return recs


# ---------------------------------------------------------------------------------------------------------------
# 合併、母體、說明
# ---------------------------------------------------------------------------------------------------------------
def merge(web_seed: Path, cands: list, targets: dict, mars_feature_ids: set) -> tuple[list, dict]:
    old = json.loads((web_seed / "earth_candidates.demo.json").read_text(encoding="utf-8"))
    keep = []
    for c in old:
        if c["id"].startswith("hf-"):
            continue
        if c.get("is_placeholder"):
            for k in ("values", "categories", "spectra", "series", "planet_values"):
                c[k] = {fid: v for fid, v in (c.get(k) or {}).items() if fid not in mars_feature_ids and not fid.startswith("r")}
        keep.append(c)
    tv = yaml.safe_load((web_seed / "target_values.demo.yaml").read_text(encoding="utf-8"))
    tv.update(targets)
    return keep + cands, tv


def population() -> dict:
    ref = json.loads((PROCESSED / "earth_reference_pct.json").read_text(encoding="utf-8"))
    out = {"reference": ref["reference"], "area_weight": ref["area_weight"],
           "note": "每個特徵的地球全球分位數（等機率間隔）。percentile(value, quantiles) 即全球百分位；np.std(quantiles) ≈ 全球標準差。",
           "features": {}}
    for fid, var in POPULATION_VAR.items():
        v = ref["variables"].get(var)
        if v:
            out["features"][fid] = {"variable": var, "quantiles": [_num(q, 5) for q in v["quantiles"]], "n": v["n"],
                                    "area_weighted_mean": _num(v["area_weighted_mean"]),
                                    "area_weighted_std": _num(v["area_weighted_std"])}
    return out


def _dump_yaml(obj, path: Path):
    path.write_text(yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def _md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in df.itertuples(index=False):
        lines.append("| " + " | ".join("" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v) for v in r) + " |")
    return "\n".join(lines)


def report(origin, variants, sel, notes, check_text) -> str:
    cur_f, prop_f = variants["current"]["features"], variants["proposed"]["features"]
    rows = []
    for fid in sorted(set(cur_f) | set(prop_f), key=lambda x: (x[:2], x)):
        c, p = cur_f.get(fid), prop_f.get(fid)
        f = p or c
        e = EARTH.get(fid)
        earth = "—" if e is None else e.get("col") or e.get("category") or {"dust": "dust_m01…12 序列", "day_night": "夜溫、日溫兩點序列"}[e["series"]]
        mode_c = f"{c['type']} / {c['compare_mode']}" if c else "（新增）"
        mode_p = f"{p['type']} / {p['compare_mode']}" if p else ""
        status_c = "有值" if c and _filled(variants["current"], fid) else ("沒有資料" if c else "")
        status_p = "有值" if p and _filled(variants["proposed"], fid) else ("沒有資料" if p else "")
        rows.append({"任務": f["_task"], "特徵 id": fid, "名稱": f["name"], "地球欄位": earth,
                     "現在的定義": mode_c, "現在": status_c, "建議的定義": mode_p if mode_p != mode_c else "同左",
                     "建議後": status_p})
    feat_tab = _md_table(pd.DataFrame(rows))
    ctab = sel[["cell_id", "lat", "lon", "place", "known", "reasons"]].copy()
    ctab["id"] = "hf-" + ctab.cell_id
    ctab["lat"] = ctab.lat.map(lambda x: f"{x:.2f}")
    ctab["lon"] = ctab.lon.map(lambda x: f"{x:.2f}")
    ctab["reasons"] = ctab.reasons.map(lambda x: "；".join(x))
    ctab["known"] = ctab.known.map(lambda x: x if isinstance(x, str) else "")
    ctab = ctab[["id", "lat", "lon", "place", "known", "reasons"]]
    note_lines = "\n".join(f"- `{k}`：" + "；".join(v) for k, v in notes.items() if v) or "- （無）"
    return f"""# 給網頁整合的資料（export_web_seed.py 產生）

契約來源：{origin}。產生時間：{time.strftime('%Y-%m-%d %H:%M')}。

## 1. 交什麼

| 檔案 | 放到網頁的哪裡 | 內容 |
|---|---|---|
| `current/merged/earth_candidates.demo.json` | `data/seed/earth_candidates.demo.json` | 月球 placeholder 候選（火星特徵值已移除）＋本隊 {len(sel)} 個火星用的地球候選（真實資料） |
| `current/merged/target_values.demo.yaml` | `data/seed/target_values.demo.yaml` | mars-ap105、mars-jezero、mars-gale 換成真實值，其他目標維持 placeholder |
| `proposed/`（同上兩檔＋`tasks_mars.yaml`、`categorical_tables.yaml`、`data_sources.yaml`） | `data/seed/` | 套用第 3 節建議後的版本：R1–R6 除了 R2 都能評分 |
| `earth_population.json` | 需要網頁改一行程式才會用到（第 4 節） | 每個特徵的地球全球分位數 |

`current/` 不用改網頁任何程式或定義，直接替換兩個檔就能跑；`proposed/` 需要整合者同意改任務定義。
沒有 `merged/` 資料夾時表示沒給 `--web-seed`，只有本隊的部分（`earth_candidates.mars.json`、`target_values.mars.yaml`），要手動併進去。

## 2. 特徵對照

{feat_tab}

「沒有資料」的特徵在網頁會顯示缺值，不會補數字。現在的定義下只有 R1（100 m 坡度、熱慣量）和 R6（沙塵、日夜溫差）評得出分數：
R3 地下冰、R5 粗糙度是 relative_rank，要火星百分位，本隊只有原始值（SWIM Ci、HRSC 粗糙度），所以目標值留空、原始值放 `planet_values`。

目標的補充說明：
{note_lines}

## 3. 建議整合者改的地方（proposed/）

1. `r3_ground_ice` 改成門檻型（永凍土比例 0.1 → 0、0.9 → 1），`r5_roughness` 改 absolute（兩邊同為 200 m 尺度、單位公尺）。
2. 新增本隊已經有資料的特徵：R1 無植被、不是冰面；R3 年均溫 < 0 °C、乾燥程度；R4 岩性大類（附對照表）、岩石裸露；
   R5 永凍土、年均溫；R6 年均地表溫。規則和本隊 `config/mission_tests.yaml` 相同。
3. R3、R5 只對有地下冰的目標評分（SWIM Ci ≥ 0.1）：網頁沒有「不適用」機制，所以 Jezero、Gale 的 R3／R5 目標值全部留空，這兩項會是「無法覆蓋」。
4. `data_sources.yaml` 新增 GMTED2010、HRSC＋MOLA、GLiM、SIM 3292、Global Aridity Index、TES 熱慣量。
5. SkyFall 另外四區（Deuteronilus、Utopia、Phlegra、Erebus）在 `target_sites.yaml` 還沒有座標：給座標後火星組可以用同一套程式抽值。

## 4. 網頁評分程式要注意的事（需要整合者決定）

1. **百分位母體**：網頁用「候選清單本身」算百分位與標準差（`services/similarity/app/engine.py` 的 `populations`）。
   候選只有幾十個、而且都是挑過的寒冷乾燥地點，在裡面排百分位和「在地球上排第幾」差很多。本隊的百分位是全球無冰陸地
   （0.1° 格、cos 緯度加權）。建議 measurements 服務多回傳 `earth_population.json`，`populations[fid]` 有全球分位數時優先用它。
   下面的檢查表把兩種母體並排（「全球分位數」那列就是只改這一行的結果）。
2. **候選數量**：邊際效益曲線與敏感度分析用窮舉組合（`fixed_k_options`，C(n, k)，k 到 6）。月球 20 個＋火星 {len(sel)} 個 =
   {20 + len(sel)} 個候選時 C({20 + len(sel)}, 6) ≈ {math.comb(20 + len(sel), 6):,} 種組合，會跑很久或記憶體不夠。建議二選一：
   (a) 算分前只留「這個任務有任何特徵值」的候選（月球、火星各自 20 多個）；(b) 固定 k 的最大覆蓋改用 PuLP（程式裡已經有）。
   (a) 也順便讓火星結果不會因為月球 placeholder 候選而一直顯示 placeholder 警告。
3. **時間序列**：r6_dust 的 phase 是「當地季節」（太陽黃經 / 360），地球每月一點、火星每 15° Ls 一點；r6_wind_temp 地球只有日、夜兩點。

{check_text}
## 5. 怎麼重跑

```
python scripts\\make_mission_tests.py --no-figures
python scripts\\export_web_seed.py --web-seed ..\\..\\nasa-main\\data\\seed --check
```

候選清單（{len(sel)} 個；每個（目標 × 測試）取本隊分數前 {PER_TEST} 名、彼此至少相隔 {MIN_SEP_KM} km，再補已知類比地，上限 {MAX_CANDIDATES}）。
候選是用目前的 outputs/mission_tests/candidate_pool.csv 挑的：本機重跑（水體遮罩、ndvi_p90、ASTER）之後要再跑一次這支程式：

{_md_table(ctab)}
"""


def _filled(variant, fid) -> bool:
    for t in variant["targets"].values():
        if fid in t["values"] or fid in t["categories"]:
            return True
    return False


# ---------------------------------------------------------------------------------------------------------------
# 用網頁自己的評分程式檢查
# ---------------------------------------------------------------------------------------------------------------
POP_LINE = ("populations={f['id']:[v for c in baseline if (v:=measurement(c,f)) is not None] "
            "for t in tasks for f in t['features'] if f['type'] not in ['categorical','spectral']}")


def _global_pop_engine(engine, pop: dict):
    """網頁 engine.calculate 的複本，只多一行：有全球分位數的特徵改用它當百分位母體（第 4 節第 1 點的建議）。"""
    import inspect
    import types
    src = inspect.getsource(engine)
    if POP_LINE not in src:
        return None
    mod = types.ModuleType("services.similarity.app._engine_global_population")
    mod.__package__ = "services.similarity.app"
    mod.GLOBAL_POPULATION = {fid: d["quantiles"] for fid, d in pop["features"].items()}
    patched = src.replace(POP_LINE, POP_LINE + "\n    populations.update({k:v for k,v in GLOBAL_POPULATION.items() if k in populations})")
    exec(compile(patched, mod.__name__, "exec"), mod.__dict__)  # noqa: S102
    return mod


def check_with_web(web_seed: Path, variant_dir: Path, label: str, pop: dict) -> str:
    web_root = web_seed.resolve().parents[1]
    tmp = Path(tempfile.mkdtemp(prefix="websd_"))
    try:
        shutil.copytree(web_seed, tmp / "seed")
        for p in (variant_dir / "merged").glob("*"):
            shutil.copy(p, tmp / "seed" / p.name)
        for n in ("tasks_mars.yaml", "categorical_tables.yaml", "data_sources.yaml"):
            if (variant_dir / n).exists():
                shutil.copy(variant_dir / n, tmp / "seed" / n)
        os.environ["DATA_DIR"] = str(tmp)
        if str(web_root) not in sys.path:
            sys.path.insert(0, str(web_root))
        for k in [k for k in sys.modules if k.startswith("services")]:
            del sys.modules[k]
        from services.catalog.app.repository import FileRepository
        from services.measurements.app.repository import MeasurementRepository
        from services.shared.contracts import Bundle, ScoreRequest
        from services.similarity.app import engine
        from services.planning.app import engine as plan
        cat = FileRepository(tmp)
        meas = MeasurementRepository()
        b = Bundle(mission=cat.mission("mars"), tasks=cat.tasks("mars"), sites=cat.sites("mars"),
                   limits=cat.limits["mars"], constraints=cat.constraints["mars"], settings=cat.settings,
                   categorical_tables=cat.tables).model_dump()
        mars_ids = {f["id"] for t in b["tasks"] for f in t["features"]}
        own = [c for c in meas.candidates if any(fid in mars_ids for k in ("values", "categories", "series") for fid in c[k])]
        repo = type("R", (), {"candidates": own, "targets": meas.targets})()
        names = {c["id"]: c["name"] for c in own}
        gp = _global_pop_engine(engine, pop)
        task_ids = [t["id"] for t in b["tasks"]]
        tau = b["settings"].get("tau", 0.7)
        lines = [f"### 網頁程式檢查：{label}", "",
                 f"契約驗證通過（catalog、measurements 的 pydantic 模型）。合併後候選 {len(meas.candidates)} 個，"
                 f"其中 {len(own)} 個有火星特徵值；下面只用這 {len(own)} 個（等同第 4 節第 2 點 (a)）。τ = {tau}。", ""]
        full = engine.calculate(ScoreRequest(mission="mars", site_id=next(iter(TARGETS)), task_ids=task_ids), b, meas)
        for wid in TARGETS:
            req = ScoreRequest(mission="mars", site_id=wid, task_ids=task_ids)
            lines.append(f"**{wid}**")
            lines.append("")
            lines.append("| 百分位母體 | 前三名（總分） | 各任務最高分 | 最少地點 | 無法覆蓋 |")
            lines.append("|---|---|---|---|---|")
            for tag, eng in (("候選本身（網頁現在）", engine), ("全球分位數（建議）", gp)):
                if eng is None:
                    lines.append(f"| {tag} | 網頁程式和預期不同，沒有跑 | | | |")
                    continue
                res = eng.calculate(req, b, repo)
                top = "、".join(f"{c['name']}（{c['overall']:.2f}）" for c in res["candidates"][:3])
                best = ", ".join(f"{tid} {max([c['tasks'][tid]['score'] for c in res['candidates'] if c['tasks'][tid]['score'] is not None], default=float('nan')):.2f}".replace('nan', '—')
                                 for tid in task_ids)
                opt = plan.optimize(res, b)
                sel = "、".join(names.get(i, i) for i in opt["selected"]) or "—"
                lines.append(f"| {tag} | {top} | {best} | {opt['minimum_sites']}：{sel} | {', '.join(sorted(opt['uncoverable'])) or '無'} |")
            lines.append("")
        n = len(meas.candidates)
        k = min(n, len(task_ids))
        lines += [f"用全部 {n} 個候選時 `uses_placeholder` = {str(full.get('uses_placeholder')).lower()}（月球 placeholder 候選造成）；"
                  f"邊際效益曲線要窮舉 C({n}, {k}) = {math.comb(n, k):,} 種組合，這裡沒有跑。", ""]
        return "\n".join(lines) + "\n"
    except Exception as err:  # noqa: BLE001
        return (f"### 網頁程式檢查：{label}\n\n沒有跑成：{type(err).__name__}: {err}\n"
                "（需要 pulp 與 CBC、pydantic、scipy、httpx；網頁 repo 的路徑由 --web-seed 推出）\n\n")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        os.environ.pop("DATA_DIR", None)


# ---------------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--web-seed", type=Path, help="網頁 repo 的 data/seed（main 分支）；給了才會輸出合併檔")
    ap.add_argument("--check", action="store_true", help="用網頁的評分程式跑一次（需要 --web-seed）")
    args = ap.parse_args()
    web_seed = args.web_seed.resolve() if args.web_seed else None

    tasks, tables, sources, origin = load_contract(web_seed)
    earth = earth_frame()
    sel = select_candidates(earth)
    print(f"候選 {len(sel)} 個")

    variants = {}
    notes = {}
    for name in ("current", "proposed"):
        t, tb, src = (tasks, tables, sources) if name == "current" else apply_proposals(tasks, tables, sources)
        feats = feature_index(t)
        cands = candidate_records(sel, earth, list(feats))
        targets = {}
        for wid, tid in TARGETS.items():
            targets[wid], n = mars_measurements(tid, feats)
            if name == "proposed":
                notes[wid] = n
        d = OUT / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "earth_candidates.mars.json").write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
        _dump_yaml(targets, d / "target_values.mars.yaml")
        if name == "proposed":
            clean = [{**x, "features": [{k: v for k, v in f.items() if not k.startswith("_")} for f in x["features"]]} for x in t]
            _dump_yaml(clean, d / "tasks_mars.yaml")
            _dump_yaml(tb, d / "categorical_tables.yaml")
            _dump_yaml(src, d / "data_sources.yaml")
        if web_seed:
            mc, mtv = merge(web_seed, cands, targets, set(feats))
            (d / "merged").mkdir(exist_ok=True)
            (d / "merged" / "earth_candidates.demo.json").write_text(json.dumps(mc, ensure_ascii=False, indent=1), encoding="utf-8")
            _dump_yaml(mtv, d / "merged" / "target_values.demo.yaml")
        variants[name] = {"features": feats, "targets": targets}
        print(f"{name}: {d}")

    pop = population()
    (OUT / "earth_population.json").write_text(json.dumps(pop, ensure_ascii=False, indent=1), encoding="utf-8")
    check_text = ""
    if args.check and web_seed:
        check_text = check_with_web(web_seed, OUT / "current", "current（網頁現在的定義）", pop) + \
            check_with_web(web_seed, OUT / "proposed", "proposed（套用本隊建議）", pop)
        print(check_text)
    (OUT / "WEB_EXPORT.md").write_text(report(origin, variants, sel, notes, check_text), encoding="utf-8")
    print("寫出", OUT / "WEB_EXPORT.md")


if __name__ == "__main__":
    main()
