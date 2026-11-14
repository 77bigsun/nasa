"""
地球端各變數在 GEE 上的算法（每個函式回傳一張 ee.Image，之後由 _gee.download_global 下載成 0.1° 陣列）。

資料來源與引用（官方規定要標出處）：
- 陸地／水體／冰雪遮罩：MODIS MCD12Q1 v061 Land Cover Type 1（IGBP），2022。
  Friedl, M., Sulla-Menashe, D. (2022). MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500m SIN Grid V061.
  NASA EOSDIS Land Processes DAAC. https://doi.org/10.5067/MODIS/MCD12Q1.061   （NASA Earthdata）
- 地形（坡度、粗糙度、海拔）：USGS/NGA GMTED2010，7.5 角秒（約 230 m，最接近火星 200 m DEM 的原生尺度）。
  Danielson, J.J., Gesch, D.B. (2011) Global multi-resolution terrain elevation data 2010 (GMTED2010).
  USGS Open-File Report 2011-1073. https://doi.org/10.3133/ofr20111073
  ※ TASK_B 原訂 Copernicus GLO-30 粗化到 200 m；為了在 11/14 中午前跑完全球，先用 GMTED2010（原生就是 ~200 m 尺度，
    不需要從 30 m 聚合，GEE 運算量少約 40 倍）。copernicus_glo30_200m() 保留給之後替換。
- 地表溫度、日夜溫差：MODIS MOD11A2 / MYD11A2 v061（Terra + Aqua，8 天合成，1 km），2015–2024。
  Wan, Z., Hook, S., Hulley, G. (2021). https://doi.org/10.5067/MODIS/MOD11A2.061 , https://doi.org/10.5067/MODIS/MYD11A2.061
- 反照率（ATI 用）：MODIS MCD43A3 v061 白空反照率短波，2019–2023 每月 1、15 日。
  Schaaf, C., Wang, Z. (2021). https://doi.org/10.5067/MODIS/MCD43A3.061
- NDVI：MODIS MOD13A2 v061（16 天，1 km），2015–2024。Didan, K. (2021). https://doi.org/10.5067/MODIS/MOD13A2.061
- 乾燥指數：Global Aridity Index and PET Database v3（Zomer, Xu, Trabucco 2022, Scientific Data 9:409,
  https://doi.org/10.1038/s41597-022-01493-1），GEE community catalog 版本，數值 ×10000。
- 沙塵：MERRA-2 tavg1_2d_aer_Nx DUEXTTAU（沙塵消光光學厚度 550 nm），2019–2023 每日 12 UTC。
  GMAO (2015). https://doi.org/10.5067/KLICLTZ8EM9D   （NASA Earthdata／GES DISC）
"""
from __future__ import annotations

import ee

from ._gee import on_grid


def landcover_fractions() -> ee.Image:
    """每格的陸地比例（不含水體、含冰雪）、冰雪比例、水體比例。海洋在 MCD12Q1 沒資料 → 視為非陸地。"""
    lc = (ee.ImageCollection("MODIS/061/MCD12Q1").filterDate("2022-01-01", "2023-01-01")
          .first().select("LC_Type1"))
    land = lc.neq(17).unmask(0).rename("land_frac")      # 17 = 水體
    ice = lc.eq(15).unmask(0).rename("ice_frac")         # 15 = 永久冰雪
    barren = lc.eq(16).unmask(0).rename("barren_frac")   # 16 = 裸地（參考用）
    img = ee.Image.cat([land, ice, barren]).toFloat()
    proj = lc.projection()
    img = img.setDefaultProjection(proj).reduceResolution(ee.Reducer.mean(), maxPixels=4096)
    return on_grid(img)


def water_fraction() -> ee.Image:
    """MODIS MOD44W v006 水體遮罩（250 m）→ 每格水體比例。MCD12Q1 會漏掉部分大湖與海冰海岸（例如大奴湖、格陵蘭峽灣），
    這些格子坡度 = 0、NDVI ≈ 0，會被誤判成「完美的平坦荒地」，所以另外用 MOD44W 排除。
    Carroll, M. et al. (2017) MOD44W MODIS/Terra Land Water Mask Derived from MODIS and SRTM L3 Global 250m SIN Grid V006.
    https://doi.org/10.5067/MODIS/MOD44W.006 （NASA Earthdata）"""
    wm = (ee.ImageCollection("MODIS/006/MOD44W").sort("system:time_start", False).first()
          .select("water_mask"))
    img = wm.unmask(1).toFloat().rename("water_frac")     # 沒資料（外海）當水
    img = img.setDefaultProjection(wm.projection()).reduceResolution(ee.Reducer.mean(), maxPixels=8192)
    return on_grid(img)


def terrain_gmted() -> ee.Image:
    """坡度（度）、粗糙度（5×5 視窗高程標準差，m）、海拔（m），在 ~230 m 計算後取 0.1° 格內中位數。"""
    dem = ee.Image("USGS/GMTED2010_FULL").select("mea").toFloat()
    slope = ee.Terrain.slope(dem).rename("slope_deg")
    rough = dem.reduceNeighborhood(ee.Reducer.stdDev(), ee.Kernel.square(2, "pixels")).rename("roughness_m")
    img = ee.Image.cat([slope, rough, dem.rename("elev_m")]).setDefaultProjection(dem.projection())
    img = img.reduceResolution(ee.Reducer.median(), maxPixels=4096)
    return on_grid(img)


def copernicus_glo30_200m() -> ee.Image:  # pragma: no cover  （之後要換回 TASK_B 原訂資料時用）
    col = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM")
    proj30 = col.first().projection()
    dem30 = col.mosaic().setDefaultProjection(proj30)
    dem200 = dem30.reduceResolution(ee.Reducer.mean(), maxPixels=128).reproject(crs="EPSG:4326", scale=200)
    slope = ee.Terrain.slope(dem200).rename("slope_deg")
    rough = dem200.reduceNeighborhood(ee.Reducer.stdDev(), ee.Kernel.square(2, "pixels")).rename("roughness_m")
    img = ee.Image.cat([slope, rough, dem200.rename("elev_m")])
    return on_grid(img.reduceResolution(ee.Reducer.median(), maxPixels=4096))


def terrain_copernicus_antarctica() -> ee.Image:
    """南極（GMTED 沒有涵蓋）：Copernicus GLO-30 在南極立體投影 EPSG:3031 粗化到 200 m 再算坡度、粗糙度。
    用等距的極區投影，避免經緯度格在高緯度東西向像素太窄而高估坡度。
    資料：ESA Copernicus DEM GLO-30, https://doi.org/10.5270/ESA-c5d3d65 （ESA Copernicus）"""
    col = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM")
    dem30 = col.mosaic().setDefaultProjection(col.first().projection())
    dem200 = dem30.reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(crs="EPSG:3031", scale=200)
    slope = ee.Terrain.slope(dem200).rename("slope_deg")
    rough = dem200.reduceNeighborhood(ee.Reducer.stdDev(), ee.Kernel.square(2, "pixels")).rename("roughness_m")
    img = ee.Image.cat([slope, rough, dem200.rename("elev_m")])
    return on_grid(img.reduceResolution(ee.Reducer.median(), maxPixels=4096))


def lst_climatology() -> ee.Image:
    """MODIS Terra+Aqua 2015–2024 多年平均：日溫、夜溫（°C）、日夜差（K）。"""
    def prep(c):
        return (ee.ImageCollection(c).filterDate("2015-01-01", "2025-01-01")
                .select(["LST_Day_1km", "LST_Night_1km"]))
    col = prep("MODIS/061/MOD11A2").merge(prep("MODIS/061/MYD11A2"))
    m = col.mean().multiply(0.02).subtract(273.15)
    day, night = m.select("LST_Day_1km").rename("lst_day_c"), m.select("LST_Night_1km").rename("lst_night_c")
    return ee.Image.cat([day, night, day.subtract(night).rename("dtr_c"),
                         day.add(night).divide(2).rename("lst_mean_c")])


def albedo_climatology() -> ee.Image:
    col = (ee.ImageCollection("MODIS/061/MCD43A3").filterDate("2019-01-01", "2024-01-01")
           .filter(ee.Filter.Or(ee.Filter.calendarRange(1, 1, "day_of_month"),
                                ee.Filter.calendarRange(15, 15, "day_of_month")))
           .select("Albedo_WSA_shortwave"))
    return col.mean().multiply(0.001).rename("albedo")


def ndvi_climatology() -> ee.Image:
    col = ee.ImageCollection("MODIS/061/MOD13A2").filterDate("2015-01-01", "2025-01-01").select("NDVI")
    return col.mean().multiply(0.0001).rename("ndvi_mean")


def aridity_index() -> ee.Image:
    return (ee.Image("projects/sat-io/open-datasets/global_ai/global_ai_yearly")
            .select("b1").toFloat().multiply(0.0001).rename("aridity_index"))


def dust_aod() -> ee.Image:
    col = (ee.ImageCollection("NASA/GSFC/MERRA/aer/2").filterDate("2019-01-01", "2024-01-01")
           .filter(ee.Filter.calendarRange(12, 12, "hour")).select("DUEXTTAU"))
    return col.mean().rename("dust_aod")
