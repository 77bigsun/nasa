"""A3: Mars percentile reference table for thermal inertia and dust -> data/processed/mars_reference_pct.json.

Quantiles 0..100 (101 numbers), area-weighted by cos(latitude) so small polar pixels do not dominate.
    python -m mars_analog.mars_reference
"""
from __future__ import annotations

import json

import numpy as np
import rasterio
from pyproj import CRS, Transformer

from .adapters.mars import thermal_inertia
from .adapters.mars._mcd import SOURCE as MCD_SOURCE, dust_quantiles
from .paths import MARS_LONLAT, PROCESSED


def weighted_quantiles(values: np.ndarray, weights: np.ndarray, n: int = 101) -> list[float]:
    o = np.argsort(values)
    cdf = np.cumsum(weights[o]) / weights.sum()
    return [round(float(np.interp(q, cdf, values[o])), 4) for q in np.linspace(0, 1, n)]


def ti_quantiles() -> tuple[list[float], int]:
    with rasterio.open(thermal_inertia.PATH) as ds:
        z = ds.read(1).astype("float64")
        crs = CRS.from_user_input(ds.crs) if ds.crs else CRS.from_proj4(MARS_LONLAT)
        to_ll = Transformer.from_crs(crs, CRS.from_proj4(MARS_LONLAT), always_xy=True)
        rows = np.arange(ds.height)
        xs, ys = rasterio.transform.xy(ds.transform, rows, np.zeros_like(rows))
        _, lat = to_ll.transform(np.asarray(xs), np.asarray(ys))
        nod = ds.nodata
    valid = np.isfinite(z) & (z > 0)
    if nod is not None and np.isfinite(nod):
        valid &= z != nod
    w = np.cos(np.radians(lat))[:, None] * np.ones_like(z)
    return weighted_quantiles(z[valid], w[valid]), int(valid.sum())


def build() -> dict:
    tiq, n_ti = ti_quantiles()
    ref = {
        "thermal_inertia": {"unit": "tiu", "source": thermal_inertia.SOURCE, "n_pixels": n_ti,
                            "weighting": "cos(latitude)", "quantiles": tiq},
        "dust": {"unit": "tau", "source": MCD_SOURCE + "_tauref_annual_mean", "weighting": "cos(latitude)",
                 "quantiles": [round(x, 4) for x in dust_quantiles()]},
    }
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = PROCESSED / "mars_reference_pct.json"
    out.write_text(json.dumps(ref, indent=1), encoding="utf-8")
    print("wrote", out, f"(TI pixels {n_ti}; TI median {tiq[50]}, dust median {ref['dust']['quantiles'][50]})")
    return ref


if __name__ == "__main__":
    build()
