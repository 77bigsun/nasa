"""roughness_fine: median of the 5x5-pixel (150 m) moving-window elevation std (m) at 30 m, from a local fine DEM (A8).

Added alongside the 200 m `roughness`; only comparable with Earth roughness at 30 m with a 5x5 window.
Citations: same fine DEMs as slope_fine (Jezero USGS CTX DTM 20 m; Gale HRSC 30 m mosaic, Persaud et al. 2021,
doi:10.5281/zenodo.5808354, CC BY 4.0).
"""
from ._dem_fine import WINDOW_PX, local_fine_dem, summarise
from .roughness import window_std


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    d, z, inside = local_fine_dem(lat, lon, radius_km)
    return summarise(None if d is None else window_std(z, WINDOW_PX), inside, d, radius_km, "m")
