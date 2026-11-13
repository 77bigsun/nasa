"""roughness: median of the 5x5-pixel (1 km) moving-window standard deviation of elevation (m), 200 m DEM.

Window size must match the Earth side (features.yaml: window_px 5 at 200 m). Plain std, no detrending.
Citation: same DEM as slope (Fergason et al., 2018, USGS Astrogeology).
"""
import numpy as np
from scipy.ndimage import uniform_filter

from ._dem import SOURCE, local_dem

WINDOW_PX = 5


def window_std(z: np.ndarray, size: int = WINDOW_PX) -> np.ndarray:
    bad = ~np.isfinite(z)
    zf = np.where(bad, 0.0, z)
    m = uniform_filter(zf, size, mode="nearest")
    m2 = uniform_filter(zf * zf, size, mode="nearest")
    out = np.sqrt(np.clip(m2 - m * m, 0, None))
    out[uniform_filter(bad.astype(float), size, mode="nearest") > 0] = np.nan   # window touches no-data
    return out


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    z, inside = local_dem(lat, lon, radius_km)
    r = window_std(z)[inside]
    r = r[np.isfinite(r)]
    if r.size == 0:
        return {"value": None, "coverage": False, "source": SOURCE, "n_pixels": 0, "unit": "m"}
    return {"value": round(float(np.median(r)), 3), "coverage": True, "source": SOURCE, "n_pixels": int(r.size),
            "unit": "m", "window_px": WINDOW_PX}
