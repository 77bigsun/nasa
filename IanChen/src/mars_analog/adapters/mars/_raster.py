"""Read the pixels of any Mars raster that fall inside a circle of radius_km around (lat, lon).

Works for rasters in any Mars CRS (geographic or projected, 0..360 or -180..180 longitudes): pixel centres are
converted back to lon/lat on the Mars sphere and kept when their great-circle distance is <= radius.
"""
from __future__ import annotations

import numpy as np
import rasterio
from pyproj import CRS, Transformer
from rasterio.windows import Window

from ...paths import MARS_LONLAT, R_MARS


def _gc_dist_m(lat0, lon0, lat, lon):
    p0, p = np.radians(lat0), np.radians(lat)
    dl = np.radians(((lon - lon0) + 180.0) % 360.0 - 180.0)
    a = np.sin((p - p0) / 2) ** 2 + np.cos(p0) * np.cos(p) * np.sin(dl / 2) ** 2
    return 2 * R_MARS * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def disc_values(path, lat: float, lon: float, radius_km: float, nodata_below: float | None = None,
                band: int = 1) -> tuple[np.ndarray, np.ndarray]:
    """Return (values, pixel_latitudes) of valid pixels inside the disc. Empty arrays if outside the raster."""
    with rasterio.open(path) as ds:
        crs = CRS.from_user_input(ds.crs) if ds.crs else CRS.from_proj4(MARS_LONLAT)
        to_ds = Transformer.from_crs(CRS.from_proj4(MARS_LONLAT), crs, always_xy=True)
        to_ll = Transformer.from_crs(crs, CRS.from_proj4(MARS_LONLAT), always_xy=True)
        dlat = np.degrees(radius_km * 1000 / R_MARS) * 1.2
        dlon = dlat / max(np.cos(np.radians(lat)), 0.05)
        best = None
        for shift in (0.0, 360.0, -360.0):          # pick the longitude convention the raster uses
            lons = np.array([lon - dlon, lon + dlon, lon, lon]) + shift
            lats = np.array([lat, lat, lat - dlat, lat + dlat])
            xs, ys = to_ds.transform(lons, lats)
            rows, cols = rasterio.transform.rowcol(ds.transform, xs, ys)
            r0, r1 = max(min(rows), 0), min(max(rows) + 1, ds.height)
            c0, c1 = max(min(cols), 0), min(max(cols) + 1, ds.width)
            if r1 > r0 and c1 > c0 and (best is None or (r1 - r0) * (c1 - c0) > best[4]):
                best = (r0, r1, c0, c1, (r1 - r0) * (c1 - c0))
        if best is None:
            return np.array([]), np.array([])
        r0, r1, c0, c1, _ = best
        z = ds.read(band, window=Window(c0, r0, c1 - c0, r1 - r0)).astype("float64")
        nod = ds.nodata
        rr, cc = np.mgrid[r0:r1, c0:c1]
        xs, ys = rasterio.transform.xy(ds.transform, rr.ravel(), cc.ravel())
        plon, plat = to_ll.transform(np.asarray(xs), np.asarray(ys))
    v = z.ravel()
    keep = np.isfinite(v) & (_gc_dist_m(lat, lon, plat, plon) <= radius_km * 1000)
    if nod is not None and np.isfinite(nod):
        keep &= v != nod
    if nodata_below is not None:
        keep &= v > nodata_below
    return v[keep], np.asarray(plat)[keep]
