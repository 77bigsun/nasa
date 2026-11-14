"""讀設定檔與交接檔。IanChen 的正式檔優先；還沒交的用 B 的暫用檔（data/provisional/）。"""
from __future__ import annotations

import json
from functools import lru_cache

import pandas as pd
import yaml

from .paths import CONFIG, LABELS, MAPPINGS, PROCESSED, PROVISIONAL, first_existing

VARIABLES = ["slope", "roughness", "thermal_inertia", "lithology", "ice",
             "temperature", "diurnal_range", "aridity", "barrenness", "dust"]
MISSIONS = ["geology", "rover", "isru_base", "landing"]
GAPS = ["gravity", "pressure", "radiation", "atmosphere_composition"]


@lru_cache
def features() -> dict:
    return yaml.safe_load((CONFIG / "features.yaml").read_text(encoding="utf-8"))


@lru_cache
def mission_priors() -> dict:
    d = json.loads((CONFIG / "missions.json").read_text(encoding="utf-8"))
    return {m: {v: float(d[m].get(v, 0.0)) for v in VARIABLES} for m in MISSIONS}


def learned_weights() -> dict | None:
    p = CONFIG / "weights_learned.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def weights_for(mission: str, source: str = "auto") -> dict:
    """source: auto（有 weights_learned.json 就用 final，否則先驗）| prior | learned"""
    if source in ("auto", "learned"):
        wl = learned_weights()
        if wl and mission in wl.get("final", {}):
            return {v: float(wl["final"][mission].get(v, 0.0)) for v in VARIABLES}
        if source == "learned":
            raise FileNotFoundError("config/weights_learned.json 不存在，先跑 --stage learn")
    return dict(mission_priors()[mission])


def _normalize_targets(d: dict) -> dict:
    """支援兩種格式：變數直接放在目標底下（暫用檔），或放在 features 底下（IanChen 的 mars_targets.json）。"""
    t = d.get("targets", d)
    out = {}
    for k, v in t.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict) and isinstance(v.get("features"), dict):
            v = {**{kk: vv for kk, vv in v.items() if kk != "features"}, **v["features"]}
        out[k] = v
    return out


@lru_cache
def mars_targets() -> dict:
    p = first_existing(PROCESSED / "mars_targets.json", PROVISIONAL / "mars_targets_provisional.json")
    if p is None:
        raise FileNotFoundError("沒有火星目標檔：先跑 python -m mars_analog.mars_provisional")
    return _normalize_targets(json.loads(p.read_text(encoding="utf-8")))


def mars_targets_source() -> str:
    p = first_existing(PROCESSED / "mars_targets.json", PROVISIONAL / "mars_targets_provisional.json")
    return str(p)


@lru_cache
def known_analogs() -> pd.DataFrame:
    p = first_existing(LABELS / "known_analogs.csv", PROVISIONAL / "known_analogs_seed.csv")
    df = pd.read_csv(p)
    df["targets"] = df["mars_target_ids"].fillna("").map(lambda s: [x.strip() for x in s.split(";") if x.strip()])
    df["mission_list"] = df["missions"].fillna("").map(lambda s: [x.strip() for x in s.split(";") if x.strip()])
    df.attrs["source"] = str(p)
    return df


@lru_cache
def lithology_table() -> dict:
    """{mars_group: {glim_class: similarity}}"""
    p = first_existing(MAPPINGS / "lithology_mars_to_glim.csv", PROVISIONAL / "lithology_mars_to_glim_provisional.csv")
    df = pd.read_csv(p)
    out: dict = {}
    for r in df.itertuples():
        out.setdefault(r.mars_group, {})[r.glim_class] = float(r.similarity)
    return out
