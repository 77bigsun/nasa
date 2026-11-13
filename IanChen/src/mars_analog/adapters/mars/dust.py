"""dust: annual-mean dust column optical depth (tau) at the target from the MCD global map, plus Mars percentile.

pct = area-weighted share of the planet with lower annual-mean dust (data/processed/mars_reference_pct.json, A3).
Citation: Mars Climate Database (see _mcd.py).
"""
import json

import numpy as np

from ...paths import PROCESSED
from ._mcd import SOURCE, global_dust


def to_pct(value: float) -> float | None:
    ref = PROCESSED / "mars_reference_pct.json"
    if not ref.exists():
        return None
    q = json.loads(ref.read_text(encoding="utf-8"))["dust"]["quantiles"]
    return round(float(np.interp(value, q, np.linspace(0, 1, len(q)))), 3)


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    try:
        la, lo, d = global_dust()
    except Exception as e:
        return {"value": None, "pct": None, "coverage": False, "source": SOURCE, "n_pixels": 0, "unit": "tau",
                "error": str(e)[:200]}
    lo_n = ((lo + 180.0) % 360.0) - 180.0
    i = int(np.argmin(np.abs(((lo_n - lon) + 180.0) % 360.0 - 180.0)))
    j = int(np.argmin(np.abs(la - lat)))
    tau = float(d[i, j])
    return {"value": round(tau, 4), "pct": to_pct(tau), "coverage": True, "source": SOURCE, "n_pixels": 1,
            "unit": "tau"}
