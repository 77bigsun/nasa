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
- Copernicus DEM GLO-30, ESA, https://doi.org/10.5270/ESA-c5d3d65（11/14 起用 GEE 新版 GLO30_2024_1，見 gee_layers.glo30）
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
HLS_MAX_SCENES = 80     # 取雲量最低的 80 張做中位數（11/14 本機：不設上限時一個方框有數百張，GEE 記憶體不足）


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
        col = L.glo30()
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
    return _on(L.lst_climatology(grid_mean=False), tf)   # 原生 1 km（全球版預設會聚合到 0.1°）


def ndvi_q1() -> ee.Image:
    col = ee.ImageCollection("MODIS/061/MOD13Q1").filterDate("2015-01-01", "2025-01-01").select("NDVI")
    return col.mean().multiply(0.0001).rename("ndvi_mean")


def surface(tf: list[float]) -> ee.Image:
    """反照率（ATI 用）、NDVI（250 m）、乾燥指數。"""
    return _on(ee.Image.cat([L.albedo_climatology(grid_mean=False), ndvi_q1(), L.aridity_index(grid_mean=False)]), tf)


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


def utm_zones(lon_w: float, lon_e: float) -> list[int]:
    """方框經度範圍涵蓋的 UTM 區號，前後各多一區（MGRS 圖幅會跨區重疊）。"""
    zw, ze = int((lon_w + 180) // 6) + 1, int((lon_e + 180) // 6) + 1
    return sorted({(z - 1) % 60 + 1 for z in range(zw - 1, ze + 2)})


def hls_collection(region: ee.Geometry, lon_range: tuple[float, float] | None = None,
                   lat: float | None = None) -> ee.ImageCollection:
    # 11/14 本機：只用 filterBounds 會抓進大量 UTM 1／60 區（換日線）的影像——它們的 footprint 跨換日線被當成全球，
    # 一個蒙古的方框選到 1,756 張、大多不在框內。所以再用影像編號（T<區號><圖幅>_<日期>）限定 UTM 區。
    # 只挑「雲量最低」會挑到冬天的雪景（雪不算雲），所以南北回歸線以外先限定當地夏季，夏季沒有影像才用全年。
    zf = None
    if lon_range is not None:
        zf = ee.Filter.Or(*[ee.Filter.stringStartsWith("system:index", f"T{z:02d}") for z in utm_zones(*lon_range)])

    def prep(c):
        col = (ee.ImageCollection(c).filterBounds(region).filterDate(*HLS_DATES)
               .filter(ee.Filter.lt("CLOUD_COVERAGE", HLS_MAX_CLOUD)))
        if zf is not None:
            col = col.filter(zf)
        return col.select(["B4", "B3", "B2"])
    col = prep("NASA/HLS/HLSS30/v002").merge(prep("NASA/HLS/HLSL30/v002"))
    if lat is not None and abs(lat) > 23.5:
        summer = col.filter(ee.Filter.calendarRange(6, 9, "month") if lat > 0
                            else ee.Filter.calendarRange(12, 3, "month"))
        col = ee.ImageCollection(ee.Algorithms.If(summer.size().gt(0), summer, col))
    return col.sort("CLOUD_COVERAGE").limit(HLS_MAX_SCENES)


def rgb(region: ee.Geometry, tf: list[float], lon_range: tuple[float, float] | None = None,
        lat: float | None = None) -> tuple[ee.Image | None, int]:
    col = hls_collection(region, lon_range, lat)
    n = int(col.size().getInfo())
    if n == 0:
        return None, 0
    return _on(col.median().rename(["red", "green", "blue"]), tf), n


def hillshade(lat: float, lon: float, tf: list[float]) -> ee.Image:
    col = L.glo30()
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


# ---------------- 最佳小區的地點細節（R1 無法全球評估的部分） ----------------
# 高解析坡度：北緯 60° 以北 ArcticDEM v3 2 m 鑲嵌、南緯 60° 以南 REMA v1.1 8 m、其他 Copernicus GLO-30。
# 雷達後向散射：Sentinel-1 C 波段（VV、VH，dB，2022–2024 中位數）、ALOS-2 PALSAR-2 L 波段年度鑲嵌
# （HH、HV，dB = 10·log10(DN²) − 83）。地球和火星波段不同，只能當岩石／粗糙度的相對代理。
# 出處：Porter, C., et al. (2018) ArcticDEM, doi:10.7910/DVN/OHHUKH；Howat, I., et al. (2019) REMA,
# The Cryosphere 13, 665–674；Copernicus Sentinel-1 GRD（ESA）；Shimada, M., et al. (2014) PALSAR mosaics, RSE 155, 13–31。
def _hires_dem(lat: float):
    if lat >= 60:
        return ee.Image("UMN/PGC/ArcticDEM/V3/2m_mosaic").select("elevation"), 2, "ArcticDEM v3 2 m"
    if lat <= -60:
        return ee.Image("UMN/PGC/REMA/V1_1/8m").select("elevation"), 8, "REMA v1.1 8 m"
    col = L.glo30()
    return col.mosaic().setDefaultProjection(col.first().projection()), 30, "Copernicus GLO-30"


def site_details(lat: float, lon: float, half_m: float = 500) -> dict:
    """以 (lat, lon) 為中心、邊長 2·half_m 的方塊：高解析坡度中位數／90 百分位／最大、雷達後向散射平均。一次 getInfo。"""
    box = ee.Geometry.Point([lon, lat]).buffer(half_m).bounds()
    dem, res, dem_name = _hires_dem(lat)
    slope = ee.Terrain.slope(dem).rename("slope")
    st = slope.reduceRegion(ee.Reducer.percentile([50, 90]).combine(ee.Reducer.max(), "", True),
                            box, scale=res, maxPixels=1e9, bestEffort=True)
    def s1col(d0, d1):
        return (ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(box).filterDate(d0, d1)
                .filter(ee.Filter.eq("instrumentMode", "IW"))
                .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH")).select(["VV", "VH"]))
    # 11/14 本機：Sentinel-1B 2021 年底故障後，中亞等地 2022–2024 沒有 IW 影像（蒙古西部測試點 0 張）；
    # 這時改用 2017–2021（S1A+S1B），並記下用了哪段時間。
    s1r, s1o = s1col("2022-01-01", "2025-01-01"), s1col("2017-01-01", "2022-01-01")
    recent = s1r.size().gt(0)
    s1c = ee.ImageCollection(ee.Algorithms.If(recent, s1r, s1o))
    s1_period = ee.Algorithms.If(recent, "2022–2024", ee.Algorithms.If(s1o.size().gt(0), "2017–2021", None))
    s1 = ee.Algorithms.If(s1c.size().gt(0),
                          s1c.median().reduceRegion(ee.Reducer.mean(), box, scale=10, maxPixels=1e9, bestEffort=True),
                          ee.Dictionary({}))
    pc = (ee.ImageCollection("JAXA/ALOS/PALSAR/YEARLY/SAR_EPOCH").filterDate("2019-01-01", "2024-01-01")
          .select(["HH", "HV"]))
    pdb = pc.median().toFloat().pow(2).log10().multiply(10).subtract(83)
    pal = ee.Algorithms.If(pc.size().gt(0),
                           pdb.reduceRegion(ee.Reducer.mean(), box, scale=25, maxPixels=1e9, bestEffort=True),
                           ee.Dictionary({}))
    d = ee.Dictionary({"slope": st, "s1": s1, "s1_period": s1_period, "s1_n": s1c.size(),
                       "palsar": pal}).getInfo()
    sl, s1d, pd_ = d.get("slope") or {}, d.get("s1") or {}, d.get("palsar") or {}
    r = lambda x, n=2: None if x is None else round(float(x), n)  # noqa: E731
    return {"box_m": int(2 * half_m), "dem": dem_name, "dem_res_m": res,
            "slope_p50_deg": r(sl.get("slope_p50")), "slope_p90_deg": r(sl.get("slope_p90")),
            "slope_max_deg": r(sl.get("slope_max")),
            "s1_vv_db": r(s1d.get("VV")), "s1_vh_db": r(s1d.get("VH")),
            "s1_period": d.get("s1_period"), "s1_scenes": d.get("s1_n"),
            "palsar_hh_db": r(pd_.get("HH")), "palsar_hv_db": r(pd_.get("HV"))}
