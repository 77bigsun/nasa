"""slope_fine: median terrain slope (degrees) inside the circle at 30 m, from a local fine DEM (A8).

Added alongside the 200 m `slope`; only comparable with Earth slope computed at 30 m (Copernicus GLO-30).
Citations:
- Jezero: USGS Astrogeology Science Center (2020). Mars 2020 Terrain Relative Navigation CTX DTM of Jezero crater
  (JEZ_ctx_B_soc_008, 20 m/px), free use. https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/
- Gale: Persaud, D.M., Putri, A.R.D., Muller, J.-P. (2021). 30 m HRSC DTM mosaic of Gale crater. Zenodo,
  doi:10.5281/zenodo.5808354 (CC BY 4.0).
"""
from ._dem_fine import RES_M, local_fine_dem, summarise
from .slope import slope_deg


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    d, z, inside = local_fine_dem(lat, lon, radius_km)
    return summarise(None if d is None else slope_deg(z, RES_M), inside, d, radius_km, "deg")
