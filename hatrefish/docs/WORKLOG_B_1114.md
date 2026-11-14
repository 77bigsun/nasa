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

---

## 10. 測試項目分數 R1–R6、AP-105、補資料程式（Claude 雲端，11/14 下午）

依整合者 Harris 的規劃（`nasa\docs\總覽.pdf`、`火星.pdf`），把「每個地點在每項測試的分數與排名」做出來。原本寫給 Claude Code 的 `docs\PROMPT_mission_tests.md` 由雲端直接做完；本機還要跑的 GEE 部分見 `docs\PROMPT_local_gee_runs.md`。

### 10.1 新增
- **目標 AP-105**（SkyFall 設計參考著陸點）：43.3295°N、198.5228°E（lon −161.4772）、半徑 50 km。座標取自 `火星.pdf`，SkyFall 原始文件待補。用 IanChen 的擷取程式抽值：坡度 0.21°、熱慣量 181（火星第 39 百分位）、Av → 玄武岩、冰 Ci 0.583、溫度 −72.7 °C、沙塵 0.41。現在共 7 個目標。目標檔備份在 `data\interim\mars_targets.before_1114_ap105.json`。
- **火星季節曲線**：7 個目標都用 MCD 查了 Ls 每 15° 的沙塵光學厚度與地表溫度，存在 `mars_targets.json` 每個目標的 `seasonal`。沙塵高峰都在 Ls 225–255°。
- **測試計分**：`config\mission_tests.yaml`、`src\mars_analog\mission_tests.py`、`scripts\make_mission_tests.py`，輸出在 `outputs\mission_tests\`：
  - `TEST_SUMMARY.md`、每個目標的 json 與地圖
  - 需求矩陣 `requirement_matrix.csv/.md`（Harris 的欄位格式）
  - 面向 × 測試交叉表
  - 候選池 `candidate_pool.csv`（3,238 格，給下一步的集合覆蓋）
- **補資料程式**（要在本機跑 GEE）：`scripts\fetch_earth_extra_gee.py`＋`adapters\earth\gee_extra.py`，抓每月沙塵、每月地表溫度、GLIMS 冰河比例（本機算冰河距離）、ASTER GED 礦物指標。抓完重跑 `make_mission_tests.py` 就會自動納入。
- **放大程式加地點細節**：每個最佳 1 km 小區算 1 km 方塊內的高解析坡度（北緯 60° 以北 ArcticDEM 2 m、南緯 60° 以南 REMA 8 m、其他 Copernicus 30 m）和雷達後向散射（Sentinel-1、PALSAR-2）。只列出、不計分。

### 10.2 和 PROMPT 規格不同的地方
1. **可選特徵全部改成必要特徵**：第一版 R3 的「乾燥」是可選，前 20 名有 11 筆是缺乾燥指數的北極格子（缺資料反而佔便宜）。改成必要特徵，並只在南緯 60° 以南補值（南極沒有乾燥指數與 NDVI 是資料設計，當極地沙漠補 1）。
2. **R1、R4 加「無冰覆蓋」必要特徵**：第一版 Jezero 的 R4 前幾名有阿拉斯加冰河。冰雪比例取三者最大：MCD12Q1 冰雪、GLIMS 冰河（補資料後）、「年均 NDVI < 0 且年均溫 < 0 °C」。最後一項是為了抓土地覆蓋圖漏標的冰河。
3. **R3、R5 適用門檻改為 SWIM Ci ≥ 0.1**：原本 Ci > 0 會讓 Gale（0.06）、Meridiani（0.03）也被算進來。
4. **R3 改測「有沒有冰可偵測」**：用永凍土比例和年均溫的門檻，不再比 Ci 機率。所以 R3 結果不隨目標改變。
5. 地圖改成畫到南緯 90°，因為 R3 前幾名在南極。

### 10.3 結果重點（各測試第 1 名；R2 全部無法評估）

| 目標 | R1 著陸 | R3 地下冰 | R4 礦物（代理） | R5 冰緣 | R6 沙塵氣象 |
|---|---|---|---|---|---|
| jezero | 64 km from Jisegumen (CN)（1.0） | 不適用 | 167 km from Torghay (KZ)（0.965） | 不適用 | 68 km from Yeyik (CN)（0.944） |
| gale | 79 km from A'yi Take (CN)（0.989） | 不適用 | 167 km from Torghay (KZ)（0.965） | 不適用 | 193 km from Zangguy (CN)（0.955） |
| arcadia | 70 km from Colchani (BO)（1.0） | 67 km from McMurdo Station (AQ)（1.0） | 328 km from Iqaluit (CA)（1.0） | 1205 km from Kugluktuk (CA)（1.0） | 61 km from Xagmakajor (CN)（0.939） |
| oxia | near Mynaral (KZ)（1.0） | 不適用 | 170 km from Turkmenbasy (TM)（0.928） | 不適用 | 49 km from Aqqan (CN)（0.927） |
| meridiani | near Xagmakajor (CN)（0.999） | 不適用 | 66 km from Colchani (BO)（1.0） | 不適用 | 139 km from Nur (CN)（0.955） |
| protonilus | 102 km from Cuozheqiangma (CN)（0.993） | 522 km from McMurdo Station (AQ)（1.0） | 847 km from Gjoa Haven (CA)（0.965） | 1389 km from Clyde River (CA)（1.0） | 132 km from Zhadong (CN)（0.934） |
| ap105 | 142 km from Jisegumen (CN)（1.0） | 67 km from McMurdo Station (AQ)（1.0） | 328 km from Iqaluit (CA)（1.0） | 1205 km from Kugluktuk (CA)（1.0） | 142 km from Leh (IN)（0.952） |

- Meridiani 的 R4 前幾名是烏尤尼、馬卡迪卡迪等鹽沼，第 6 名在已知類比地 Kachchh 附近：硫酸鹽覆寫有作用。
- **門檻型測試（R1、R3、R5）很多地點同時拿滿分**（例如 AP-105 的 R1 前 20 名全是 1.0），先後順序靠類比剖面的整體相似度決定。下一步的集合覆蓋本來就只看「有沒有達到門檻 τ」，所以影響不大。
- **交叉驗證**：用面向分數組成的測試分數 vs 逐特徵算的，全部格子的等級相關：R4 約 0.9、R6 約 0.8、R3 約 0.7、R5 約 0.6、R1 約 0.5。R1 低是預期的：一個用門檻，一個跟目標比。
- **已知類比地檢查**：標了 landing／rover 的已知類比地，在 R1 的全球排名反而比沒標的後面（AP-105：中位數前 79%，沒標的前 53%）。已知的漫遊車場址大多是為了地質多樣性挑的（熔岩流、火山區），不是平坦著陸面。簡報可以拿來說明「測試導向」和「傳統類比場址」的差別。
- 單元檢查：滿意度函數邊界值正確；手算兩格（Meridiani R4、AP-105 R1）和程式一致。
- 類比剖面（原本 6 個目標）重跑後和之前逐字相同；AP-105 新增剖面，前幾名在蒙古西部、阿爾泰。

### 10.4 待辦
- [ ] 本機跑 `docs\PROMPT_local_gee_runs.md`：補資料 → 重跑測試計分 → 放大 `--test`、全部 → `run_pipeline.py --stage all`。
- [ ] 下一步：集合覆蓋＋邊際效益曲線（用 `candidate_pool.csv`）。
- [ ] R2 視覺導航（Sentinel-2 紋理對 CTX 紋理）；Deuteronilus、Phlegra 等其他 SkyFall 區的具體座標（向 Harris 要 SkyFall 資料包）。
- [ ] 跟 Harris 對齊分工：我們的全球網格和計分程式可以給月球組用。

---

## 11. 本機 GEE 執行（Claude Code，11/14）

依 `docs\PROMPT_local_gee_runs.md`，在本機（`conda activate nasa_hackathon`）跑完 6 步，約 15:15–16:05。
- 只修了 PROMPT 允許的小錯（GEE 記憶體上限、影像篩選、沒資料時的退路、圖的版面），另外 `export.py` 修了一行當機（不在 PROMPT 列的程式裡，見 11.1 第 6 步）。
- 設計和門檻都沒改，要改的寫在 11.5「建議」。
- 沒有動 `IanChen\`、沒有 commit／push、沒有動 GEE 登入設定、沒有刪除任何檔案。
- 備份：
  - 補資料前的測試結果：`data\interim\mission_tests.before_extra_1114\`（11.2 的對照就是用它）
  - 本節寫入前的工作紀錄：`data\interim\WORKLOG_B_1114.before_sec11.md`

### 11.1 每一步：時間、錯誤、修法

| 步驟 | 執行時間 | 結果 |
|---|---|---|
| 1. `fetch_earth_extra_gee.py --test` | 27 秒（修好後；除錯約 10 分鐘） | 第一次在每月沙塵就失敗 → 修好後四層都通過 |
| 2. `fetch_earth_extra_gee.py`（全球） | **7.5 分鐘**（沙塵 94 秒、地表溫 92 秒、冰河 210 秒、ASTER 37 秒） | 沒有失敗的塊，不需要 `--only … --refresh` |
| 3. `make_mission_tests.py` | 2 分鐘 | 「待補資料」消失；結果見 11.2 |
| 4. `zoom_candidates.py --test` | 37 秒（修好後；第一次 52 秒） | 第一次底圖失敗、雷達空白 → 修好後正常 |
| 5. `zoom_candidates.py --top 3` | 3 分鐘（下載 136 秒）；改底圖後 `--refresh` 重跑一次，也是 3 分鐘 | 21 個候選全部完成；結果見 11.3 |
| 6. `run_pipeline.py --stage all` | 約 8 分鐘（grid 15、learn 116、validate 155、crosscheck 133、export 53、figures 2 秒） | export 第一次當掉 → 修好後補跑 export、figures；結果見 11.4 |

執行順序：
- 第 4 步的 `--test` 是和第 2 步的全球下載同時跑的：放大程式不用補資料，只抓一個方框。
- 第 6 步會重寫 `earth_grid.parquet`，所以等第 5 步結束才跑。重寫後的檔案和之前**逐位元組相同**（md5 一樣），所以第 3–5 步的結果不受影響。

**第 1 步**
- **錯誤**：每月沙塵 `dust_m` 在 GEE 回「User memory limit exceeded」，10×10 格、只算一個月也一樣；同一批影像算全球年平均（凌晨的 `dust_aod`）卻可以。問題出在 `filterDate` + `calendarRange(hour)` + `calendarRange(month)` 這種篩法。
- **修法**（`gee_extra.dust_monthly`）：直接列出每天 12 UTC 的影像編號（`NASA/GSFC/MERRA/aer/2/YYYYMMDD12`，5 年 1,826 張）再平均。12 個月一次約 8 秒，數值和原寫法在單月測到的一樣（Atacama 1 月 0.0109）。
- GLIMS 資產 `GLIMS/current` 存在，ASTER GED 波段名稱是 `emissivity_band10…14`，**都不用改**。
- 檢查值（都在 PROMPT 給的範圍內）：
  - 沙塵 0.008–0.011（Atacama 各月）
  - 地表溫 Atacama 1 月 30.7 °C、6 月 20.3 °C
  - 冰河比例 Juneau 冰原 0.28
  - ASTER QI／CI／MI 為 0.99／0.995／0.94

**第 2 步**（`earth_monthly.parquet` 1,441,608 × 25、`earth_extra.parquet` 1,441,608 × 6；程式只印前兩欄的缺值，我另外檢查了全部欄位）
- 缺值：沙塵、地表溫 12 個月都是 0%；冰河 0%；**ASTER 3.0%**。
  - 南極 100% 沒有：ASTER GED 不涵蓋南極。
  - **紐西蘭整塊沒有**：查過 GEE 原始像素本來就是空的，不是下載失敗。
  - 北緯 60° 以北 7.6%。
- 一致性：
  - 每月地表溫的 12 個月平均 vs 凌晨的年均溫：相關 0.9999，中位差 −0.01 °C。
  - 每月沙塵平均 vs 年均沙塵：比值中位數 1.000。
- 範圍：
  - 沙塵 0.001–0.88（p99 約 0.5）。
  - 冰河比例：Juneau 0.58、Vatnajökull 0.46、Baltoro 0.53，Atacama、撒哈拉 0；≥ 0.05 的格子 14,292 個。
  - ASTER CI／MI 的 p1–p99 在 0.78–1.10，但有 **692 格（0.05%）超出合理範圍**（CI 最大 43.8），幾乎都在多雲熱帶（新幾內亞、亞馬遜，NDVI 0.6–0.8）。荒蕪度把它們擋掉了，沒有進任何 R4 前 20 名（已逐格確認）。

**第 4 步**：三個問題，前兩個修了
1. **HLS 底圖失敗**（記憶體不足），而且失敗後沒有改畫陰影圖，底圖變成空白。
   - 原因：`filterBounds` 抓進大量 UTM 1／60 區（換日線附近）的 HLS 影像。它們的 footprint 跨換日線、被當成全球，一個蒙古的方框選到 1,756 張，前幾張在框內的像素數是 0。
   - 修法（`gee_zoom.hls_collection`、`zoom.fetch_box`）：
     - 用影像編號 `T<區號>…` 限定方框所在的 UTM 區（前後各多一區）；
     - 取雲量最低的 80 張；
     - HLS 失敗或合成結果全空時，改畫 Copernicus 陰影圖。
   - 修好後約 8 秒，方框 100% 有值。
   - 第 5 步看圖時又發現：只挑雲量最低會挑到冬天雪景（雪不算雲），楚科奇、蒙古的方框整片白。所以再改成南北回歸線以外優先取當地夏季（北半球 6–9 月、南半球 12–3 月，夏季沒有影像才用全年），並縮短底圖來源字串（原本被截在 80 字）。
2. **Sentinel-1 雷達是空值**：這個蒙古西部的點在 2022–2024 沒有任何 IW 影像（Sentinel-1B 2021 年底故障後覆蓋變少），2015–2021 有 150 張。
   - 修法（`gee_zoom.site_details`）：2022–2024 沒有影像時改用 2017–2021，並在結果記下 `s1_period`、`s1_scenes`。
3. `COPERNICUS/DEM/GLO30` 被 GEE 標為過時（只是警告，仍可用），**沒改**，見 11.5。

`--test` 的數值對照：
- 原本印的是整個方框的中位數。我在 `--test` 加印了「同一 0.1° 格內子格的中位數」，才能和 0.1° 格直接比。
- 一致的：坡度 1.68 vs 1.72°、粗糙度 8.4 vs 7.8 m、乾燥指數 0.075 vs 0.075。
- **不一致的**：年均地表溫 4.8 vs 2.3 °C、日溫差 21.8 vs 8.6 K、NDVI 0.076 vs 0.033。追查後是全球 0.1° 格混到旁邊的湖，不是放大程式的問題，見 11.5 第 4 點。
- 地點細節有坡度（p50 2.2°、p90 6.3°）和雷達數值。

**第 5 步**
- 7 個目標 × 前 3 名 = 21 個候選、20 個方框。
- 全部有 HLS 底圖；63 個最佳小區的地點細節全部成功，`ZOOM_SUMMARY.md` 沒有「—」。
- 看了 `zoom_jezero_1`、`zoom_arcadia_2`、`zoom_gale_3`：三格都正常，文字沒有重疊。
- 改底圖後用 `--refresh` 重跑，和第一次比：子格分數、最佳小區、地點細節**完全相同**，只有底圖變了。

**第 6 步**
- export 在 `jezero/isru_base` 當掉：`round(float(elev_m))` 遇到 NaN。
  - 原因：南極極點附近（南緯 84.8–86.4°）有 7 格沒有地形資料，其中一格進了前 20 名。上午改冰的目標值後排名變了，凌晨的版本沒遇到。
  - 這是 PROMPT 沒列的程式，但不修第 6 步就跑不完，所以只在 `export.py` 的 `earth_values` 加了 NaN → null（坡度、粗糙度、溫度、日溫差、海拔），然後補跑 `--stage export`、`--stage figures`。
- 前面四個階段沒有重跑（已經成功寫出）。
- 另外照第 2 節的一鍵流程跑了 `summarize_results.py`，讓 `outputs/summary_tables.md`、`new_candidates.md` 和新結果一致。

**這次改的程式**（都可以用 `git diff` 看）：
- `src/mars_analog/adapters/earth/gee_extra.py`：`dust_monthly` 改成列影像編號。
- `src/mars_analog/adapters/earth/gee_zoom.py`：
  - `utm_zones`、`hls_collection`（UTM 區篩選、最多 80 張、夏季優先）、`rgb`
  - `site_details`：Sentinel-1 退回 2017–2021
- `src/mars_analog/zoom.py`：`fetch_box` 的底圖退路（HLS 失敗或全空 → 陰影圖）、底圖來源字串。
- `scripts/zoom_candidates.py`：`--test` 多印同一 0.1° 格內的子格中位數。
- `src/mars_analog/export.py`：`earth_values` 的 NaN 防護（PROMPT 沒列的程式，見上）。

### 11.2 補資料前後，各測試第 1 名（`make_mission_tests.py`）

`TEST_SUMMARY.md` 開頭的「待補資料」已經消失；R4 礦物指標、R5 冰河距離、R6 三個季節特徵全部有分數，需求矩陣也有這些列。
粗體 = 第 1 名換了；括號是測試分數。R2 全部無法評估，表中省略。

| 目標 | R1 著陸 | R3 地下冰 | R4 礦物 | R5 冰緣 | R6 沙塵氣象 |
|---|---|---|---|---|---|
| jezero | 不變：64 km from Jisegumen (CN)（1.0） | 不適用 | 167 km from Torghay (KZ)（0.965）→ **145 km from Haines Junction (CA)**（0.973） | 不適用 | 68 km from Yeyik (CN)（0.944）→ **near Zuogaiduoma (CN)**（0.738） |
| gale | 不變：79 km from A'yi Take (CN)（0.989） | 不適用 | 不變：167 km from Torghay (KZ)（0.965） | 不適用 | 193 km from Zangguy (CN)（0.955）→ **80 km from Hoit Taria (CN)**（0.947） |
| arcadia | 不變：70 km from Colchani (BO)（1.0） | 不變：67 km from McMurdo Station (AQ)（1.0） | 328 km from Iqaluit (CA)（1.0）→ **272 km from Talnakh (RU)**（0.995） | 不變：1205 km from Kugluktuk (CA)（1.0） | 61 km from Xagmakajor (CN)（0.939）→ **near Patambuco (PE)**（0.775） |
| oxia | 不變：near Mynaral (KZ)（1.0） | 不適用 | 不變：170 km from Turkmenbasy (TM)（0.928） | 不適用 | 49 km from Aqqan (CN)（0.927）→ **66 km from Toksun (CN)**（0.742） |
| meridiani | 不變：near Xagmakajor (CN)（0.999） | 不適用 | 不變：66 km from Colchani (BO)（1.0） | 不適用 | 139 km from Nur (CN)（0.955）→ **86 km from Yeyik (CN)**（0.943） |
| protonilus | 不變：102 km from Cuozheqiangma (CN)（0.993） | 不變：522 km from McMurdo Station (AQ)（1.0） | 不變：847 km from Gjoa Haven (CA)（0.965） | 1389 km from Clyde River (CA)（1.0）→ **881 km from Kugluktuk (CA)**（1.0） | 132 km from Zhadong (CN)（0.934）→ **near Quero (EC)**（0.802） |
| ap105 | 不變：142 km from Jisegumen (CN)（1.0） | 不變：67 km from McMurdo Station (AQ)（1.0） | 328 km from Iqaluit (CA)（1.0）→ **272 km from Talnakh (RU)**（0.995） | 不變：1205 km from Kugluktuk (CA)（1.0） | 142 km from Leh (IN)（0.952）→ **near Zuogaiduoma (CN)**（0.769） |

PROMPT 第 3 步的檢查：
- **R6**：季節形狀分數沒有擠在同一個值。
  - 前 20 名的沙塵形狀分數範圍：Jezero 0.21–0.74、Oxia 0.24–0.41、AP-105 0.25–0.43、Gale 0.91–0.98、Meridiani 0.90–0.98。
  - 溫度形狀分數範圍 0.59–1.0，每個目標有 7–19 個不同值。
  - **7 個目標的 R6 第 1 名全部換了**，分數也普遍下降（Jezero 0.944 → 0.738、Arcadia 0.939 → 0.775）。Jezero 的 R6 現在沒有任何陸地 ≥ 0.8：火星沙塵季節曲線（Ls 225–255° 高峰）在地球很難找到同形狀的地方。
  - Jezero R6 第 3 名是 Tenerife 的 Vilaflor（Teide 火山），文獻常見的火星類比地。
  - 但 Arcadia、Protonilus 的第 1 名是赤道高山，有問題，見 11.5 第 3 點。
- **R5**：Protonilus 的 `glacier_distance` 有分數，前 10 名離最近冰河 0–11 km（≤ 20 km 滿分），前幾名都在冰河附近。第 1 名換成 Kugluktuk 北方的格子。Arcadia、AP-105 沒有標 `glacial_landforms`，照設計不算這項。
- **R4**：Jezero（碳酸鹽＋鎂鐵質）、Arcadia／AP-105（鎂鐵質）的 `mineral_signature` 有分數。
  - 同分變少：前 20 名裡和其他名次同分的個數，Jezero 16 → 7、Arcadia／AP-105 9 → 4；Arcadia／AP-105 原本前 20 名有 7 格滿分 1.0，現在 0 格。
  - Arcadia／AP-105 的新第 1 名在 Talnakh 附近（Putorana 高原，西伯利亞暗色岩的玄武岩），很合理。
  - **但 Jezero 的新前 20 名全部在北極**（加拿大北極群島、西伯利亞、阿拉斯加／育空），見 11.5 第 1 點。
- **冰河併進「無冰覆蓋」**：R1、R4 前 20 名沒有任何冰雪比例 > 0.1 的格子。GLIMS 冰河比例把幾個冰河格子擠出了前 20 名：
  - Gale R1 的 Los Antiguos（AR，巴塔哥尼亞冰原邊，冰河比例 0.155）
  - Gale R4 的 4 格（3 格在中國西部、1 格在 Gjoa Haven，0.12–0.26）
  - Oxia R4 的 Longyearbyen（Svalbard，0.157）
  - Protonilus R4 的 2 格

  R1 的第 1 名全部不變，「≥ 0.8、≥ 0.9 的陸地比例」到小數第 4 位都沒變。
- R3 不受補資料影響（只用永凍土、溫度、乾燥度），7 個目標都不變。

### 11.3 放大結果重點（`zoom_candidates.py --top 3`）

每個目標第 1 名的最佳 1 km 小區：
- 「0.1° 原分數」是全球版的整體相似度；「1 km 中位數」是同一 0.1° 格內子格的中位數。
- 坡度是最佳小區 1 km 方塊內的高解析坡度 p50 / **p90** / 最大。這 7 個地點都在南北緯 60° 之間，所以都是 Copernicus 30 m。
- 雷達：S1 = Sentinel-1 VV，括號是影像年份；HH = PALSAR-2。單位都是 dB。

| 目標 | 候選（0.1° 格） | 0.1° 原分數 | 1 km 中位數 | 最佳 1 km 小區 | 1 km 分數 | 高解析坡度 p50 / **p90** / 最大 | 雷達 |
|---|---|---|---|---|---|---|---|
| jezero | 33 km from Urdgol (MN)（48.05, 92.95） | 90.4 | 81.1 | **48.035, 92.995** | 88.3 | 2.44° / **5.08°** / 22.17° | S1 −16.3（2017–2021）；HH −23.7 |
| gale | near Altanteel (MN)（47.05, 92.85） | 88.2 | 77.4 | **47.065, 92.815** | 88.4 | 5.42° / **6.18°** / 6.89° | S1 −9.1（2017–2021）；HH −12.2 |
| arcadia | 46 km from Urdgol (MN)（48.25, 92.65） | 83.2 | 70.0 | **48.215, 92.655** | 84.3 | 0.70° / **2.05°** / 5.03° | S1 −14.2（2017–2021）；HH −18.6 |
| oxia | 125 km from Shumanay Shahri (UZ)（41.85, 57.85） | 90.9 | 82.5 | **41.685, 57.805** | 91.2 | 0.41° / **1.07°** / 2.09° | S1 −19.8（2022–2024）；HH −18.9 |
| meridiani | 127 km from Mazongshan (CN)（42.85, 97.65） | 89.6 | 89.1 | **42.905, 97.595** | 90.8 | 4.55° / **8.57°** / 18.39° | S1 −11.1（2022–2024）；HH −16.0 |
| protonilus | 93 km from Maindong (CN)（30.95, 84.55） | 89.9 | 73.0 | **30.805, 84.505** | 87.7 | 4.07° / **7.20°** / 18.57° | S1 −16.3（2022–2024）；HH −19.7 |
| ap105 | 46 km from Urdgol (MN)（48.25, 92.65） | 88.7 | 71.6 | **48.245, 92.625** | 89.6 | 0.86° / **1.92°** / 4.79° | S1 −17.5（2017–2021）；HH −21.1 |

- **四個目標的第 1 名都在蒙古西部大湖盆地**：Jezero、Arcadia、AP-105 在 Urdgol 附近，Gale 在 Altanteel；Arcadia 和 AP-105 是同一格。Jezero 的 0.1° 格就在大湖岸邊，三個最佳小區有兩個貼著湖岸（`zoom_jezero_1.png`），見 11.5 第 4 點。
- **高解析坡度 p90 全部 < 15°**（SkyFall 要求 1–5 m 尺度坡度 < 15°）。但這裡是 30 m 的坡度，比要求粗，只能當初篩。
  - 最平的是 Oxia（p90 1.1°）、AP-105（1.9°）、Arcadia（2.1°）；Meridiani 最陡（p90 8.6°，最大 18.4°）。
  - 第 2、3 名裡，Gale #2（Barkol 西方山地，p90 29.6°）和 Gale #3（Bayinbaolige 山前，p90 25.1°）不適合著陸。
- **0.1° 原分數 vs 1 km**：
  - 21 個候選裡有 13 個「1 km 中位數」比 0.1° 原分數低 5 分以上；最佳 1 km 小區和原分數相差 −2.2 到 +2.6。
  - Meridiani 三個候選幾乎不變（例如 89.6 → 89.1），是唯一 0.1° 和 1 km 一致的目標：戈壁地形均勻、附近沒有湖。
  - Gale #3 最極端：0.1° 格跨在山前斷層線上（一半山、一半平原），原分數 86.6，1 km 中位數只有 48.0。
- 雷達：表中 4 個蒙古地點，加上 Arcadia #2（楚科奇）、AP-105 #2（阿爾泰 Kosh-Agach），2022–2024 都沒有 Sentinel-1，改用 2017–2021。PALSAR-2 每個地點都有值。

### 11.4 任務版重跑（`run_pipeline.py --stage all`）

- `outputs/` 現在有 7 個目標 × 4 個任務 = 28 個結果檔和熱度圖（原本只有前 3 個目標）。
- 前 3 個目標的第 1 名和 git 裡上午版本的比較（變化主要來自 8.4 冰的目標值改成 clip(Ci, 0, 1)）：

| 目標 | 任務 | 上午第 1 名 | 現在第 1 名 | 前 20 名重疊 |
|---|---|---|---|---|
| jezero | geology | 68 km from Jisegumen (CN)（88.2） | **33 km from Urdgol (MN)**（90.5） | 13/20 |
| jezero | rover | 68 km from Jisegumen (CN)（93.7） | 不變 | 20/20 |
| jezero | isru_base | 110 km from Cuozheqiangma (CN)（88.7） | **33 km from Urdgol (MN)**（91.5） | 0/20 |
| jezero | landing | 83 km from Abu Sunbul (EG)（96.8） | 不變（97.1） | 19/20 |
| gale | geology | 111 km from Jisegumen (CN)（86.1） | **132 km from Bohu (CN)**（86.4） | 8/20 |
| gale | rover | 111 km from Jisegumen (CN)（92.2） | 不變 | 20/20 |
| gale | isru_base | 85 km from Lasite (CN)（85.8） | **4718 km from Waitangi (NZ)**（87.6，南極，見 11.5 第 9 點） | 0/20 |
| gale | landing | 36 km from Abu Sunbul (EG)（92.8） | 不變（93.3） | 17/20 |
| arcadia | geology | near McMurdo Station (AQ)（90.8） | **193 km from Qimantage (CN)**（89.2） | 13/20 |
| arcadia | rover | 1205 km from Kugluktuk (CA)（95.9） | 不變 | 20/20 |
| arcadia | isru_base | 1205 km from Kugluktuk (CA)（86.1） | **46 km from Urdgol (MN)**（85.0） | 1/20 |
| arcadia | landing | 76 km from San Luis (MX)（95.7） | 不變（96.5） | 16/20 |

- 權重：isru_base 的冰權重 0.329 → 0.313，landing 0.011 → 0.006，其他差不多。
- 留一法 AUC（`summary_tables.md`）：
  - **isru_base 先驗 0.552 → 0.441**（低於 0.5），全域混合 0.729 → 0.673；
  - geology 任務專屬混合 0.626 → 0.593（仍採用先驗）；
  - rover、landing 幾乎不變。
- **第 6.5 節的表和 `WEIGHTS_EXPLAINED.md` 裡的數字是凌晨版本，已經過時**，要用新的 `outputs/summary_tables.md` 更新（這次沒改文件）。

### 11.5 還沒解決的問題與建議（都沒有改，要你決定）

1. **ASTER 礦物指標在高緯度系統性偏高 → Jezero 的 R4 前 20 名全在北極。**
   - 按緯度分帶看全球百分位：
     - 北緯 70° 以北 57% 的格子 CI（碳酸鹽）在全球前 10%，中緯度只有約 5%。
     - 同一種岩性內，年均溫 < −5 °C 的格子 CI 百分位中位數約 0.83，> 10 °C 的約 0.4–0.5（碎屑沉積岩、碳酸鹽岩、玄武岩都一樣）；MI（鎂鐵質）也一樣。
   - 原因應該是 ASTER GED 的放射率混到雪、霜或寒冷大氣：雪在 band 13 比 band 14 高，看起來像「碳酸鹽」。
   - Jezero 用碳酸鹽＋鎂鐵質，兩個都被推高；Arcadia／AP-105 只用鎂鐵質，前 20 名混合了 Putorana 玄武岩、阿根廷 Puna 火山區、堪察加，比較合理。
   - **修正前，Jezero 的 R4 結果不要放進簡報。**
   - 可選：
     - (a) 只在年均溫 > 0 °C（或南北緯 60° 以內）的格子算礦物指標，其他當缺資料；
     - (b) 百分位改在同一緯度帶或同一岩性內算；
     - (c) 用 ASTER GED 自己的 `ndvi`、`num_obs` 波段做品質篩選。
2. **ASTER 壞值**：692 格的 CI／MI 超出合理範圍（第 2 步），目前被荒蕪度擋掉。建議在 `gee_extra.aster_indices` 加合理範圍檢查（各波段放射率 0.6–1.0，比值 0.7–1.3）。紐西蘭、南極在 GEE 上本來就沒有 ASTER GED，R4 在那裡不評分（只影響有礦物指標的目標）。
3. **R6 溫度季節「形狀」不看振幅 → 赤道高山拿高分。**
   - Arcadia 的 R6 第 1 名在秘魯 Patambuco（Titicaca 湖附近），地表溫季節變化只有 4.6 °C，火星目標是 67 °C。
   - Protonilus 的第 1 名在厄瓜多 Quero（赤道），4.0 °C，火星 47 °C；Protonilus 的 R6 前 5 名都在厄瓜多和肯亞高地。
   - 相關係數只看形狀，平平的曲線也可能相關很高；沙塵有振幅特徵，溫度沒有。
   - 建議在 `config\mission_tests.yaml` 的 R6 加 `temperature_season_amplitude`。用「最高 − 最低（K）」的對數比，不要用 (最大 − 最小)／平均，因為攝氏平均可能接近 0。
4. **全球 0.1° 的地表溫度與 NDVI 會混到附近的湖 → 湖邊格子的分數被墊高。**
   - 這是凌晨的全球層（`gee_layers.lst_climatology`、NDVI），不在這次可以修的範圍；今天的每月 LST 也用同一套，所以結果彼此一致。
   - 這兩層直接重投影到 0.1°，沒有先 `reduceResolution`，GEE 會從 MODIS 金字塔取樣。全球有 41% 的東西向相鄰格數值完全相同（南北向 0.2%），有效解析度在經度方向比 0.1° 粗。
   - 放大的 21 個候選中，有 **7 個 0.1° 格是這種情況**（Jezero #1、#3，Oxia #1、#3，Protonilus #1–#3）：
     - 它們的日溫差、白天地表溫、NDVI 都明顯低於周圍 5×5 格。例：Jezero #1 日溫差 8.6 K，周圍 21 K，1 km 資料 21.8 K。
     - 格內或隔壁格有湖（水體比例 0.15–1.0）。湖面讓格子看起來更冷、更荒，所以分數變高。
   - 放大程式排除水體子格、改用 1 km 資料，所以 1 km 中位數比 0.1° 原分數低很多（Protonilus #1 89.9 → 73.0、#2 88.7 → 70.1）。
   - 建議：
     - (a) 全球 LST、NDVI 改成先遮掉 MOD44W 水體，再 `reduceResolution(mean)` 到 0.1°，重跑 `fetch_earth_gee.py`（約 20 分鐘）＋ `earth_grid` ＋剖面＋測試；
     - (b) 在那之前，排名池排除「格內或相鄰格水體 > 10%」的格子，或在表上標出。
   - 放大程式本身也有一點同樣的問題：子格只排除水體 > 50% 的，Jezero #1 的最佳小區有兩個貼著湖岸，1 km MODIS 地表溫在湖岸可能仍偏涼。可以在 `zoom.subgrid_frame` 把「水體 > 0 或緊鄰水體」的子格排出排名池。
5. **0.1° 原分數普遍高於同格的 1 km 中位數**（21 個候選裡 13 個低 5 分以上）。原因有三：上面的湖、地形資料不同（GMTED vs Copernicus），以及挑前幾名本身的選擇偏差（挑的是全球最高分，再量一次通常會變低）。所以放大結果要看「最佳 1 km」和「1 km 中位數」，不要和 0.1° 原分數比（`ZOOM_SUMMARY.md` 開頭已經這樣寫）。
6. **`COPERNICUS/DEM/GLO30` 已被 GEE 標為過時**，新版是 `COPERNICUS/DEM/GLO30_2024_1`。目前還能用，只會印警告。南極地形（`gee_layers`）和放大地形（`gee_zoom`）都用舊版；要換就兩邊一起換，再重抓南極和放大方框。
7. **HLS 底圖**：已改成優先取當地夏季。少數地方夏季的低雲影像不多（Protonilus #1 只有 13 張、Arcadia #3 14 張），底圖可能比較雜。只影響圖，不影響分數。
8. **雷達年份不一致**：Sentinel-1 有的地點是 2022–2024、有的是 2017–2021（json 的 `s1_period` 有記）。只列出不計分，比較不同地點時要注意。
9. **任務版（`export.py`）的排名沒有變數覆蓋率門檻 → 只有 5／10 個變數的南極格當上第 1 名。**
   - 南緯 86.15°、西經 157.25°（Transantarctic Mountains）沒有坡度、粗糙度、熱慣量、乾燥度、NDVI，信心度 0.615。
   - 它是 Gale／isru_base 第 1 名、Protonilus／geology 第 2 名、Protonilus／isru_base 第 3 名，也在 Jezero／isru_base、Gale／geology 的前 20 名。
   - 類比剖面和測試都有「覆蓋率 ≥ 80%」或「必要特徵」的規則，任務版沒有。建議 `export_one` 的排名池加上 `confidence ≥ profiles.MIN_CONF`。
10. **isru_base 的先驗權重留一法 AUC 0.441**（比隨機還差）：冰的目標值改成 clip(Ci, 0, 1) 之後，先驗的冰權重方向可能和已知取冰類比地不合。要配合 `docs/MISSION_WEIGHTS_BASIS.md` 重看 isru_base 的先驗。
11. `summary_tables.md` 的「目標 × 任務」表，新目標（沒有標給它們的已知類比地）整列是 nan，只是顯示問題。
12. **環境檔**：`git status` 顯示 `env/nasa_hackathon.yml`、`environment.yml` 在工作目錄裡被刪除，這次執行前就是這樣，我沒動。第 1 節的重建步驟要用它，請確認是不是故意的。
13. 之前就有、這次沒處理的：缺岩性的格子佔便宜（8.6）、Protonilus 冰的目標值用圓內中位數（8.6）、門檻型測試很多格同時滿分（10.3）、R2 無法評估、B8 人工確認新候選地。

---

## 12. 修正 11.5 的問題（Claude 雲端，11/14 傍晚）

照 11.5 的建議改程式。全球資料要重抓、重跑，在本機做，見 `docs\PROMPT_local_rerun_1114.md`。

### 12.1 全球資料的抓法（11.5 第 4 點，最重要）
- 在目前的全球網格確認了問題：地表溫度、日夜溫差、NDVI、反照率的東西向相鄰格有 22% 數值完全相同（南北向只有 0.3%）；有做格內聚合的坡度只有 1%。Jezero 剖面第 1 名那一格日溫差 8.6 K。
- `gee_layers.land_mean_on_grid`：先用 MOD44W 把水體像素（原生像素水體比例 > 0.5）遮掉，再 `reduceResolution(mean)` 到 0.1°。套用在：
  - 全球的地表溫度（4 層）、反照率、NDVI、乾燥指數
  - 每月地表溫度（`gee_extra.lst_monthly`）
- `_gee._fetch`：連續逾時就把區塊切小（格內平均比金字塔取樣重）。`fetch_earth_gee.py` 這四層改成 150 px 的區塊、12 個平行。
- `fetch_earth_gee.py --test --at LAT LON`：抓指定格附近 10×10 格，和目前的陣列並排比較（中心格新舊值、東西相鄰相同的比例）。

### 12.2 測試計分
- **ASTER 礦物指標**（第 1、2 點）：
  - 百分位改在同一年均地表溫帶內算（−5、5、15、25 °C 分帶）。
  - 指標超出 0.7–1.3 當缺資料；GEE 端也加了放射率 0.6–1.0 的檢查，並改成先 1 km 再 0.1° 的格內平均。
  - 驗證：「碳酸鹽和鎂鐵質都在前 10%」的格子比例，各溫度帶都在 2–3%，不再偏向寒冷地區。
- **Jezero R4 還是北極居多**：查出另一個原因——「無植被」用年平均 NDVI，積雪把凍原的年平均拉低。新增特徵 `summer_barren`（生長季高峰 NDVI，MOD13A2 2015–2024 第 90 百分位；≤ 0.15 滿分、≥ 0.4 為 0），加在 R1、R4、R5，需要本機新抓 `ndvi_p90`（`fetch_earth_extra_gee.py` 的 ndvi 層）。**這層抓到之前，Jezero 的 R4 還是不要放進簡報。**
- **R6 加 `temperature_season_amplitude`**（第 3 點）：季節溫差（最高月 − 最低月，K）的對數比，σ = ln 2。用目前資料驗證，赤道高山不見了：
  - Arcadia 第 1 名換成內蒙古（季節溫差 55 K，火星 67 K）
  - AP-105 換成阿爾泰 Kosh-Agach（50 K 對 53 K）
  - Jezero 換成特內里費島 Vilaflor（16.5 K 對 15.6 K）
- `outputs\mission_tests\` 已用目前資料重跑一次（全球資料重抓後還要再跑）。

### 12.3 任務版與放大
- `export.py`（第 9 點）：排名池加「加權信心度 ≥ 0.8 且變數覆蓋率 ≥ 0.8」。驗證：Gale／isru_base 第 1 名從南極格換成 79 km from Xagmakajor（信心度 1.0）。Claude Code 加的 NaN 防護保留。
- `zoom.py`（第 4 點的放大部分）：自己或 8 個鄰格水體比例 > 5% 的子格不參加排名（分數照算、地圖照畫），json 記 `n_near_water`。用一個假湖測過，湖旁一圈子格被排除，最佳小區都在湖外。
- `gee_zoom.py`（第 6 點）：放大地形改用 `COPERNICUS/DEM/GLO30_2024_1`（`gee_layers.glo30()`，不存在時退回舊版）。全球網格的南極地形這次不重抓，所以 `gee_layers` 的全球地形函式維持舊版，以免程式和資料對不上。

### 12.4 沒改的
- isru_base 先驗 AUC 0.441（第 10 點）：簡報改用 R3 地下冰測試，不用任務版的 isru_base 排名，先不調。
- 第 6.5 節和 `WEIGHTS_EXPLAINED.md` 的數字：等本機重跑完一次更新。
- 環境檔 `env/nasa_hackathon.yml`、`environment.yml`：工作目錄裡確實被刪了（中午還在）。我這邊沒有刪除權限，Claude Code 也說沒動。要救回就跑 `git restore env/nasa_hackathon.yml environment.yml`，交給 B 決定。

### 12.5 給網頁整合的資料（Claude 雲端，11/14 傍晚）
整合者 Harris 的網頁在 77bigsun/nasa 的 main（c875ba6，本機 checkout 在 `C:\Users\plusl\nasa-main`）。網頁自己算分數：我們交的是**原始量測值**，放進它的 `data/seed/`，不是交排名。
- 新程式 `scripts/export_web_seed.py`；契約快照在 `config/web_contract/`；輸出在 `outputs/web/`（說明見 `outputs/web/WEB_EXPORT.md`）。
- `current/`：照網頁現在的任務定義填，網頁不用改。只有 R1（100 m 坡度、熱慣量）和 R6（沙塵、日夜溫差）有分數：R3 地下冰、R5 粗糙度是 relative_rank，要火星百分位，我們只有原始值。
- `proposed/`：建議 Harris 改定義（`r3_ground_ice` 改門檻型、`r5_roughness` 改 absolute，新增 R1 無植被／不是冰面、R3 年均溫／乾燥、R4 岩性大類＋對照表／岩石裸露、R5 永凍土／年均溫、R6 年均溫），規則同 `config/mission_tests.yaml`。R2 仍然沒有資料。
- 地球候選 28 個：AP-105、Jezero、Gale 每個測試取本隊分數前 2 名（相隔 ≥ 150 km）＋已知類比地。上限 28 是因為網頁的邊際效益曲線用窮舉 C(n, 6)。
- `merged/`：和網頁現有檔合併（月球 placeholder 保留，placeholder 候選身上的火星特徵值移除），可以直接放進 `data/seed/`。網頁的 pydantic 契約驗證通過，評分與集合覆蓋程式在雲端跑通。
- 網頁程式要 Harris 決定的兩件事：
  1. 百分位母體是「候選清單本身」，不是全球。只改這一行、改用 `earth_population.json` 的全球分位數時，proposed 版 R6 的最高分從 0.33–0.41 變成 0.79–0.93（AP-105、Jezero、Gale），R6 才覆蓋得到。
  2. 月球＋火星候選共 48 個時窮舉 C(48, 6) ≈ 1,227 萬種組合，跑不動；建議算分前只留該任務有值的候選，或改用 PuLP。
- 還缺：SkyFall 另外四區（Deuteronilus、Utopia、Phlegra、Erebus）在網頁的 `target_sites.yaml` 沒有座標；候選要等本機重跑後再產生一次（`PROMPT_local_rerun_1114.md` 第 2 節第 8 步）。

### 12.6 只留 R1–R6、類比剖面加「每個變數的前 5 名」（Claude 雲端，11/14 晚上）
- **任務版停用**（B 決定只留一個任務導向的版本）：留測試項目 R1–R6。理由：整合者的規劃、網頁、集合覆蓋都用 R1–R6；任務版的四種任務對不上題目的測試，isru_base 先驗 AUC 只有 0.441，岩性權重因為資料太粗學到接近 0。任務版程式與文件保留備查；`PROMPT_local_rerun_1114.md` 第 7 步改成不用跑，第 6.5 節和 `WEIGHTS_EXPLAINED.md` 不再更新。方法 B 的驗證結論保留。
- **類比剖面新增每個變數的前 5 名**：`profiles.py` 的 `top_variable()`，結果檔多 `top_by_variable`。新圖 `board_{目標}.png`：每一列是一個面向，第一格是面向前 5 名，後面是面向內每個變數的前 5 名。總表多一節，列出每個地點該變數的分數、地球值、整體相似度。用目前資料重跑了 7 個目標。
  - 溫度的前 5 名幾乎都在高緯北極：火星比地球任何地方都冷，所以溫度分數是「越冷越好」，最冷的地方自然在北極。
  - 岩性、無植被、坡度常常很多格子同為 1.00，排序靠「同分時整體相似度高的優先」決定。
- 網頁的排名方法是暫時的（Harris 之後會改），本隊方法不用配合；`outputs/web/` 只當資料交付。

## 13. 重抓全球資料與重跑（Claude Code，11/14 晚）

> 任務定義：`docs/PROMPT_local_rerun_1114.md`；22:10 改計畫後，第 2–8 步改照 `docs/PROMPT_run_1114_night.md`。中途交接：`docs/HANDOFF_rerun_1114pm.md`。
> log：`run_1114/logs/stageA.log`、`stageB.log`、`zoom_top3.out`；遠端下載 log 在朋友電腦的 `C:\Users\pypd\hatrefish_gee\logs\lst5.log`（本機沒有留副本）。工具：`data/interim/rerun_1114_tools/`。重抓前的備份：`data/interim/before_1114pm/`。
> 任務版（learn、validate、crosscheck、export、figures、`summarize_results.py`）照第 12.6 節停用，**沒有跑**；第 6.5 節和 `WEIGHTS_EXPLAINED.md` 沒改。

### 13.1 經過：時間、錯誤、修法

**16:35 新抓法檢查**（遮水體＋格內平均，各約 20 秒）
- Jezero 剖面第 1 名的湖邊格（48.05, 92.95）新 vs 舊：日溫差 21.48 vs 8.61 K、年均溫 4.82 vs 2.29 °C、NDVI 0.074 vs 0.033、反照率 0.264 vs 0.232；這個 10×10 塊「東西相鄰相同」的比例 49% → 0%。
- Atacama 10×10 中位數新舊一致：年均溫 26.42 vs 26.57、日溫差 34.22 vs 34.09。沒有湖的地方新舊一樣。

**16:36–21:42 全球重抓**（地表溫、反照率、NDVI、乾燥指數，以及補資料的 ASTER、夏季 NDVI）
1. 150 px 一塊太慢：20 分鐘只完成地表溫 23／234 塊。改成 50／75 px、更多平行，地表溫從約 2 塊／分鐘變成約 5 塊／分鐘。
2. 17:35 左右 `nasa-spaceapp-hackathon` 用完 Community 額度（每月 150 EECU 小時），進入 Restricted Mode（同時只能約 5 個請求，多的回 429）。組員把帳號加進 `active-venture-430707-a8` 的 IAM（18:39 生效）。
3. 補抓失敗的塊（`patch_tiles.py`）：NDVI 104 塊、反照率 119 塊。乾燥指數在新專案從頭抓；請求範圍含南北極點時，遮水體的換投影會失敗（「Can't transform」）：北邊 19 塊改用 50 px 補完，南極 24 塊不補（乾燥指數在南緯 60° 以南本來就設缺值）。
4. ASTER（36 分鐘）：缺值 3.04% → 2.48%，超出 0.7–1.3 的格子 692 → 0，新舊排名相關 QI 0.91、CI 0.93、MI 0.98。夏季 NDVI `ndvi_p90`（28 分鐘）：寒冷地區（年均溫 < −5 °C）比年平均高 0.415；北緯 55° 以北「看起來很荒」的 51,356 格裡，6,706 格夏季 NDVI ≥ 0.4（`summer_barren` = 0）。
5. 舊專案上的全球地表溫做到 1440／1448 後卡住（只剩一條連線在等不回應的請求），19:44 停掉。程式只在整層結束才存檔，全部重來。
6. **錯誤修正：南極被當成水**。MOD44W 不涵蓋南極，新抓法把「沒資料」當水，整個南極的地表溫都變空值（McMurdo 舊值 −27.9 °C）。`gee_layers.water_at` 改成南緯 60° 以南沒資料時當陸地，和 `earth_grid` 的水體規則（只用在 −60° 以北）一致。
7. **錯誤修正：放大拿到 0.1° 聚合影像**。第 12 節把 `lst_climatology` 等函式改成直接回傳 0.1° 格內平均，放大程式再投到 0.01° 時，每個 1 km 子格都只拿到所屬 0.1° 格的值。加參數 `grid_mean`（預設 True），`gee_zoom.climate`、`surface` 用 False。
   - 6、7 兩點不是方法改變，是第 12 節改動的連帶錯誤，所以直接修。
8. 約 20:1x，本機記憶體不足，Claude Code 停掉了新專案上的全球地表溫（約 600 塊）和每月地表溫（約 300 塊）兩個背景工作，進度全丟。依規則沒有自己重開。
9. 約 20:50，`active-venture-430707-a8` 也進入 Restricted Mode（這個月都會限速，要跟組員說）。
10. 使用者同意在朋友電腦（Tailscale，`ssh pypd@100.119.21.3`）用自己的 GEE 帳號跑，並把 `nasa-spaceapp-hackathon` 升級成 Contributor（每月 1,000 EECU 小時）。朋友電腦沒有 scp，檔案用 `xfer.sh` 經 ssh 標準輸入輸出傳，用 SHA-256 核對。下載程式改成每 2 分鐘存檔、可續傳（`remote_fetch.py`）。21:42 依使用者要求暫停（地表溫 206／1448、每月地表溫 512／1448），寫交接文件。

**22:10 改計畫（使用者決定，時間不夠）**
- 全球地表溫的平均期間從 2015–2024 十年縮成 **2020–2024 五年**；五年仍是正常的氣候平均，運算量約減半。
- 不再抓每月地表溫，改用推算（`scripts/derive_monthly_lst.py`）：新每月值 = 舊每月值 +（新年均 − 舊每月平均）。季節形狀沿用舊值。新舊年均差 > 1.5 K 或日夜溫差差 > 3 K 的格子設空值。
- 總工作量約少 66%。「只重抓有水的塊」沒用：1,448 塊裡 1,175 塊至少有一個混水格。

**23:11–23:46 下載**（使用者開的 `run_1114/1_start_download.cmd`，朋友電腦）
- 1,448 塊，20 條平行，2,128 秒，0 失敗，log 裡沒有 429。

**23:46 傳回**：4 個檔案都 `OK`（SHA-256 一致）。

**23:47–23:49 階段 A**、**23:49–00:03 階段 B**：每一步都 exit 0，細節見 13.3、13.4。這次沒有工作因記憶體不足被停掉。

### 13.2 這次改過的程式（都還沒 commit）

| 檔案 | 改了什麼 |
|---|---|
| `scripts/fetch_earth_gee.py` | `lst` 50 px／24 平行；`albedo`、`ndvi` 75 px／12；`aridity` 50 px（避開含極點的請求） |
| `scripts/fetch_earth_extra_gee.py` | `lst`、`aster`、`ndvi` 改 50 px／16 平行 |
| `src/mars_analog/adapters/earth/gee_layers.py` | `water_at` 南極修正（13.1 第 6 點）；`lst_climatology`、`albedo_climatology`、`aridity_index` 加 `grid_mean`（第 7 點）；`lst_climatology` 加 `start`（預設 2015-01-01 不變，全球重抓用 2020-01-01） |
| `src/mars_analog/adapters/earth/gee_zoom.py` | `climate`、`surface` 用 `grid_mean=False` |
| `scripts/derive_monthly_lst.py`（新，雲端寫） | 每月地表溫推算 |
| `data/interim/rerun_1114_tools/` | 遠端下載（`remote_fetch.py`）、傳檔（`xfer.sh`）、補抓（`patch_tiles.py`）、檢查（`check_grid.py`） |

### 13.3 階段 A：檢查數字（全部通過）

| 條件 | 結果 |
|---|---|
| 地表溫 4 層陸地缺值增加 < 0.5 個百分點 | 0.01% → 0.01%（多 80 格） |
| 「東西相鄰相同」明顯下降 | 陣列 40.9% → 0.0%；網格 `lst_mean_c`、`dtr_c` 22.1% → 0.0% |
| `same cell ids: True`、列數不變 | True，1,441,608 列 |
| Jezero 湖邊格 `dtr_c` 在 15–25 K | 21.07 K（舊 8.61） |
| McMurdo `lst_mean_c` 不是 NaN | −24.45 °C |
| 每月地表溫推算被遮掉 < 15% | 6.9% |

單格（新 vs 舊，°C 或 K）：

| 地點 | 白天 | 夜間 | 日溫差 | 年均 |
|---|---|---|---|---|
| Jezero 湖邊格（48.05, 92.95） | 15.40 vs 6.60 | −5.67 vs −2.01 | 21.07 vs 8.61 | 4.86 vs 2.29 |
| McMurdo（−77.2, 161.5） | −23.01 vs −27.50 | −25.89 vs −30.20 | 2.88 vs 2.70 | −24.45 vs −28.85 |
| Atacama（−24.1, −69.9） | 45.51 vs 46.02 | 8.29 vs 8.52 | 37.22 vs 37.50 | 26.90 vs 27.27 |

- McMurdo 比預期（約 −28 °C）暖 4.4 K，但不是整個南極偏暖：南緯 60° 以南的新舊差中位數 −0.11 K（5–95 百分位 −0.79 ～ +0.68）。舊值是同一個像素複製整排（周圍 5×5 每列數值相同），新值在周圍 5×5 內從 −21.6 到 −29.0 °C，是乾谷岩石與冰雪交界的真實差異。
- 全球新舊差（網格）：年均溫差中位數 0.40 K、95 百分位 1.54 K，相關 0.9989；日溫差差中位數 0.45 K、95 百分位 1.86 K，相關 0.9902。北緯 30–60° 的年均溫差中位數 +0.64 K，其他緯度帶在 ±0.15 K 內。這同時含「遮水體」和「十年 → 五年」兩種差異。
- 陣列層級的反照率、乾燥指數在南極是空值（`land_frac` > 0.5 的格子缺值 28%），這是 16:36 抓的時候南極修正還沒做；網格（無冰陸地）裡反照率缺值 0%，熱慣量缺值 45.11% → 45.16%，不影響計分。

### 13.4 階段 B：結果

1. **每月地表溫推算**：有舊月值的陸地格 2,130,016 個，遮掉 147,980 個（6.9%）；保留的格子平移量中位數 0.34 K、95 百分位 1.19 K。`earth_monthly.parquet` 裡每月地表溫缺值 8.81%（12 個月同時缺；舊版 0%）。舊月值備份在 `data/interim/earth_0p1_extra/_old_monthly/`。
2. **剖面**：7 個目標都有；看了 `board_jezero.png`、`board_arcadia.png`，每格 5 個地點，文字沒有被裁掉（一個太長的地名用「…」截短，是設計）。
3. **測試 R1–R6**：`TEST_SUMMARY.md` 開頭沒有「待補資料」。
   - **Jezero R4 前 20 名：北緯 60° 以北 19 → 15 個，70° 以北 15 → 12 個。下降不多。**
   - 第 1 名從 Haines Junction 附近（59.45°N）變成 Gjoa Haven 以北 548 km（73.55°N，加拿大北極群島）。
   - 原因：前 20 名多數是加拿大北極群島的極地荒漠，夏季高峰 NDVI 0.13–0.17、年平均 NDVI 0.00–0.03，是真的沒有植被，不是凍原被誤判。`summer_barren` 有作用（夏季 NDVI ≥ 0.4 的凍原已經被排掉），但門檻（≤ 0.15 滿分、≥ 0.4 零分）讓極地荒漠照樣滿分。要不要再排除，是方法決定（見 13.8）。
4. **集合覆蓋**（`outputs/set_cover/`）：

   | | 重抓前（22:55 試跑） | 重抓後 |
   |---|---|---|
   | 需求數 | 27 | 27 |
   | 最少地點數 | 5 | 5 |
   | 邊際曲線 | 14 → 20 → 24 → 26 → 27 | 15 → 20 → 24 → 26 → 27 |
   | 換門檻 0.8／0.85／0.9／0.95 × 最高分 | 地點數 3–7 | 3／3／5／7（和預設組合相同的地點 0/3、0/3、5/5、3/7） |
   | Jezero R4 指派到 | 加拿大北極 76.95°N | **仍在北極：72.95°N, −91.95（Gjoa Haven 以北 502 km，最近的已知類比地 Haughton 隕石坑 279 km）** |

   - 新的 5 個地點：加拿大北極群島（72.95, −91.95）、甘肅（36.45, 103.95）、西崑崙（35.65, 82.55）、加拉巴哥群島（−0.35, −91.45）、玻利維亞烏尤尼鹽沼（−20.35, −67.55）。
   - 只看 Jezero 自己時，R4 指派到印度 Rapar 附近（23.2, 70.8），不在北極；七個目標一起時，北極那一點同時滿足 Jezero R4、Oxia R4、Arcadia R5、AP-105 R5，所以被選上。
   - 「要幾個地點」比「是哪幾個」穩：換門檻時具體地點變動大。
5. **網頁資料**（`outputs/web/`）：`--check` 失敗，`TypeError: COIN_CMD.__init__() got an unexpected keyword argument 'randomSeed'`。網頁 repo 的 `services/planning/app/core/optimize.py` 呼叫 `pulp.COIN_CMD(..., randomSeed=42, ...)`，`services/planning/requirements.txt` 指定 `pulp[cbc]==4.2.0`；本機 `nasa_hackathon` 是 pulp 3.3.2。照 PROMPT 先不加 `--check` 重跑，成功。
   - **11/15 00:2x 補跑 `--check`（使用者要求）**：pulp 4.x 要 Python ≥ 3.12，`nasa_hackathon` 是 3.11 升不上去，所以另外建一個只跑這一步的 venv：`C:\Users\plusl\.venvs\nasa_webcheck`（miniconda 內附的 Python 3.13.11；照網頁 requirements 裝 pulp[cbc] 4.2.0、pydantic 2.14.3、numpy 2.5.4、scipy 1.18.1、httpx 0.28.1、pyyaml 6.0.3、fastapi 0.162.7，另加 pandas、pyarrow、reverse_geocoder、matplotlib）。`nasa_hackathon` 沒動。2.7 分鐘，兩段檢查都跑成。除了 `WEB_EXPORT.md` 多了檢查表，`outputs/web/` 其他檔案和不加 `--check` 那次逐位元組相同。新舊檢查表見 13.6。
   - Jezero R4 的網頁候選：舊（59.45°N、72.35°N）→ 新（73.55°N、74.65°N），**兩個都在 70°N 以北**，和第 3 點同一個原因。
6. **放大**：
   - `--test`（Jezero 第 1 名 Wutumeiren 以東 92 km，37.45, 93.95，方框 63×50 子格）：下載 27 秒，14 個變數子格都有值。0.1° 格值 vs 格內 91 個子格中位數：年均溫 6.84 vs 8.25 °C、日溫差 11.76 vs 14.97 K、NDVI −0.007 vs −0.002；整體相似度 0.1° 格 88.4、格內子格中位數 87.3。
   - `--top 3 --refresh`：21 個候選、20 個方框，下載 126 秒，63 個最佳小區的地點細節，共 2.9 分鐘，沒有錯誤。21 張圖都重畫，所以沒有舊圖要移到 `_old_1114`（0 個）。
   - 唯一警告：`UMN/PGC/ArcticDEM/V3/2m_mosaic` 已被 V4 取代（還能用）。
   - 看了 3 張圖：
     - `zoom_protonilus_1`、`zoom_meridiani_1`：最佳小區離湖約 10 km 以上，正常。
     - **`zoom_jezero_1`（和 Oxia 第 1 名同一個方框）：最佳小區 #1（37.495, 93.745）貼著方框西北角的深色湖面。** 它的 1 km 日溫差只有 12.1 K（方框中位數 34.0 K），被水面壓低。近水排除（`NEAR_WATER`）用 MOD44W，但這個湖在真彩色底圖上比 MOD44W 的水體範圍大（推測是湖面擴張或人工滷水池，沒查證），所以沒被排除。方框內被近水排除的子格有 170 個。
   - Meridiani 第 1 名的相似度圖在 42.5°N／97.5°E 有一條方塊邊界（岩性來自 0.5° 的 GLiM）；真彩色底圖右上角沒有 HLS 影像。都只影響畫面。
7. **前後比較**：見 13.5。

### 13.5 前後比較（`data/interim/before_1114pm/compare_out.md`）

備份裡各結果的產生時間不同：剖面 15:13（第 10 節版）、測試 16:31（第 12 節新程式＋舊資料，`summer_barren` 當時是待補資料）、放大 15:50、網頁資料 17:09。所以差異同時含資料和程式兩種改變；地表溫度的差異又同時含「遮水體」和「十年 → 五年」。

**類比剖面（整體前 20 名）**

| 目標 | 第 1 名（舊 → 新） | 前 20 名重疊（150 km 內） | 前 20 名近水體（舊 → 新） |
|---|---|---|---|
| jezero | 33 km from Urdgol (MN)（90.4） → **92 km from Wutumeiren (CN)（88.4）** | 11/20 | 11 → 3 |
| gale | 不變：near Altanteel (MN)（87.4） | 15/20 | 4 → 1 |
| arcadia | 46 km from Urdgol (MN)（83.2） → **138 km from Chernyshevskiy (RU)（81.7）** | 14/20 | 8 → 7 |
| oxia | 125 km from Shumanay Shahri (UZ)（90.9） → **92 km from Wutumeiren (CN)（88.9）** | 7/20 | 20 → 14 |
| meridiani | 127 km from Mazongshan (CN)（89.6） → **97 km from Mazongshan (CN)（89.9）** | 17/20 | 7 → 7 |
| protonilus | 不變：93 km from Maindong (CN)（86.6） | 17/20 | 7 → 4 |
| ap105 | 46 km from Urdgol (MN)（88.7） → **near Kosh-Agach (RU)（86.1）** | 19/20 | 9 → 9 |

（近水體 = 3×3 鄰格 `water_frac` > 0.1。舊的 Jezero 第 1 名就是第 11.5 節說的蒙古湖邊格；Arcadia、AP-105 的舊第 1 名也在同一區（Urdgol 附近）。）

**測試第 1 名（括號是測試分數）**

| 目標 | R1 | R3 | R4 | R5 | R6 |
|---|---|---|---|---|---|
| jezero | 64 km from Jisegumen (CN)（1.0） → **113 km from Mori (CN)（0.985）** | 不適用 | 145 km from Haines Junction (CA)（0.973） → **548 km from Gjoa Haven (CA)（0.956）** | 不適用 | 不變：near Vilaflor (ES)（0.773） |
| gale | 79 km from A'yi Take (CN)（0.989） → **39 km from Ocucaje (PE)（0.976）** | 不適用 | 167 km from Torghay (KZ)（0.965） → **92 km from Wutumeiren (CN)（0.974）** | 不適用 | 183 km from Koramlik (CN)（0.947） → **118 km from Khapalu (PK)（0.95）** |
| arcadia | 70 km from Colchani (BO)（1.0） → **75 km from Colchani (BO)（1.0）** | 不變：67 km from McMurdo Station (AQ)（1.0） | 272 km from Talnakh (RU)（0.995） → **260 km from Talnakh (RU)（0.986）** | 1205 km from Kugluktuk (CA)（1.0） → **1196 km from Kugluktuk (CA)（1.0）** | 34 km from Todok (CN)（0.784） → **37 km from Todok (CN)（0.788）** |
| oxia | near Mynaral (KZ)（1.0） → **160 km from Yeyik (CN)（1.0）** | 不適用 | 170 km from Turkmenbasy (TM)（0.928） → **156 km from Beyneu (KZ)（0.946）** | 不適用 | near Zuogaiduoma (CN)（0.761） → **near Zuogaiduoma (CN)（0.757）** |
| meridiani | near Xagmakajor (CN)（0.999） → **160 km from Yeyik (CN)（0.99）** | 不適用 | 66 km from Colchani (BO)（1.0） → **65 km from Colchani (BO)（1.0）** | 不適用 | 108 km from Aqqan (CN)（0.947） → **37 km from Yeyik (CN)（0.938）** |
| protonilus | 102 km from Cuozheqiangma (CN)（0.993） → **67 km from Khash (IR)（0.98）** | 不變：522 km from McMurdo Station (AQ)（1.0） | 847 km from Gjoa Haven (CA)（0.965） → **40 km from Xitieshan (CN)（0.974）** | 不變：881 km from Kugluktuk (CA)（1.0） | 不變：128 km from Jumla (NP)（0.742） |
| ap105 | 142 km from Jisegumen (CN)（1.0） → **75 km from Colchani (BO)（1.0）** | 不變：67 km from McMurdo Station (AQ)（1.0） | 272 km from Talnakh (RU)（0.995） → **260 km from Talnakh (RU)（0.986）** | 1205 km from Kugluktuk (CA)（1.0） → **1196 km from Kugluktuk (CA)（1.0）** | near Kosh-Agach (RU)（0.781） → **near Kyzyl-Mazhalyk (RU)（0.788）** |

- 南極的 R3 第 1 名（McMurdo 附近）都還在：南極修正有作用。

**任務版**：這次沒有重跑（第 12.6 節停用），28 列（7 目標 × 4 任務）的第 1 名、前 20 名重疊、AUC 全部「不變」，完整表在 `compare_out.md`。

| 任務 | 採用（舊 → 新） | 留一法 AUC 先驗（舊 → 新） | 留一法 AUC 採用方案（舊 → 新） |
|---|---|---|---|
| geology | prior → prior | 0.681 → 0.681 | 0.681 → 0.681 |
| rover | blend → blend | 0.596 → 0.596 | 0.724 → 0.724 |
| isru_base | blend → blend | 0.441 → 0.441 | 0.673 → 0.673 |
| landing | blend → blend | 0.009 → 0.009 | 0.013 → 0.013 |

**放大（每個目標第 1 名：0.1° 原分數 − 0.1° 格內 1 km 中位數）**

| 目標 | 舊：候選、原分數 / 1 km 中位數（差） | 新：候選、原分數 / 1 km 中位數（差） |
|---|---|---|
| jezero | 33 km from Urdgol (MN)：90.4 / 81.1（+9.3） | 92 km from Wutumeiren (CN)：88.4 / 87.3（+1.1） |
| gale | near Altanteel (MN)：88.2 / 77.4（+10.8） | near Altanteel (MN)：87.4 / 77.4（+10.0） |
| arcadia | 46 km from Urdgol (MN)：83.2 / 70.0（+13.2） | 138 km from Chernyshevskiy (RU)：81.7 / 81.4（+0.3） |
| oxia | 125 km from Shumanay Shahri (UZ)：90.9 / 82.5（+8.4） | 92 km from Wutumeiren (CN)：88.9 / 87.5（+1.4） |
| meridiani | 127 km from Mazongshan (CN)：89.6 / 89.1（+0.5） | 97 km from Mazongshan (CN)：89.9 / 89.1（+0.8） |
| protonilus | 93 km from Maindong (CN)：89.9 / 73.0（+16.9） | 93 km from Maindong (CN)：86.6 / 73.1（+13.5） |
| ap105 | 46 km from Urdgol (MN)：88.7 / 71.6（+17.1） | near Kosh-Agach (RU)：86.1 / 85.6（+0.5） |

全部 21 個候選：差距中位數 +7.1 → **+0.8**、平均 +8.9 → +3.7、≥ 5 分的 13 個 → 5 個。0.1° 分數和 1 km 子格分數變得一致，這是遮水體最主要的效果。Gale、Protonilus 第 1 名的差距還很大（+10.0、+13.5），原因沒有查（Protonilus 那一格本身有湖）。

### 13.6 `WEB_EXPORT.md` 新舊差別

**檢查表**（網頁自己的評分程式；舊版 17:09、新版 11/15 00:2x 用 pulp 4.2.0 補跑；只用 28 個有火星特徵值的候選，τ = 0.7）。每格是「總分第 1 名（分數）／最少地點（地點）／無法覆蓋」，「候選」= 百分位母體用候選本身（網頁現在），「全球」= 全球分位數（本隊建議）。

current（網頁現在的定義）：

| 目標 | 母體 | 舊 | 新 |
|---|---|---|---|
| AP-105 | 候選 | Zuogaiduoma 附近（0.52）／1（MDRS Hanksville）／R2–R5 | Jisegumen 以東 120 km（0.47）／2（南極 74.3°S、Hoit Taria 以東 78 km）／R2–R5 |
| AP-105 | 全球 | Zuogaiduoma 附近（0.53）／1（Zuogaiduoma）／R2–R5 | Mori 以東 113 km（0.50）／1（Jisegumen 以東 120 km）／R2–R5 |
| Jezero | 候選 | Zuogaiduoma 附近（0.52）／1（南極 74.3°S）／R2–R6 | Zuogaiduoma 附近（0.43）／2（Zuogaiduoma、Sultanah 以東 147 km）／R2–R5 |
| Jezero | 全球 | Zuogaiduoma 附近（0.53）／1（Zuogaiduoma）／R2–R5 | Zuogaiduoma 附近（0.50）／2（南極 82.2°S、Sultanah 以東 147 km）／R2–R5 |
| Gale | 候選 | Zuogaiduoma 附近（0.54）／1（Zuogaiduoma）／R2–R5 | Zuogaiduoma 附近（0.43）／2（Zuogaiduoma、Khapalu 以東 118 km）／R2–R5 |
| Gale | 全球 | Zuogaiduoma 附近（0.56）／1（Zuogaiduoma）／R2–R5 | Zuogaiduoma 附近（0.52）／1（Zuogaiduoma）／R2–R5 |

proposed（套用本隊建議的任務定義）：

| 目標 | 母體 | 舊 | 新 |
|---|---|---|---|
| AP-105 | 候選 | Jisegumen 以東 64 km（0.52）／2（Talnakh 以東 272 km、南極 74.3°S）／R2、R6 | Jisegumen 以東 120 km（0.52）／2（Talnakh 以東 260 km、南極 82.2°S）／R2、R6 |
| AP-105 | 全球 | A'yi Take 以東 79 km（0.64）／2（Talnakh、Khapalu）／R2 | Kosh-Agach 附近（0.59）／2（Talnakh、Khapalu）／R2 |
| Jezero | 候選 | Aswan 以東 38 km（0.47）／1（Aswan）／R2、R3、R5、R6 | Torghay 以東 167 km（0.47）／1（Torghay）／R2、R3、R5、R6 |
| Jezero | 全球 | Aswan 以東 38 km（0.47）／2（Aswan、Khapalu）／R2、R3、R5 | **73.5°N 95.3°W（Gjoa Haven 以北 548 km）（0.46）**／2（同一點、Khapalu）／R2、R3、R5 |
| Gale | 候選 | Aswan 以東 38 km（0.47）／1（Aswan）／R2、R3、R5、R6 | Torghay 以東 167 km（0.47）／1（Torghay）／R2、R3、R5、R6 |
| Gale | 全球 | Aswan 以東 38 km（0.47）／2（Aswan、Khapalu）／R2、R3、R5 | **73.5°N 95.3°W（0.46）**／2（同一點、Khapalu）／R2、R3、R5 |

- 「各任務最高分」新舊大致相同：R1 都是 1.00；R6 在 current 0.74–0.98（舊 0.68–0.97）、proposed 0.33–0.94（舊 0.33–0.93）；proposed 的 R4 都是 0.95–1.00。
- **最少地點**：current 從每個目標 1 個變成多數 2 個；proposed 不變（1–2 個）。
- **無法覆蓋**：只有 current 的 Jezero（候選母體）從 R2–R6 變成 R2–R5（R6 現在能覆蓋），其他不變。
- **第 1 名**：current 仍以 Zuogaiduoma 附近為主，總分從 0.52–0.56 降到 0.43–0.52；proposed 的 Jezero、Gale 全球母體第 1 名變成加拿大北極（73.5°N），和 13.4 第 3 點的 R4 問題同一個原因。Aswan 以東 38 km 這個候選已經不在新的 28 個裡。
- **候選（28 個，每個目標 × 測試取第 1、2 名）**：22 個目標 × 測試的位置裡有 16 個換了地點（相距超過約 150 km），6 個不變。主要變動：
  - Jezero R1：Jisegumen (CN)、Edd (ER) → Toksun (CN)、Mori (CN)
  - Jezero R4：Haines Junction (CA) 59.45°N、Iskateley (RU) 72.35°N → Gjoa Haven (CA) 以北 73.55°N、74.65°N
  - Gale R1：A'yi Take (CN)、Jiajuedibu (CN) → Ocucaje (PE)、Khur (IR)
  - Gale R4：Torghay (KZ)、Aswan (EG) → Jisegumen (CN)、Torghay (KZ)
  - AP-105 R1：Bhuj (IN)、Antofagasta de la Sierra (AR) → Xitieshan (CN)、Sidi el Hani (TN)
  - AP-105 R3：第 1 名換成南極 82.25°S, 163.25°E，舊第 1 名（74.35°S, 163.45°E）變第 2 名；舊第 2 名（73.05°S, 66.55°E）掉出
- 交給網頁組的打包：`_handoff/handoff_web_1115.zip`（50 個檔；11/15 補跑 `--check` 後重新打包）。

### 13.7 限制（要寫在對外說明裡）

- 全球地表溫度平均期間是 **2020–2024**；備份（舊）是 2015–2024。新舊比較同時含「遮水體」和「年份範圍」兩種差異，不能全部歸因給遮罩。
- 放大程式（1 km）仍用 **2015–2024**，和全球的 2020–2024 不一致。全球新舊差中位數 0.4 K，預期影響很小，但要註明。
- **每月地表溫度是推算值**：年均來自新資料，季節形狀來自舊資料（2015–2024，金字塔取樣）。湖邊、海岸格的舊季節幅度偏小，新舊差超過門檻的 147,980 個陸地格（6.9%）設成空值，R5／R6 的季節特徵對它們不評分。**R5／R6 的季節測試是近似值**，其他測試不受影響。
- 反照率、NDVI、乾燥指數在南極是空值（抓的時候南極修正還沒做）。現在的計分用不到；要補的話清單在 `data/interim/rerun_1114_tools/antarctic_tiles.log`（308 塊）。
- 近水排除用的 MOD44W 是舊的水體圖；新出現或擴張的湖（例如 13.4 第 6 點）排除不到。

### 13.8 還沒解決、建議（都沒有改，要你決定）

1. **Jezero R4 仍以北極為主**（13.4 第 3、4、5 點）。可選：(a) 接受，北極荒漠本來就是岩石裸露的地方，Haughton 隕石坑就在附近；(b) R4 加溫度或緯度條件；(c) 把 `summer_barren` 的滿分門檻從 0.15 調低。這是方法決定。
2. **放大的近水排除漏掉 Jezero／Oxia 第 1 名旁邊的湖**（13.4 第 6 點）。建議改用較新的水體資料（例如 JRC Global Surface Water），或排除「1 km 日溫差遠低於方框中位數」的子格。
3. **網頁 `--check` 要 pulp 4.2.0（已補跑）**：pulp 4 要 Python ≥ 3.12，所以用另外的 venv 跑：`C:\Users\plusl\.venvs\nasa_webcheck\Scripts\python.exe scripts\export_web_seed.py --web-seed ..\..\nasa-main\data\seed --check`。之後要重跑也用這個 venv；`nasa_hackathon` 維持 pulp 3.3.2（`make_set_cover.py` 用它，雲端測過 3.3.2 和 4 結果相同）。
4. ArcticDEM V3 已被 V4 取代，改 `gee_zoom.py` 的資產名稱即可（資料版本改變，所以先列在這裡）。
5. Jezero、Oxia 第 1 名那一格（37.45, 93.95）在真彩色底圖上有矩形格線，看起來像人工鹽田（沒查證）。如果是，要不要排除人工地物也是方法決定。
6. `docs/DATA_SOURCES.md` 已新增；第 4 節列了程式註解裡沒有的引用（MERRA-2 兩處 DOI 不一致、ESA CCI 永凍土 DOI、REMA、Sentinel-1、PALSAR-2、GEE 平台、軟體），要補。
7. 收尾：
   - 朋友電腦上的 GEE 憑證和 `hatrefish_gee` 資料夾：使用者決定**先不刪**（11/15）。要刪時見 `PROMPT_run_1114_night.md` 第 5 節；所有 GEE 步驟做完後到 Google 帳號撤銷 Earth Engine 授權。
   - `run_1114/1_start_download.cmd` 第 2/4 步已改（11/15）：`tasklist | findstr` 換成 `powershell.exe -NoProfile -Command (Get-Process python -ErrorAction SilentlyContinue).Id`，輸出寫到 `%TEMP%\pyids.txt`，用檔案大小判斷有沒有 Python 在跑；ssh 連不上（exit 255）就停。UTF-8 無 BOM、CRLF。判斷邏輯在本機用不存在／存在的行程測過；朋友電腦當時連不上，沒有實際跑過。改之前的版本：`data/interim/rerun_1114_tools/1_start_download.before_fix.cmd`。
   - `run_1114/2_status.cmd` 也用 `tasklist`（在朋友電腦上會出錯），沒改。
8. 第 11.5 節其他待辦（缺岩性佔便宜、門檻型測試很多同分、R2 無法評估等）都還在。
