"""Mars Climate Database (MCD v6.x) web-interface client, shared by temperature, diurnal_range and dust.

Query code adapted from the teammate's scripts/fetch_mcd.py (same parameters). The MCD web interface is meant for
moderate use, so each query is followed by a pause, and every answer is cached under data/raw/mars/mcd/.
Citation: Millour, E., Forget, F., et al. The Mars Climate Database (MCD version 6.x, version as served by the
web interface on the query date), LMD/OU/IAA/ESA/CNES.
https://www-mars.lmd.jussieu.fr
"""
from __future__ import annotations

import json
import re
import time
from functools import lru_cache

import numpy as np
import requests

from ...paths import RAW_MARS

BASE = "https://www-mars.lmd.jussieu.fr/mcd_python/"
PAUSE_S = 3
CACHE = RAW_MARS / "mcd"
SOURCE = "mcd_v6_web_climatology"


def query(var, ls, localtime, lat, lon, dust_scenario=1) -> str:
    params = {
        "var1": var, "var2": "none", "var3": "none", "var4": "none",
        "datekeyhtml": 1, "ls": ls, "localtime": localtime,
        "latitude": lat, "longitude": lon, "altitude": "10.", "zkey": 3,
        "isfixedlt": "off", "dust": dust_scenario, "hrkey": 1,
        "averaging": "off", "diumean": "off", "dpi": 80, "islog": "off",
        "colorm": "jet", "proj": "cyl", "zonmean": "off", "iswind": "off", "trans": "off",
    }
    r = requests.get(BASE + "cgi-bin/mcdcgi.py", params=params, timeout=300)
    r.raise_for_status()
    m = re.search(r"txt/[0-9a-f]+\.txt", r.text)
    if not m:
        raise RuntimeError(f"MCD returned no data file (var={var}, ls={ls}, lat={lat}, lon={lon})")
    t = requests.get(BASE + m.group(0), timeout=120)
    t.raise_for_status()
    time.sleep(PAUSE_S)
    return t.text


def parse_table(text):
    """MCD 2D ASCII table -> (column axis, row axis, values[row, col])."""
    cols, rows, vals = None, [], []
    for line in text.splitlines():
        if line.startswith("#") or line.startswith("-----") or not line.strip():
            continue
        left, _, right = line.partition("||")
        nums = [float(x) for x in right.split()]
        if left.strip().startswith("----"):
            cols = np.array(nums)
        else:
            rows.append(float(left.strip()))
            vals.append(nums)
    return cols, np.array(rows), np.array(vals)


@lru_cache(maxsize=32)
def tsurf_table(lat: float, lon: float) -> np.ndarray:
    """Surface temperature (K), rows = season (Ls), columns = local time 0..23 (the duplicate 24 h column dropped)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"tsurf_{lat:.3f}_{lon:.3f}.txt"
    if not f.exists():
        f.write_text(query("tsurf", "all", "all", lat, lon), encoding="utf-8")
    _, _, v = parse_table(f.read_text(encoding="utf-8"))
    return v[:, :-1]


@lru_cache(maxsize=1)
def global_dust(ls_step: int = 30):
    """Annual-mean dust column optical depth (tauref) on the MCD global grid: (lat axis, lon axis, values[lon, lat])."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / "dust_annual_mean.npz"
    if not f.exists():
        maps, lat, lon = [], None, None
        for ls in range(0, 360, ls_step):
            print(f"  MCD global dust map Ls={ls}")
            lat, lon, v = parse_table(query("tauref", ls, 12, "all", "all"))
            maps.append(v)
        np.savez(f, lat=lat, lon=lon, dust=np.mean(maps, axis=0))
    d = np.load(f)
    return d["lat"], d["lon"], d["dust"]


def dust_quantiles() -> list[float]:
    """101 area-weighted (cos latitude) quantiles of annual-mean dust over the whole planet."""
    lat, _, dust = global_dust()
    w = (np.cos(np.radians(lat))[None, :] * np.ones_like(dust)).ravel()
    v = dust.ravel()
    o = np.argsort(v)
    cdf = np.cumsum(w[o]) / w.sum()
    return [float(np.interp(q, cdf, v[o])) for q in np.linspace(0, 1, 101)]


def save_json(name: str, obj) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / name).write_text(json.dumps(obj, indent=1), encoding="utf-8")
