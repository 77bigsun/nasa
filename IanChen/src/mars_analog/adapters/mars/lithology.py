"""lithology: SIM 3292 geologic unit at the target centre, its rock group (A5 mapping), and the units in the circle.

The shapefile SIM3292_Global_Geology.shp is in Mars lon/lat (+R=3396190); the point is converted to the layer CRS
(whatever it is) and tested against the unit polygons. Area shares inside the circle use a local equal-area projection.
Group names come from data/mappings/sim3292_unit_groups.csv (A5); missing mapping -> group None.
Citation: Tanaka, K.L., Skinner, J.A., Jr., Dohm, J.M., et al. (2014) Geologic map of Mars. USGS Scientific
Investigations Map 3292, scale 1:20,000,000. https://doi.org/10.3133/sim3292
"""
from __future__ import annotations

import csv
from functools import lru_cache

import numpy as np

from ...paths import MAPPINGS, MARS_LONLAT, R_MARS, RAW_MARS

SOURCE = "usgs_sim3292"
UNIT_FIELD = "Unit"


def shapefile():
    hits = sorted((RAW_MARS / "sim3292").rglob("*.shp"))
    pick = [p for p in hits if "geolog" in p.name.lower() and "unit" not in p.name.lower()] or \
           [p for p in hits if "unit" in p.name.lower()] or hits
    return pick[0] if pick else None


@lru_cache(maxsize=1)
def layer():
    import geopandas as gpd
    p = shapefile()
    if p is None:
        raise FileNotFoundError("SIM3292 shapefile not found under data/raw/mars/sim3292/")
    g = gpd.read_file(p)
    return g[[c for c in g.columns if c in (UNIT_FIELD, "UnitDesc", "geometry")]]


@lru_cache(maxsize=1)
def unit_groups() -> dict:
    f = MAPPINGS / "sim3292_unit_groups.csv"
    if not f.exists():
        return {}
    with open(f, encoding="utf-8") as fh:
        return {r["unit"]: r["mars_group"] for r in csv.DictReader(fh)}


def _disc(lat, lon, radius_km, n=72):
    from shapely.geometry import Polygon
    d = radius_km * 1000 / R_MARS
    p0, l0 = np.radians(lat), np.radians(lon)
    b = np.linspace(0, 2 * np.pi, n, endpoint=False)
    p = np.arcsin(np.sin(p0) * np.cos(d) + np.cos(p0) * np.sin(d) * np.cos(b))
    l = l0 + np.arctan2(np.sin(b) * np.sin(d) * np.cos(p0), np.cos(d) - np.sin(p0) * np.sin(p))
    return np.degrees(l), np.degrees(p)


def load(lat: float, lon: float, radius_km: float, cfg: dict | None = None) -> dict:
    from pyproj import Transformer
    from shapely.geometry import Point, Polygon
    try:
        g = layer()
    except Exception as e:
        return {"value": None, "group": None, "coverage": False, "source": SOURCE, "n_pixels": 0, "error": str(e)[:200]}
    tf = Transformer.from_crs(MARS_LONLAT, g.crs, always_xy=True)
    x, y = tf.transform(lon, lat)
    hit = g[g.contains(Point(x, y))]
    if hit.empty:
        return {"value": None, "group": None, "coverage": False, "source": SOURCE, "n_pixels": 0}
    unit = str(hit.iloc[0][UNIT_FIELD])
    desc = str(hit.iloc[0].get("UnitDesc", ""))
    lons, lats = _disc(lat, lon, radius_km)
    dx, dy = tf.transform(lons, lats)
    disc = Polygon(zip(dx, dy))
    near = g[g.intersects(disc)].copy()
    local = f"+proj=laea +lat_0={lat} +lon_0={lon} +R={R_MARS} +units=m +no_defs"   # equal-area for the shares
    import geopandas as gpd
    disc_m = gpd.GeoSeries([disc], crs=g.crs).to_crs(local).iloc[0]
    near["a"] = near.geometry.to_crs(local).intersection(disc_m).area
    share = (near.groupby(UNIT_FIELD)["a"].sum() / near["a"].sum()).sort_values(ascending=False)
    groups = unit_groups()
    return {"value": unit, "unit_desc": desc, "group": groups.get(unit), "coverage": True, "source": SOURCE,
            "n_pixels": 0,
            "units_in_radius": [{"unit": str(u), "share": round(float(s), 3), "group": groups.get(str(u))}
                                for u, s in share.head(5).items()]}
