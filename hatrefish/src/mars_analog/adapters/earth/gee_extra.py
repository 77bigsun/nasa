"""
地球端補充圖層（全球 0.1°），給測試項目 R4、R5、R6 用；由 scripts/fetch_earth_extra_gee.py 下載。

- 每月沙塵（R6 季節曲線）：MERRA-2 DUEXTTAU，2019–2023 每日 12 UTC，依月份平均 → dust_m01…dust_m12
- 每月地表溫度（R6 季節曲線）：MODIS MOD11A2 + MYD11A2，2015–2024，(日 + 夜) / 2 依月份平均（°C）→ lst_m01…lst_m12
- 冰河比例（R5 冰河距離、R1／R4 無冰覆蓋）：GLIMS 冰河輪廓畫成 0.01° 遮罩，再取 0.1° 格內比例 → glacier_frac
  （離最近冰河的距離 glacier_km 在本機用 KD 樹算，見 fetch_earth_extra_gee.py）
- 生長季高峰 NDVI（R1、R4、R5 的「夏季也沒有植被」）：MOD13A2 2015–2024 第 90 百分位 → ndvi_p90
- 礦物指標（R4）：ASTER GED AG100 v003 熱紅外放射率（band 10–14），Ninomiya (2003) 指標
    石英 QI = B11² / (B10 · B12)、碳酸鹽 CI = B13 / B14、鎂鐵質 MI = B12 / B13 → aster_qi、aster_ci、aster_mi

資料出處：
- MERRA-2: Gelaro, R., et al. (2017), J. Climate 30, 5419–5454; GMAO (2015) doi:10.5067/LTVB4GPCOTK2
- MODIS LST: Wan, Z., Hook, S., Hulley, G. (2021) MOD11A2/MYD11A2 v061, doi:10.5067/MODIS/MOD11A2.061
- GLIMS: GLIMS Consortium (2005, updated), Global Land Ice Measurements from Space glacier database,
  NSIDC, doi:10.7265/N5V98602
- ASTER GED: Hulley, G., Hook, S. (2015) AG100 v003, NASA LP DAAC, doi:10.5067/Community/ASTER_GED/AG100.003
- Ninomiya, Y. (2003). A stabilized vegetation index and several mineralogic indices defined for ASTER VNIR and
  SWIR data. IGARSS 2003（TIR 指標見 Ninomiya, Fu & Cudahy 2005, Remote Sensing of Environment 99, 127–139）
"""
from __future__ import annotations

from ._gee import on_grid  # noqa: F401  （也會套用 truststore）
from .gee_layers import land_mean_on_grid

import ee  # noqa: E402

MONTHS = range(1, 13)


MERRA_AER = "NASA/GSFC/MERRA/aer/2"
DUST_YEARS = range(2019, 2024)


def dust_monthly() -> ee.Image:
    # 直接列出每天 12 UTC 的影像編號（YYYYMMDDHH）。11/14 本機測試：原本 filterDate + calendarRange(hour) +
    # calendarRange(month) 的寫法在 GEE 上「User memory limit exceeded」（連 10×10 格、單一月份都失敗）；
    # 列編號的寫法 12 個月一次約 8 秒，數值相同（Atacama 1 月 0.0109）。
    import calendar
    bands = []
    for m in MONTHS:
        ims = [ee.Image(f"{MERRA_AER}/{y}{m:02d}{d:02d}12").select("DUEXTTAU")
               for y in DUST_YEARS for d in range(1, calendar.monthrange(y, m)[1] + 1)]
        bands.append(ee.ImageCollection.fromImages(ims).mean().rename(f"dust_m{m:02d}"))
    return on_grid(ee.Image.cat(bands))


def lst_monthly(months=MONTHS) -> ee.Image:
    def prep(c):
        return (ee.ImageCollection(c).filterDate("2015-01-01", "2025-01-01")
                .select(["LST_Day_1km", "LST_Night_1km"]))
    col = prep("MODIS/061/MOD11A2").merge(prep("MODIS/061/MYD11A2"))
    proj = ee.Image(col.first()).select("LST_Day_1km").projection()
    bands = []
    for m in months:
        mm = col.filter(ee.Filter.calendarRange(m, m, "month")).mean().multiply(0.02).subtract(273.15)
        bands.append(mm.select("LST_Day_1km").add(mm.select("LST_Night_1km")).divide(2).rename(f"lst_m{m:02d}"))
    # 11/14：和全球年均地表溫一樣，先遮水體再取 0.1° 格內平均（gee_layers.land_mean_on_grid）
    return land_mean_on_grid(ee.Image.cat(bands), proj)


def ndvi_peak() -> ee.Image:
    """生長季高峰 NDVI：MOD13A2 2015–2024 所有 16 天合成的第 90 百分位，遮水體後取 0.1° 格內平均 → ndvi_p90。
    11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原看起來和沙漠一樣「荒」，所以測試另外要求「夏季也沒有植被」。"""
    col = ee.ImageCollection("MODIS/061/MOD13A2").filterDate("2015-01-01", "2025-01-01").select("NDVI")
    proj = ee.Image(col.first()).projection()
    p90 = col.reduce(ee.Reducer.percentile([90])).multiply(0.0001).rename("ndvi_p90")
    return land_mean_on_grid(p90, proj)


GLIMS_IDS = ("GLIMS/current", "GLIMS/20230607", "GLIMS/20210914")


def glims_id() -> str:
    """GEE 上 GLIMS 的資產編號（新版會換日期），依序試到存在的那個。"""
    for cid in GLIMS_IDS:
        try:
            ee.data.getAsset(cid)
            return cid
        except Exception:  # noqa: BLE001
            continue
    raise RuntimeError(f"GLIMS not found in Earth Engine under {GLIMS_IDS}; check the data catalog for the current ID")


def glacier_fraction() -> ee.Image:
    fc = ee.FeatureCollection(glims_id())
    mask = ee.Image(0).byte().paint(fc, 1).rename("glacier_frac").toFloat()
    mask = mask.reproject(crs="EPSG:4326", scale=1000)
    return on_grid(mask.reduceResolution(ee.Reducer.mean(), maxPixels=1024))


def aster_band_names() -> list[str]:
    return ee.Image("NASA/ASTER_GED/AG100_003").bandNames().getInfo()


def aster_indices() -> ee.Image:
    img = ee.Image("NASA/ASTER_GED/AG100_003")
    names = img.bandNames().getInfo()

    def band(n):
        hit = [b for b in names if b.lower().startswith("emissivity") and b.endswith(f"band{n}")]
        if not hit:
            raise RuntimeError(f"ASTER GED: band {n} not found in {names}")
        return img.select(hit[0]).toFloat().multiply(0.001)

    b10, b11, b12, b13, b14 = (band(n) for n in (10, 11, 12, 13, 14))
    # 11/14 範圍檢查：任一波段放射率不在 0.6–1.0（多雲熱帶的壞值）就遮掉，指標超出 0.7–1.3 也遮掉
    ok = ee.Image.cat([b10, b11, b12, b13, b14]).reduce(ee.Reducer.min()).gte(0.6).And(
        ee.Image.cat([b10, b11, b12, b13, b14]).reduce(ee.Reducer.max()).lte(1.0))
    qi = b11.multiply(b11).divide(b10.multiply(b12)).rename("aster_qi")
    ci = b13.divide(b14).rename("aster_ci")
    mi = b12.divide(b13).rename("aster_mi")
    idx = ee.Image.cat([qi, ci, mi])
    idx = idx.updateMask(ok).updateMask(idx.gte(0.7).And(idx.lte(1.3)))
    # 先在 1 km 平均、再取 0.1° 格內平均（原本從金字塔取樣）
    proj100 = img.select(0).projection()
    idx = idx.setDefaultProjection(proj100).reduceResolution(ee.Reducer.mean(), maxPixels=256) \
        .reproject(crs="EPSG:4326", scale=1000)
    return on_grid(idx.reduceResolution(ee.Reducer.mean(), maxPixels=1024))
