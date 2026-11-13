"""Mars 200 m DEM around a point, reprojected to a local metric grid (shared by slope and roughness).

Source: HRSC and MOLA Blended Digital Elevation Model at 200 m, v2 (Fergason, Hare & Laura, 2018, USGS Astrogeology).
The 11 GB global GeoTIFF is read over HTTP (GDAL /vsicurl/), only the window needed.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject, transform_bounds
from rasterio.windows import from_bounds

from ...paths import R_MARS

DEM_URL = ("https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars/HRSC_MOLA_Blend/"
           "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif")
SOURCE = "hrsc_mola_blend_200m_v2"
RES_M = 200.0


@lru_cache(maxsize=16)
def local_dem(lat: float, lon: float, radius_km: float) -> tuple[np.ndarray, np.ndarray]:
    """(elevation grid in m, boolean mask of pixels inside the circle) on a 200 m local equirectangular grid."""
    half = radius_km * 1000 + 4 * RES_M                       # margin so 5x5 windows at the edge are complete
    crs = rasterio.crs.CRS.from_proj4(f"+proj=eqc +lat_ts={lat} +lat_0={lat} +lon_0={lon} +R={R_MARS} +units=m +no_defs")
    n = int(np.ceil(2 * half / RES_M))
    tf = from_origin(-n * RES_M / 2, n * RES_M / 2, RES_M, RES_M)
    with rasterio.open("/vsicurl/" + DEM_URL) as src:
        l, b, r, t = transform_bounds(crs, src.crs, -half, -half, half, half, densify_pts=21)
        pad = 3 * abs(src.transform.a)
        win = from_bounds(l - pad, b - pad, r + pad, t + pad, src.transform).round_offsets().round_lengths()
        z = src.read(1, window=win, boundless=True, fill_value=src.nodata).astype("float32")
        if src.nodata is not None:
            z[z == src.nodata] = np.nan
        dst = np.full((n, n), np.nan, dtype="float32")
        reproject(z, dst, src_transform=src.window_transform(win), src_crs=src.crs, src_nodata=np.nan,
                  dst_transform=tf, dst_crs=crs, dst_nodata=np.nan, resampling=Resampling.bilinear)
    yy, xx = np.mgrid[0:n, 0:n]
    x = (xx + 0.5) * RES_M - n * RES_M / 2
    y = n * RES_M / 2 - (yy + 0.5) * RES_M
    inside = np.hypot(x, y) <= radius_km * 1000
    return dst.astype("float64"), inside
