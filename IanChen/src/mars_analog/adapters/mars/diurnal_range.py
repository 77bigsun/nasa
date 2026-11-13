"""diurnal_range: mean daily surface-temperature range (K = deg C difference), MCD climatology.

For each season (row of the Ls x local-time table) take max - min over the day, then average over seasons.
New in TASK_A (11/13); scoring weight is 0 for now.
Citation: Mars Climate Database (see _mcd.py).
"""
import numpy as np

from ._mcd import SOURCE, tsurf_table


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    try:
        v = tsurf_table(round(lat, 3), round(lon, 3))
    except Exception as e:
        return {"value": None, "coverage": False, "source": SOURCE, "n_pixels": 0, "unit": "C", "error": str(e)[:200]}
    rng = v.max(axis=1) - v.min(axis=1)
    return {"value": round(float(rng.mean()), 2), "coverage": True, "source": SOURCE, "n_pixels": int(v.size),
            "unit": "C", "min_season": round(float(rng.min()), 2), "max_season": round(float(rng.max()), 2)}
