"""temperature: annual-mean surface temperature (deg C), MCD climatology, all seasons x all local times.

Citation: Mars Climate Database (see _mcd.py).
"""
import numpy as np

from ._mcd import SOURCE, tsurf_table


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    try:
        v = tsurf_table(round(lat, 3), round(lon, 3))
    except Exception as e:                                   # service down -> no data, never a guess
        return {"value": None, "coverage": False, "source": SOURCE, "n_pixels": 0, "unit": "C", "error": str(e)[:200]}
    k = 273.15
    return {"value": round(float(v.mean() - k), 2), "coverage": True, "source": SOURCE, "n_pixels": int(v.size),
            "unit": "C", "min_c": round(float(v.min() - k), 2), "max_c": round(float(v.max() - k), 2),
            "note": "point value at the target centre (MCD grid ~5 deg); radius not used"}
