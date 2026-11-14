# 給網頁整合的資料（export_web_seed.py 產生）

契約來源：C:\Users\plusl\nasa-main\data\seed。產生時間：2026-11-15 00:50。

## 1. 交什麼

| 檔案 | 放到網頁的哪裡 | 內容 |
|---|---|---|
| `current/merged/earth_candidates.demo.json` | `data/seed/earth_candidates.demo.json` | 月球 placeholder 候選（火星特徵值已移除）＋本隊 28 個火星用的地球候選（真實資料） |
| `current/merged/target_values.demo.yaml` | `data/seed/target_values.demo.yaml` | mars-ap105、mars-jezero、mars-gale 換成真實值，其他目標維持 placeholder |
| `proposed/`（同上兩檔＋`tasks_mars.yaml`、`categorical_tables.yaml`、`data_sources.yaml`） | `data/seed/` | 套用第 3 節建議後的版本：R1–R6 除了 R2 都能評分 |
| `earth_population.json` | 需要網頁改一行程式才會用到（第 4 節） | 每個特徵的地球全球分位數 |

`current/` 不用改網頁任何程式或定義，直接替換兩個檔就能跑；`proposed/` 需要整合者同意改任務定義。
沒有 `merged/` 資料夾時表示沒給 `--web-seed`，只有本隊的部分（`earth_candidates.mars.json`、`target_values.mars.yaml`），要手動併進去。

## 2. 特徵對照

| 任務 | 特徵 id | 名稱 | 地球欄位 | 現在的定義 | 現在 | 建議的定義 | 建議後 |
|---|---|---|---|---|---|---|---|
| R1 | r1_barren | 無植被 | ndvi_mean | （新增） |  | threshold / absolute | 有值 |
| R1 | r1_ice_free | 不是冰面 | icy_frac | （新增） |  | threshold / absolute | 有值 |
| R1 | r1_rock | 岩石覆蓋率 | — | threshold / relative_rank | 沒有資料 | 同左 | 沒有資料 |
| R1 | r1_slope_100m | 100 m 坡度 | slope_deg | threshold / absolute | 有值 | 同左 | 有值 |
| R1 | r1_slope_1_5m | 1–5 m 坡度 | — | threshold / absolute | 沒有資料 | 同左 | 沒有資料 |
| R1 | r1_thermal_inertia | 熱慣量 | ati | threshold / relative_rank | 有值 | 同左 | 有值 |
| R2 | r2_dune_fraction | 沙丘與沙原比例 | — | threshold / absolute | 沒有資料 | 同左 | 沒有資料 |
| R2 | r2_texture | 影像紋理豐富度 | — | profile / relative_rank | 沒有資料 | 同左 | 沒有資料 |
| R3 | r3_cold | 年均地表溫低於 0 °C | lst_mean_c | （新增） |  | threshold / absolute | 有值 |
| R3 | r3_dryness | 乾燥程度 | aridity_index | （新增） |  | profile / relative_rank | 有值 |
| R3 | r3_ground_ice | 地下冰分布與深度 | permafrost_frac | profile / relative_rank | 沒有資料 | threshold / absolute | 有值 |
| R3 | r3_polygons | 多邊形地 | — | categorical / absolute | 沒有資料 | 同左 | 沒有資料 |
| R3 | r3_subsurface_radar | 地表下雷達 | — | profile / relative_rank | 沒有資料 | 同左 | 沒有資料 |
| R4 | r4_barren | 岩石裸露 | ndvi_mean | （新增） |  | threshold / absolute | 有值 |
| R4 | r4_hydrated_spectra | 含水礦物光譜 | — | spectral / absolute | 沒有資料 | 同左 | 沒有資料 |
| R4 | r4_lithology | 岩性大類 | glim_class | （新增） |  | categorical / absolute | 有值 |
| R5 | r5_cold | 年均地表溫低於 0 °C | lst_mean_c | （新增） |  | threshold / absolute | 有值 |
| R5 | r5_ground_ice | 永凍土 | permafrost_frac | （新增） |  | threshold / absolute | 有值 |
| R5 | r5_landform | 地貌類型 | — | categorical / absolute | 沒有資料 | 同左 | 沒有資料 |
| R5 | r5_polygon_size | 多邊形尺寸 | — | profile / absolute | 沒有資料 | 同左 | 沒有資料 |
| R5 | r5_roughness | 地表粗糙度 | roughness_m | profile / relative_rank | 沒有資料 | profile / absolute | 有值 |
| R6 | r6_dust | 沙塵頻率與季節性 | dust_m01…12 序列 | timeseries / relative_rank | 有值 | 同左 | 有值 |
| R6 | r6_temperature | 年均地表溫（越冷越好） | lst_mean_c | （新增） |  | profile / relative_rank | 有值 |
| R6 | r6_wind_temp | 風、近地表溫度日變化 | 夜溫、日溫兩點序列 | timeseries / relative_rank | 有值 | 同左 | 有值 |

「沒有資料」的特徵在網頁會顯示缺值，不會補數字。現在的定義下只有 R1（100 m 坡度、熱慣量）和 R6（沙塵、日夜溫差）評得出分數：
R3 地下冰、R5 粗糙度是 relative_rank，要火星百分位，本隊只有原始值（SWIM Ci、HRSC 粗糙度），所以目標值留空、原始值放 `planet_values`。

目標的補充說明：
- `mars-jezero`：SWIM Ci = -0.206（< 0.1）：R3、R5 不適用，這兩項的目標值全部留空
- `mars-gale`：SWIM Ci = 0.059（< 0.1）：R3、R5 不適用，這兩項的目標值全部留空

## 3. 建議整合者改的地方（proposed/）

1. `r3_ground_ice` 改成門檻型（永凍土比例 0.1 → 0、0.9 → 1），`r5_roughness` 改 absolute（兩邊同為 200 m 尺度、單位公尺）。
2. 新增本隊已經有資料的特徵：R1 無植被、不是冰面；R3 年均溫 < 0 °C、乾燥程度；R4 岩性大類（附對照表）、岩石裸露；
   R5 永凍土、年均溫；R6 年均地表溫。規則和本隊 `config/mission_tests.yaml` 相同。
3. R3、R5 只對有地下冰的目標評分（SWIM Ci ≥ 0.1）：網頁沒有「不適用」機制，所以 Jezero、Gale 的 R3／R5 目標值全部留空，這兩項會是「無法覆蓋」。
4. `data_sources.yaml` 新增 GMTED2010、HRSC＋MOLA、GLiM、SIM 3292、Global Aridity Index、TES 熱慣量。
5. SkyFall 另外四區（Deuteronilus、Utopia、Phlegra、Erebus）在 `target_sites.yaml` 還沒有座標：給座標後火星組可以用同一套程式抽值。

## 4. 網頁評分程式要注意的事（需要整合者決定）

1. **百分位母體**：網頁用「候選清單本身」算百分位與標準差（`services/similarity/app/engine.py` 的 `populations`）。
   候選只有幾十個、而且都是挑過的寒冷乾燥地點，在裡面排百分位和「在地球上排第幾」差很多。本隊的百分位是全球無冰陸地
   （0.1° 格、cos 緯度加權）。建議 measurements 服務多回傳 `earth_population.json`，`populations[fid]` 有全球分位數時優先用它。
   下面的檢查表把兩種母體並排（「全球分位數」那列就是只改這一行的結果）。
2. **候選數量**：邊際效益曲線與敏感度分析用窮舉組合（`fixed_k_options`，C(n, k)，k 到 6）。月球 20 個＋火星 28 個 =
   48 個候選時 C(48, 6) ≈ 12,271,512 種組合，會跑很久或記憶體不夠。建議二選一：
   (a) 算分前只留「這個任務有任何特徵值」的候選（月球、火星各自 20 多個）；(b) 固定 k 的最大覆蓋改用 PuLP（程式裡已經有）。
   (a) 也順便讓火星結果不會因為月球 placeholder 候選而一直顯示 placeholder 警告。
3. **時間序列**：r6_dust 的 phase 是「當地季節」（太陽黃經 / 360），地球每月一點、火星每 15° Ls 一點；r6_wind_temp 地球只有日、夜兩點。

### 網頁程式檢查：current（網頁現在的定義）

契約驗證通過（catalog、measurements 的 pydantic 模型）。合併後候選 48 個，其中 28 個有火星特徵值；下面只用這 28 個（等同第 4 節第 2 點 (a)）。τ = 0.7。

**mars-ap105**

| 百分位母體 | 前三名（總分） | 各任務最高分 | 最少地點 | 無法覆蓋 |
|---|---|---|---|---|
| 候選本身（網頁現在） | 距 Jisegumen (CN) 120 km（0.47）、Zuogaiduoma (CN) 附近（0.43）、Kosh-Agach (RU) 附近（0.42） | R1 1.00, R2 —, R3 —, R4 —, R5 —, R6 0.74 | 2：南極 74.3°S 163.4°E、距 Hoit Taria (CN) 78 km | R2, R3, R4, R5 |
| 全球分位數（建議） | 距 Mori (CN) 113 km（0.50）、Zuogaiduoma (CN) 附近（0.50）、距 Ocucaje (PE) 39 km（0.49） | R1 1.00, R2 —, R3 —, R4 —, R5 —, R6 0.84 | 1：距 Jisegumen (CN) 120 km | R2, R3, R4, R5 |

**mars-jezero**

| 百分位母體 | 前三名（總分） | 各任務最高分 | 最少地點 | 無法覆蓋 |
|---|---|---|---|---|
| 候選本身（網頁現在） | Zuogaiduoma (CN) 附近（0.43）、距 Talnakh (RU) 260 km（0.41）、72.5°N 114.5°W（最近城鎮 Kugluktuk (CA)，526 km）（0.41） | R1 1.00, R2 —, R3 —, R4 —, R5 —, R6 0.91 | 2：Zuogaiduoma (CN) 附近、距 Sultanah (SA) 147 km | R2, R3, R4, R5 |
| 全球分位數（建議） | Zuogaiduoma (CN) 附近（0.50）、距 Talnakh (RU) 260 km（0.41）、80.8°N 92.8°E（最近城鎮 Talnakh (RU)，1258 km）（0.41） | R1 1.00, R2 —, R3 —, R4 —, R5 —, R6 0.97 | 2：南極 82.2°S 163.2°E、距 Sultanah (SA) 147 km | R2, R3, R4, R5 |

**mars-gale**

| 百分位母體 | 前三名（總分） | 各任務最高分 | 最少地點 | 無法覆蓋 |
|---|---|---|---|---|
| 候選本身（網頁現在） | Zuogaiduoma (CN) 附近（0.43）、距 Torghay (KZ) 167 km（0.41）、距 Talnakh (RU) 260 km（0.41） | R1 1.00, R2 —, R3 —, R4 —, R5 —, R6 0.84 | 2：Zuogaiduoma (CN) 附近、距 Khapalu (PK) 118 km | R2, R3, R4, R5 |
| 全球分位數（建議） | Zuogaiduoma (CN) 附近（0.52）、Sidi el Hani (TN) 附近（0.41）、距 Talnakh (RU) 260 km（0.41） | R1 1.00, R2 —, R3 —, R4 —, R5 —, R6 0.98 | 1：Zuogaiduoma (CN) 附近 | R2, R3, R4, R5 |

用全部 48 個候選時 `uses_placeholder` = true（月球 placeholder 候選造成）；邊際效益曲線要窮舉 C(48, 6) = 12,271,512 種組合，這裡沒有跑。

### 網頁程式檢查：proposed（套用本隊建議）

契約驗證通過（catalog、measurements 的 pydantic 模型）。合併後候選 48 個，其中 28 個有火星特徵值；下面只用這 28 個（等同第 4 節第 2 點 (a)）。τ = 0.7。

**mars-ap105**

| 百分位母體 | 前三名（總分） | 各任務最高分 | 最少地點 | 無法覆蓋 |
|---|---|---|---|---|
| 候選本身（網頁現在） | 距 Jisegumen (CN) 120 km（0.52）、距 Talnakh (RU) 260 km（0.50）、73.5°N 95.3°W（最近城鎮 Gjoa Haven (CA)，548 km）（0.46） | R1 1.00, R2 —, R3 0.98, R4 1.00, R5 1.00, R6 0.33 | 2：距 Talnakh (RU) 260 km、南極 82.2°S 163.2°E | R2, R6 |
| 全球分位數（建議） | Kosh-Agach (RU) 附近（0.59）、距 Jisegumen (CN) 120 km（0.58）、距 Hoit Taria (CN) 78 km（0.54） | R1 1.00, R2 —, R3 1.00, R4 1.00, R5 1.00, R6 0.80 | 2：距 Talnakh (RU) 260 km、距 Khapalu (PK) 118 km | R2 |

**mars-jezero**

| 百分位母體 | 前三名（總分） | 各任務最高分 | 最少地點 | 無法覆蓋 |
|---|---|---|---|---|
| 候選本身（網頁現在） | 距 Torghay (KZ) 167 km（0.47）、73.5°N 95.3°W（最近城鎮 Gjoa Haven (CA)，548 km）（0.46）、Haughton impact crater Devon Island (Canada)（0.46） | R1 1.00, R2 —, R3 —, R4 0.95, R5 —, R6 0.33 | 1：距 Torghay (KZ) 167 km | R2, R3, R5, R6 |
| 全球分位數（建議） | 73.5°N 95.3°W（最近城鎮 Gjoa Haven (CA)，548 km）（0.46）、Haughton impact crater Devon Island (Canada)（0.46）、74.7°N 84.8°W（最近城鎮 Gjoa Haven (CA)，772 km）（0.46） | R1 1.00, R2 —, R3 —, R4 0.95, R5 —, R6 0.84 | 2：73.5°N 95.3°W（最近城鎮 Gjoa Haven (CA)，548 km）、距 Khapalu (PK) 118 km | R2, R3, R5 |

**mars-gale**

| 百分位母體 | 前三名（總分） | 各任務最高分 | 最少地點 | 無法覆蓋 |
|---|---|---|---|---|
| 候選本身（網頁現在） | 距 Torghay (KZ) 167 km（0.47）、73.5°N 95.3°W（最近城鎮 Gjoa Haven (CA)，548 km）（0.46）、距 Xitieshan (CN) 40 km（0.46） | R1 1.00, R2 —, R3 —, R4 0.95, R5 —, R6 0.38 | 1：距 Torghay (KZ) 167 km | R2, R3, R5, R6 |
| 全球分位數（建議） | 73.5°N 95.3°W（最近城鎮 Gjoa Haven (CA)，548 km）（0.46）、Sidi el Hani (TN) 附近（0.46）、Haughton impact crater Devon Island (Canada)（0.46） | R1 1.00, R2 —, R3 —, R4 0.95, R5 —, R6 0.94 | 2：73.5°N 95.3°W（最近城鎮 Gjoa Haven (CA)，548 km）、距 Khapalu (PK) 118 km | R2, R3, R5 |

用全部 48 個候選時 `uses_placeholder` = true（月球 placeholder 候選造成）；邊際效益曲線要窮舉 C(48, 6) = 12,271,512 種組合，這裡沒有跑。


## 5. 怎麼重跑

```
python scripts\make_mission_tests.py --no-figures
python scripts\export_web_seed.py --web-seed ..\..\nasa-main\data\seed --check
```

候選清單（28 個；每個（目標 × 測試）取本隊分數前 2 名、彼此至少相隔 150 km，再補已知類比地，上限 28）。
候選是用目前的 outputs/mission_tests/candidate_pool.csv 挑的：本機重跑（水體遮罩、ndvi_p90、ASTER）之後要再跑一次這支程式：

| id | lat | lon | place | known | reasons |
|---|---|---|---|---|---|
| hf-e_1910756 | 36.95 | 95.65 | 40 km from Xitieshan (CN) |  | ap105 R1 第 1 名（本隊分數 1.00） |
| hf-e_1960304 | 35.55 | 10.45 | near Sidi el Hani (TN) |  | ap105 R1 第 2 名（本隊分數 1.00） |
| hf-e_6202632 | -82.25 | 163.25 | 494 km from McMurdo Station (AQ) |  | ap105 R3 第 1 名（本隊分數 1.00） |
| hf-e_5918234 | -74.35 | 163.45 | 398 km from McMurdo Station (AQ) |  | ap105 R3 第 2 名（本隊分數 1.00） |
| hf-e_751549 | 69.15 | 94.95 | 260 km from Talnakh (RU) |  | ap105 R4 第 1 名（本隊分數 0.99） |
| hf-e_2313400 | 25.75 | 40.05 | 147 km from Sultanah (SA) |  | ap105 R4 第 2 名（本隊分數 0.97） |
| hf-e_333927 | 80.75 | 92.75 | 1258 km from Talnakh (RU) |  | ap105 R5 第 1 名（本隊分數 1.00） |
| hf-e_627054 | 72.55 | -114.55 | 526 km from Kugluktuk (CA) |  | ap105 R5 第 2 名（本隊分數 1.00） |
| hf-e_1403104 | 51.05 | 90.45 | near Kyzyl-Mazhalyk (RU) |  | ap105 R6 第 1 名（本隊分數 0.79） |
| hf-e_1446286 | 49.85 | 88.65 | near Kosh-Agach (RU) |  | ap105 R6 第 2 名（本隊分數 0.78） |
| hf-e_1694683 | 42.95 | 88.35 | near Toksun (CN) |  | jezero R1 第 1 名（本隊分數 0.99） |
| hf-e_1673115 | 43.55 | 91.55 | 113 km from Mori (CN) |  | jezero R1 第 2 名（本隊分數 0.98） |
| hf-e_591246 | 73.55 | -95.35 | 548 km from Gjoa Haven (CA) |  | jezero R4 第 1 名（本隊分數 0.96） |
| hf-e_551752 | 74.65 | -84.75 | 772 km from Gjoa Haven (CA) |  | jezero R4 第 2 名（本隊分數 0.96） |
| hf-e_2222833 | 28.25 | -16.65 | near Vilaflor (ES) |  | jezero R6 第 1 名（本隊分數 0.77） |
| hf-e_1975632 | 35.15 | 103.25 | near Zuogaiduoma (CN) |  | jezero R6 第 2 名（本隊分數 0.76） |
| hf-e_3766641 | -14.65 | -75.85 | 39 km from Ocucaje (PE) |  | gale R1 第 1 名（本隊分數 0.98） |
| hf-e_2039944 | 33.35 | 54.45 | 75 km from Khur (IR) |  | gale R1 第 2 名（本隊分數 0.97） |
| hf-e_1979002 | 35.05 | 80.25 | 120 km from Jisegumen (CN) |  | gale R4 第 1 名（本隊分數 0.97） |
| hf-e_1507231 | 48.15 | 63.15 | 167 km from Torghay (KZ) |  | gale R4 第 2 名（本隊分數 0.97） |
| hf-e_1942970 | 36.05 | 77.05 | 118 km from Khapalu (PK) |  | gale R6 第 1 名（本隊分數 0.95） |
| hf-e_1871167 | 38.05 | 96.75 | 78 km from Hoit Taria (CN) |  | gale R6 第 2 名（本隊分數 0.95） |
| hf-e_6033417 | -77.55 | 161.75 | 121 km from McMurdo Station (AQ) | mcmurdo_dry_valleys | 已知類比地（對照用） |
| hf-e_526503 | 75.35 | -89.65 | 777 km from Gjoa Haven (CA) | haughton_crater | 已知類比地（對照用） |
| hf-e_4105100 | -24.05 | -69.95 | 63 km from Antofagasta (CL) | atacama_yungay | 已知類比地（對照用） |
| hf-e_1888496 | 37.55 | 29.65 | near Yesilova (TR) | lake_salda | 已知類比地（對照用） |
| hf-e_1854692 | 38.45 | -110.75 | 79 km from Ferron (US) | mdrs_hanksville | 已知類比地（對照用） |
| hf-e_898032 | 65.05 | -16.75 | 80 km from Laugar (IS) | askja_vikrahraun | 已知類比地（對照用） |
