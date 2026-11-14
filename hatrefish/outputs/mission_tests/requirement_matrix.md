# 需求矩陣（給整合者；自動產生自 config/mission_tests.yaml）

| 目標地點 | 測試代號 | 特徵 | 目標值或門檻 | 特徵類型 | 行星端資料 | 地球端資料 | 特徵權重 | 狀態 | 備註 |
|---|---|---|---|---|---|---|---|---|---|
| Jezero Crater | R1 | slope | 100 m 尺度坡度 < 5–15°（SkyFall，待定；規劃建議先取 15°） | 門檻 | CTX／HRSC 地形（本隊用 HRSC+MOLA 200 m） | GMTED2010 230 m 坡度，0.1° 格內中位數 | 0.167 | scored | 地球端是 200 m 尺度坡度的格內中位數，不是 100 m；格內可能有局部陡坡 |
| Jezero Crater | R1 | roughness | 和目標的 5×5 視窗高程標準差相近（高斯） | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 230 m | 0.167 | scored |  |
| Jezero Crater | R1 | thermal_inertia | 熱慣量 > 100（最好 > 150），避開厚塵；只比相對排名 | 門檻（相對排名） | TES 夜間熱慣量 2007 的全球分位數 | 表觀熱慣量 ATI（MODIS）的全球百分位 | 0.167 | scored |  |
| Jezero Crater | R1 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.167 | scored |  |
| Jezero Crater | R1 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.167 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Jezero Crater | R1 | ice_free | 降落面是岩石與風化層，不是冰 | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.167 | scored | 排除冰河、冰原覆蓋的格子 |
| Jezero Crater | R1 | — | 1–5 m 尺度坡度（火星要 HiRISE 地形模型；地球沒有全球資料，只有極區 ArcticDEM／REMA 與美國光達，留到放大階段） | — | — | — | — | not_evaluated |  |
| Jezero Crater | R1 | — | 岩石高度 < 11 cm、覆蓋率 < 5%（地球沒有全球岩石資料；代理用雷達後向散射，留到放大階段） | — | — | — | — | not_evaluated |  |
| Jezero Crater | R1 | — | 雷達粗糙度（Sentinel-1／PALSAR，波段和火星不同，只能比相對排名，留到放大階段） | — | — | — | — | not_evaluated |  |
| Jezero Crater | R2 | — | — | — | — | — | — | not_evaluated | 全球網格沒有影像紋理與沙丘比例；需要 Sentinel-2 紋理（地球）與 CTX 紋理、MGD3 沙丘資料庫（火星），留到放大階段 |
| Jezero Crater | R3 | permafrost | 目標區有淺層地下冰（SWIM Ci > 0） | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 v5.0（2023） | — | not_applicable |  |
| Jezero Crater | R3 | cold | 年均地表溫 < 0 °C（地球能維持永凍土） | 門檻 | MCD 年均地表溫 | MODIS MOD11A2+MYD11A2 2015–2024 | — | not_applicable |  |
| Jezero Crater | R3 | dryness | 極乾（火星地下冰在乾燥環境中） | 剖面（和目標比） | — | Global Aridity Index v3 | — | not_applicable |  |
| Jezero Crater | R3 | — | 多邊形地（地球沒有全球資料） | — | — | — | — | not_evaluated |  |
| Jezero Crater | R3 | — | 地下雷達與 3–5 m 深度（SHARAD；地球沒有同深度的全球資料） | — | — | — | — | not_evaluated |  |
| Jezero Crater | R4 | lithology | 和目標同類的岩性（oxia、meridiani 用文獻覆寫的礦物類別） | 剖面（和目標比） | USGS SIM3292 全球地質圖＋文獻覆寫 | GLiM 0.5° | 0.2 | scored | 只是岩性大類代理，很粗 |
| Jezero Crater | R4 | barrenness | 岩石裸露（植被會遮住光譜） | 剖面（和目標比） | — | MODIS NDVI | 0.2 | scored |  |
| Jezero Crater | R4 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.2 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Jezero Crater | R4 | ice_free | 岩石裸露（冰雪會遮住光譜） | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.2 | scored | 排除冰河、冰原覆蓋的格子 |
| Jezero Crater | R4 | mineral_signature | 目標的主要礦物（碳酸鹽、鎂鐵質）在地球同樣明顯 | 類別（礦物指標） | 文獻（見 target_attributes） | ASTER GED AG100 熱紅外放射率算的 Ninomiya 指標 | 0.2 | scored | 只對有列出指標的目標計算；黏土、硫酸鹽、赤鐵礦沒有熱紅外指標；百分位在同一年均地表溫帶內算（−5、5、15、25 °C 分帶），指標超出 0.7–1.3 當缺資料 |
| Jezero Crater | R4 | — | 逐條光譜比對（CRISM／OMEGA 對 EMIT／ASTER 短波紅外） | — | — | — | — | not_evaluated |  |
| Jezero Crater | R5 | permafrost | 有地下冰 | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 | — | not_applicable |  |
| Jezero Crater | R5 | cold | 年均地表溫 < 0 °C | 門檻 | MCD | MODIS LST | — | not_applicable |  |
| Jezero Crater | R5 | slope | 地形起伏和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | — | not_applicable |  |
| Jezero Crater | R5 | roughness | 地形粗糙度和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | — | not_applicable |  |
| Jezero Crater | R5 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | — | not_applicable |  |
| Jezero Crater | R5 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | — | not_applicable | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Jezero Crater | R5 | glacier_distance | 目標附近有類冰河地形或葉狀碎屑裙 | 門檻 | 文獻（見 target_attributes） | GLIMS 冰河輪廓（離最近冰河的距離） | — | not_applicable | 只對 target_attributes 標了 glacial_landforms 的目標計算 |
| Jezero Crater | R5 | — | 多邊形尺寸（地球冰楔多邊形 10–30 m，沒有全球資料） | — | — | — | — | not_evaluated |  |
| Jezero Crater | R6 | dust | 年均沙塵光學厚度的相對排名相近 | 剖面（和目標比） | MCD 全球沙塵（Ls 每 30°） | MERRA-2 DUEXTTAU | 0.143 | scored |  |
| Jezero Crater | R6 | temperature | 盡量冷（地球到不了火星溫度，取極端百分位） | 剖面（和目標比） | MCD | MODIS LST | 0.143 | scored |  |
| Jezero Crater | R6 | diurnal_range | 日溫差盡量大（取極端百分位） | 剖面（和目標比） | MCD | MODIS LST 日夜差 | 0.143 | scored | R6 本來就包含近地表溫度日變化，所以納入；類比剖面的環境面向仍不納入 |
| Jezero Crater | R6 | dust_season_shape | 沙塵季節變化的形狀相近（依當地季節對齊） | 時間序列（形狀） | MCD tauref（Ls 每 15°） | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Jezero Crater | R6 | dust_season_amplitude | 沙塵季節振幅（相對平均）相近 | 時間序列（振幅） | MCD tauref | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Jezero Crater | R6 | temperature_season_shape | 地表溫度季節變化的形狀相近 | 時間序列（形狀） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored |  |
| Jezero Crater | R6 | temperature_season_amplitude | 地表溫度季節溫差（最高月 − 最低月）相近（對數比，σ = ln 2） | 時間序列（季節溫差） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored | 11/14 加：只比形狀時，季節溫差只有 4 °C 的赤道高山也能拿高分 |
| Jezero Crater | R6 | — | 風（地球有 MERRA-2，火星只有 MCD；還沒做） | — | — | — | — | not_evaluated |  |
| Jezero Crater | R6 | — | 逐日時間序列的分布比較（Wasserstein）與 TOST 等價性檢定 | — | — | — | — | not_evaluated |  |
| Gale Crater | R1 | slope | 100 m 尺度坡度 < 5–15°（SkyFall，待定；規劃建議先取 15°） | 門檻 | CTX／HRSC 地形（本隊用 HRSC+MOLA 200 m） | GMTED2010 230 m 坡度，0.1° 格內中位數 | 0.167 | scored | 地球端是 200 m 尺度坡度的格內中位數，不是 100 m；格內可能有局部陡坡 |
| Gale Crater | R1 | roughness | 和目標的 5×5 視窗高程標準差相近（高斯） | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 230 m | 0.167 | scored |  |
| Gale Crater | R1 | thermal_inertia | 熱慣量 > 100（最好 > 150），避開厚塵；只比相對排名 | 門檻（相對排名） | TES 夜間熱慣量 2007 的全球分位數 | 表觀熱慣量 ATI（MODIS）的全球百分位 | 0.167 | scored |  |
| Gale Crater | R1 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.167 | scored |  |
| Gale Crater | R1 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.167 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Gale Crater | R1 | ice_free | 降落面是岩石與風化層，不是冰 | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.167 | scored | 排除冰河、冰原覆蓋的格子 |
| Gale Crater | R1 | — | 1–5 m 尺度坡度（火星要 HiRISE 地形模型；地球沒有全球資料，只有極區 ArcticDEM／REMA 與美國光達，留到放大階段） | — | — | — | — | not_evaluated |  |
| Gale Crater | R1 | — | 岩石高度 < 11 cm、覆蓋率 < 5%（地球沒有全球岩石資料；代理用雷達後向散射，留到放大階段） | — | — | — | — | not_evaluated |  |
| Gale Crater | R1 | — | 雷達粗糙度（Sentinel-1／PALSAR，波段和火星不同，只能比相對排名，留到放大階段） | — | — | — | — | not_evaluated |  |
| Gale Crater | R2 | — | — | — | — | — | — | not_evaluated | 全球網格沒有影像紋理與沙丘比例；需要 Sentinel-2 紋理（地球）與 CTX 紋理、MGD3 沙丘資料庫（火星），留到放大階段 |
| Gale Crater | R3 | permafrost | 目標區有淺層地下冰（SWIM Ci > 0） | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 v5.0（2023） | — | not_applicable |  |
| Gale Crater | R3 | cold | 年均地表溫 < 0 °C（地球能維持永凍土） | 門檻 | MCD 年均地表溫 | MODIS MOD11A2+MYD11A2 2015–2024 | — | not_applicable |  |
| Gale Crater | R3 | dryness | 極乾（火星地下冰在乾燥環境中） | 剖面（和目標比） | — | Global Aridity Index v3 | — | not_applicable |  |
| Gale Crater | R3 | — | 多邊形地（地球沒有全球資料） | — | — | — | — | not_evaluated |  |
| Gale Crater | R3 | — | 地下雷達與 3–5 m 深度（SHARAD；地球沒有同深度的全球資料） | — | — | — | — | not_evaluated |  |
| Gale Crater | R4 | lithology | 和目標同類的岩性（oxia、meridiani 用文獻覆寫的礦物類別） | 剖面（和目標比） | USGS SIM3292 全球地質圖＋文獻覆寫 | GLiM 0.5° | 0.25 | scored | 只是岩性大類代理，很粗 |
| Gale Crater | R4 | barrenness | 岩石裸露（植被會遮住光譜） | 剖面（和目標比） | — | MODIS NDVI | 0.25 | scored |  |
| Gale Crater | R4 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.25 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Gale Crater | R4 | ice_free | 岩石裸露（冰雪會遮住光譜） | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.25 | scored | 排除冰河、冰原覆蓋的格子 |
| Gale Crater | R4 | mineral_signature | 目標的主要礦物（碳酸鹽、鎂鐵質）在地球同樣明顯 | 類別（礦物指標） | 文獻（見 target_attributes） | ASTER GED AG100 熱紅外放射率算的 Ninomiya 指標 | — | not_applicable_for_target | 只對有列出指標的目標計算；黏土、硫酸鹽、赤鐵礦沒有熱紅外指標；百分位在同一年均地表溫帶內算（−5、5、15、25 °C 分帶），指標超出 0.7–1.3 當缺資料 |
| Gale Crater | R4 | — | 逐條光譜比對（CRISM／OMEGA 對 EMIT／ASTER 短波紅外） | — | — | — | — | not_evaluated |  |
| Gale Crater | R5 | permafrost | 有地下冰 | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 | — | not_applicable |  |
| Gale Crater | R5 | cold | 年均地表溫 < 0 °C | 門檻 | MCD | MODIS LST | — | not_applicable |  |
| Gale Crater | R5 | slope | 地形起伏和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | — | not_applicable |  |
| Gale Crater | R5 | roughness | 地形粗糙度和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | — | not_applicable |  |
| Gale Crater | R5 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | — | not_applicable |  |
| Gale Crater | R5 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | — | not_applicable | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Gale Crater | R5 | glacier_distance | 目標附近有類冰河地形或葉狀碎屑裙 | 門檻 | 文獻（見 target_attributes） | GLIMS 冰河輪廓（離最近冰河的距離） | — | not_applicable | 只對 target_attributes 標了 glacial_landforms 的目標計算 |
| Gale Crater | R5 | — | 多邊形尺寸（地球冰楔多邊形 10–30 m，沒有全球資料） | — | — | — | — | not_evaluated |  |
| Gale Crater | R6 | dust | 年均沙塵光學厚度的相對排名相近 | 剖面（和目標比） | MCD 全球沙塵（Ls 每 30°） | MERRA-2 DUEXTTAU | 0.143 | scored |  |
| Gale Crater | R6 | temperature | 盡量冷（地球到不了火星溫度，取極端百分位） | 剖面（和目標比） | MCD | MODIS LST | 0.143 | scored |  |
| Gale Crater | R6 | diurnal_range | 日溫差盡量大（取極端百分位） | 剖面（和目標比） | MCD | MODIS LST 日夜差 | 0.143 | scored | R6 本來就包含近地表溫度日變化，所以納入；類比剖面的環境面向仍不納入 |
| Gale Crater | R6 | dust_season_shape | 沙塵季節變化的形狀相近（依當地季節對齊） | 時間序列（形狀） | MCD tauref（Ls 每 15°） | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Gale Crater | R6 | dust_season_amplitude | 沙塵季節振幅（相對平均）相近 | 時間序列（振幅） | MCD tauref | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Gale Crater | R6 | temperature_season_shape | 地表溫度季節變化的形狀相近 | 時間序列（形狀） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored |  |
| Gale Crater | R6 | temperature_season_amplitude | 地表溫度季節溫差（最高月 − 最低月）相近（對數比，σ = ln 2） | 時間序列（季節溫差） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored | 11/14 加：只比形狀時，季節溫差只有 4 °C 的赤道高山也能拿高分 |
| Gale Crater | R6 | — | 風（地球有 MERRA-2，火星只有 MCD；還沒做） | — | — | — | — | not_evaluated |  |
| Gale Crater | R6 | — | 逐日時間序列的分布比較（Wasserstein）與 TOST 等價性檢定 | — | — | — | — | not_evaluated |  |
| Arcadia Planitia (shallow ground ice) | R1 | slope | 100 m 尺度坡度 < 5–15°（SkyFall，待定；規劃建議先取 15°） | 門檻 | CTX／HRSC 地形（本隊用 HRSC+MOLA 200 m） | GMTED2010 230 m 坡度，0.1° 格內中位數 | 0.167 | scored | 地球端是 200 m 尺度坡度的格內中位數，不是 100 m；格內可能有局部陡坡 |
| Arcadia Planitia (shallow ground ice) | R1 | roughness | 和目標的 5×5 視窗高程標準差相近（高斯） | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 230 m | 0.167 | scored |  |
| Arcadia Planitia (shallow ground ice) | R1 | thermal_inertia | 熱慣量 > 100（最好 > 150），避開厚塵；只比相對排名 | 門檻（相對排名） | TES 夜間熱慣量 2007 的全球分位數 | 表觀熱慣量 ATI（MODIS）的全球百分位 | 0.167 | scored |  |
| Arcadia Planitia (shallow ground ice) | R1 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.167 | scored |  |
| Arcadia Planitia (shallow ground ice) | R1 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.167 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Arcadia Planitia (shallow ground ice) | R1 | ice_free | 降落面是岩石與風化層，不是冰 | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.167 | scored | 排除冰河、冰原覆蓋的格子 |
| Arcadia Planitia (shallow ground ice) | R1 | — | 1–5 m 尺度坡度（火星要 HiRISE 地形模型；地球沒有全球資料，只有極區 ArcticDEM／REMA 與美國光達，留到放大階段） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia (shallow ground ice) | R1 | — | 岩石高度 < 11 cm、覆蓋率 < 5%（地球沒有全球岩石資料；代理用雷達後向散射，留到放大階段） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia (shallow ground ice) | R1 | — | 雷達粗糙度（Sentinel-1／PALSAR，波段和火星不同，只能比相對排名，留到放大階段） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia (shallow ground ice) | R2 | — | — | — | — | — | — | not_evaluated | 全球網格沒有影像紋理與沙丘比例；需要 Sentinel-2 紋理（地球）與 CTX 紋理、MGD3 沙丘資料庫（火星），留到放大階段 |
| Arcadia Planitia (shallow ground ice) | R3 | permafrost | 目標區有淺層地下冰（SWIM Ci > 0） | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 v5.0（2023） | 0.333 | scored |  |
| Arcadia Planitia (shallow ground ice) | R3 | cold | 年均地表溫 < 0 °C（地球能維持永凍土） | 門檻 | MCD 年均地表溫 | MODIS MOD11A2+MYD11A2 2015–2024 | 0.333 | scored |  |
| Arcadia Planitia (shallow ground ice) | R3 | dryness | 極乾（火星地下冰在乾燥環境中） | 剖面（和目標比） | — | Global Aridity Index v3 | 0.333 | scored |  |
| Arcadia Planitia (shallow ground ice) | R3 | — | 多邊形地（地球沒有全球資料） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia (shallow ground ice) | R3 | — | 地下雷達與 3–5 m 深度（SHARAD；地球沒有同深度的全球資料） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia (shallow ground ice) | R4 | lithology | 和目標同類的岩性（oxia、meridiani 用文獻覆寫的礦物類別） | 剖面（和目標比） | USGS SIM3292 全球地質圖＋文獻覆寫 | GLiM 0.5° | 0.2 | scored | 只是岩性大類代理，很粗 |
| Arcadia Planitia (shallow ground ice) | R4 | barrenness | 岩石裸露（植被會遮住光譜） | 剖面（和目標比） | — | MODIS NDVI | 0.2 | scored |  |
| Arcadia Planitia (shallow ground ice) | R4 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.2 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Arcadia Planitia (shallow ground ice) | R4 | ice_free | 岩石裸露（冰雪會遮住光譜） | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.2 | scored | 排除冰河、冰原覆蓋的格子 |
| Arcadia Planitia (shallow ground ice) | R4 | mineral_signature | 目標的主要礦物（碳酸鹽、鎂鐵質）在地球同樣明顯 | 類別（礦物指標） | 文獻（見 target_attributes） | ASTER GED AG100 熱紅外放射率算的 Ninomiya 指標 | 0.2 | scored | 只對有列出指標的目標計算；黏土、硫酸鹽、赤鐵礦沒有熱紅外指標；百分位在同一年均地表溫帶內算（−5、5、15、25 °C 分帶），指標超出 0.7–1.3 當缺資料 |
| Arcadia Planitia (shallow ground ice) | R4 | — | 逐條光譜比對（CRISM／OMEGA 對 EMIT／ASTER 短波紅外） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia (shallow ground ice) | R5 | permafrost | 有地下冰 | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 | 0.167 | scored |  |
| Arcadia Planitia (shallow ground ice) | R5 | cold | 年均地表溫 < 0 °C | 門檻 | MCD | MODIS LST | 0.167 | scored |  |
| Arcadia Planitia (shallow ground ice) | R5 | slope | 地形起伏和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | 0.167 | scored |  |
| Arcadia Planitia (shallow ground ice) | R5 | roughness | 地形粗糙度和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | 0.167 | scored |  |
| Arcadia Planitia (shallow ground ice) | R5 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.167 | scored |  |
| Arcadia Planitia (shallow ground ice) | R5 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.167 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Arcadia Planitia (shallow ground ice) | R5 | glacier_distance | 目標附近有類冰河地形或葉狀碎屑裙 | 門檻 | 文獻（見 target_attributes） | GLIMS 冰河輪廓（離最近冰河的距離） | — | not_applicable_for_target | 只對 target_attributes 標了 glacial_landforms 的目標計算 |
| Arcadia Planitia (shallow ground ice) | R5 | — | 多邊形尺寸（地球冰楔多邊形 10–30 m，沒有全球資料） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia (shallow ground ice) | R6 | dust | 年均沙塵光學厚度的相對排名相近 | 剖面（和目標比） | MCD 全球沙塵（Ls 每 30°） | MERRA-2 DUEXTTAU | 0.143 | scored |  |
| Arcadia Planitia (shallow ground ice) | R6 | temperature | 盡量冷（地球到不了火星溫度，取極端百分位） | 剖面（和目標比） | MCD | MODIS LST | 0.143 | scored |  |
| Arcadia Planitia (shallow ground ice) | R6 | diurnal_range | 日溫差盡量大（取極端百分位） | 剖面（和目標比） | MCD | MODIS LST 日夜差 | 0.143 | scored | R6 本來就包含近地表溫度日變化，所以納入；類比剖面的環境面向仍不納入 |
| Arcadia Planitia (shallow ground ice) | R6 | dust_season_shape | 沙塵季節變化的形狀相近（依當地季節對齊） | 時間序列（形狀） | MCD tauref（Ls 每 15°） | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Arcadia Planitia (shallow ground ice) | R6 | dust_season_amplitude | 沙塵季節振幅（相對平均）相近 | 時間序列（振幅） | MCD tauref | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Arcadia Planitia (shallow ground ice) | R6 | temperature_season_shape | 地表溫度季節變化的形狀相近 | 時間序列（形狀） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored |  |
| Arcadia Planitia (shallow ground ice) | R6 | temperature_season_amplitude | 地表溫度季節溫差（最高月 − 最低月）相近（對數比，σ = ln 2） | 時間序列（季節溫差） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored | 11/14 加：只比形狀時，季節溫差只有 4 °C 的赤道高山也能拿高分 |
| Arcadia Planitia (shallow ground ice) | R6 | — | 風（地球有 MERRA-2，火星只有 MCD；還沒做） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia (shallow ground ice) | R6 | — | 逐日時間序列的分布比較（Wasserstein）與 TOST 等價性檢定 | — | — | — | — | not_evaluated |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R1 | slope | 100 m 尺度坡度 < 5–15°（SkyFall，待定；規劃建議先取 15°） | 門檻 | CTX／HRSC 地形（本隊用 HRSC+MOLA 200 m） | GMTED2010 230 m 坡度，0.1° 格內中位數 | 0.167 | scored | 地球端是 200 m 尺度坡度的格內中位數，不是 100 m；格內可能有局部陡坡 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R1 | roughness | 和目標的 5×5 視窗高程標準差相近（高斯） | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 230 m | 0.167 | scored |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R1 | thermal_inertia | 熱慣量 > 100（最好 > 150），避開厚塵；只比相對排名 | 門檻（相對排名） | TES 夜間熱慣量 2007 的全球分位數 | 表觀熱慣量 ATI（MODIS）的全球百分位 | 0.167 | scored |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R1 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.167 | scored |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R1 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.167 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R1 | ice_free | 降落面是岩石與風化層，不是冰 | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.167 | scored | 排除冰河、冰原覆蓋的格子 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R1 | — | 1–5 m 尺度坡度（火星要 HiRISE 地形模型；地球沒有全球資料，只有極區 ArcticDEM／REMA 與美國光達，留到放大階段） | — | — | — | — | not_evaluated |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R1 | — | 岩石高度 < 11 cm、覆蓋率 < 5%（地球沒有全球岩石資料；代理用雷達後向散射，留到放大階段） | — | — | — | — | not_evaluated |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R1 | — | 雷達粗糙度（Sentinel-1／PALSAR，波段和火星不同，只能比相對排名，留到放大階段） | — | — | — | — | not_evaluated |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R2 | — | — | — | — | — | — | not_evaluated | 全球網格沒有影像紋理與沙丘比例；需要 Sentinel-2 紋理（地球）與 CTX 紋理、MGD3 沙丘資料庫（火星），留到放大階段 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R3 | permafrost | 目標區有淺層地下冰（SWIM Ci > 0） | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 v5.0（2023） | — | not_applicable |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R3 | cold | 年均地表溫 < 0 °C（地球能維持永凍土） | 門檻 | MCD 年均地表溫 | MODIS MOD11A2+MYD11A2 2015–2024 | — | not_applicable |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R3 | dryness | 極乾（火星地下冰在乾燥環境中） | 剖面（和目標比） | — | Global Aridity Index v3 | — | not_applicable |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R3 | — | 多邊形地（地球沒有全球資料） | — | — | — | — | not_evaluated |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R3 | — | 地下雷達與 3–5 m 深度（SHARAD；地球沒有同深度的全球資料） | — | — | — | — | not_evaluated |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R4 | lithology | 和目標同類的岩性（oxia、meridiani 用文獻覆寫的礦物類別） | 剖面（和目標比） | USGS SIM3292 全球地質圖＋文獻覆寫 | GLiM 0.5° | 0.25 | scored | 只是岩性大類代理，很粗 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R4 | barrenness | 岩石裸露（植被會遮住光譜） | 剖面（和目標比） | — | MODIS NDVI | 0.25 | scored |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R4 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.25 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R4 | ice_free | 岩石裸露（冰雪會遮住光譜） | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.25 | scored | 排除冰河、冰原覆蓋的格子 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R4 | mineral_signature | 目標的主要礦物（碳酸鹽、鎂鐵質）在地球同樣明顯 | 類別（礦物指標） | 文獻（見 target_attributes） | ASTER GED AG100 熱紅外放射率算的 Ninomiya 指標 | — | not_applicable_for_target | 只對有列出指標的目標計算；黏土、硫酸鹽、赤鐵礦沒有熱紅外指標；百分位在同一年均地表溫帶內算（−5、5、15、25 °C 分帶），指標超出 0.7–1.3 當缺資料 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R4 | — | 逐條光譜比對（CRISM／OMEGA 對 EMIT／ASTER 短波紅外） | — | — | — | — | not_evaluated |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R5 | permafrost | 有地下冰 | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 | — | not_applicable |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R5 | cold | 年均地表溫 < 0 °C | 門檻 | MCD | MODIS LST | — | not_applicable |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R5 | slope | 地形起伏和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | — | not_applicable |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R5 | roughness | 地形粗糙度和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | — | not_applicable |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R5 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | — | not_applicable |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R5 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | — | not_applicable | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R5 | glacier_distance | 目標附近有類冰河地形或葉狀碎屑裙 | 門檻 | 文獻（見 target_attributes） | GLIMS 冰河輪廓（離最近冰河的距離） | — | not_applicable | 只對 target_attributes 標了 glacial_landforms 的目標計算 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R5 | — | 多邊形尺寸（地球冰楔多邊形 10–30 m，沒有全球資料） | — | — | — | — | not_evaluated |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R6 | dust | 年均沙塵光學厚度的相對排名相近 | 剖面（和目標比） | MCD 全球沙塵（Ls 每 30°） | MERRA-2 DUEXTTAU | 0.143 | scored |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R6 | temperature | 盡量冷（地球到不了火星溫度，取極端百分位） | 剖面（和目標比） | MCD | MODIS LST | 0.143 | scored |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R6 | diurnal_range | 日溫差盡量大（取極端百分位） | 剖面（和目標比） | MCD | MODIS LST 日夜差 | 0.143 | scored | R6 本來就包含近地表溫度日變化，所以納入；類比剖面的環境面向仍不納入 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R6 | dust_season_shape | 沙塵季節變化的形狀相近（依當地季節對齊） | 時間序列（形狀） | MCD tauref（Ls 每 15°） | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R6 | dust_season_amplitude | 沙塵季節振幅（相對平均）相近 | 時間序列（振幅） | MCD tauref | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R6 | temperature_season_shape | 地表溫度季節變化的形狀相近 | 時間序列（形狀） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R6 | temperature_season_amplitude | 地表溫度季節溫差（最高月 − 最低月）相近（對數比，σ = ln 2） | 時間序列（季節溫差） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored | 11/14 加：只比形狀時，季節溫差只有 4 °C 的赤道高山也能拿高分 |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R6 | — | 風（地球有 MERRA-2，火星只有 MCD；還沒做） | — | — | — | — | not_evaluated |  |
| Oxia Planum (ExoMars Rosalind Franklin landing site) | R6 | — | 逐日時間序列的分布比較（Wasserstein）與 TOST 等價性檢定 | — | — | — | — | not_evaluated |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R1 | slope | 100 m 尺度坡度 < 5–15°（SkyFall，待定；規劃建議先取 15°） | 門檻 | CTX／HRSC 地形（本隊用 HRSC+MOLA 200 m） | GMTED2010 230 m 坡度，0.1° 格內中位數 | 0.167 | scored | 地球端是 200 m 尺度坡度的格內中位數，不是 100 m；格內可能有局部陡坡 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R1 | roughness | 和目標的 5×5 視窗高程標準差相近（高斯） | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 230 m | 0.167 | scored |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R1 | thermal_inertia | 熱慣量 > 100（最好 > 150），避開厚塵；只比相對排名 | 門檻（相對排名） | TES 夜間熱慣量 2007 的全球分位數 | 表觀熱慣量 ATI（MODIS）的全球百分位 | 0.167 | scored |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R1 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.167 | scored |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R1 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.167 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R1 | ice_free | 降落面是岩石與風化層，不是冰 | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.167 | scored | 排除冰河、冰原覆蓋的格子 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R1 | — | 1–5 m 尺度坡度（火星要 HiRISE 地形模型；地球沒有全球資料，只有極區 ArcticDEM／REMA 與美國光達，留到放大階段） | — | — | — | — | not_evaluated |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R1 | — | 岩石高度 < 11 cm、覆蓋率 < 5%（地球沒有全球岩石資料；代理用雷達後向散射，留到放大階段） | — | — | — | — | not_evaluated |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R1 | — | 雷達粗糙度（Sentinel-1／PALSAR，波段和火星不同，只能比相對排名，留到放大階段） | — | — | — | — | not_evaluated |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R2 | — | — | — | — | — | — | not_evaluated | 全球網格沒有影像紋理與沙丘比例；需要 Sentinel-2 紋理（地球）與 CTX 紋理、MGD3 沙丘資料庫（火星），留到放大階段 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R3 | permafrost | 目標區有淺層地下冰（SWIM Ci > 0） | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 v5.0（2023） | — | not_applicable |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R3 | cold | 年均地表溫 < 0 °C（地球能維持永凍土） | 門檻 | MCD 年均地表溫 | MODIS MOD11A2+MYD11A2 2015–2024 | — | not_applicable |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R3 | dryness | 極乾（火星地下冰在乾燥環境中） | 剖面（和目標比） | — | Global Aridity Index v3 | — | not_applicable |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R3 | — | 多邊形地（地球沒有全球資料） | — | — | — | — | not_evaluated |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R3 | — | 地下雷達與 3–5 m 深度（SHARAD；地球沒有同深度的全球資料） | — | — | — | — | not_evaluated |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R4 | lithology | 和目標同類的岩性（oxia、meridiani 用文獻覆寫的礦物類別） | 剖面（和目標比） | USGS SIM3292 全球地質圖＋文獻覆寫 | GLiM 0.5° | 0.25 | scored | 只是岩性大類代理，很粗 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R4 | barrenness | 岩石裸露（植被會遮住光譜） | 剖面（和目標比） | — | MODIS NDVI | 0.25 | scored |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R4 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.25 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R4 | ice_free | 岩石裸露（冰雪會遮住光譜） | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.25 | scored | 排除冰河、冰原覆蓋的格子 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R4 | mineral_signature | 目標的主要礦物（碳酸鹽、鎂鐵質）在地球同樣明顯 | 類別（礦物指標） | 文獻（見 target_attributes） | ASTER GED AG100 熱紅外放射率算的 Ninomiya 指標 | — | not_applicable_for_target | 只對有列出指標的目標計算；黏土、硫酸鹽、赤鐵礦沒有熱紅外指標；百分位在同一年均地表溫帶內算（−5、5、15、25 °C 分帶），指標超出 0.7–1.3 當缺資料 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R4 | — | 逐條光譜比對（CRISM／OMEGA 對 EMIT／ASTER 短波紅外） | — | — | — | — | not_evaluated |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R5 | permafrost | 有地下冰 | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 | — | not_applicable |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R5 | cold | 年均地表溫 < 0 °C | 門檻 | MCD | MODIS LST | — | not_applicable |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R5 | slope | 地形起伏和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | — | not_applicable |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R5 | roughness | 地形粗糙度和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | — | not_applicable |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R5 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | — | not_applicable |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R5 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | — | not_applicable | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R5 | glacier_distance | 目標附近有類冰河地形或葉狀碎屑裙 | 門檻 | 文獻（見 target_attributes） | GLIMS 冰河輪廓（離最近冰河的距離） | — | not_applicable | 只對 target_attributes 標了 glacial_landforms 的目標計算 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R5 | — | 多邊形尺寸（地球冰楔多邊形 10–30 m，沒有全球資料） | — | — | — | — | not_evaluated |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R6 | dust | 年均沙塵光學厚度的相對排名相近 | 剖面（和目標比） | MCD 全球沙塵（Ls 每 30°） | MERRA-2 DUEXTTAU | 0.143 | scored |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R6 | temperature | 盡量冷（地球到不了火星溫度，取極端百分位） | 剖面（和目標比） | MCD | MODIS LST | 0.143 | scored |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R6 | diurnal_range | 日溫差盡量大（取極端百分位） | 剖面（和目標比） | MCD | MODIS LST 日夜差 | 0.143 | scored | R6 本來就包含近地表溫度日變化，所以納入；類比剖面的環境面向仍不納入 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R6 | dust_season_shape | 沙塵季節變化的形狀相近（依當地季節對齊） | 時間序列（形狀） | MCD tauref（Ls 每 15°） | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R6 | dust_season_amplitude | 沙塵季節振幅（相對平均）相近 | 時間序列（振幅） | MCD tauref | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R6 | temperature_season_shape | 地表溫度季節變化的形狀相近 | 時間序列（形狀） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R6 | temperature_season_amplitude | 地表溫度季節溫差（最高月 − 最低月）相近（對數比，σ = ln 2） | 時間序列（季節溫差） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored | 11/14 加：只比形狀時，季節溫差只有 4 °C 的赤道高山也能拿高分 |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R6 | — | 風（地球有 MERRA-2，火星只有 MCD；還沒做） | — | — | — | — | not_evaluated |  |
| Meridiani Planum (Opportunity landing site, Eagle crater) | R6 | — | 逐日時間序列的分布比較（Wasserstein）與 TOST 等價性檢定 | — | — | — | — | not_evaluated |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R1 | slope | 100 m 尺度坡度 < 5–15°（SkyFall，待定；規劃建議先取 15°） | 門檻 | CTX／HRSC 地形（本隊用 HRSC+MOLA 200 m） | GMTED2010 230 m 坡度，0.1° 格內中位數 | 0.167 | scored | 地球端是 200 m 尺度坡度的格內中位數，不是 100 m；格內可能有局部陡坡 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R1 | roughness | 和目標的 5×5 視窗高程標準差相近（高斯） | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 230 m | 0.167 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R1 | thermal_inertia | 熱慣量 > 100（最好 > 150），避開厚塵；只比相對排名 | 門檻（相對排名） | TES 夜間熱慣量 2007 的全球分位數 | 表觀熱慣量 ATI（MODIS）的全球百分位 | 0.167 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R1 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.167 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R1 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.167 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R1 | ice_free | 降落面是岩石與風化層，不是冰 | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.167 | scored | 排除冰河、冰原覆蓋的格子 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R1 | — | 1–5 m 尺度坡度（火星要 HiRISE 地形模型；地球沒有全球資料，只有極區 ArcticDEM／REMA 與美國光達，留到放大階段） | — | — | — | — | not_evaluated |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R1 | — | 岩石高度 < 11 cm、覆蓋率 < 5%（地球沒有全球岩石資料；代理用雷達後向散射，留到放大階段） | — | — | — | — | not_evaluated |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R1 | — | 雷達粗糙度（Sentinel-1／PALSAR，波段和火星不同，只能比相對排名，留到放大階段） | — | — | — | — | not_evaluated |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R2 | — | — | — | — | — | — | not_evaluated | 全球網格沒有影像紋理與沙丘比例；需要 Sentinel-2 紋理（地球）與 CTX 紋理、MGD3 沙丘資料庫（火星），留到放大階段 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R3 | permafrost | 目標區有淺層地下冰（SWIM Ci > 0） | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 v5.0（2023） | 0.333 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R3 | cold | 年均地表溫 < 0 °C（地球能維持永凍土） | 門檻 | MCD 年均地表溫 | MODIS MOD11A2+MYD11A2 2015–2024 | 0.333 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R3 | dryness | 極乾（火星地下冰在乾燥環境中） | 剖面（和目標比） | — | Global Aridity Index v3 | 0.333 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R3 | — | 多邊形地（地球沒有全球資料） | — | — | — | — | not_evaluated |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R3 | — | 地下雷達與 3–5 m 深度（SHARAD；地球沒有同深度的全球資料） | — | — | — | — | not_evaluated |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R4 | lithology | 和目標同類的岩性（oxia、meridiani 用文獻覆寫的礦物類別） | 剖面（和目標比） | USGS SIM3292 全球地質圖＋文獻覆寫 | GLiM 0.5° | 0.25 | scored | 只是岩性大類代理，很粗 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R4 | barrenness | 岩石裸露（植被會遮住光譜） | 剖面（和目標比） | — | MODIS NDVI | 0.25 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R4 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.25 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R4 | ice_free | 岩石裸露（冰雪會遮住光譜） | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.25 | scored | 排除冰河、冰原覆蓋的格子 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R4 | mineral_signature | 目標的主要礦物（碳酸鹽、鎂鐵質）在地球同樣明顯 | 類別（礦物指標） | 文獻（見 target_attributes） | ASTER GED AG100 熱紅外放射率算的 Ninomiya 指標 | — | not_applicable_for_target | 只對有列出指標的目標計算；黏土、硫酸鹽、赤鐵礦沒有熱紅外指標；百分位在同一年均地表溫帶內算（−5、5、15、25 °C 分帶），指標超出 0.7–1.3 當缺資料 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R4 | — | 逐條光譜比對（CRISM／OMEGA 對 EMIT／ASTER 短波紅外） | — | — | — | — | not_evaluated |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R5 | permafrost | 有地下冰 | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R5 | cold | 年均地表溫 < 0 °C | 門檻 | MCD | MODIS LST | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R5 | slope | 地形起伏和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R5 | roughness | 地形粗糙度和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R5 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R5 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.143 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R5 | glacier_distance | 目標附近有類冰河地形或葉狀碎屑裙 | 門檻 | 文獻（見 target_attributes） | GLIMS 冰河輪廓（離最近冰河的距離） | 0.143 | scored | 只對 target_attributes 標了 glacial_landforms 的目標計算 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R5 | — | 多邊形尺寸（地球冰楔多邊形 10–30 m，沒有全球資料） | — | — | — | — | not_evaluated |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R6 | dust | 年均沙塵光學厚度的相對排名相近 | 剖面（和目標比） | MCD 全球沙塵（Ls 每 30°） | MERRA-2 DUEXTTAU | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R6 | temperature | 盡量冷（地球到不了火星溫度，取極端百分位） | 剖面（和目標比） | MCD | MODIS LST | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R6 | diurnal_range | 日溫差盡量大（取極端百分位） | 剖面（和目標比） | MCD | MODIS LST 日夜差 | 0.143 | scored | R6 本來就包含近地表溫度日變化，所以納入；類比剖面的環境面向仍不納入 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R6 | dust_season_shape | 沙塵季節變化的形狀相近（依當地季節對齊） | 時間序列（形狀） | MCD tauref（Ls 每 15°） | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R6 | dust_season_amplitude | 沙塵季節振幅（相對平均）相近 | 時間序列（振幅） | MCD tauref | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R6 | temperature_season_shape | 地表溫度季節變化的形狀相近 | 時間序列（形狀） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R6 | temperature_season_amplitude | 地表溫度季節溫差（最高月 − 最低月）相近（對數比，σ = ln 2） | 時間序列（季節溫差） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored | 11/14 加：只比形狀時，季節溫差只有 4 °C 的赤道高山也能拿高分 |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R6 | — | 風（地球有 MERRA-2，火星只有 MCD；還沒做） | — | — | — | — | not_evaluated |  |
| Protonilus Mensae (candidate human exploration zone, buried glacial ice) | R6 | — | 逐日時間序列的分布比較（Wasserstein）與 TOST 等價性檢定 | — | — | — | — | not_evaluated |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R1 | slope | 100 m 尺度坡度 < 5–15°（SkyFall，待定；規劃建議先取 15°） | 門檻 | CTX／HRSC 地形（本隊用 HRSC+MOLA 200 m） | GMTED2010 230 m 坡度，0.1° 格內中位數 | 0.167 | scored | 地球端是 200 m 尺度坡度的格內中位數，不是 100 m；格內可能有局部陡坡 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R1 | roughness | 和目標的 5×5 視窗高程標準差相近（高斯） | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 230 m | 0.167 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R1 | thermal_inertia | 熱慣量 > 100（最好 > 150），避開厚塵；只比相對排名 | 門檻（相對排名） | TES 夜間熱慣量 2007 的全球分位數 | 表觀熱慣量 ATI（MODIS）的全球百分位 | 0.167 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R1 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.167 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R1 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.167 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R1 | ice_free | 降落面是岩石與風化層，不是冰 | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.167 | scored | 排除冰河、冰原覆蓋的格子 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R1 | — | 1–5 m 尺度坡度（火星要 HiRISE 地形模型；地球沒有全球資料，只有極區 ArcticDEM／REMA 與美國光達，留到放大階段） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R1 | — | 岩石高度 < 11 cm、覆蓋率 < 5%（地球沒有全球岩石資料；代理用雷達後向散射，留到放大階段） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R1 | — | 雷達粗糙度（Sentinel-1／PALSAR，波段和火星不同，只能比相對排名，留到放大階段） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R2 | — | — | — | — | — | — | not_evaluated | 全球網格沒有影像紋理與沙丘比例；需要 Sentinel-2 紋理（地球）與 CTX 紋理、MGD3 沙丘資料庫（火星），留到放大階段 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R3 | permafrost | 目標區有淺層地下冰（SWIM Ci > 0） | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 v5.0（2023） | 0.333 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R3 | cold | 年均地表溫 < 0 °C（地球能維持永凍土） | 門檻 | MCD 年均地表溫 | MODIS MOD11A2+MYD11A2 2015–2024 | 0.333 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R3 | dryness | 極乾（火星地下冰在乾燥環境中） | 剖面（和目標比） | — | Global Aridity Index v3 | 0.333 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R3 | — | 多邊形地（地球沒有全球資料） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R3 | — | 地下雷達與 3–5 m 深度（SHARAD；地球沒有同深度的全球資料） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R4 | lithology | 和目標同類的岩性（oxia、meridiani 用文獻覆寫的礦物類別） | 剖面（和目標比） | USGS SIM3292 全球地質圖＋文獻覆寫 | GLiM 0.5° | 0.2 | scored | 只是岩性大類代理，很粗 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R4 | barrenness | 岩石裸露（植被會遮住光譜） | 剖面（和目標比） | — | MODIS NDVI | 0.2 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R4 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.2 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R4 | ice_free | 岩石裸露（冰雪會遮住光譜） | 門檻 | — | MCD12Q1 冰雪比例、GLIMS 冰河比例、年均 NDVI < 0 且年均溫 < 0 °C 取最大 | 0.2 | scored | 排除冰河、冰原覆蓋的格子 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R4 | mineral_signature | 目標的主要礦物（碳酸鹽、鎂鐵質）在地球同樣明顯 | 類別（礦物指標） | 文獻（見 target_attributes） | ASTER GED AG100 熱紅外放射率算的 Ninomiya 指標 | 0.2 | scored | 只對有列出指標的目標計算；黏土、硫酸鹽、赤鐵礦沒有熱紅外指標；百分位在同一年均地表溫帶內算（−5、5、15、25 °C 分帶），指標超出 0.7–1.3 當缺資料 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R4 | — | 逐條光譜比對（CRISM／OMEGA 對 EMIT／ASTER 短波紅外） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R5 | permafrost | 有地下冰 | 門檻 | SWIM4MIM Ci | ESA CCI 永凍土 | 0.167 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R5 | cold | 年均地表溫 < 0 °C | 門檻 | MCD | MODIS LST | 0.167 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R5 | slope | 地形起伏和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | 0.167 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R5 | roughness | 地形粗糙度和目標相近 | 剖面（和目標比） | HRSC+MOLA 200 m | GMTED2010 | 0.167 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R5 | barrenness | 無植被 | 剖面（和目標比） | — | MODIS NDVI | 0.167 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R5 | summer_barren | 夏季也沒有植被（生長季高峰 NDVI 低） | 門檻 | — | MOD13A2 2015–2024 NDVI 第 90 百分位 | 0.167 | scored | 11/14 加：年平均 NDVI 在寒冷地區被積雪拉低，凍原會被誤當成荒地 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R5 | glacier_distance | 目標附近有類冰河地形或葉狀碎屑裙 | 門檻 | 文獻（見 target_attributes） | GLIMS 冰河輪廓（離最近冰河的距離） | — | not_applicable_for_target | 只對 target_attributes 標了 glacial_landforms 的目標計算 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R5 | — | 多邊形尺寸（地球冰楔多邊形 10–30 m，沒有全球資料） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R6 | dust | 年均沙塵光學厚度的相對排名相近 | 剖面（和目標比） | MCD 全球沙塵（Ls 每 30°） | MERRA-2 DUEXTTAU | 0.143 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R6 | temperature | 盡量冷（地球到不了火星溫度，取極端百分位） | 剖面（和目標比） | MCD | MODIS LST | 0.143 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R6 | diurnal_range | 日溫差盡量大（取極端百分位） | 剖面（和目標比） | MCD | MODIS LST 日夜差 | 0.143 | scored | R6 本來就包含近地表溫度日變化，所以納入；類比剖面的環境面向仍不納入 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R6 | dust_season_shape | 沙塵季節變化的形狀相近（依當地季節對齊） | 時間序列（形狀） | MCD tauref（Ls 每 15°） | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R6 | dust_season_amplitude | 沙塵季節振幅（相對平均）相近 | 時間序列（振幅） | MCD tauref | MERRA-2 DUEXTTAU 月平均 | 0.143 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R6 | temperature_season_shape | 地表溫度季節變化的形狀相近 | 時間序列（形狀） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R6 | temperature_season_amplitude | 地表溫度季節溫差（最高月 − 最低月）相近（對數比，σ = ln 2） | 時間序列（季節溫差） | MCD 地表溫（Ls 每 15°） | MODIS LST 月平均 | 0.143 | scored | 11/14 加：只比形狀時，季節溫差只有 4 °C 的赤道高山也能拿高分 |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R6 | — | 風（地球有 MERRA-2，火星只有 MCD；還沒做） | — | — | — | — | not_evaluated |  |
| Arcadia Planitia AP-105 (SkyFall design reference landing site) | R6 | — | 逐日時間序列的分布比較（Wasserstein）與 TOST 等價性檢定 | — | — | — | — | not_evaluated |  |
