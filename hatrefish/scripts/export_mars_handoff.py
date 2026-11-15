"""火星端交給網站（Harris）的交接檔 → outputs/mars_handoff/

格式仿照 nasa-main 月球端的交接檔（data/lunar/handoff-source/moon_results.json、moon_global_grid.json），
讓網站可以照 scripts/import_lunar_handoff.py 的做法寫一支 import_mars_handoff.py。
網站只要「選」預先算好的排名，不需要重算分數。

兩個步驟：
  1. 預設：只讀現有輸出（outputs/mission_tests、outputs/profiles、outputs/set_cover、outputs/validation），
     組成 mars_results.json。不重算，只要標準函式庫＋pyyaml，幾秒鐘。
  2. --grid：重算全球分數（需要 pandas、pyarrow 和 mars_analog），每個目標約 1–3 分鐘。
     產生 1° 全球格（給地圖）和每項測試「最不像」的 3 個地點。結果先存在 outputs/mars_handoff/_work/，
     中斷可以續跑；算完會自動再組一次 mars_results.json 和 mars_global_grid.json。

用法：
  python scripts/export_mars_handoff.py                 # 組 mars_results.json（有 _work 就一起併入）
  python scripts/export_mars_handoff.py --grid          # 算全部目標的全球格，再組檔
  python scripts/export_mars_handoff.py --grid --target jezero   # 只算一個目標（可分次跑）
  python scripts/export_mars_handoff.py --check         # 檢查輸出（JSON 合法、分數可從特徵重算）
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "mars_handoff"
WORK = OUT / "_work"
MT = ROOT / "outputs" / "mission_tests"
PR = ROOT / "outputs" / "profiles"
SET_COVER = ROOT / "outputs" / "set_cover" / "set_cover.json"
VALIDATION = ROOT / "outputs" / "validation" / "validation.json"
TARGETS_JSON = ROOT / "data" / "processed" / "mars_targets.json"
KNOWN_CSV = ROOT / "data" / "labels" / "known_analogs.csv"
SPEC_YAML = ROOT / "config" / "mission_tests.yaml"
FEATURES_YAML = ROOT / "config" / "features.yaml"
DIMENSIONS_YAML = ROOT / "config" / "dimensions.yaml"

TZ = timezone(timedelta(hours=8))
VERSION = "mars-handoff-v1"
TARGET_ORDER = ["jezero", "gale", "arcadia", "oxia", "meridiani", "protonilus", "ap105"]
TEST_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6"]
SIMILAR, DIFFERENT = 0.6, 0.3          # 和月球端相同的分類門檻
N_NEW = 10                             # 每個目標 × 測試的新候選地數
N_BEST = 3                             # mars_sites 裡的 best_earth_analogs_by_task
N_LEAST = 3                            # 最不像的地點數（只有 --grid 才有）
N_PROFILE = 10                         # 類比剖面整體排名
N_DIM = 5                              # 每個面向的排名


def site_id(t: str) -> str:
    """網站用的火星地點 id（沿用網站原本的 mars-jezero、mars-gale、mars-ap105）。"""
    return f"mars-{t}"


def rnd(x, nd=3):
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    if isinstance(x, int):
        return x
    try:
        x = float(x)
    except (TypeError, ValueError):
        return x
    return round(x, nd) if math.isfinite(x) else None


def finite(o):
    """把 NaN / inf 換成 null，確保輸出是嚴格 JSON。"""
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: finite(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [finite(v) for v in o]
    return o


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def dump_json(p: Path, obj, indent=1):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(finite(obj), ensure_ascii=False, indent=indent, allow_nan=False), encoding="utf-8")


def classify(s):
    if s is None:
        return None
    return "similar" if s >= SIMILAR else ("different" if s < DIFFERENT else "partial")


# ---------------- 輸入 ----------------
def spec() -> dict:
    return yaml.safe_load(SPEC_YAML.read_text(encoding="utf-8"))


def features_spec() -> dict:
    return yaml.safe_load(FEATURES_YAML.read_text(encoding="utf-8"))


def mars_targets() -> dict:
    return load_json(TARGETS_JSON)["targets"]


def known_sites() -> dict:
    with KNOWN_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for r in rows:
        out[r["site_id"]] = {"site_id": r["site_id"], "name_en": r["name"], "lat": rnd(r["lat"], 3), "lon": rnd(r["lon"], 3),
                             "radius_km": rnd(r["radius_km"], 1), "analog_for": r.get("analog_for"),
                             "mars_target_ids": [x.strip() for x in (r.get("mars_target_ids") or "").split(";") if x.strip()],
                             "missions": [x.strip() for x in (r.get("missions") or "").split(";") if x.strip()],
                             "reference_url": r.get("reference_url")}
    return out


def targets_present() -> list[str]:
    return [t for t in TARGET_ORDER if (MT / f"{t}_tests.json").exists()]


# ---------------- 公式說明 ----------------
def similarity_formula(var: str, fs: dict) -> str:
    v = fs["variables"].get(var, {})
    c = v.get("compare")
    if c == "gaussian":
        sig = v.get("sigma")
        sig = "0.5 x Earth land standard deviation" if sig == "auto" else f"{sig} {v.get('unit', '')}".strip()
        return f"s = exp(-(x_earth - x_mars)^2 / (2 sigma^2)), sigma = {sig}"
    if c == "abs_pct_diff":
        return "s = 1 - |p_earth - p_mars|, p = percentile on its own planet (area-weighted)"
    if c == "earth_extreme_pct":
        return "s = Earth percentile of extremeness (colder / drier = closer to 1); target-independent"
    if c == "lookup":
        return "s = lookup table Mars geologic unit group -> Earth GLiM rock class (default 0.1)"
    if c == "abs_prob_diff":
        return "s = 1 - |permafrost_fraction_earth - clip(SWIM Ci, 0, 1)|"
    if c == "ndvi_linear":
        return f"s = clip(1 - NDVI / {v.get('ndvi_max', 0.3)}, 0, 1)"
    return f"similarity ({c})"


def feature_formula(f: dict, fs: dict) -> str:
    k = f["kind"]
    if k == "similarity":
        return similarity_formula(f["var"], fs)
    if k == "threshold":
        if f["rule"] == "smaller_is_better":
            return f"D({f['column']}): x <= {f['full_at']} -> 1, x >= {f['zero_at']} -> 0, linear between"
        return f"D({f['column']}): x <= {f['zero_at']} -> 0, x >= {f['full_at']} -> 1, linear between"
    if k == "mars_rank_threshold":
        return (f"Mars threshold {f['mars_zero_at']} -> {f['mars_full_at']} converted to Mars percentiles; "
                f"Earth percentile of {f['column']} scored larger_is_better between them")
    if k == "seasonal_shape":
        return "s = (1 + r) / 2, r = correlation of Earth 12-month curve with Mars Ls curve aligned by local season"
    if k == "seasonal_amplitude":
        return "s = exp(-(ln(A_earth / A_mars))^2 / (2 (ln 2)^2)), A = (max - min) / mean of the seasonal curve"
    if k == "seasonal_range_ratio":
        return "s = exp(-(ln(R_earth / R_mars))^2 / (2 (ln 2)^2)), R = warmest minus coldest month (K)"
    if k == "index_rank":
        return (f"D(percentile of the ASTER Ninomiya index within the same annual-LST band): "
                f"{f.get('zero_at')} -> 0, {f.get('full_at')} -> 1")
    return k


def tasks_block(sp: dict, fs: dict) -> dict:
    out = {}
    for tid in TEST_ORDER:
        t = sp["tests"][tid]
        out[tid] = {
            "name": t.get("name_en"), "name_zh": t.get("name_zh"), "goal_zh": t.get("goal"), "basis_zh": t.get("basis"),
            "weight_roc": sp["test_weights"]["roc"].get(tid),
            "applies": t.get("applies", "all"),
            "applies_rule": ("all Mars targets" if t.get("applies", "all") == "all"
                             else f"only Mars targets with SWIM Ci >= {sp['ice_min_ci']}"),
            "depends_on_mars_site": True,
            "status": t.get("status", "scored"),
            "reason_zh": t.get("reason"),
            "dimensions": t.get("dimensions"),
            "features": [{
                "id": f["id"], "kind": f["kind"], "w": float(f.get("weight", 1.0)), "c": 1.0,
                "required": bool(f.get("required", True)), "unit": f.get("unit"),
                "formula": feature_formula(f, fs),
                "mars_requirement_zh": f.get("mars_requirement"), "mars_data": f.get("mars_data"),
                "earth_data": f.get("earth_data"), "note_zh": f.get("note"),
                "fill": f.get("fill"), "when_available": bool(f.get("when_available", False)),
            } for f in t.get("features", [])],
            "not_evaluated_zh": t.get("not_evaluated", []),
        }
    return out


# ---------------- 候選地紀錄 ----------------
def candidate(rec: dict, tid: str, t: str, known: dict, group: str, rank: int, test_feats: list[str]) -> dict:
    feats = []
    vals = rec.get("values") or {}
    for fid in test_feats:
        s = (rec.get("features") or {}).get(fid)
        v = vals.get(fid) or {}
        feats.append({"feature": fid, "value": v.get("earth"), "mars_value": v.get("mars"), "unit": v.get("unit"),
                      "s": rnd(s), "w": 1.0, "c": 1.0, "classification": classify(s)})
    near = rec.get("nearest_known")
    is_known = bool(rec.get("known_analog"))
    return {
        "id": f"{site_id(t)}:{tid}:{rec.get('cell_id')}",
        "rank": rank, "rank_including_known": rec.get("rank"),
        "group": group,
        "cell_id": rec.get("cell_id"), "lat": rec.get("lat"), "lon": rec.get("lon"),
        "name_en": rec.get("name"), "name_zh": None,
        "score": rnd((rec.get("score") or 0) * 100, 1) if rec.get("score") is not None else None,
        "known_analog_region": (known.get(near, {}).get("name_en") if (is_known and near) else None),
        "nearest_known_analog": ({"site_id": near, "name_en": known.get(near, {}).get("name_en"),
                                  "distance_km": rec.get("nearest_known_km")} if near else None),
        "features": feats,
        "available_features": sum(1 for f in feats if f["s"] is not None),
        "total_features": len(feats),
        "weakest_feature": rec.get("weakest_feature"),
        "breaks": rec.get("breaks", []),
        "dimension_scores": rec.get("dimension_scores"),
        "profile_overall": rec.get("profile_overall"),
        "worldview_url": rec.get("worldview_url"),
        "notes": None,
    }


def scored_features(status: dict, tid: str) -> list[str]:
    return [fid for fid, st in (status.get(tid, {}).get("features") or {}).items() if st == "scored"]


def known_validation(res: dict, tid: str, known: dict, sp: dict) -> list[dict]:
    missions = {m for m, ts in sp["mission_to_tests"].items() if tid in ts}
    out = []
    for k in res.get("known_analogs", []):
        v = (k.get("tests") or {}).get(tid)
        if not v:
            continue
        ks = known.get(k["site_id"], {})
        out.append({"site_id": k["site_id"], "name_en": k.get("name"), "lat": ks.get("lat"), "lon": ks.get("lon"),
                    "missions": k.get("missions"), "tagged_for_this_test": bool(missions & set(k.get("missions") or [])),
                    "score": rnd(v["score"] * 100, 1) if v.get("score") is not None else None,
                    "global_top_pct": v.get("global_top_pct"),
                    "score_basis": "median over the site's 0.1-deg cells (radius from known_analogs.csv)",
                    "group": "known_analog_validation", "features": []})
    out.sort(key=lambda r: (r["global_top_pct"] is None, r["global_top_pct"] if r["global_top_pct"] is not None else 0))
    for i, r in enumerate(out):
        r["rank"] = i + 1
    return out


# ---------------- 類比剖面 ----------------
def profile_record(r: dict, known: dict, rank: int) -> dict:
    near = r.get("nearest_known")
    return {"rank": rank, "cell_id": r.get("cell_id"), "lat": r.get("lat"), "lon": r.get("lon"),
            "name_en": r.get("name"), "score": r.get("overall"),
            "known_analog_region": known.get(near, {}).get("name_en") if (r.get("known_analog") and near) else None,
            "nearest_known_analog": ({"site_id": near, "distance_km": r.get("nearest_known_km")} if near else None),
            "confidence": r.get("confidence"), "variable_coverage": r.get("variable_coverage"),
            "dimension_scores": {k: v for k, v in (r.get("dimension_scores") or {}).items() if v is not None},
            "strongest_dimension": r.get("strongest_dimension"), "weakest_dimension": r.get("weakest_dimension"),
            "variable_scores": r.get("variable_scores"), "earth_values": r.get("earth_values"),
            "breaks": r.get("breaks", []), "worldview_url": r.get("worldview_url")}


def profile_block(t: str, known: dict) -> dict | None:
    p = PR / f"mars_{t}_profile.json"
    if not p.exists():
        return None
    d = load_json(p)
    return {
        "method": d.get("method"), "generated_at": d.get("generated_at"),
        "dimensions": {k: v for k, v in d["dimensions"].items() if k not in d.get("not_evaluated", [])},
        "not_evaluated": d.get("not_evaluated", []),
        "scoring": d.get("scoring"), "strong_share": d.get("strong_share"),
        "overall_top": [profile_record(r, known, i + 1) for i, r in enumerate(d["top_overall"][:N_PROFILE])],
        "by_dimension": {k: [profile_record(r, known, i + 1) for i, r in enumerate(v[:N_DIM])]
                         for k, v in d["top_by_dimension"].items()},
        "known_analogs": [{"site_id": k["site_id"], "name_en": k.get("name"), "lat": k.get("lat"), "lon": k.get("lon"),
                           "tagged_for_this_target": k.get("tagged_for_this_target"), "missions": k.get("missions"),
                           "score": k.get("overall"), "global_top_pct": k.get("global_top_pct"),
                           "dimension_scores": {a: b for a, b in (k.get("dimension_scores") or {}).items() if b is not None},
                           "strongest_dimension": k.get("strongest_dimension"),
                           "weakest_dimension": k.get("weakest_dimension")} for k in d.get("known_analogs", [])],
    }


# ---------------- 火星地點 ----------------
def mars_site(t: str, tg: dict, res: dict, sp: dict, rankings: dict) -> dict:
    f = tg.get("features", {})
    values = {}
    for var, x in f.items():
        if var.endswith("_fine"):
            continue
        values[var] = {k: x.get(k) for k in ("value", "pct", "unit", "source", "group", "unit_desc", "coverage") if k in x}
    lith = f.get("lithology") or {}
    ice_t = res.get("ice_target")
    status = {tid: res["status"].get(tid, {}).get("status") for tid in TEST_ORDER}
    best = {}
    for tid in TEST_ORDER:
        grp = rankings.get(tid, {}).get(site_id(t))
        if grp:
            best[tid] = [{"name_en": c["name_en"], "lat": c["lat"], "lon": c["lon"], "score": c["score"]}
                         for c in grp["new_candidates"][:N_BEST]]
    return {
        "id": site_id(t), "target_id": t, "name": tg.get("name"), "lat": tg.get("lat"), "lon": tg.get("lon"),
        "radius_km": tg.get("radius_km"), "missions": tg.get("missions"), "source": tg.get("source"),
        "lithology_group": lith.get("group"), "lithology_unit": lith.get("value"),
        "ice_ci": (f.get("ice") or {}).get("value"), "ice_target": ice_t,
        "has_ice": (ice_t is not None and ice_t >= sp["ice_min_ci"]),
        "test_status": status,
        "scored_tests": [k for k, v in status.items() if v == "scored"],
        "values": values,
        "best_earth_analogs_by_task": best,
    }


# ---------------- 驗證與集合覆蓋 ----------------
def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def validation_block() -> dict | None:
    if not VALIDATION.exists():
        return None
    v = load_json(VALIDATION)
    per, best_all, overall_all, neg_all, stab_all = {}, [], [], [], []
    for e in v:
        t = e["target"]
        known = [k for k in e.get("known", []) if k.get("best_dim_pct") is not None]
        best_all += [k["best_dim_pct"] for k in known]
        overall_all += [k["overall_pct"] for k in known if k.get("overall_pct") is not None]
        neg = e.get("negative", [])
        neg_all += [n.get("pct") for n in neg]
        stab = (e.get("robust") or {}).get("stability", [])
        stab_all += [s.get("stability") for s in stab[:N_PROFILE]]
        per[site_id(t)] = {
            "pool_cells": e.get("pool_cells"),
            "known_recovery": [{"site_id": k["site_id"], "name_en": k.get("name"), "dimensions": k.get("dims"),
                                "best_dimension_top_pct": rnd(k.get("best_dim_pct"), 1),
                                "overall_top_pct": rnd(k.get("overall_pct"), 1)} for k in known],
            "negative_controls": [{"name_en": n.get("name"), "lat": n.get("lat"), "lon": n.get("lon"),
                                   "score": n.get("overall"), "global_top_pct": rnd(n.get("pct"), 1)} for n in neg],
            "top_site_stability": [{"rank": s.get("rank"), "lat": s.get("lat"), "lon": s.get("lon"), "name_en": s.get("name"),
                                    "score": s.get("overall"), "stability": rnd(s.get("stability"), 2),
                                    "by_family": {a: rnd(b, 2) for a, b in (s.get("by_family") or {}).items()}}
                                   for s in stab[:N_PROFILE]],
            "region_enrichment": e.get("region"),
        }
    def share(xs, thr):
        xs = [x for x in xs if x is not None]
        return rnd(sum(1 for x in xs if x <= thr) / len(xs), 3) if xs else None
    return {
        "what": "known Earth analogs recovered by the dimension they are known for; negative controls; ranking stability",
        "details": "outputs/validation/VALIDATION.md",
        "summary": {
            "known_pairs": len(best_all),
            "median_best_dimension_top_pct": rnd(median(best_all), 1),
            "median_overall_top_pct": rnd(median(overall_all), 1),
            "share_in_top10pct": share(best_all, 10), "share_in_top25pct": share(best_all, 25),
            "negative_controls": len(neg_all),
            "negatives_in_top25pct": sum(1 for x in neg_all if x is not None and x <= 25),
            "top10_sites_stability_ge_0.8": f"{sum(1 for x in stab_all if x is not None and x >= 0.8)}/{len(stab_all)}",
            "percent_note": "top x% = share of the global pool that scores higher (smaller is better)",
        },
        "per_target": per,
    }


def set_cover_block() -> dict | None:
    if not SET_COVER.exists():
        return None
    s = load_json(SET_COVER)
    a = s.get("all", {})
    return {
        "what": "fewest Earth sites that together cover every (Mars target x test) requirement",
        "rule": s.get("rule"), "rule_zh": s.get("rule_zh"), "n_requirements": s.get("n_req"),
        "requirements": s.get("requirements"), "best_scores": s.get("best_scores"),
        "k_star": a.get("k_star"), "uncoverable": a.get("uncoverable"), "weak": a.get("weak"),
        "sites": a.get("sites"), "marginal_curve": a.get("curve"),
        "per_target": s.get("per_target"), "sensitivity": s.get("sensitivity"),
        "target_id_to_site_id": {t: site_id(t) for t in TARGET_ORDER},
    }


def data_sources(sp: dict, tg: dict) -> dict:
    earth, mars = set(), set()
    for t in sp["tests"].values():
        for f in t.get("features", []):
            for key, bag in (("earth_data", earth), ("mars_data", mars)):
                x = f.get(key)
                if x and x != "—":
                    bag.add(str(x))
    msrc = set()
    for x in tg.values():
        for var, v in (x.get("features") or {}).items():
            if v.get("source") and not var.endswith("_fine"):
                msrc.add(v["source"])
    return {"earth_datasets": sorted(earth), "mars_datasets": sorted(mars), "mars_target_value_sources": sorted(msrc),
            "full_citations": "docs/DATA_SOURCES.md"}


# ---------------- 組 mars_results.json ----------------
def build_results() -> dict:
    sp, fs = spec(), features_spec()
    tg_all = mars_targets()
    known = known_sites()
    eps = sp["eps"]
    targets = targets_present()
    rankings: dict = {tid: {} for tid in TEST_ORDER}
    results = {}
    for t in targets:
        res = load_json(MT / f"{t}_tests.json")
        results[t] = res
        extra = load_json(WORK / f"extra_{t}.json") if (WORK / f"extra_{t}.json").exists() else {}
        for tid in TEST_ORDER:
            if res["status"].get(tid, {}).get("status") != "scored" or tid not in res.get("tests", {}):
                continue
            feats = scored_features(res["status"], tid)
            top = res["tests"][tid]["top"]
            new = [r for r in top if not r.get("known_analog")][:N_NEW]
            grp = {
                "test": tid, "mars_site": site_id(t),
                "n_cells_scored": res["tests"][tid].get("n_cells"),
                "share_ge": res["tests"][tid].get("share_ge"),
                "new_candidates": [candidate(r, tid, t, known, "new_candidate", i + 1, feats) for i, r in enumerate(new)],
                "known_analogs_in_top": [candidate(r, tid, t, known, "known_analog_in_top", i + 1, feats)
                                         for i, r in enumerate([r for r in top if r.get("known_analog")])],
                "known_analogs_validation": known_validation(res, tid, known, sp),
                "least_similar": [candidate(r, tid, t, known, "least_similar", i + 1, feats)
                                  for i, r in enumerate((extra.get(tid) or {}).get("least_similar", []))],
            }
            rankings[tid][site_id(t)] = grp
    rankings = {k: v for k, v in rankings.items() if v}
    sites = [mars_site(t, tg_all[t], results[t], sp, rankings) for t in targets]
    gen = max((results[t].get("generated_at") or "") for t in targets) if targets else None
    meta = {
        "version": VERSION, "body": "mars",
        "generated": datetime.now(TZ).isoformat(timespec="seconds"),
        "source_results_generated": gen,
        "status": "final for Space Apps 2026 submission; place names are automatic (GeoNames reverse geocoding) - verify before publishing",
        "grid": "Earth 0.1-degree land cells (water-masked); MODIS LST 2020-2024",
        "score_formula": ("task score = 100 * exp( sum(w * ln(max(s, eps))) / sum(w) ), eps = %s, w = 1 for every feature "
                          "(equal-weight geometric mean). Every listed feature is required: a cell missing any feature is not scored." % eps),
        "score_formula_note": ("Not the lunar weighted arithmetic mean 100*sum(w*c*s)/sum(w*c): one feature near 0 pulls the Mars "
                               "score toward 0 (a site that fails one requirement cannot be compensated by others). c = 1 everywhere."),
        "total_score_optional": ("weighted geometric mean of the scored tests with weight_roc renormalised over the tests the user "
                                 "selects; reference only"),
        "task_weights_roc": sp["test_weights"]["roc"],
        "profile_formula": ("dimension = equal-weight geometric mean of its variable similarities (floor 0.01); overall = "
                            "equal-weight geometric mean of the 5 scored dimensions x 100; ranked cells need >= 80% of dimensions "
                            "and >= 80% of variables with data"),
        "classification_cutoffs": {"similar": SIMILAR, "different": DIFFERENT},
        "classification_rule": f"s >= {SIMILAR} similar; s < {DIFFERENT} different; otherwise partial",
        "known_analog_rule": (f"a candidate within {sp['known_radius_km']} km of a known analog site (data/labels/known_analogs.csv) "
                              "is flagged and listed under known_analogs_in_top instead of new_candidates"),
        "min_separation_km": sp["min_sep_km"],
        "ice_rule": f"tests with applies = ice (R3, R5) are scored only for Mars targets with SWIM Ci >= {sp['ice_min_ci']}",
        "ranking_groups": {
            "new_candidates": f"top {N_NEW} Earth sites for this test and Mars site, known analogs removed, >= {sp['min_sep_km']} km apart",
            "known_analogs_in_top": "known analog sites that made the top 20 (shown for credibility)",
            "known_analogs_validation": "every known analog site with its score and global top-% for this test",
            "least_similar": f"{N_LEAST} lowest-scoring fully observed sites (contrast); present only after --grid",
        },
        "mars_sites": [site_id(t) for t in targets],
        "data_sources": data_sources(sp, tg_all),
        "ai_disclosure": ("Scoring code, data-processing scripts and this export were written with Claude (Anthropic); "
                          "the team chose the method, reviewed the code and checked the results."),
        "limitations": [
            "R2 (visual navigation) is not evaluated: no global image-texture data.",
            "Earth cells are 0.1 degree (~11 km); Mars targets are 25 km circles. Local features smaller than a cell are not seen.",
            "Earth slope is the 230 m GMTED2010 median per cell, not the 100 m scale in the landing requirement.",
            "Lithology is a coarse class match (GLiM 0.5 degree vs USGS SIM 3292).",
            "Temperature and aridity are scored as 'more extreme is closer' (Earth cannot reach Mars values), so they do not change between Mars targets.",
            "Seven Mars targets; biology and subsurface dimensions are not scored.",
        ],
    }
    return {
        "meta": meta,
        "tasks": tasks_block(sp, fs),
        "mars_sites": sites,
        "task_rankings": rankings,
        "profile_rankings": {site_id(t): profile_block(t, known) for t in targets},
        "set_cover": set_cover_block(),
        "validation": validation_block(),
        "known_analog_sites": list(known.values()),
    }


# ---------------- 全球格（--grid） ----------------
def compute_target(t: str):
    """重算一個目標：1° 全球格（各格內 0.1° 格的最高分）＋每項測試最不像的地點。存到 _work/。"""
    import gc

    import numpy as np
    import pandas as pd

    sys.path.insert(0, str(ROOT / "src"))
    from mars_analog import mission_tests as mt
    from mars_analog import profiles
    from mars_analog.novelty import distinct_sites

    sp = mt.spec()
    pt = profiles.profile_table(t)
    ok = (pt.confidence >= profiles.MIN_CONF) & (pt.var_coverage >= profiles.MIN_CONF) & np.isfinite(pt.overall)
    dims = pt[[c for c in pt.columns if c.startswith("dim_")] + ["overall"]].copy()
    overall = pt.overall.where(ok).astype("float32")
    profiles._CACHE.pop(t, None)
    del pt
    gc.collect()

    df, status = mt.score_target(t)
    scored = [k for k, v in status.items() if v["status"] == "scored" and f"T_{k}" in df.columns]
    lat1 = (np.floor(df.lat.values) + 0.5).astype("float32")
    lon1 = (np.floor(df.lon.values) + 0.5).astype("float32")
    g = pd.DataFrame({"lat": lat1, "lon": lon1, f"overall_{t}": overall.reindex(df.index).values})
    for k in scored:
        g[f"{t}_{k}"] = (df[f"T_{k}"].values * 100).astype("float32")
    agg = g.groupby(["lat", "lon"], sort=True).max()
    agg.insert(0, f"n_{t}", g.groupby(["lat", "lon"], sort=True).size())
    agg = agg.round(1).reset_index()
    WORK.mkdir(parents=True, exist_ok=True)
    agg.to_csv(WORK / f"grid_{t}.csv", index=False, float_format="%.1f")

    extra = {}
    full = ok.reindex(df.index).fillna(False).values
    ov = dims["overall"].reindex(df.index).fillna(100).values
    for k in scored:
        v = df[f"T_{k}"].values
        m = np.isfinite(v) & full
        p = df.loc[m, ["lat", "lon"]].copy()
        p["_key"] = -(np.round(v[m], 3) * 1000) - ov[m] / 1000
        sel = distinct_sites(p, "_key", N_LEAST, sp["min_sep_km"], pool=5000)
        recs = profiles._annotate([mt._record(t, k, i, n + 1, df, dims, status) for n, i in enumerate(sel.index)])
        extra[k] = {"least_similar": recs}
    dump_json(WORK / f"extra_{t}.json", extra)
    del df, dims, g, agg
    gc.collect()
    print(f"[grid] {t}: done ({', '.join(scored)})", flush=True)


def build_grid() -> dict | None:
    files = [(t, WORK / f"grid_{t}.csv") for t in TARGET_ORDER if (WORK / f"grid_{t}.csv").exists()]
    if not files:
        return None
    rows: dict = {}
    cols = ["lat", "lon"]
    for t, p in files:
        with p.open(encoding="utf-8", newline="") as f:
            r = csv.reader(f)
            head = next(r)
            extra_cols = head[2:]
            start = len(cols)
            cols += extra_cols
            for line in r:
                key = (float(line[0]), float(line[1]))
                row = rows.setdefault(key, {})
                for j, c in enumerate(extra_cols):
                    x = line[2 + j]
                    row[c] = (int(float(x)) if c.startswith("n_") else float(x)) if x not in ("", "nan") else None
    # 每格的 0.1° 陸地格數（各目標相同，取第一個）
    ncol = f"n_{files[0][0]}"
    value_cols = [c for c in cols[2:] if not c.startswith("n_")]
    columns = ["lat", "lon", "n_cells"] + value_cols
    out_rows = []
    for (la, lo) in sorted(rows):
        row = rows[(la, lo)]
        out_rows.append([la, lo, row.get(ncol)] + [row.get(c) for c in value_cols])
    return {
        "meta": {
            "version": VERSION, "generated": datetime.now(TZ).isoformat(timespec="seconds"),
            "grid": "1-deg cells; lat/lon = cell centre; n_cells = Earth 0.1-deg land cells inside",
            "aggregation": "max of the 0.1-deg cell scores inside the 1-deg cell (best spot in the cell)",
            "scale": "0-100",
            "columns": columns,
            "column_meaning": {"overall_<target>": "analog-profile overall similarity to that Mars target (ranking pool only)",
                               "<target>_<test>": "mission test score for that Mars target"},
            "mars_site_ids": {t: site_id(t) for t, _ in files},
            "null": "no scored 0.1-deg cell in this 1-deg cell (missing data or test not applicable)",
        },
        "rows": out_rows,
    }


# ---------------- 說明檔 ----------------
README = """# Mars handoff for the website (`outputs/mars_handoff/`)

Produced by `python scripts/export_mars_handoff.py` (add `--grid` to rebuild the global map). Same idea as the lunar
handoff in `nasa-main/data/lunar/handoff-source/`: the website reads precomputed rankings and does **not** recompute scores.

| File | What it is |
|---|---|
| `mars_results.json` | Everything the site needs: tests (R1–R6), Mars sites, rankings, analog profile, set cover, validation |
| `mars_global_grid.json` | 1° world map of scores per Mars site (overall profile + each test). Only after `--grid` |
| `mars_candidate_pool.csv` | Candidate pool used by the set cover (0.1° cells, every target × test score) |
| `marsHandoffTypes.ts` | TypeScript types for `mars_results.json` (mirrors `frontend/src/lunarHandoffTypes.ts`) |

## `mars_results.json`

- `meta`: formula, cut-offs, rules, data sources, AI disclosure, limitations.
- `tasks.R1…R6`: name, weight (ROC), `applies` (`all` or `ice`), `status` (`scored` / `not_evaluated`), features with `w`, `c`, `formula`.
- `mars_sites[]`: `id` (`mars-jezero` …), lat/lon, Mars values, `test_status`, `scored_tests`, `best_earth_analogs_by_task` (top 3).
- `task_rankings[test][mars_site_id]` → groups (every Mars test depends on the site, like the lunar M4):
  - `new_candidates` (top 10, known analogs removed), `known_analogs_in_top`, `known_analogs_validation`, `least_similar` (after `--grid`).
  - Each candidate: `id, rank, cell_id, lat, lon, name_en, score (0–100), known_analog_region, nearest_known_analog,
    features[{feature, value, mars_value, unit, s, w, c, classification}], available_features, total_features, weakest_feature,
    breaks, dimension_scores, profile_overall, worldview_url`.
  - A test that is not applicable to a site (R3/R5 without ice) or not evaluated (R2) has no entry; see `mars_sites[].test_status`.
- `profile_rankings[mars_site_id]`: "how much like this Mars site" – `overall_top` (10), `by_dimension` (5 each), `known_analogs`.
- `set_cover`: smallest set of Earth sites covering every target × test, with the marginal curve and sensitivity.
- `validation`: known-analog recovery, negative controls, stability of the top sites.

## Score

`score = 100 · exp(Σ w·ln(max(s, 0.01)) / Σ w)` with `w = 1` – an equal-weight **geometric** mean, all features required.
This is different from the lunar `100·Σ(w·c·s)/Σ(w·c)`: one feature near 0 pulls the Mars score toward 0.
`classification`: `s ≥ 0.6` similar, `s < 0.3` different, otherwise partial (same cut-offs as the lunar file).
`python scripts/export_mars_handoff.py --check` reproduces every candidate score from its features.

## Site ids

`mars-jezero, mars-gale, mars-arcadia, mars-oxia, mars-meridiani, mars-protonilus, mars-ap105` (the first three and ap105 match the ids already used on the site).
"""

TS_TYPES = """// Types for outputs/mars_handoff/mars_results.json (mirrors lunarHandoffTypes.ts)
export type Classification = 'similar' | 'partial' | 'different' | null;

export interface MarsFeatureScore {
  feature: string;
  value: number | string | Record<string, number | null> | null;   // Earth value
  mars_value: number | string | string[] | null;                    // Mars value or requirement text
  unit: string | null;
  s: number | null;          // 0–1
  w: number;                 // always 1
  c: number;                 // always 1
  classification: Classification;
}

export interface MarsEarthCandidate {
  id: string;
  rank: number;
  rank_including_known?: number;
  group: 'new_candidate' | 'known_analog_in_top' | 'least_similar';
  cell_id: string;
  lat: number;
  lon: number;
  name_en: string | null;
  name_zh: string | null;
  score: number | null;      // 0–100
  known_analog_region: string | null;
  nearest_known_analog: { site_id: string; name_en?: string | null; distance_km: number | null } | null;
  features: MarsFeatureScore[];
  available_features: number;
  total_features: number;
  weakest_feature: string | null;
  breaks: Array<Record<string, unknown>>;
  dimension_scores: Record<string, number | null> | null;
  profile_overall: number | null;
  worldview_url: string | null;
  notes: string | null;
}

export interface MarsKnownAnalogValidation {
  rank: number;
  site_id: string;
  name_en: string;
  lat: number | null;
  lon: number | null;
  missions: string[];
  tagged_for_this_test: boolean;
  score: number | null;          // 0–100
  global_top_pct: number | null; // smaller is better
  score_basis: string;
  group: 'known_analog_validation';
  features: [];
}

export interface MarsRankingGroup {
  test: string;
  mars_site: string;
  n_cells_scored: number;
  share_ge: Record<string, number | null>;
  new_candidates: MarsEarthCandidate[];
  known_analogs_in_top: MarsEarthCandidate[];
  known_analogs_validation: MarsKnownAnalogValidation[];
  least_similar: MarsEarthCandidate[];
}

export interface MarsSite {
  id: string;
  target_id: string;
  name: string;
  lat: number;
  lon: number;
  radius_km: number;
  missions: string[];
  lithology_group: string | null;
  lithology_unit: string | null;
  ice_ci: number | null;
  ice_target: number | null;
  has_ice: boolean;
  test_status: Record<string, 'scored' | 'not_applicable' | 'not_evaluated' | string>;
  scored_tests: string[];
  values: Record<string, Record<string, unknown>>;
  best_earth_analogs_by_task: Record<string, Array<{ name_en: string | null; lat: number; lon: number; score: number | null }>>;
}

export interface MarsTask {
  name: string;
  name_zh: string;
  weight_roc: number | null;
  applies: 'all' | 'ice';
  status: 'scored' | 'not_evaluated';
  features: Array<{ id: string; kind: string; w: number; c: number; required: boolean; unit: string | null; formula: string }>;
}

export interface MarsResults {
  meta: Record<string, unknown>;
  tasks: Record<string, MarsTask>;
  mars_sites: MarsSite[];
  task_rankings: Record<string, Record<string, MarsRankingGroup>>;
  profile_rankings: Record<string, unknown>;
  set_cover: Record<string, unknown> | null;
  validation: Record<string, unknown> | null;
  known_analog_sites: Array<Record<string, unknown>>;
}

export interface MarsGlobalGrid {
  meta: { columns: string[]; grid: string; aggregation: string; scale: string } & Record<string, unknown>;
  rows: Array<Array<number | null>>;
}
"""


def assemble():
    OUT.mkdir(parents=True, exist_ok=True)
    res = build_results()
    dump_json(OUT / "mars_results.json", res)
    gridj = build_grid()
    if gridj:
        res["meta"]["global_grid"] = "mars_global_grid.json"
        dump_json(OUT / "mars_global_grid.json", gridj, indent=None)
        dump_json(OUT / "mars_results.json", res)
    pool = MT / "candidate_pool.csv"
    if pool.exists():
        shutil.copyfile(pool, OUT / "mars_candidate_pool.csv")
    (OUT / "README.md").write_text(README, encoding="utf-8")
    (OUT / "marsHandoffTypes.ts").write_text(TS_TYPES, encoding="utf-8")
    n = sum(len(g["new_candidates"]) for tt in res["task_rankings"].values() for g in tt.values())
    print(f"mars_results.json: {len(res['mars_sites'])} Mars sites, {sum(len(v) for v in res['task_rankings'].values())} "
          f"site x test groups, {n} new candidates" + (f"; grid {len(gridj['rows'])} 1-deg cells" if gridj else "; no grid yet (--grid)"))


# ---------------- 檢查 ----------------
def check() -> int:
    p = OUT / "mars_results.json"
    txt = p.read_text(encoding="utf-8")
    d = json.loads(txt, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(f"non-finite {c}")))
    eps = d["meta"]["score_formula"].split("eps = ")[1].split(",")[0]
    eps = float(eps)
    worst, n, bad = 0.0, 0, []
    for tid, by in d["task_rankings"].items():
        for sid, g in by.items():
            for grp in ("new_candidates", "known_analogs_in_top", "least_similar"):
                for c in g[grp]:
                    ss = [f["s"] for f in c["features"] if f["s"] is not None]
                    if not ss or c["score"] is None:
                        continue
                    rep = 100 * math.exp(sum(math.log(max(s, eps)) for s in ss) / len(ss))
                    diff = abs(rep - c["score"])
                    n += 1
                    worst = max(worst, diff)
                    if diff > 1.0:
                        bad.append((tid, sid, grp, c["rank"], c["score"], round(rep, 1)))
    print(f"scores reproduced from features: {n} candidates, max |diff| = {worst:.2f} points")
    for b in bad[:10]:
        print("  MISMATCH", b)
    issues = 0
    for s in d["mars_sites"]:
        for tid in s["scored_tests"]:
            if tid not in d["task_rankings"] or s["id"] not in d["task_rankings"][tid]:
                print("  missing ranking", s["id"], tid)
                issues += 1
            elif len(d["task_rankings"][tid][s["id"]]["new_candidates"]) < N_NEW:
                print("  fewer than", N_NEW, "new candidates:", s["id"], tid)
    gp = OUT / "mars_global_grid.json"
    if gp.exists():
        g = json.loads(gp.read_text(encoding="utf-8"), parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
        ncol = len(g["meta"]["columns"])
        badrow = sum(1 for r in g["rows"] if len(r) != ncol)
        print(f"global grid: {len(g['rows'])} rows x {ncol} columns, bad rows {badrow}")
        issues += badrow
    else:
        print("global grid: not built yet (run with --grid)")
    print(f"mars_results.json {p.stat().st_size / 1e6:.2f} MB; strict JSON OK")
    return 1 if (bad or issues) else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", action="store_true", help="重算全球 1° 格與最不像的地點（需要 pandas、pyarrow）")
    ap.add_argument("--target", nargs="*", help="只算這些目標（搭配 --grid）")
    ap.add_argument("--force", action="store_true", help="--grid 時重算已經算過的目標")
    ap.add_argument("--check", action="store_true", help="只檢查輸出")
    a = ap.parse_args()
    if a.check:
        sys.exit(check())
    if a.grid:
        todo = a.target or targets_present()
        for t in todo:
            if not a.force and (WORK / f"grid_{t}.csv").exists() and (WORK / f"extra_{t}.json").exists():
                print(f"[grid] {t}: already done (use --force to redo)")
                continue
            compute_target(t)
    assemble()
    sys.exit(check())


if __name__ == "__main__":
    main()
