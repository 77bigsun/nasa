"""slope: median terrain slope (degrees) inside the circle, from the 200 m HRSC+MOLA blended DEM.

Citation: Fergason, R.L., Hare, T.M., Laura, J. (2018) HRSC and MOLA Blended Digital Elevation Model at 200 m v2.
USGS Astrogeology Science Center, PDS Annex. https://astrogeology.usgs.gov/search/map/mars_mgs_mola_mex_hrsc_blended_dem_global_200m
"""
import numpy as np

from ._dem import RES_M, SOURCE, local_dem


def slope_deg(z: np.ndarray, res_m: float = RES_M) -> np.ndarray:
    gy, gx = np.gradient(z, res_m)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    z, inside = local_dem(lat, lon, radius_km)
    s = slope_deg(z)[inside]
    s = s[np.isfinite(s)]
    if s.size == 0:
        return {"value": None, "coverage": False, "source": SOURCE, "n_pixels": 0, "unit": "deg"}
    return {"value": round(float(np.median(s)), 3), "coverage": True, "source": SOURCE, "n_pixels": int(s.size),
            "unit": "deg", "p90": round(float(np.percentile(s, 90)), 3)}
