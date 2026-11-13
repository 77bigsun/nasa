"""thermal_inertia: TES nighttime thermal inertia (J m^-2 K^-1 s^-1/2, "tiu"), median inside the circle.

Compared with Earth as a within-planet percentile (pct), from data/processed/mars_reference_pct.json (A3).
Note: global_ti_msk_night_2007 is a mask, not thermal inertia; use global_ti_night_2007.
Citation: Putzig, N.E., Mellon, M.T. (2007) Apparent thermal inertia and the surface heterogeneity of Mars.
Icarus 191, 68-94. Data: MGS TES Thermal Inertia Map (MGS-M-TES-5-TIMAP-V1.0), PDS Geosciences Node,
https://pds-geosciences.wustl.edu/mgs/mgs-m-tes-5-timap-v1/mgst_9001/data/
"""
import json

import numpy as np

from ...paths import PROCESSED, RAW_MARS
from ._raster import disc_values

PATH = RAW_MARS / "tes" / "global_ti_night_2007.lbl"
SOURCE = "tes_night_2007"


def to_pct(value: float) -> float | None:
    ref = PROCESSED / "mars_reference_pct.json"
    if not ref.exists():
        return None
    q = json.loads(ref.read_text(encoding="utf-8"))["thermal_inertia"]["quantiles"]
    return round(float(np.interp(value, q, np.linspace(0, 1, len(q)))), 3)


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    v, _ = disc_values(PATH, lat, lon, radius_km, nodata_below=0.0)
    if v.size == 0:
        return {"value": None, "pct": None, "coverage": False, "source": SOURCE, "n_pixels": 0, "unit": "tiu"}
    ti = float(np.median(v))
    return {"value": round(ti, 1), "pct": to_pct(ti), "coverage": True, "source": SOURCE,
            "n_pixels": int(v.size), "unit": "tiu"}
