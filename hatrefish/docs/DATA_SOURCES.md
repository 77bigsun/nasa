# 資料來源與引用（火星端＋地球端）

> 11/14 晚由本機 Claude Code 整理（`PROJECT_CONTEXT.md` 第 10 節要求的文件）。
> 只列**程式裡實際有用到、而且檔案開頭有引用註解**的來源。內容照抄自下列檔案的開頭註解，沒有另外查證；程式裡找不到的引用資訊列在第 4 節「待補」，沒有自己補 DOI。
>
> - 地球端：`src\mars_analog\adapters\earth\gee_layers.py`、`gee_extra.py`、`gee_zoom.py`，以及 `src\mars_analog\earth_grid.py`（本機檔案）
> - 火星端：任務 A 的 `IanChen\src\mars_analog\adapters\mars\*.py`（說明見 `IanChen\docs\DATA_SOURCES.md`），本 repo 的 `src\mars_analog\mars_provisional.py`（暫用版）、`scripts\fetch_mcd.py`
>
> 官方條款：用到的每個資料來源都要引用，即使是開源或免費的。

## 1. 地球端

### 1.1 全球 0.1° 網格（`earth_grid.parquet`、`earth_monthly.parquet`、`earth_extra.parquet`）

| 變數 | 資料 | 提供單位 | DOI／網址 | GEE 資產 | 官方入口 |
|---|---|---|---|---|---|
| 陸地、冰雪、裸地比例 | MODIS MCD12Q1 v061 Land Cover Type 1（IGBP），2022 | NASA EOSDIS LP DAAC | https://doi.org/10.5067/MODIS/MCD12Q1.061 | `MODIS/061/MCD12Q1` | NASA Earthdata |
| 水體比例、各層的水體遮罩 | MODIS MOD44W v006 Land Water Mask，250 m | NASA EOSDIS LP DAAC | https://doi.org/10.5067/MODIS/MOD44W.006 | `MODIS/006/MOD44W` | NASA Earthdata |
| 坡度、粗糙度、海拔 | GMTED2010，7.5 角秒（約 230 m） | USGS／NGA | https://doi.org/10.3133/ofr20111073 | `USGS/GMTED2010_FULL` | USGS |
| 地表溫度、日夜溫差 | MODIS MOD11A2／MYD11A2 v061（Terra＋Aqua，8 天，1 km）。全球網格用 2020–2024（11/14 晚起），放大用 2015–2024 | NASA EOSDIS LP DAAC | https://doi.org/10.5067/MODIS/MOD11A2.061 、https://doi.org/10.5067/MODIS/MYD11A2.061 | `MODIS/061/MOD11A2`、`MODIS/061/MYD11A2` | NASA Earthdata |
| 每月地表溫度（R5／R6 季節特徵） | 同上，2015–2024 依月份平均；11/14 晚起用新年均平移（推算值，見 `scripts\derive_monthly_lst.py`） | 同上 | 同上 | 同上 | NASA Earthdata |
| 反照率（ATI 用） | MODIS MCD43A3 v061 白空反照率短波，2019–2023 | NASA EOSDIS LP DAAC | https://doi.org/10.5067/MODIS/MCD43A3.061 | `MODIS/061/MCD43A3` | NASA Earthdata |
| NDVI 年均、生長季高峰（第 90 百分位） | MODIS MOD13A2 v061（16 天，1 km），2015–2024 | NASA EOSDIS LP DAAC | https://doi.org/10.5067/MODIS/MOD13A2.061 | `MODIS/061/MOD13A2` | NASA Earthdata |
| 乾燥指數 | Global Aridity Index and PET Database v3（GEE community catalog 版，數值 ×10000） | Zomer, Xu, Trabucco | https://doi.org/10.1038/s41597-022-01493-1 （論文） | `projects/sat-io/open-datasets/global_ai/global_ai_yearly` | —（見第 4 節） |
| 沙塵光學厚度、每月沙塵 | MERRA-2 tavg1_2d_aer_Nx DUEXTTAU（550 nm），2019–2023 每日 12 UTC | NASA GMAO | 見第 4 節（程式裡兩處 DOI 不同） | `NASA/GSFC/MERRA/aer/2` | NASA Earthdata（GES DISC） |
| 冰河比例、離冰河距離 | GLIMS 冰河資料庫 | GLIMS Consortium，NSIDC | doi:10.7265/N5V98602 | `GLIMS/current`（依序試 `GLIMS/20230607`、`GLIMS/20210914`） | NASA Earthdata（NSIDC DAAC） |
| 礦物指標（石英、碳酸鹽、鎂鐵質） | ASTER GED AG100 v003 熱紅外放射率（band 10–14） | NASA JPL／LP DAAC | doi:10.5067/Community/ASTER_GED/AG100.003 | `NASA/ASTER_GED/AG100_003` | NASA Earthdata |
| 岩性 | GLiM Global Lithological Map v1.0（0.5° 版） | Hartmann & Moosdorf，PANGAEA | https://doi.org/10.1594/PANGAEA.788537 | 本機 `data\raw\glim\` | PANGAEA |
| 永凍土比例 | ESA CCI Permafrost v5.0（北半球 AREA4、南極 AREA27，2023） | ESA Climate Change Initiative，CEDA Archive | https://catalogue.ceda.ac.uk/ （DOI 見第 4 節） | 本機 `data\raw\permafrost\` | ESA Open Science Catalog／CEDA |

### 1.2 放大（約 1 km 子格與候選格細節，`scripts\zoom_candidates.py`）

除了 1.1 的資料（放大程式的地表溫度仍是 2015–2024），另外用：

| 用途 | 資料 | 提供單位 | DOI／網址 | GEE 資產 | 官方入口 |
|---|---|---|---|---|---|
| 子格地形（200 m）、候選格 30 m 坡度（南北緯 60° 之間） | Copernicus DEM GLO-30 | ESA | https://doi.org/10.5270/ESA-c5d3d65 | `COPERNICUS/DEM/GLO30`、`COPERNICUS/DEM/GLO30_2024_1` | Copernicus |
| 子格 NDVI（250 m） | MODIS MOD13Q1 v061 | NASA EOSDIS LP DAAC | https://doi.org/10.5067/MODIS/MOD13Q1.061 | `MODIS/061/MOD13Q1` | NASA Earthdata |
| 底圖（只畫圖，不計分） | HLS S30／L30 v2.0（30 m） | NASA LP DAAC | https://doi.org/10.5067/HLS/HLSS30.002 、https://doi.org/10.5067/HLS/HLSL30.002 | `NASA/HLS/HLSS30/v002`、`NASA/HLS/HLSL30/v002` | NASA Earthdata |
| 候選格高解析坡度（北緯 60° 以北） | ArcticDEM v3 2 m 鑲嵌 | Polar Geospatial Center | doi:10.7910/DVN/OHHUKH | `UMN/PGC/ArcticDEM/V3/2m_mosaic` | PGC |
| 候選格高解析坡度（南緯 60° 以南） | REMA v1.1 8 m | Polar Geospatial Center | 見第 4 節 | `UMN/PGC/REMA/V1_1/8m` | PGC |
| 雷達後向散射 C 波段（VV、VH） | Copernicus Sentinel-1 GRD，2022–2024（沒有影像時退回 2017–2021） | ESA | 見第 4 節 | `COPERNICUS/S1_GRD` | Copernicus |
| 雷達後向散射 L 波段（HH、HV） | ALOS-2 PALSAR-2 年度鑲嵌，2019–2023 | JAXA | 見第 4 節 | `JAXA/ALOS/PALSAR/YEARLY/SAR_EPOCH` | JAXA |

### 1.3 引用格式（照程式註解）

- Friedl, M., Sulla-Menashe, D. (2022). MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500m SIN Grid V061. NASA EOSDIS Land Processes DAAC. https://doi.org/10.5067/MODIS/MCD12Q1.061
- Carroll, M. et al. (2017). MOD44W MODIS/Terra Land Water Mask Derived from MODIS and SRTM L3 Global 250m SIN Grid V006. https://doi.org/10.5067/MODIS/MOD44W.006
- Danielson, J.J., Gesch, D.B. (2011). Global multi-resolution terrain elevation data 2010 (GMTED2010). USGS Open-File Report 2011-1073. https://doi.org/10.3133/ofr20111073
- Wan, Z., Hook, S., Hulley, G. (2021). MOD11A2 / MYD11A2 v061. https://doi.org/10.5067/MODIS/MOD11A2.061 , https://doi.org/10.5067/MODIS/MYD11A2.061
- Schaaf, C., Wang, Z. (2021). MCD43A3 v061. https://doi.org/10.5067/MODIS/MCD43A3.061
- Didan, K. (2021). MOD13A2 v061. https://doi.org/10.5067/MODIS/MOD13A2.061
- Didan, K. (2021). MOD13Q1 v061. https://doi.org/10.5067/MODIS/MOD13Q1.061
- Zomer, Xu, Trabucco (2022). Global Aridity Index and PET Database v3. Scientific Data 9:409. https://doi.org/10.1038/s41597-022-01493-1
- Gelaro, R., et al. (2017). J. Climate 30, 5419–5454.（MERRA-2）
- GMAO (2015). MERRA-2 tavg1_2d_aer_Nx. https://doi.org/10.5067/KLICLTZ8EM9D （`gee_layers.py` 的寫法；`gee_extra.py` 寫 doi:10.5067/LTVB4GPCOTK2，見第 4 節）
- GLIMS Consortium (2005, updated). Global Land Ice Measurements from Space glacier database. NSIDC. doi:10.7265/N5V98602
- Hulley, G., Hook, S. (2015). ASTER Global Emissivity Dataset AG100 v003. NASA LP DAAC. doi:10.5067/Community/ASTER_GED/AG100.003
- Hartmann, J., Moosdorf, N. (2012). Global Lithological Map Database v1.0 (gridded to 0.5°). PANGAEA. https://doi.org/10.1594/PANGAEA.788537 ；論文：G-cubed 13, Q12004. https://doi.org/10.1029/2012GC004370
- Obu, J. et al. ESA CCI Permafrost v5.0（AREA4、AREA27，2023）。CEDA Archive. https://catalogue.ceda.ac.uk/
- ESA Copernicus DEM GLO-30. https://doi.org/10.5270/ESA-c5d3d65
- Masek, J. et al. (2021). HLSS30 / HLSL30 v2.0. NASA LP DAAC. https://doi.org/10.5067/HLS/HLSS30.002 , https://doi.org/10.5067/HLS/HLSL30.002
- Porter, C., et al. (2018). ArcticDEM. doi:10.7910/DVN/OHHUKH
- Howat, I., et al. (2019). REMA. The Cryosphere 13, 665–674.
- Copernicus Sentinel-1 GRD（ESA）。
- Shimada, M., et al. (2014). PALSAR mosaics. Remote Sensing of Environment 155, 13–31.

### 1.4 方法引用（不是資料，但程式用到）

- Ninomiya, Y. (2003). A stabilized vegetation index and several mineralogic indices defined for ASTER VNIR and SWIR data. IGARSS 2003.
- Ninomiya, Y., Fu, B., Cudahy (2005). Remote Sensing of Environment 99, 127–139.（熱紅外指標：石英 QI、碳酸鹽 CI、鎂鐵質 MI）

## 2. 火星端

本隊計分用的火星目標數值來自任務 A 的正式檔 `data\processed\mars_targets.json`，各變數的來源寫在 `IanChen\src\mars_analog\adapters\mars\*.py` 開頭。`src\mars_analog\mars_provisional.py` 是正式檔到之前的暫用版，用同一批資料（HRSC-MOLA、TES、SIM3292）。

| 變數 | 資料 | 提供單位 | DOI／網址 | 官方入口 |
|---|---|---|---|---|
| 坡度、粗糙度（200 m） | HRSC and MOLA Blended DEM 200 m v2 | USGS Astrogeology（MOLA = NASA MGS，HRSC = ESA Mars Express） | https://astrogeology.usgs.gov/search/map/mars_mgs_mola_mex_hrsc_blended_dem_global_200m | NASA PDS（Astrogeology PDS Annex） |
| 熱慣量 | MGS TES 夜間熱慣量圖 2007（MGS-M-TES-5-TIMAP-V1.0） | NASA PDS Geosciences Node | https://pds-geosciences.wustl.edu/mgs/mgs-m-tes-5-timap-v1/mgst_9001/data/ | NASA PDS |
| 岩性 | Geologic Map of Mars，SIM 3292，1:20,000,000 | USGS | https://doi.org/10.3133/sim3292 | USGS |
| 地下冰 | SWIM 綜合冰一致性指數 Ci（`SWIM4MIM_Ci_0_1.tif`） | Planetary Science Institute（NASA 資助的 SWIM 計畫） | https://swim.psi.edu | — |
| 地表溫度、日夜溫差、沙塵 | Mars Climate Database v6.x 網頁介面（`tsurf`、`tauref`） | LMD／OU／IAA／ESA／CNES | https://www-mars.lmd.jussieu.fr | —（ESA／CNES 合作資料） |
| 細尺度坡度、粗糙度（Jezero） | Mars 2020 TRN CTX DTM，20 m（JEZ_ctx_B_soc_008） | USGS Astrogeology（CTX = NASA MRO） | https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/ | USGS／NASA |
| 細尺度坡度、粗糙度（Gale） | HRSC 30 m DTM 鑲嵌（CC BY 4.0） | UCL（Persaud, Putri & Muller） | https://doi.org/10.5281/zenodo.5808354 | Zenodo（ESA Mars Express 資料） |
| 乾燥、裸地 | 固定值（火星表面極乾、沒有植被） | — | — | — |

引用格式（照程式註解）：

- Fergason, R.L., Hare, T.M., Laura, J. (2018). HRSC and MOLA Blended Digital Elevation Model at 200 m v2. USGS Astrogeology Science Center, PDS Annex.
- Putzig, N.E., Mellon, M.T. (2007). Apparent thermal inertia and the surface heterogeneity of Mars. Icarus 191, 68–94.
- Tanaka, K.L., Skinner, J.A., Jr., Dohm, J.M., et al. (2014). Geologic map of Mars. USGS Scientific Investigations Map 3292. https://doi.org/10.3133/sim3292
- Morgan, G.A., Putzig, N.E., Perry, M.R., et al. (2021). Availability of subsurface water-ice resources in the northern mid-latitudes of Mars. Nature Astronomy 5, 230–236.
- Millour, E., Forget, F., et al. The Mars Climate Database (MCD version 6.x). LMD/OU/IAA/ESA/CNES. https://www-mars.lmd.jussieu.fr
- USGS Astrogeology Science Center (2020). Mars 2020 Terrain Relative Navigation CTX DTM of Jezero crater (JEZ_ctx_B_soc_008, 20 m/px).
- Persaud, D.M., Putri, A.R.D., Muller, J.-P. (2021). 30 m HRSC DTM mosaic of Gale crater. Zenodo. https://doi.org/10.5281/zenodo.5808354

## 3. 平台

- Google Earth Engine：地球端資料都在 GEE 上計算後下載（`src\mars_analog\adapters\earth\_gee.py`）。程式裡沒有平台的引用格式，見第 4 節。

## 4. 待補（程式註解裡沒有，不要自己編）

| 項目 | 缺什麼 |
|---|---|
| MERRA-2 沙塵 | `gee_layers.py` 寫 10.5067/KLICLTZ8EM9D，`gee_extra.py` 寫 10.5067/LTVB4GPCOTK2，兩處不同。要對照 GES DISC 上 tavg1_2d_aer_Nx（M2T1NXAER）的 DOI，統一成一個 |
| ESA CCI Permafrost v5.0 | 資料集 DOI、完整作者 |
| Global Aridity Index v3 | 資料集本身的 DOI（程式只引用論文）；GEE community catalog 版本的出處 |
| REMA v1.1 | 資料集 DOI（程式只引用論文） |
| Sentinel-1 GRD | Copernicus 規定的標註文字、資料集 DOI |
| ALOS-2 PALSAR-2 年度鑲嵌 | 這份產品本身的引用與 DOI（程式只引用 Shimada et al. 2014 的 PALSAR 鑲嵌論文） |
| Copernicus GLO-30 2024_1 | GEE 新版 `GLO30_2024_1` 是否沿用同一個 DOI |
| Google Earth Engine | 平台引用 |
| 軟體 | earthengine-api、numpy、pandas、xarray、PuLP／CBC 等開源套件的引用與授權 |
