"""
學權重與驗證共用的資料準備：已知類比地 → 正樣本格子；隨機陸地＋高植被 → 負樣本（其實是「未標記」）。

正樣本 = 已知類比地半徑內的陸地格（每個類比地當一組，留一法時整組拿掉）。
負樣本 = 隨機陸地格（面積加權）＋ 高 NDVI 格（雨林、農地），排除已知類比地 50 km 內。
  注意：隨機陸地格裡可能有「還沒被發現的類比地」，所以它們嚴格說是「未標記」而不是「確定不像」。
  這是 Positive-Unlabeled（PU）學習：Elkan & Noto (2008) 證明在「已知類比地是從所有真類比地中隨機被發現」的假設下，
  分「已標記 vs 未標記」的模型和分「真類比 vs 非類比」的模型排名順序相同 → 排名前面的未標記格就是新候選地。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from . import config, earth_grid
from .config import VARIABLES
from .similarity import similarity_vector

EARTH_R_KM = 6371.0
SEED = 20261114


@lru_cache
def grid() -> pd.DataFrame:
    return earth_grid.load()


@lru_cache
def ref() -> dict:
    return earth_grid.reference()


@lru_cache
def tree() -> BallTree:
    g = grid()
    return BallTree(np.radians(g[["lat", "lon"]].values), metric="haversine")


_SIM_CACHE: dict = {}


def sim_for(target_id: str, method: str = "B", dust_mode: str | None = None) -> pd.DataFrame:
    key = (target_id, method, dust_mode)
    if key not in _SIM_CACHE:
        _SIM_CACHE[key] = similarity_vector(config.mars_targets()[target_id], grid(), ref(), method, dust_mode)
    return _SIM_CACHE[key]


def cells_within(lat, lon, radius_km) -> np.ndarray:
    return tree().query_radius(np.radians([[lat, lon]]), r=radius_km / EARTH_R_KM)[0]


@lru_cache
def site_cells() -> dict:
    """{site_id: 陣列（grid 的列號）}。半徑內沒有陸地格就取 50 km 內最近的一格。"""
    out = {}
    for r in config.known_analogs().itertuples():
        idx = cells_within(r.lat, r.lon, float(r.radius_km))
        if len(idx) == 0:
            d, i = tree().query(np.radians([[r.lat, r.lon]]), k=1)
            if d[0, 0] * EARTH_R_KM <= 50:
                idx = i[0]
        out[r.site_id] = np.asarray(idx, dtype=int)
    return out


@lru_cache
def negative_cells(n_random: int = 6000, n_veg: int = 600, exclude_km: float = 50) -> np.ndarray:
    g = grid()
    rng = np.random.default_rng(SEED)
    near = np.zeros(len(g), bool)
    for r in config.known_analogs().itertuples():
        near[cells_within(r.lat, r.lon, exclude_km)] = True
    w = np.cos(np.radians(g.lat.values)) * (~near)
    rand = rng.choice(len(g), size=n_random, replace=False, p=w / w.sum())
    veg_pool = np.where((g.ndvi_mean.values > 0.6) & ~near)[0]
    veg = rng.choice(veg_pool, size=min(n_veg, len(veg_pool)), replace=False)
    return np.unique(np.concatenate([rand, veg]))


@lru_cache
def eval_sample(n: int = 150_000) -> np.ndarray:
    """估全球排名百分位用的大樣本（面積加權）。"""
    g = grid()
    rng = np.random.default_rng(SEED + 1)
    w = np.cos(np.radians(g.lat.values))
    return rng.choice(len(g), size=n, replace=False, p=w / w.sum())


def mission_targets(mission: str) -> list[str]:
    return [t for t, v in config.mars_targets().items() if mission in v.get("missions", [])]


def positive_pairs(mission: str | None) -> list[tuple[str, str]]:
    """(site_id, target_id)：類比地標的任務包含 mission、標的火星目標也做這個任務。mission=None → 全部任務。"""
    sc = site_cells()
    pairs = []
    for r in config.known_analogs().itertuples():
        if len(sc[r.site_id]) == 0:
            continue
        ms = r.mission_list if mission is None else [mission] if mission in r.mission_list else []
        for m in ms:
            for t in r.targets:
                if t in mission_targets(m) and (r.site_id, t) not in pairs:
                    pairs.append((r.site_id, t))
    return pairs


@dataclass
class TrainSet:
    X: np.ndarray          # ln(max(s, 0.01))，缺值補負樣本平均
    S: np.ndarray          # 原始 s（含 NaN），給樹模型用
    y: np.ndarray
    w: np.ndarray          # 樣本權重：每個 (類比地, 目標) 總權重 1；負樣本總權重 = 正樣本總權重
    group: np.ndarray      # 類比地 id（負樣本 = "neg"）
    target: np.ndarray
    pairs: list = field(default_factory=list)


def build_trainset(mission: str | None, method: str = "B", dust_mode: str | None = None,
                   exclude_sites: tuple = ()) -> TrainSet:
    pairs = [p for p in positive_pairs(mission) if p[0] not in exclude_sites]
    targets = sorted({t for _, t in pairs}) or (mission_targets(mission) if mission else list(config.mars_targets()))
    sc, neg = site_cells(), negative_cells()
    Xs, Ss, ys, ws, gs, ts = [], [], [], [], [], []
    cols = [f"s_{v}" for v in VARIABLES]
    for site, t in pairs:
        s = sim_for(t, method, dust_mode).iloc[sc[site]][cols].values.astype("float64")
        Ss.append(s); ys.append(np.ones(len(s))); ws.append(np.full(len(s), 1.0 / len(s)))
        gs.append(np.full(len(s), site, dtype=object)); ts.append(np.full(len(s), t, dtype=object))
    n_pos_w = float(len(pairs))
    for t in targets:
        s = sim_for(t, method, dust_mode).iloc[neg][cols].values.astype("float64")
        Ss.append(s); ys.append(np.zeros(len(s)))
        ws.append(np.full(len(s), n_pos_w / (len(neg) * len(targets))))
        gs.append(np.full(len(s), "neg", dtype=object)); ts.append(np.full(len(s), t, dtype=object))
    S = np.vstack(Ss)
    y = np.concatenate(ys)
    X = np.log(np.maximum(S, 0.01))
    neg_mean = np.nanmean(np.where(y[:, None] == 0, X, np.nan), axis=0)
    neg_mean = np.where(np.isfinite(neg_mean), neg_mean, 0.0)
    X = np.where(np.isnan(X), neg_mean[None, :], X)
    return TrainSet(X, S, y, np.concatenate(ws), np.concatenate(gs), np.concatenate(ts), pairs)
