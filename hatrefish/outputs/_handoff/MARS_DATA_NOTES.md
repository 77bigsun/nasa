# 火星端數據說明（交接包 `mars_handoff_1115`）

> 給整合網站的 Harris。檔案由 `scripts/export_mars_handoff.py` 產生（2026-11-15 17:32），分數來自 11/14 晚重跑的結果（2026-11-14 23:54）。
> 這份說明裡的數字都是從交接檔直接讀出來的；欄位格式的英文版在交接包的 `README.md`。

## 1. 這包在回答什麼

給定一個火星地點，找出地球上哪裡最像，分兩種角度：

- **類比剖面**（`profile_rankings`）：地形、地表、環境、水冰、沙塵 5 個面向各有多像，整體有多像。
- **任務測試**（`task_rankings`）：依任務需求 R1–R6，地球哪裡最適合拿來練習那項任務。

網站不用重算分數，只要依使用者選的火星地點與測試，挑出預先算好的排名。

## 2. 檔案

| 檔案 | 大小 | 內容 |
|---|---|---|
| `mars_results.json` | 1.83 MB | 測試定義、火星地點、所有排名、類比剖面、集合覆蓋、驗證 |
| `mars_global_grid.json` | 3.75 MB | 1° 全球地圖：17,225 格 × 37 欄（每格取格內 0.1° 格的最高分） |
| `mars_candidate_pool.csv` | 0.82 MB | 集合覆蓋用的候選池：3,317 個 0.1° 格，每格有各目標 × 測試的分數（0–1） |
| `README.md` | 2.9 KB | 欄位格式（英文） |
| `marsHandoffTypes.ts` | 3.5 KB | 前端型別，對應 `lunarHandoffTypes.ts` |

## 3. 地球網格

- 全球 0.1° 格（約 11 km），只用陸地格（MOD44W 水體遮罩）；地表溫度用 MODIS 2020–2024。
- 排名時，同一份名單裡的地點至少相隔 150 km。
- 離已知類比地 50 km 內的候選地會標成已知類比地，放在 `known_analogs_in_top`，不算進 `new_candidates`。已知類比地共 28 個（`known_analog_sites`，來自 `data/labels/known_analogs.csv`）。

## 4. 火星地點（7 個）

| id | 名稱 | 緯度 | 經度 | 半徑 km | 岩性（SIM 3292 單位 → 類別） | SWIM Ci | 有評分的測試 |
|---|---|---|---|---|---|---|---|
| `mars-jezero` | Jezero Crater | 18.4 | 77.5 | 25 | HNt → clastic | -0.206 | R1、R4、R6 |
| `mars-gale` | Gale Crater | -5.4 | 137.8 | 25 | Htu → clastic | 0.059 | R1、R4、R6 |
| `mars-arcadia` | Arcadia Planitia (shallow ground ice) | 47.2 | -175.7 | 50 | Av → basalt | 0.526 | R1、R3、R4、R5、R6 |
| `mars-oxia` | Oxia Planum (ExoMars Rosalind Franklin landing site) | 18.2 | -24.55 | 25 | lNh → sedimentary_carbonate_clay | -0.323 | R1、R4、R6 |
| `mars-meridiani` | Meridiani Planum (Opportunity landing site, Eagle crater) | -1.95 | -5.53 | 25 | HNhu → evaporite_sulfate_clastic | 0.034 | R1、R4、R6 |
| `mars-protonilus` | Protonilus Mensae (candidate human exploration zone, buried glacial ice) | 41.905 | 48.548 | 50 | HNt → clastic | 0.162 | R1、R3、R4、R5、R6 |
| `mars-ap105` | Arcadia Planitia AP-105 (SkyFall design reference landing site) | 43.33 | -161.477 | 50 | Av → basalt | 0.583 | R1、R3、R4、R5、R6 |

SWIM Ci ≥ 0.1 才算有冰（Ci 接近 0 的訊號不可靠），所以 R3、R5 只有 mars-arcadia、mars-protonilus、mars-ap105 有排名。R2 全部沒評分（第 5 節）。

火星端的目標值（地形、熱慣量取地點半徑內的值；溫度、日夜溫差、沙塵是 Mars Climate Database 在地點中心的值，MCD 網格約 5°）：

| id | 坡度 ° | 粗糙度 m | 熱慣量 tiu | 年均地表溫 °C | 日夜溫差 °C | 沙塵光學厚度 |
|---|---|---|---|---|---|---|
| `mars-jezero` | 2.24 | 10.61 | 296 | -49.47 | 84.69 | 0.55 |
| `mars-gale` | 5.46 | 27.25 | 283 | -50.85 | 93.3 | 0.46 |
| `mars-arcadia` | 0.21 | 1.01 | 233 | -75.93 | 62.61 | 0.35 |
| `mars-oxia` | 0.56 | 2.77 | 416 | -50.75 | 77.07 | 0.62 |
| `mars-meridiani` | 1.28 | 6.36 | 190 | -46.09 | 95.43 | 0.52 |
| `mars-protonilus` | 4.59 | 22.6 | 197 | -71.24 | 79.45 | 0.34 |
| `mars-ap105` | 0.21 | 0.99 | 181 | -72.67 | 75.45 | 0.41 |

乾燥與無植被在火星端是固定值（極乾、NDVI = 0）。

## 5. 任務測試 R1–R6

| 測試 | 名稱 | ROC 權重 | 適用 | 狀態 | 特徵數 | 有分數的地球格數 |
|---|---|---|---|---|---|---|
| R1 | 著陸地表條件（Landing surface） | 0.408 | 全部 | 已評分 | 6 | 790,599 |
| R2 | 視覺導航可行性（Visual navigation） | 0.103 | 全部 | 未評分 | 0 | — |
| R3 | 淺層地下冰（Shallow ground ice） | 0.242 | 有冰的地點 | 已評分 | 3 | 1,434,261 |
| R4 | 含水礦物辨識（Hydrated minerals） | 0.061 | 全部 | 已評分 | 5 | 1,434,366 |
| R5 | 冰河與冰緣地形（Periglacial landforms） | 0.028 | 有冰的地點 | 已評分 | 7 | 1,435,234 |
| R6 | 沙塵與近地表氣象（Dust and near-surface weather） | 0.158 | 全部 | 已評分 | 7 | 1,314,474 |

- ROC 權重只用在「選幾項測試算加權總分」的參考功能，排名本身每項測試分開。
- 每個特徵都是必要的：任一項缺資料，那一格的這項測試就不評分，所以各測試有分數的格數不同。
- R2：全球網格沒有影像紋理與沙丘比例；需要 Sentinel-2 紋理（地球）與 CTX 紋理、MGD3 沙丘資料庫（火星），留到放大階段

每項測試的特徵（`w` 和 `c` 都是 1）：

| 測試 | 特徵 | 種類 | 公式 | 地球資料 | 火星資料 |
|---|---|---|---|---|---|
| R1 | `slope` | threshold | `slope_deg` ≤ 5 → 1，≥ 15 → 0，中間線性 | GMTED2010 230 m 坡度，0.1° 格內中位數 | CTX／HRSC 地形（本隊用 HRSC+MOLA 200 m） |
| R1 | `roughness` | similarity | 高斯，σ = 地球陸地標準差 × 0.5 | GMTED2010 230 m | HRSC+MOLA 200 m |
| R1 | `thermal_inertia` | mars_rank_threshold | 火星熱慣量 100 → 150 換成火星百分位，地球表觀熱慣量百分位落在兩者之間線性給分（越高越好） | 表觀熱慣量 ATI（MODIS）的全球百分位 | TES 夜間熱慣量 2007 的全球分位數 |
| R1 | `barrenness` | similarity | clip(1 − NDVI / 0.3, 0, 1) | MODIS NDVI | — |
| R1 | `summer_barren` | threshold | `ndvi_p90` ≤ 0.15 → 1，≥ 0.4 → 0，中間線性 | MOD13A2 2015–2024 NDVI 第 90 百分位 | — |
| R1 | `ice_free` | threshold | `icy_frac` ≤ 0.1 → 1，≥ 0.5 → 0，中間線性 | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | — |
| R3 | `permafrost` | threshold | `permafrost_frac` ≤ 0.1 → 0，≥ 0.9 → 1，中間線性 | ESA CCI 永凍土 v5.0（2023） | SWIM4MIM Ci |
| R3 | `cold` | threshold | `lst_mean_c` ≤ -2 → 1，≥ 2 → 0，中間線性 | MODIS MOD11A2+MYD11A2 2015–2024 | MCD 年均地表溫 |
| R3 | `dryness` | similarity | 地球越乾越高分（百分位，和目標無關） | Global Aridity Index v3 | — |
| R4 | `lithology` | similarity | 查表：火星地質單位類別 → 地球 GLiM 岩類（預設 0.1） | GLiM 0.5° | USGS SIM3292 全球地質圖＋文獻覆寫 |
| R4 | `barrenness` | similarity | clip(1 − NDVI / 0.3, 0, 1) | MODIS NDVI | — |
| R4 | `summer_barren` | threshold | `ndvi_p90` ≤ 0.15 → 1，≥ 0.4 → 0，中間線性 | MOD13A2 2015–2024 NDVI 第 90 百分位 | — |
| R4 | `ice_free` | threshold | `icy_frac` ≤ 0.1 → 1，≥ 0.5 → 0，中間線性 | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | — |
| R4 | `mineral_signature` | index_rank | ASTER 礦物指標在同一年均溫帶內的百分位：0.5 → 0，0.9 → 1 | ASTER GED AG100 熱紅外放射率算的 Ninomiya 指標 | 文獻（見 target_attributes） |
| R5 | `permafrost` | threshold | `permafrost_frac` ≤ 0.1 → 0，≥ 0.9 → 1，中間線性 | ESA CCI 永凍土 | SWIM4MIM Ci |
| R5 | `cold` | threshold | `lst_mean_c` ≤ -2 → 1，≥ 2 → 0，中間線性 | MODIS LST | MCD |
| R5 | `slope` | similarity | 高斯，σ = 3° | GMTED2010 | HRSC+MOLA 200 m |
| R5 | `roughness` | similarity | 高斯，σ = 地球陸地標準差 × 0.5 | GMTED2010 | HRSC+MOLA 200 m |
| R5 | `barrenness` | similarity | clip(1 − NDVI / 0.3, 0, 1) | MODIS NDVI | — |
| R5 | `summer_barren` | threshold | `ndvi_p90` ≤ 0.15 → 1，≥ 0.4 → 0，中間線性 | MOD13A2 2015–2024 NDVI 第 90 百分位 | — |
| R5 | `glacier_distance` | threshold | `glacier_km` ≤ 20 → 1，≥ 300 → 0，中間線性 | GLIMS 冰河輪廓（離最近冰河的距離） | 文獻（見 target_attributes） |
| R6 | `dust` | similarity | 1 − \|p 火星 − p 地球\|，p = 在自己星球上的百分位 | MERRA-2 DUEXTTAU | MCD 全球沙塵（Ls 每 30°） |
| R6 | `temperature` | similarity | 地球越冷越高分（百分位，和目標無關） | MODIS LST | MCD |
| R6 | `diurnal_range` | similarity | 地球日夜溫差越大越高分（百分位，和目標無關） | MODIS LST 日夜差 | MCD |
| R6 | `dust_season_shape` | seasonal_shape | (1 + r) / 2，r = 地球 12 個月曲線和火星 Ls 曲線（依當地季節對齊）的相關係數 | MERRA-2 DUEXTTAU 月平均 | MCD tauref（Ls 每 15°） |
| R6 | `dust_season_amplitude` | seasonal_amplitude | 季節相對振幅（(最大 − 最小) / 平均）的對數比，高斯 σ = ln 2 | MERRA-2 DUEXTTAU 月平均 | MCD tauref |
| R6 | `temperature_season_shape` | seasonal_shape | (1 + r) / 2，r = 地球 12 個月曲線和火星 Ls 曲線（依當地季節對齊）的相關係數 | MODIS LST 月平均 | MCD 地表溫（Ls 每 15°） |
| R6 | `temperature_season_amplitude` | seasonal_range_ratio | 季節溫差（最暖月 − 最冷月）的對數比，高斯 σ = ln 2 | MODIS LST 月平均 | MCD 地表溫（Ls 每 15°） |

## 6. 類比剖面的 5 個面向

| 面向 | 變數 | 怎麼比 |
|---|---|---|
| 地形（`terrain`） | slope、roughness | slope：高斯（σ = 3°）；roughness：高斯（σ = 地球陸地標準差 × 0.5） |
| 地表物質與裸露（`surface`） | lithology、thermal_inertia、barrenness | lithology：查表（火星地質單位 → GLiM 岩類）；thermal_inertia：百分位差：1 − \|p 火星 − p 地球\|；barrenness：clip(1 − NDVI / 0.3, 0, 1) |
| 環境極端（`environment`） | temperature、aridity | temperature：地球越冷越高分（和目標無關）；aridity：地球越乾越高分（和目標無關） |
| 水與冰（`water_ice`） | ice | ice：1 − \|永凍土比例 − clip(SWIM Ci, 0, 1)\| |
| 大氣與沙塵（`atmosphere_dust`） | dust | dust：百分位差：1 − \|p 火星 − p 地球\| |

- 面向分數 = 變數分數的等權重幾何平均（下限 0.01）；整體相似度 = 5 個面向的等權重幾何平均 × 100。
- 排名只用至少 80% 面向、80% 變數有資料的格子。生物、地下兩個面向沒有全球資料，不評分。
- 溫度和乾燥：地球達不到火星的值，所以改成「越極端越像」，這兩項對 7 個火星地點都一樣。

## 7. 分數怎麼算、怎麼讀

- 測試分數 = 100 × 特徵分數的等權重幾何平均：`100 × exp(Σ ln(max(s, 0.01)) / n)`。每個特徵都是必要的，缺任一項就不評分。
- **和月球端不同**：月球端是加權算術平均 `100·Σ(w·c·s)/Σ(w·c)`。火星端用幾何平均，只要有一項接近 0，總分就會被拉到接近 0（有一項不合格，其他項再好也補不回來）。`w`、`c` 都是 1。
- 每個特徵的 `classification`：s ≥ 0.6 為 similar，s < 0.3 為 different，其他為 partial（門檻和月球端一樣）。
- 分數 0–100。不同測試的分數不能直接比大小（特徵不同）；同一測試裡比排名。
- 可以重算：`python scripts/export_mars_handoff.py --check` 會從每個候選地的特徵重算分數（這次 352 筆，最大誤差 0.09 分，來自特徵四捨五入到小數 3 位）。

## 8. 欄位重點

`mars_results.json`

| 鍵 | 內容 |
|---|---|
| `meta` | 公式、門檻、規則、資料來源、AI 使用聲明、限制 |
| `tasks.R1…R6` | 測試名稱、權重、適用條件、特徵（含公式與資料） |
| `mars_sites[]` | 7 個火星地點：座標、目標值、`test_status`、`scored_tests`、每項測試前 3 名（`best_earth_analogs_by_task`） |
| `task_rankings[測試][火星 id]` | `new_candidates`（前 10，已排除已知類比地）、`known_analogs_in_top`、`known_analogs_validation`（全部已知類比地的分數與全球前百分比）、`least_similar`（最不像的 3 個） |
| `profile_rankings[火星 id]` | `overall_top`（前 10）、`by_dimension`（每個面向前 5）、`known_analogs` |
| `set_cover` | 最少幾個地球地點可以涵蓋全部需求，含邊際曲線與敏感度 |
| `validation` | 已知類比地找回率、對照組、排名穩定度 |

候選地（`new_candidates` 等）每筆：

| 欄位 | 意思 |
|---|---|
| `id` | `火星 id:測試:cell_id`，全包唯一 |
| `rank`／`rank_including_known` | 排除已知類比地後的名次／原本前 20 名裡的名次 |
| `lat`、`lon` | 0.1° 格中心 |
| `name_en` | 自動反查的地名（GeoNames），例如「92 km from Wutumeiren (CN)」；`name_zh` 目前是空的 |
| `score` | 這項測試的分數，0–100 |
| `features[]` | `feature`、地球值 `value`、火星值或需求 `mars_value`、`unit`、分數 `s`（0–1）、`classification` |
| `weakest_feature`、`breaks` | 最弱的特徵、分數低於 0.3 的特徵（哪裡不像） |
| `dimension_scores`、`profile_overall` | 同一格的類比剖面分數（交叉參考） |
| `nearest_known_analog` | 最近的已知類比地與距離 |
| `worldview_url` | NASA Worldview 衛星影像連結 |

`mars_global_grid.json`：`meta.columns` 依序是 `lat, lon, n_cells`，再來每個火星地點的 `overall_<id>`（類比剖面整體）和 `<id>_<測試>`（測試分數）。數值是 1° 格內最高的 0.1° 格分數（0–100），`null` 表示這格沒有可評分的陸地格或測試不適用。

`mars_candidate_pool.csv`：`S_<id>_<測試>` 是 0–1 的測試分數，另有 `known_analog`、`nearest_known`、`nearest_known_km`、`place`。

## 9. 驗證結果

| 檢查 | 結果 |
|---|---|
| 已知類比地用它代表的面向排名（越小越好） | 34 組，全球前百分比中位數 11.7%（用整體相似度排是 31.5%）；47% 在前 10%、71% 在前 25% |
| 對照組（雨林、三角洲等明顯不像的地方） | 56 組，進入前 25% 的有 0 組 |
| 各目標前 10 名的穩定度 | 64/70 個地點穩定度 ≥ 0.8（穩定度 = 改權重、隨機權重、改聚合方式、改資料篩選、改間距 5 類情境裡，150 km 內仍有地點留在前 20 名的比例，5 類取平均） |

完整報告：`outputs/validation/VALIDATION.md`。

## 10. 集合覆蓋

規則：分數 ≥ 0.9 × 該需求的最高分。27 個需求（火星地點 × 測試）最少要 **5 個地球地點**，沒有無法涵蓋的需求。

| # | 地點 | 緯度 | 經度 | 負責的需求數 |
|---|---|---|---|---|
| 1 | 502 km from Gjoa Haven (CA) | 72.95 | -91.95 | 4 |
| 2 | near Gaolan Chengguanzhen (CN) | 36.45 | 103.95 | 5 |
| 3 | 105 km from Aqqan (CN) | 35.65 | 82.55 | 8 |
| 4 | 86 km from Puerto Villamil (EC) | -0.35 | -91.45 | 4 |
| 5 | 65 km from Colchani (BO) | -20.35 | -67.55 | 6 |

## 11. 資料來源

地球端（全球 0.1° 網格，Google Earth Engine 計算後下載）：

| 用途 | 資料 | 期間 | DOI／出處 |
|---|---|---|---|
| 陸地、冰雪比例 | MODIS MCD12Q1 v061 土地覆蓋（IGBP） | 2022 | 10.5067/MODIS/MCD12Q1.061 |
| 水體遮罩 | MODIS MOD44W v006（250 m） | — | 10.5067/MODIS/MOD44W.006 |
| 坡度、粗糙度 | USGS GMTED2010（7.5 角秒，約 230 m） | — | 10.3133/ofr20111073 |
| 地表溫度、日夜溫差 | MODIS MOD11A2＋MYD11A2 v061（1 km） | 2020–2024 | 10.5067/MODIS/MOD11A2.061、10.5067/MODIS/MYD11A2.061 |
| 每月地表溫度（R5、R6 季節） | 同上，2015–2024 月平均平移到 2020–2024 年均；年均差 > 1.5 K 或日夜溫差差 > 3 K 的格設缺資料 | 2015–2024 | 同上 |
| 反照率（表觀熱慣量 ATI） | MODIS MCD43A3 v061 | 2019–2023 | 10.5067/MODIS/MCD43A3.061 |
| NDVI 年均、生長季高峰 | MODIS MOD13A2 v061（1 km） | 2015–2024 | 10.5067/MODIS/MOD13A2.061 |
| 乾燥指數 | Global Aridity Index and PET Database v3 | — | Zomer et al. 2022, Sci. Data 9:409, 10.1038/s41597-022-01493-1 |
| 沙塵光學厚度、每月沙塵 | MERRA-2 M2T1NXAER（tavg1_2d_aer_Nx）DUEXTTAU 550 nm | 2019–2023 | 10.5067/KLICLTZ8EM9D |
| 冰河比例、離冰河距離 | GLIMS 冰河資料庫（NSIDC） | — | 10.7265/N5V98602 |
| 礦物指標 | ASTER GED AG100 v003 熱紅外放射率 | — | 10.5067/Community/ASTER_GED/AG100.003 |
| 岩性 | GLiM Global Lithological Map v1.0（0.5°） | — | 10.1594/PANGAEA.788537 |
| 永凍土比例 | ESA CCI Permafrost v5.0 | 2023 | CEDA Archive（資料集 DOI 待補） |

火星端（`data/processed/mars_targets.json`，任務 A 的正式檔）：

| 用途 | 資料 | 出處 |
|---|---|---|
| 坡度、粗糙度（200 m） | HRSC and MOLA Blended DEM 200 m v2 | Fergason et al. 2018, USGS Astrogeology |
| 熱慣量 | MGS TES 夜間熱慣量圖（2007） | Putzig & Mellon 2007, Icarus 191 |
| 岩性 | Geologic Map of Mars, SIM 3292 | Tanaka et al. 2014, 10.3133/sim3292 |
| 地下冰 | SWIM 冰一致性指數 Ci | Morgan et al. 2021, Nature Astronomy 5; swim.psi.edu |
| 地表溫度、日夜溫差、沙塵、季節曲線 | Mars Climate Database v6（網頁介面氣候值） | LMD／OU／IAA／ESA／CNES |
| 乾燥、無植被 | 固定值 | — |

完整引用與待補項目：`docs/DATA_SOURCES.md`。MERRA-2 的 DOI 已對照 data.gov 上 M2T1NXAER 的資料頁，是 10.5067/KLICLTZ8EM9D（程式 `gee_extra.py` 的註解寫錯，待改）。

## 12. 限制與上網站前要注意

- R2（視覺導航）沒有評分：沒有全球的影像紋理資料。
- 地球格是 0.1°（約 11 km），火星地點是半徑 25–50 km 的圓；比一格小的地形看不到。
- 地球坡度是格內 GMTED2010 230 m 坡度的中位數，不是著陸需求的 100 m 尺度。
- 岩性只比大類（GLiM 0.5° 對 USGS SIM 3292），很粗。
- 溫度和乾燥用「越極端越像」（地球達不到火星的值），所以 7 個火星地點這兩項都一樣。
- 只有 7 個火星地點；生物、地下兩個面向沒有評分。
- 地名是自動反查最近的城鎮，偏遠地區會很怪（例如南極內陸顯示成「2641 km from Port-aux-Francais」），上線前要人工看過；中文地名還沒填。
- 每月地表溫度是推算值（舊月平均平移到新年均），6.9% 的格子差太多設成缺資料。
- 尚待補的引用：ESA CCI 永凍土資料集 DOI、乾燥指數資料集本身的 DOI、Google Earth Engine 平台引用。
- AI 使用：評分程式、資料處理腳本和這份匯出是用 Claude（Anthropic）協助寫的；方法由團隊決定，程式與結果經團隊檢查。（`meta.ai_disclosure` 有英文版）

## 13. 重新產生

```
python scripts\export_mars_handoff.py --grid --force   # 重算全球格與最不像的地點，再組檔（約 2 分鐘）
python scripts\export_mars_handoff.py --check          # 檢查
```
