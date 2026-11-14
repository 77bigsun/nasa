"""
【B 的暫用版】火星目標數值與火星百分位表。

IanChen（任務 A）的正式檔案 data/processed/mars_targets.json、mars_reference_pct.json 還沒交之前，
B 需要一份火星輸入才能訓練權重、做驗證。依 TASK_B「火星數值還沒好之前」的指示做一份暫用檔：
- 能從資料直接算的就算：坡度、粗糙度（HRSC-MOLA 200 m DEM 遠端讀取）、熱慣量與其百分位（TES 2007 夜間）、
  岩性（SIM3292 地質圖 → 大類）。
- 需要 MCD／SWIM 伺服器的（溫度、沙塵、SWIM 冰）先用 TASK_A A2 表上「之前實際測過」的參考值。
- 輸出到 data/provisional/，不會覆蓋 IanChen 的檔案。正式檔一到，config.load_mars_targets() 會自動改用正式檔。

資料來源：
- Fergason, R.L., Hare, T.M., Laura, J. (2018) HRSC and MOLA Blended Digital Elevation Model at 200m v2. USGS Astrogeology.
  https://astrogeology.usgs.gov/search/map/mars_mgs_mola_mex_hrsc_blended_dem_global_200m （NASA PDS 相關產品）
- Putzig, N.E., Mellon, M.T. (2007) Apparent thermal inertia and the surface heterogeneity of Mars. Icarus 191, 68–94.
  TES 全球夜間熱慣量圖 MGS-M-TES-5-TIMAP-V1.0（NASA PDS Geosciences Node）
- Tanaka, K.L. et al. (2014) Geologic Map of Mars. USGS SIM 3292. https://doi.org/10.3133/sim3292
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np

from .paths import PROVISIONAL, RAW, ROOT

MARS_R = 3396190.0
DEM_200M = ("/vsicurl/https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars/"
            "HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif")
TES_IMG = RAW / "tes" / "global_ti_night_2007.img"
SIM3292_SHP = (RAW / "sim3292_database" / "SIM3292_MarsGlobalGeologicGIS_20M" / "SIM3292_Shapefiles"
               / "SIM3292_Global_Geology.shp")

# 暫用目標（座標說明見 docs/WORKLOG_B_1114.md）。Arcadia 用 A2 參考值所在的 47.2, -175.7。
TARGETS = [
    {"id": "jezero", "name": "Jezero Crater delta", "lat": 18.38, "lon": 77.58, "radius_km": 25,
     "missions": ["geology", "rover"]},
    {"id": "gale", "name": "Gale Crater (Aeolis Mons / Curiosity area)", "lat": -5.4, "lon": 137.8, "radius_km": 25,
     "missions": ["geology", "rover"]},
    {"id": "arcadia", "name": "Arcadia Planitia (shallow ice)", "lat": 47.2, "lon": -175.7, "radius_km": 50,
     "missions": ["isru_base", "landing"]},
]

# TASK_A A2「用來檢查程式的參考值」（之前實際用 MCD v6.2、SWIM 量過的）
A2_REFERENCE = {
    "jezero": {"tsurf_mean_c": -49.5, "swim_ci": -0.19, "dust_tau": 0.55, "dust_pct": 0.87, "ti_ref": 281},
    "gale": {"tsurf_mean_c": -50.9, "swim_ci": 0.06, "dust_tau": 0.46, "dust_pct": 0.73, "ti_ref": 433},
    "arcadia": {"tsurf_mean_c": -75.9, "swim_ci": 0.51, "dust_tau": 0.35, "dust_pct": 0.42, "ti_ref": 241},
}

# SIM3292 地質單元 → 火星大類（暫用，依單元描述的關鍵字；正式版是 IanChen 的 sim3292_unit_groups.csv）
def unit_to_group(unit: str, desc: str) -> str:
    d = desc.lower()
    if "polar" in d:
        return "polar_layered"
    if "volcanic" in d:
        return "basalt"
    if "impact" in d or "highland" in d:
        return "impact_breccia_carbonate"   # 高地 = 撞擊角礫化的古老地殼
    if "basin" in d:
        return "mudstone_clastic"           # 盆地充填的細粒沉積
    return "clastic"                        # transition / lowland / apron / outflow


def _ca_env():
    """GDAL 用 curl 讀遠端檔；防毒攔截 HTTPS 時要給它系統憑證。"""
    pem = ROOT / "data" / "ca_bundle_windows.pem"
    if pem.exists():
        os.environ.setdefault("CURL_CA_BUNDLE", str(pem))
        os.environ.setdefault("GDAL_CURL_CA_BUNDLE", str(pem))


def _dist_km(lat0, lon0, lat, lon):
    p0, p = np.radians(lat0), np.radians(lat)
    dlat, dlon = p - p0, np.radians(lon - lon0)
    a = np.sin(dlat / 2) ** 2 + np.cos(p0) * np.cos(p) * np.sin(dlon / 2) ** 2
    return 2 * MARS_R / 1000 * np.arcsin(np.sqrt(a))


def terrain(lat, lon, radius_km):
    import rasterio
    from rasterio.windows import from_bounds
    from scipy.ndimage import uniform_filter

    _ca_env()
    dlat = radius_km / (MARS_R / 1000) * 180 / math.pi + 0.02
    dlon = dlat / max(0.05, math.cos(math.radians(lat)))
    env = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
               GDAL_HTTP_MULTIRANGE="YES", VSI_CACHE="TRUE")
    try:  # 防毒攔截 HTTPS 時 GDAL 的 curl 會失敗 → 改用 Python（truststore）讀遠端位元組
        import truststore
        truststore.inject_into_ssl()
        import fsspec
        src, opener = DEM_200M.replace("/vsicurl/", ""), fsspec.filesystem("http", block_size=8 * 2**20)
    except ImportError:
        src, opener = DEM_200M, None
    with rasterio.Env(**env), rasterio.open(src, opener=opener) as ds:
        w = from_bounds(lon - dlon, lat - dlat, lon + dlon, lat + dlat, ds.transform)
        dem = ds.read(1, window=w, masked=True).astype("float64").filled(np.nan)
        tr = ds.window_transform(w)
        res = ds.res[0]
    dy = MARS_R * math.radians(res)
    dx = dy * math.cos(math.radians(lat))
    gy, gx = np.gradient(dem, dy, dx)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    m = uniform_filter(dem, 5)
    m2 = uniform_filter(dem * dem, 5)
    rough = np.sqrt(np.clip(m2 - m * m, 0, None))           # 5×5 像素（約 1 km）視窗的高程標準差
    rows, cols = np.indices(dem.shape)
    plon = tr.c + (cols + 0.5) * tr.a
    plat = tr.f + (rows + 0.5) * tr.e
    inside = _dist_km(lat, lon, plat, plon) <= radius_km
    inside[:2, :] = inside[-2:, :] = inside[:, :2] = inside[:, -2:] = False   # 邊緣視窗不完整
    return {"slope_deg": float(np.nanmedian(slope[inside])), "roughness_m": float(np.nanmedian(rough[inside])),
            "n_pixels": int(np.isfinite(slope[inside]).sum())}


def tes_global():
    a = np.fromfile(TES_IMG, dtype=">i2").reshape(3600, 7200).astype("float32")
    a[a <= 0] = np.nan
    lat = 90 - (np.arange(3600) + 0.5) / 20
    lon = -180 + (np.arange(7200) + 0.5) / 20
    return a, lat, lon


def weighted_quantiles(values, weights, qs):
    o = np.argsort(values)
    v, w = values[o], weights[o]
    c = (np.cumsum(w) - 0.5 * w) / w.sum()
    return np.interp(qs, c, v)


def build(out_dir: Path = PROVISIONAL):
    import geopandas as gpd
    import pyproj
    from shapely.geometry import Point

    ti, tlat, tlon = tes_global()
    wt = np.cos(np.radians(tlat))[:, None] * np.ones_like(ti)
    ok = np.isfinite(ti)
    qs = np.linspace(0, 1, 101)
    ti_q = weighted_quantiles(ti[ok], wt[ok], qs)

    def ti_pct(x):
        o = np.argsort(ti[ok])
        v, w = ti[ok][o], wt[ok][o]
        return float(np.interp(x, v, np.cumsum(w) / w.sum()))

    # 火星沙塵百分位：fetch_mcd.py 有全球圖才用；沒有就只能用 A2 參考值，quantiles 留空
    ref = {"thermal_inertia": {"unit": "tiu", "source": "tes_night_2007", "quantiles": [float(x) for x in ti_q]},
           "dust": {"unit": "tau", "source": "mcd_v6.2_tauref_annual", "quantiles": None,
                    "note": "provisional: target dust percentiles taken from TASK_A A2 reference values"}}
    (out_dir / "mars_reference_pct_provisional.json").write_text(json.dumps(ref, indent=1), encoding="utf-8")

    geo = gpd.read_file(SIM3292_SHP)
    tf = pyproj.Transformer.from_crs("+proj=longlat +R=3396190 +no_defs", geo.crs, always_xy=True)

    out = {"_provisional": True,
           "_note": "B 製作的暫用火星目標檔（IanChen 的 mars_targets.json 交了之後自動不再使用）。",
           "targets": {}}
    for t in TARGETS:
        r = A2_REFERENCE[t["id"]]
        print("target", t["id"], flush=True)
        try:
            ter = terrain(t["lat"], t["lon"], t["radius_km"])
            ter_ok = True
        except Exception as e:  # noqa: BLE001
            print("  ! DEM 遠端讀取失敗：", e)
            ter, ter_ok = {"slope_deg": None, "roughness_m": None, "n_pixels": 0}, False
        d = _dist_km(t["lat"], t["lon"], tlat[:, None], tlon[None, :])
        sel = (d <= t["radius_km"]) & np.isfinite(ti)
        if sel.sum() == 0:  # 半徑內沒有 TES 像素中心 → 取最近的有效像素
            dd = np.where(np.isfinite(ti), d, np.inf)
            sel = dd == dd.min()
        ti_val = float(np.nanmedian(ti[sel]))
        x, y = tf.transform(t["lon"], t["lat"])
        hit = geo[geo.contains(Point(x, y))]
        unit = hit.Unit.iloc[0] if len(hit) else None
        desc = hit.UnitDesc.iloc[0] if len(hit) else ""
        group = unit_to_group(unit, desc) if unit else None
        p_ice = (r["swim_ci"] + 1) / 2
        out["targets"][t["id"]] = {
            **{k: t[k] for k in ("name", "lat", "lon", "radius_km", "missions")},
            "slope": {"value": ter["slope_deg"], "coverage": ter_ok, "unit": "deg", "source": "hrsc_mola_200m",
                      "n_pixels": ter["n_pixels"]},
            "roughness": {"value": ter["roughness_m"], "coverage": ter_ok, "unit": "m", "source": "hrsc_mola_200m",
                          "window_px": 5},
            "thermal_inertia": {"value": ti_val, "pct": ti_pct(ti_val), "coverage": True, "unit": "tiu",
                                "source": "tes_ti_night_2007", "n_pixels": int(sel.sum()), "a2_reference": r["ti_ref"]},
            "lithology": {"value": unit, "unit_desc": desc, "group": group, "coverage": unit is not None,
                          "source": "usgs_sim3292"},
            "ice": {"value": r["swim_ci"], "p": p_ice, "coverage": True, "source": "swim (TASK_A A2 reference value)"},
            "temperature": {"value": r["tsurf_mean_c"], "coverage": True, "unit": "C",
                            "source": "mcd_v62_tsurf (TASK_A A2 reference value)"},
            "diurnal_range": {"value": None, "coverage": True, "unit": "C",
                              "source": "earth_extreme_pct 不需要火星值；MCD 日溫差待 IanChen 補"},
            "aridity": {"value": "max", "coverage": True, "source": "fixed_max"},
            "barrenness": {"value": 0.0, "coverage": True, "source": "fixed_zero_ndvi"},
            "dust": {"value": r["dust_tau"], "pct": r["dust_pct"], "coverage": True, "unit": "tau",
                     "source": "mcd_v62_tauref (TASK_A A2 reference value)"},
        }
        print("  ", {k: (v.get("value"), v.get("pct", v.get("group"))) for k, v in out["targets"][t["id"]].items()
                     if isinstance(v, dict)}, flush=True)
    (out_dir / "mars_targets_provisional.json").write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                                         encoding="utf-8")
    return out


if __name__ == "__main__":
    build()
