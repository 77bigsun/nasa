"""Fine-resolution Mars DEMs around a point, reprojected to a local 30 m metric grid (shared by slope_fine and roughness_fine).

Two local DTMs, used only where they actually contain the target point (no global fine DEM exists):
- Jezero: USGS Astrogeology CTX DTM, 20 m/px (Mars 2020 Terrain Relative Navigation products), free use.
  https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif
- Gale: HRSC 30 m DTM mosaic (Persaud, Putri & Muller, 2021), Zenodo doi:10.5281/zenodo.5808354, CC BY 4.0.
Both files are downloaded once to data/raw/mars/fine/ (gitignored). 30 m matches Earth Copernicus GLO-30.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject, transform, transform_bounds
from rasterio.windows import from_bounds

from ...paths import RAW_MARS, R_MARS

FINE_DIR = RAW_MARS / "fine"
RES_M = 30.0
WINDOW_PX = 5                 # 5 x 30 m = 150 m roughness window
MIN_COVERAGE = 0.5            # valid pixels / pixels in circle needed to report a value

DATASETS = [
    {"source": "usgs_ctx_dtm_jezero_20m",
     "file": "JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif",
     "dataset": "USGS CTX DTM of Jezero crater, 20 m/px (Mars 2020 TRN), resampled to 30 m (average)"},
    {"source": "hrsc_dtm_mosaic_gale_30m",
     "file": "hrsc_km09_h1938_h1927_h1916-dtm-mosaic.tif",
     "dataset": "HRSC 30 m DTM mosaic of Gale crater (Persaud, Putri & Muller 2021, doi:10.5281/zenodo.5808354)"},
]


def _valid_at(path, lat: float, lon: float) -> bool:
    """True if the raster has a valid (non-nodata) elevation at the target point."""
    with rasterio.open(path) as src:
        xs, ys = transform(rasterio.crs.CRS.from_proj4(f"+proj=longlat +R={R_MARS} +no_defs"), src.crs, [lon], [lat])
        row, col = src.index(xs[0], ys[0])
        if not (0 <= row < src.height and 0 <= col < src.width):
            return False
        v = src.read(1, window=((row, row + 1), (col, col + 1)))[0, 0]
        return bool(np.isfinite(v) and (src.nodata is None or v != src.nodata))


def pick_dataset(lat: float, lon: float) -> dict | None:
    """The first fine DEM that is on disk and contains a valid pixel at the target point, else None."""
    for d in DATASETS:
        p = FINE_DIR / d["file"]
        if p.exists() and _valid_at(p, lat, lon):
            return d
    return None


@lru_cache(maxsize=16)
def local_fine_dem(lat: float, lon: float, radius_km: float):
    """(dataset dict or None, elevation grid in m on a 30 m local eqc grid, boolean inside-circle mask)."""
    d = pick_dataset(lat, lon)
    if d is None:
        return None, None, None
    half = radius_km * 1000 + 4 * RES_M
    crs = rasterio.crs.CRS.from_proj4(f"+proj=eqc +lat_ts={lat} +lat_0={lat} +lon_0={lon} +R={R_MARS} +units=m +no_defs")
    n = int(np.ceil(2 * half / RES_M))
    tf = from_origin(-n * RES_M / 2, n * RES_M / 2, RES_M, RES_M)
    with rasterio.open(FINE_DIR / d["file"]) as src:
        l, b, r, t = transform_bounds(crs, src.crs, -half, -half, half, half, densify_pts=21)
        pad = 3 * abs(src.transform.a)
        win = from_bounds(l - pad, b - pad, r + pad, t + pad, src.transform).round_offsets().round_lengths()
        z = src.read(1, window=win, boundless=True, fill_value=src.nodata if src.nodata is not None else np.nan)
        z = z.astype("float32")
        if src.nodata is not None:
            z[z == src.nodata] = np.nan
        z[~np.isfinite(z)] = np.nan
        finer = abs(src.transform.a) < 0.9 * RES_M
        dst = np.full((n, n), np.nan, dtype="float32")
        reproject(z, dst, src_transform=src.window_transform(win), src_crs=src.crs, src_nodata=np.nan,
                  dst_transform=tf, dst_crs=crs, dst_nodata=np.nan,
                  resampling=Resampling.average if finer else Resampling.bilinear)
    yy, xx = np.mgrid[0:n, 0:n]
    x = (xx + 0.5) * RES_M - n * RES_M / 2
    y = n * RES_M / 2 - (yy + 0.5) * RES_M
    inside = np.hypot(x, y) <= radius_km * 1000
    return d, dst.astype("float64"), inside


def summarise(metric: np.ndarray | None, inside, d: dict | None, radius_km: float, unit: str) -> dict:
    """Median of the metric over valid pixels in the circle; value only if coverage_fraction >= MIN_COVERAGE."""
    base = {"unit": unit, "resolution_m": int(RES_M), "window_px": WINDOW_PX, "radius_km": radius_km}
    if d is None:
        return {"value": None, "coverage": False, "source": None, "n_pixels": 0, **base,
                "coverage_fraction": 0.0, "dataset": None,
                "note": "no fine (<=30 m) DEM on disk contains this point (only Jezero CTX 20 m and Gale HRSC 30 m)"}
    vals = metric[inside]
    ok = np.isfinite(vals)
    frac = round(float(ok.sum()) / float(inside.sum()), 3)
    out = {"source": d["source"], "n_pixels": int(ok.sum()), **base, "coverage_fraction": frac, "dataset": d["dataset"]}
    if frac < MIN_COVERAGE:
        return {"value": None, "coverage": False, **out,
                "note": f"fine DEM covers only {frac:.0%} of the {radius_km} km circle (< {MIN_COVERAGE:.0%})"}
    v = vals[ok]
    return {"value": round(float(np.median(v)), 3), "coverage": True, **out,
            "p90": round(float(np.percentile(v, 90)), 3)}
