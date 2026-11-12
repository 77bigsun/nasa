嗨！火星組資料更新：第一版「實測資料」好了，請用這兩個檔案（取代之前的 mock）：

1. `mars_candidates_features.json`：2 個火星目標（Jezero 200 m、Arcadia 463 m，每個指標有 target 和 sigma）＋ 12 個地球候選點（6 個 NASA 已知類比地、4 個台灣案例、2 個負樣本）。`is_mock` 現在是 `false`，數值來自 Copernicus 30 m DEM、MODIS、CHIRPS / ERA5-Land（2015–2024 平均）。
2. `candidates_points.geojson`：同樣 12 個點，帶全部特徵，給前端地圖用。

8 個特徵欄位沒變：
`slope_deg`, `roughness_m`, `mean_temp_c`, `diurnal_temp_range_c`, `precip_mm_yr`, `ndvi`, `subsurface_ice_index`, `lithology`

每個點多了 `data_confidence` 和 `fallback_fields`（哪些欄位還是估計值），你可以拿來加權。

## 資料問題（先跟你說）

- Atacama 的降雨 161 mm/yr 是 CHIRPS 的偏差，Yungay 實際 < 2 mm/yr。
- McMurdo 的 NDVI 是估計值（冰雪覆蓋沒資料）。
- 澎湖的地形範圍大部分是海，坡度和粗糙度偏低。
- 冰島 Askja 的 `subsurface_ice_index` = 0.3 還是猜測值。
- 火星目標值還是預設值（Jezero 坡度 4.1°、Arcadia 1.4°），我們實測是 3.15° 和 0.23°，明天會議再決定要不要換。

我先用高斯相似度＋等權重幾何平均算了一個初步排名，6 個已知類比地都排在台灣點和負樣本前面。你的權重設計如果不同，我再配合調整格式。

## 想跟你確認

1. 8 個欄位夠不夠你用？`lithology` 是固定詞彙（basalt、basalt_permafrost、clastic、clastic_permafrost、mudstone_clastic、evaporite_sulfate_clastic、impact_breccia_carbonate、sedimentary_carbonate_clay、hydrothermal_sulfate、soil），你可能需要一張岩性相似度對照表。
2. 前端地圖（MapLibre 或 CesiumJS）只要點位 GeoJSON，還是要我另外切幾塊重點區域（阿塔卡馬、田寮月世界）的網格熱度圖？

小提醒：Arcadia Planitia 的經度是 172.0（原本草稿的 -188 超出 -180～180 的範圍，指的是同一個位置）。
