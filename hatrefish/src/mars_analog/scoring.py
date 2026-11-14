"""
B5：總分與排名（PROJECT_CONTEXT 第 4 節）。

    V   = { i | coverage_i 且 w_i > 0 }
    w'_i = w_i / Σ_{j∈V} w_j
    S   = 100 × exp( Σ_{i∈V} w'_i × ln(max(s_i, 0.01)) )     ← 加權幾何平均
    C   = Σ_{i∈V} w_i                                         ← 信心度

解讀：ln S = Σ w'_i ln s_i，所以 w_i 是「彈性」——s_i 下降 10%，總分大約下降 w_i × 10%。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import VARIABLES

MIN_S = 0.01


def aggregate(sim: pd.DataFrame, weights: dict) -> pd.DataFrame:
    w = np.array([float(weights.get(v, 0.0)) for v in VARIABLES])
    s = np.column_stack([sim[f"s_{v}"].values for v in VARIABLES]).astype("float64")
    cov = np.column_stack([sim[f"cov_{v}"].values for v in VARIABLES]) & (w > 0)[None, :]
    wm = np.where(cov, w[None, :], 0.0)
    wsum = wm.sum(1)
    logs = np.log(np.maximum(np.nan_to_num(s, nan=1.0), MIN_S))
    with np.errstate(invalid="ignore", divide="ignore"):
        total = 100 * np.exp((wm * logs).sum(1) / wsum)
    total[wsum == 0] = np.nan
    return pd.DataFrame({"total": total, "confidence": wsum}, index=sim.index)


def contributions(sim_row: pd.Series, weights: dict) -> dict:
    """每個變數對 ln(總分) 的貢獻（w'_i × ln s_i，負值越大代表越拉低分數）。給「為什麼這裡分數高／低」用。"""
    w = {v: float(weights.get(v, 0.0)) for v in VARIABLES}
    valid = [v for v in VARIABLES if sim_row[f"cov_{v}"] and w[v] > 0]
    ws = sum(w[v] for v in valid)
    return {v: w[v] / ws * float(np.log(max(sim_row[f"s_{v}"], MIN_S))) for v in valid}


def _self_test():
    """TASK_B B5 的手算範例：著陸 78.2、探測車 75.0、地質 69.8、取冰 43.0。"""
    from .config import mission_priors
    s = {"slope": 0.92, "roughness": 0.85, "thermal_inertia": 0.60, "lithology": 0.70, "ice": 0.20,
         "temperature": 0.45, "aridity": 0.90, "barrenness": 0.98, "dust": 0.55}
    row = {f"s_{v}": [s.get(v, np.nan)] for v in VARIABLES}
    row.update({f"cov_{v}": [v in s] for v in VARIABLES})
    sim = pd.DataFrame(row)
    got = {m: round(float(aggregate(sim, w).total.iloc[0]), 1) for m, w in mission_priors().items()}
    want = {"landing": 78.2, "rover": 75.0, "geology": 69.8, "isru_base": 43.0}
    assert got == {k: got[k] for k in want} and all(abs(got[k] - want[k]) < 0.051 for k in want), (got, want)
    return got


if __name__ == "__main__":
    print(_self_test())
