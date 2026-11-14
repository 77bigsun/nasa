"""
放大（zoom）用的 GEE 影像：一個小方框（預設 0.5° × 0.5°）在約 1 km 子格（0.01°）上的地球變數。

和全球 0.1° 版（gee_layers.py）用同一批資料、同一套算法，差別只有：
- 地形預設改用 Copernicus GLO-30，在當地 UTM（極區用極地立體投影）粗化到 200 m 再算坡度、5×5 粗糙度，
  然後取子格內中位數。這是 TASK_B 原訂做法（火星 DEM 也是 200 m）；全球版為了趕時間用 GMTED2010。
  加 --dem gmted 可以改回和全球版完全一樣的資料。
- NDVI 改用 MODIS MOD13Q1（250 m；全球版是 MOD13A2 1 km）。
- 地表溫度（1 km）、反照率（500 m）、乾燥指數（約 1 km）、陸地／水體／冰雪比例：和全球版同一份資料。
- 另外抓 NASA HLS（Harmonized Landsat Sentinel-2，30 m）的真彩色中位數合成，只畫底圖，不計分。
  HLS 沒有涵蓋的地方（例如南極）改畫 DEM 陰影圖。

資料出處（官方規定要標出處）：
- Copernicus DEM GLO-30, ESA, https://doi.org/10.5270/ESA-c5d3d65
- MODIS MOD13Q1 v061: Didan, K. (2021), https://doi.org/10.5067/MODIS/MOD13Q1.061 （NASA Earthdata）
- HLSS30 / HLSL30 v2.0: Masek, J. et al. (2021), https://doi.org/10.5067/HLS/HLSS30.002 ,
  https://doi.org/10.5067/HLS/HLSL30.002 （NASA LP DAAC）
- 其餘同 gee_layers.py（MOD11A2/MYD11A2、MCD43A3、MCD12Q1、MOD44W、GMTED2010、Global Aridity Index v3）
"""
from __future__ import annotations

import time

import numpy as np

from . import _gee  # noqa: F401  （順便套用 truststore）
from . import gee_layers as L
from ._gee import NODATA

import ee  # noqa: E402

HLS_DATES = ("2022-01-01", "2025-01-01")
HLS_MAX_CLOUD = 20


def local_crs(lat: float, lon: float) -> str:
    """等距的當地投影：一般用 UTM，北緯 80° 以北用 EPSG:3413，南緯 80° 以南用 EPSG:3031。"""
    if lat > 80:
        return "EPSG:3413"
    if lat < -80:
        return "EPSG:3031"
    zone = int((lon + 180) // 6) % 60 + 1
    return f"EPSG:{(32600 if lat >= 0 else 32700) + zone}"


def transform(x0: float, y0: float, res: float) -> list[float]:
    return [res, 0, x0, 0, -res, y0]


def _on(img: ee.Image, tf: list[float]) -> ee.Image:
    return img.reproject(crs="EPSG:4326", crsTransform=tf)


def terrain(lat: float, lon: float, tf: list[float], dem: str = "copernicus") -> ee.Image:
    """坡度（度）、粗糙度（5×5 視窗高程標準差，m）、海拔（m）：200 m 尺度計算，取子格內中位數。"""
    if dem == "gmted":
        base = ee.Image("USGS/GMTED2010_FULL").select("mea").toFloat()
        proj = base.projection()
    else:
        col = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM")
        dem30 = col.mosaic().setDefaultProjection(col.first().projection())
        base = (dem30.reduceResolution(ee.Reducer.mean(), maxPixels=1024)
                .reproject(crs=local_crs(lat, lon), scale=200))
        proj = None
    slope = ee.Terrain.slope(base).rename("slope_deg")
    rough = base.reduceNeighborhood(ee.Reducer.stdDev(), ee.Kernel.square(2, "pixels")).rename("roughness_m")
    img = ee.Image.cat([slope, rough, base.rename("elev_m")])
    if proj is not None:
        img = img.setDefaultProjection(proj)
    return _on(img.reduceResolution(ee.Reducer.median(), maxPixels=1024), tf)


def climate(tf: list[float]) -> ee.Image:
    """MODIS 地表溫度多年平均（同全球版）。"""
    return _on(L.lst_climatology(), tf)


def ndvi_q1() -> ee.Image:
    col = ee.ImageCollection("MODIS/061/MOD13Q1").filterDate("2015-01-01", "2025-01-01").select("NDVI")
    return col.mean().multiply(0.0001).rename("ndvi_mean")


def surface(tf: list[float]) -> ee.Image:
    """反照率（ATI 用）、NDVI（250 m）、乾燥指數。"""
    return _on(ee.Image.cat([L.albedo_climatology(), ndvi_q1(), L.aridity_index()]), tf)


def masks(tf: list[float]) -> ee.Image:
    """子格內的陸地、冰雪、裸地比例（MCD12Q1 500 m）與水體比例（MOD44W 250 m）。"""
    lc = (ee.ImageCollection("MODIS/061/MCD12Q1").filterDate("2022-01-01", "2023-01-01")
          .first().select("LC_Type1"))
    fr = ee.Image.cat([lc.neq(17).unmask(0).rename("land_frac"), lc.eq(15).unmask(0).rename("ice_frac"),
                       lc.eq(16).unmask(0).rename("barren_frac")]).toFloat()
    fr = fr.setDefaultProjection(lc.projection()).reduceResolution(ee.Reducer.mean(), maxPixels=4096)
    wm = (ee.ImageCollection("MODIS/006/MOD44W").sort("system:time_start", False).first()
          .select("water_mask"))
    w = wm.unmask(1).toFloat().rename("water_frac")
    w = w.setDefaultProjection(wm.projection()).reduceResolution(ee.Reducer.mean(), maxPixels=4096)
    return _on(ee.Image.cat([fr, w]), tf)


def hls_collection(region: ee.Geometry) -> ee.ImageCollection:
    def prep(c):
        return (ee.ImageCollection(c).filterBounds(region).filterDate(*HLS_DATES)
                .filter(ee.Filter.lt("CLOUD_COVERAGE", HLS_MAX_CLOUD)).select(["B4", "B3", "B2"]))
    return prep("NASA/HLS/HLSS30/v002").merge(prep("NASA/HLS/HLSL30/v002"))


def rgb(region: ee.Geometry, tf: list[float]) -> tuple[ee.Image | None, int]:
    col = hls_collection(region)
    n = int(col.size().getInfo())
    if n == 0:
        return None, 0
    return _on(col.median().rename(["red", "green", "blue"]), tf), n


def hillshade(lat: float, lon: float, tf: list[float]) -> ee.Image:
    col = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM")
    dem30 = col.mosaic().setDefaultProjection(col.first().projection())
    base = dem30.reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(crs=local_crs(lat, lon), scale=100)
    return _on(ee.Terrain.hillshade(base).toFloat().rename("hillshade"), tf)


class TooBig(Exception):
    pass


def fetch(img: ee.Image, bands: list[str], x0: float, y0: float, w: int, h: int, res: float) -> dict:
    """computePixels：在 (x0, y0) 左上角、解析度 res 度的 w × h 網格上抓 bands。失敗會退避重試。"""
    req = {
        "expression": img.select(bands).unmask(NODATA, False),
        "fileFormat": "NUMPY_NDARRAY",
        "grid": {
            "dimensions": {"width": int(w), "height": int(h)},
            "affineTransform": {"scaleX": res, "shearX": 0, "translateX": x0,
                                "shearY": 0, "scaleY": -res, "translateY": y0},
            "crsCode": "EPSG:4326",
        },
    }
    last = None
    for attempt in range(6):
        try:
            arr = ee.data.computePixels(req)
            out = {}
            for b in bands:
                a = np.asarray(arr[b], dtype="float32")
                a[a <= NODATA + 1] = np.nan
                out[b] = a
            return out
        except Exception as e:  # noqa: BLE001  （配額、逾時、暫時性錯誤 → 退避重試）
            last = e
            msg = str(e)
            if "too large" in msg or "Too many pixels" in msg or "memory" in msg.lower():
                raise TooBig(msg) from e
            time.sleep(min(60, 2 ** attempt + np.random.rand()))
    raise RuntimeError(f"computePixels failed at ({x0:.2f}, {y0:.2f}): {last}")
