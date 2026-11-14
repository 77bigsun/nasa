# 任務 B 工作紀錄（11/14 凌晨 04:10–）— 我做了什麼、怎麼重跑、哪裡和原規格不同

> 給 B 本人（Youle Lee）和組員看。權重怎麼解釋、會議裡的問題怎麼回答，請看 **`docs/WEIGHTS_EXPLAINED.md`**。
> 所有數字來自 `outputs/`，由程式產生；`outputs/summary_tables.md` 是自動整理的數字總表。

---

## 0. 一句話

在你的電腦（RTX 5050）上建好 `nasa_hackathon` 環境 → 從 Google Earth Engine 抓出**全球 144.2 萬個 0.1° 陸地格**的 10 個變數 →
做好相似度、總分、**每個任務的權重學習（非負邏輯迴歸 + 收縮混合）**、驗證（AUC、留一法、敏感度、算法比較）、
**Random Forest / XGBoost(GPU) 交叉檢查**、3 個火星目標 × 4 個任務的結果檔與熱度圖、簡報用圖。

TASK_B 的 B1–B8、B10 都有第一版；B9（先粗後細）、B11 的簡報本身、B12 沒做（見第 7 節）。

---

## 1. 環境建立（你要自己重建時照這個做）

```powershell
# 在 hatrefish\ 底下
$env:CONDA_SSL_VERIFY = "truststore"          # 你的電腦有 Norton HTTPS 掃描，conda 不加這個會 SSL 失敗
conda env create -f env\nasa_hackathon.yml
conda activate nasa_hackathon
pip install truststore reverse_geocoder fsspec aiohttp
pip install -e .                              # 之後就能 import mars_analog
python scripts\make_ca_bundle.py              # 匯出 Windows 憑證給 GDAL 用（選用）
```

- 套件：Python 3.11、GDAL/rasterio/geopandas/xarray、numpy/scipy/pandas、scikit-learn 1.9、**xgboost 3.4（CUDA 版，已確認在 RTX 5050 上能跑）**、shap 0.51、earthengine-api。清單在 `env/nasa_hackathon.yml`。
- **一定要 `conda activate nasa_hackathon` 再跑**。沒啟用、直接呼叫 `envs\nasa_hackathon\python.exe` 的話，MKL 的 DLL 找不到，`scipy.linalg` 會直接閃退（錯誤碼 0xc06d007f）。
- **SSL 問題（重要）**：你的 Norton 會攔截 HTTPS，Python、conda、GDAL 都會出現 `CERTIFICATE_VERIFY_FAILED`／`schannel: the certificate chain is incomplete`。
  解法：Python 用 `truststore`（程式裡已自動啟用）；conda 用 `CONDA_SSL_VERIFY=truststore`；GDAL 讀火星 DEM 改用 fsspec（`mars_provisional.py` 已處理）。
  我**沒有**改你的全域 conda 設定，也沒有關掉任何憑證檢查。
- Earth Engine：你電腦上已經有登入憑證，專案 `nasa-spaceapp-hackathon` 可以用。
- GPU 用在哪：只有 XGBoost 交叉檢查用到 GPU。主模型（邏輯迴歸）資料只有 2 萬列 × 10 個特徵，CPU 一秒內就跑完；**TASK_B 也規定不要用深度學習**（資料太少會過擬合），所以 GPU 不是必要的。

## 2. 一鍵重跑

```powershell
conda activate nasa_hackathon
cd hatrefish
python scripts\fetch_earth_gee.py          # 重新從 GEE 抓全球資料（約 20 分鐘；已抓好的在 data\interim\earth_0p1\）
python scripts\run_pipeline.py --stage all  # grid → learn → validate → crosscheck → export → figures（約 7 分鐘）
python scripts\summarize_results.py         # outputs\new_candidates.md、outputs\summary_tables.md
```

IanChen 的正式檔一交（`data/processed/mars_targets.json`、`data/labels/known_analogs.csv`、`data/mappings/*.csv`），
**程式會自動改用正式檔**，不用改程式，重跑 `--stage all` 就好。

## 3. 做了哪些檔案

```
hatrefish/
  env/nasa_hackathon.yml            環境
  pyproject.toml                    pip install -e .
  scripts/
    fetch_earth_gee.py              GEE → 全球 0.1° 陣列（平行下載、失敗自動切小塊重試）
    run_pipeline.py                 一鍵流程
    summarize_results.py            新候選地清單、數字總表
    make_ca_bundle.py               Windows 憑證 → PEM（給 GDAL）
  src/mars_analog/
    __init__.py                     score()：給後端呼叫（PROJECT_CONTEXT 7.2）
    config.py  paths.py             設定與路徑；IanChen 正式檔優先、沒有就用暫用檔
    adapters/registry.py            資料來源註冊表（B1）
    adapters/earth/_gee.py          GEE 下載工具
    adapters/earth/gee_layers.py    每個變數在 GEE 上的算法＋資料引用
    earth_grid.py                   B3：組成 earth_grid.parquet、地球百分位表
    similarity.py                   B4：單項相似度（方法 A / B / C）
    scoring.py                      B5：加權幾何平均、信心度（已通過 TASK_B 手算範例 69.8/75.0/43.0/78.2）
    training.py                     正負樣本準備（已知類比地 vs 隨機陸地＋高植被）
    learn_weights.py                B7：每個任務的權重學習
    validate.py                     B6：AUC、recall、留一法、敏感度、算法比較、IanChen 12 點檢查
    crosscheck.py                   會議提的 Random Forest ＋ XGBoost(GPU) ＋ SHAP 交叉檢查
    novelty.py                      B8：已知／新候選、相鄰高分格合併、地名
    export.py                       B10：7.1 格式結果檔、熱度圖
    plots.py                        B11：簡報用圖
    mars_provisional.py             【暫用】IanChen 交檔前的火星目標值（見第 5 節）
  data/provisional/                 【暫用】已知類比地 29 個、岩性對照表、火星目標（IanChen 交檔後自動不用）
  data/processed/earth_grid.parquet 全球網格（144.2 萬格 × 38 欄，不進 git）
  config/weights_learned.json       學到的權重（每個任務的 final）
  outputs/                          結果檔、報告、圖
```

## 4. 地球資料（全部在 GEE 上算、只下載每格結果）

| 變數 | 用的資料 | 和 TASK_B 的差別 |
|---|---|---|
| 陸地／冰雪遮罩 | MODIS MCD12Q1 2022 + **MOD44W 水體（250 m）**（NASA） | 原訂 WorldCover。改用 NASA 的 500 m 土地覆蓋算比例，運算量小很多。另外**保留「裸地 ≥ 25%」的格子**，不然南極乾谷幾乎全被當成冰蓋排除（PROJECT_CONTEXT 3.3 要求保留）。MCD12Q1 會把大奴湖、格陵蘭峽灣海冰當成陸地（坡度 0、NDVI≈0 → 變成「完美平坦荒地」排到第 1 名），所以再用 MOD44W 排除水體 > 50% 的格子、並排除 DEM 上「海拔 ≈ 0 且完全平坦」的格子 |
| 坡度、粗糙度、海拔 | **GMTED2010 7.5″（約 230 m）**；南極用 Copernicus GLO-30 在 EPSG:3031 粗化到 200 m | 原訂全球都用 Copernicus GLO-30 粗化到 200 m。GMTED 原生就是 ~200 m 尺度，運算量少約 40 倍，才能在今天早上跑完全球；GMTED 不含南極，所以南極另外用 Copernicus。之後要全換 Copernicus：`gee_layers.copernicus_glo30_200m()` 已寫好 |
| 地表溫度、日溫差 | MODIS MOD11A2 + MYD11A2，2015–2024 | 同規格 |
| 熱慣量 ATI | (1 − MCD43A3 反照率) / 日夜溫差 | 用多年平均算 ATI（不是每期算再取中位數），比較穩。日夜差 < 5 K 設沒資料。**只在乾燥地區（乾燥指數 < 0.65）計算**：第一版發現已知類比地的熱慣量相似度反而低於隨機陸地（ATI 被土壤水分主導），依 B2「潮濕地區不準」限制範圍 |
| NDVI | MODIS MOD13A2，2015–2024 | 同規格。南極沒有 NDVI → 沒資料 |
| 乾燥指數 | Global Aridity Index v3（Zomer 2022） | **南緯 60° 以南設沒資料**：南極 PET 接近 0，McMurdo 乾谷算出 0.30（「半乾燥」），不可信 |
| 沙塵 | MERRA-2 DUEXTTAU，2019–2023 每日 12 UTC | 同規格（取樣成每天一筆以加快） |
| 岩性 | GLiM 0.5°（PANGAEA） | 同規格（先用 0.5° 版） |
| 永凍土 | ESA CCI Permafrost **v5.0，2023**（北半球 + 南極） | 同規格。**注意**：CCI 檔案在「沒有永凍土」的地方是空值不是 0，範圍內空值要當 0（一開始沒處理，25–60°N 有 71% 被誤判成沒資料，已修正） |

抽查（Atacama Yungay）：年均地表溫度 26.6 °C、日夜溫差 34 K、NDVI 0.08、乾燥指數 0.0008（極乾）——和 IanChen 之前量的 27.0 °C / 34.9 / 0.096 一致。

## 5. 暫用檔（IanChen 交檔後會被取代）

**火星目標**（`data/provisional/mars_targets_provisional.json`）：

| | Jezero (18.38, 77.58, r 25 km) | Gale (−5.4, 137.8, r 25 km) | Arcadia (47.2, −175.7, r 50 km) | 來源 |
|---|---|---|---|---|
| 坡度 | 2.41° | 5.48° | 0.25° | **從資料算**：HRSC-MOLA 200 m DEM 遠端讀 |
| 粗糙度 | 11.1 m | 27.3 m | 0.89 m | 同上，5×5 像素視窗 |
| 熱慣量 | 294（火星第 87 百分位） | 269（第 80） | 231（第 63） | **從資料算**：TES 2007 夜間圖（面積加權百分位） |
| 岩性 | HNt → clastic | Htu → clastic | Av → basalt | **從資料算**：SIM3292（大類對照是我暫定的） |
| 冰 SWIM Ci | −0.19 | 0.06 | 0.51 | TASK_A A2 參考值 |
| 年均溫 | −49.5 °C | −50.9 °C | −75.9 °C | TASK_A A2 參考值 |
| 沙塵（百分位） | 0.55（0.87） | 0.46（0.73） | 0.35（0.42） | TASK_A A2 參考值 |

- Arcadia 用 A2 參考值所在的 47.2, −175.7（不是 IanChen 的 39.2, 172.0）；**A1 座標還沒定案**，定了重跑即可。
- Gale 的 TES 熱慣量我算出 269，A2 表上是 433：A2 可能用了不同座標或 THEMIS。請 IanChen 確認。
- 1:20M 地質圖解析度太粗，Jezero 落在「HNt 過渡單元」，看不到三角洲的碳酸鹽／黏土。岩性大類請 IanChen 在 A5 決定。

**已知類比地**（`data/provisional/known_analogs_seed.csv`，29 個）：IanChen 的 6 個 + TASK_A A6 建議的 + 我補的
（Lake Salda、El Tatio、Qaidam、Axel Heiberg、Tuktoyaktuk、Death Valley LVS、Mojave Xombie、White Sands、BASALT 計畫兩處、AMADEE-18/20 等）。
**全部標 `verified=false`**：參考連結有些是我記得的論文 DOI，有些我不確定，就改成 Google Scholar 搜尋連結。**請 IanChen 逐筆確認**。
任務分布：geology 26、rover 13、isru_base 11、landing 3（with 對應的火星目標後：geology 24、rover 13、isru_base 8、landing 3）。

**岩性對照表**（`data/provisional/lithology_mars_to_glim_provisional.csv`）：每格附理由，等 IanChen 的 A5 取代。

## 6. 和規格不同、需要你知道的決定

1. **最後權重用「收縮混合」而不是「逐項相乘」**：
   `w_final = (1−α)·先驗 + α·學到的`，α = n/(n+20)，n = 該任務的已知類比地數。
   原規格的逐項相乘在 geology 會把岩性從 0.35 乘到 0.04、讓荒蕪度（植被）變成 0.68（因為 0.5° 岩性圖看不出小型類比地，學到 0）。
   兩種都有算，數字都在 `outputs/weights_learning_report.json`；細節見 WEIGHTS_EXPLAINED.md。
2. **任務專屬 vs 全域**：每個任務比較「只用自己的類比地學」和「29 個合併學」（都和先驗混合），留一法 AUC 高的勝。結果 geology、rover、isru_base 都是任務專屬勝出。
   原本照 TASK_B「少於 20 個不學、改用全域」時，探測車會從極地類比地借到 0.18 的冰權重（沒有物理意義）；收縮混合的 α 已經處理了「資料少就少相信」，所以不需要硬門檻。
3. **landing 保留先驗**：只有 3 個類比地，混合後留一法 AUC（0.683）沒有比先驗（0.686）好，依 TASK_B 規則保留先驗。
4. **乾燥指數在南極設沒資料**、**永凍土空值當 0**、**遮罩保留裸地 ≥ 25%**（第 4 節）。
5. 前 20 名用「彼此至少相距 150 km」挑選（50 km 時前 20 名全擠在西藏西部），每筆仍附 cell_id；「已知類比地」仍照規格用 50 km 判斷。
6. 新候選地的地名用離線反向地理編碼，最近城鎮超過 30 km 時寫「X km from 某地」（北極群島的最近城鎮可能在 1,000 km 外）。
7. 修正前（沒有水體遮罩、ATI 沒限制乾燥區、探測車借全域權重）的報告留在 `outputs/archive_v0_before_water_ti_fix/`，可以對照修正的效果。

## 6.5 主要結果（細節見 WEIGHTS_EXPLAINED.md）

| 任務 | 已知類比地 | 留一法 AUC 先驗 → 最後 | 最重的三個權重（最後） |
|---|---|---|---|
| geology | 24 | 0.68 → 0.70 | 荒蕪度 0.29、溫度 0.18、岩性 0.16 |
| rover | 13 | 0.66 → 0.82 | 荒蕪度 0.32、坡度 0.17、粗糙度 0.15 |
| isru_base | 8 | 0.61 → 0.81 | 永凍土 0.34、溫度 0.19、荒蕪度 0.18 |
| landing | 3 | 0.69（保留先驗） | 坡度 0.30、粗糙度 0.30、熱慣量／沙塵 0.15 |

- Random Forest／XGBoost（GPU）交叉檢查：三個模型都同意荒蕪度、溫度最重要；樹模型留一法 AUC 高 0.06–0.10，但給不出可放進公式的權重（第 4 節）。
- 每個權重 ±20%，前 10 名平均重疊 0.92–1.00。
- 新候選地前幾名：Jezero／Gale → 藏北羌塘、崑崙南側高原；Arcadia 取冰 → 加拿大北極群島西北部（伊莉莎白女王群島，Haughton 的西北方）、Ungava 半島；Arcadia 著陸 → 墨西哥 Baja（Vizcaíno 沙漠）、秘魯 Sechura 沙漠、阿根廷 La Pampa 西部等平坦荒地。**都還沒人工確認。**

## 7. 還沒做／下一步

- [ ] **IanChen 交檔後重跑**：`python scripts\run_pipeline.py --stage all`（約 7 分鐘）。數字會變，WEIGHTS_EXPLAINED.md 裡的表要更新（`outputs/summary_tables.md` 會自動重產）。
- [ ] **B8 人工確認**：`outputs/new_candidates.md` 每個目標前 3 名新候選地，點 Worldview 連結看衛星影像，填 ✅／❌。
- [ ] B9 先粗後細（Jezero 20 m、Gale 30 m 重排前 50 名）：還沒做。
- [ ] 全球坡度換回 Copernicus GLO-30（目前 GMTED 230 m）：程式已寫好，GEE 運算約 1–2 小時，可以晚上丟著跑。
- [ ] 火星日溫差（MCD）還沒有，`diurnal_range` 的 Mars 值是空的（計分只需要地球端，不影響分數；只影響 breaks 顯示）。
- [ ] `score()` 任意座標：要等 IanChen 的 `extract_mars_features`；現在只能查三個預設目標附近。
- [ ] 程式碼**還沒 commit / push**（會議提到大會對提前公開程式碼有規定，請你確認後再推）。`data/processed/`、`*.parquet`、`*.npy` 都很大，不要進 git（`.gitignore` 已擋 parquet；`data/interim/` 我建議也加進去）。

---

## 8. 11/14 上午（Claude 對話，接續凌晨的工作）

### 8.1 整合 IanChen 的正式檔
- 接進 `data/processed/mars_targets.json`、`mars_reference_pct.json`、`data/labels/known_analogs.csv`（28 個）、`data/mappings/*.csv`。程式自動改用正式檔，`data/provisional/` 不再使用。
- IanChen 的 JSON 把變數包在 `features` 底下 → 改 `config._normalize_targets` 攤平。
- 第 5 節的 Gale 熱慣量疑問：A2 表上的 433 是錯的參考值；IanChen 量到 283，和我的 269 接近。
- 用正式資料重跑 `outputs/`（約 11:17）。

### 8.2 方法討論（沒有改程式）
- 說明凌晨的模型怎麼訓練（第 6 節）；提醒報告要用留一法 AUC，不要用訓練資料自己算的 AUC。
- 討論「全球格當訓練集、已知類比地當驗證／測試集」的構想：缺少可靠的負例，已知類比地也太少，不能同時拿來訓練和測試。
- 對照題目 PDF：題目沒有要求一定要依任務分類。
- 任務權重的文件依據寫成 `docs/MISSION_WEIGHTS_BASIS.md`（**只是提案，沒有套用**）。GEE 上的生物相關資料：土壤有機碳、土壤鹽度有；地表紫外線沒有。

### 8.3 決定：先做類比剖面，不管任務權重與生物面向
- 排名 = 七個面向等權重的整體相似度 ＋ 每個面向各自的前 5 名（PROJECT_CONTEXT 3.4）。
- 新增 `config/dimensions.yaml`、`src/mars_analog/profiles.py`、`scripts/make_profiles.py`，輸出在 `outputs/profiles/`（約 11:34 首次產出）。

### 8.4 方法修正
1. **冰的目標值改成 clip(SWIM Ci, 0, 1)**：舊版 (Ci+1)/2 會讓 Jezero（Ci −0.21）去找有 40% 永凍土的地方。改了 `similarity.py`（`ice_target`）與 `export.py`。
2. **日溫差移出環境面向**：火星日溫差主要來自稀薄大氣，地球做不到，會讓極區地點被扣分；只留在 breaks 當參考。
3. **各面向前 5 名只用該面向變數齊全的格子**，排名池也要求變數覆蓋率 ≥ 80%：之前各面向前幾名被缺熱慣量的北極、凱爾蓋朗格子佔滿。
4. 雷達圖只畫可評估的面向（沒資料的面向不畫成 0 分），修好標籤重疊。

### 8.5 新火星目標與放大程式（細節見 `docs/NEW_TARGETS_AND_ZOOM.md`）
- 用 IanChen 的擷取程式重抽 Jezero，數值完全一致；新增 **Oxia Planum、Meridiani Planum、Protonilus Mensae**，座標都有出處。Oxia（黏土）、Meridiani（硫酸鹽）的岩性類別依文獻覆寫。
- 六個目標的剖面都重跑了。沒有標給某目標的已知類比地時，改列全球排名最前的 8 個。
- 修正剖面 JSON 的 `cell_id`：之前寫成表格列號，座標和分數本來就是對的。
- `profiles.py` 把計分抽成 `score_table()`，全球格和放大子格共用同一套算法。
- **放大程式**：`scripts/zoom_candidates.py`、`src/mars_analog/zoom.py`、`src/mars_analog/adapters/earth/gee_zoom.py`。把前幾名候選從 0.1° 格放大到約 1 km 子格重新計分，用合成資料測過；GEE 部分還沒在本機跑。

### 8.6 發現、尚未決定
- **缺岩性的格子在排名上佔便宜**：GLiM 沒資料的陸地只佔 0.15%，但佔 Meridiani 整體前 20 名的 11 個、Oxia 的 9 個、Jezero 的 5 個。可選 (a) 排名要求岩性有資料、(b) 缺的用該目標的全球中位分數補、(c) 維持現狀並標出。**目前結果是未修正版。**
- Protonilus 的 SWIM Ci 在 50 km 圓內中位數只有 0.16，永凍土地區沒有因此被往前推；要不要改用圓內高百分位，還沒決定。

## 9. 第 7 節待辦的最新狀態（11/14 中午）

- [x] IanChen 交檔：已整合（8.1）。
- [ ] **重跑任務版流程**：冰的算法在 8.4 改了，`python scripts\run_pipeline.py --stage all` 要再跑一次，`outputs/` 的任務結果才會一致。
- [ ] 放大程式：先跑 `python scripts\zoom_candidates.py --test`，正常再跑全部。
- [ ] 決定缺岩性的處理方式（8.6）。
- [ ] B8 人工確認新候選地（Worldview）：還沒做。放大結果的總表也有 Worldview 與衛星圖連結，可以一起看。
- [ ] B9 先粗後細（火星端 Jezero 20 m、Gale 30 m 重排）：還沒做。放大程式細化的是地球端，不是這一項。
- [x] 火星日溫差：IanChen 的正式檔已有。
- [ ] `score()` 任意座標：IanChen 的擷取程式可以用了（8.5 就是用它），還沒確認 `score()` 有沒有接上。
- [ ] commit／push：今天的改動都還沒 commit（大會公開程式碼的規定確認後再推）。`data/interim/` 有放大的方框快取和備份檔，不要進 git。
