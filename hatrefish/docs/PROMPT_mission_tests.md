> **11/14 15:20 更新：這份已由 Claude（雲端）照做完成，不用再交給 Claude Code。** 實作和這份規格不同的地方記在 `docs/WORKLOG_B_1114.md` 第 10 節；本機還要跑的 GEE 部分見 `docs/PROMPT_local_gee_runs.md`。

# 給 Claude Code 的任務：火星測試項目 R1–R6 的分數與排名（先不做集合覆蓋）

你在 `nasa\hatrefish\` 工作（NASA Space Apps 2026，火星組 B）。全程自主完成，不要停下來問；判斷不確定時選合理的做法，並寫進工作紀錄。

## 0. 先讀
- `nasa\docs\總覽.pdf`、`nasa\docs\火星.pdf`（整合者 Harris 的規劃）：R1–R6 的定義、特徵、門檻、ROC 權重，以及需求矩陣欄位（總覽第三節）。用 pdftotext 或 PDF 工具讀。
- `docs\PROJECT_CONTEXT.md`（3.4 類比剖面、3.5 缺資料規則）、`docs\WORKLOG_B_1114.md` 第 8–9 節、`docs\NEW_TARGETS_AND_ZOOM.md`。
- 程式：`src\mars_analog\similarity.py`（`similarity_vector`、`ice_target`）、`profiles.py`（`score_table`、`_record`、`_annotate`、`dim_map`、配色、`known_profiles`）、`novelty.py`（`distinct_sites`、`place_name`、`haversine_km`）、`config.py`、`config\features.yaml`、`config\dimensions.yaml`。
- 資料：`data\processed\earth_grid.parquet`（全球 0.1° 陸地格，坡度只有格內中位數）、`mars_targets.json`（6 個目標）、`mars_reference_pct.json`（火星 TES 熱慣量 101 個分位數）、`data\labels\known_analogs.csv`。

## 1. 要做什麼
對每個火星目標 × 每項測試（R1–R6），算全球每個 0.1° 陸地格的測試分數（0–1），並做排名。這次**不做集合覆蓋**，但要輸出候選池給下一步用。

## 2. 設計（照做；有更好的理由可以調整，但要寫進紀錄）
1. 新檔：`config\mission_tests.yaml`、`src\mars_analog\mission_tests.py`、`scripts\make_mission_tests.py`，輸出在 `outputs\mission_tests\`。檔名不要用 `test_` 開頭（pytest 會誤收）。
2. 特徵分數有兩種：
   - (a) 沿用 `similarity_vector` 的單項相似度 `s_<變數>`（和火星目標值比）。
   - (b) 新的門檻型滿意度函數（Derringer–Suich 梯形，線性）：`smaller_is_better(full_at, zero_at)`、`larger_is_better(zero_at, full_at)`。
3. 測試分數 ＝ 測試內特徵的加權幾何平均（預設等權重，下限 0.01，同 profiles 的 EPS）。每個特徵標 `required`：
   - `required` 的特徵缺資料 → 該格這項測試不評分（NaN），不准用其他特徵補。
   - `optional` 的特徵有資料才納入。
4. 適用性：R3、R5 只對有冰的目標適用（`ice_target(target) > 0`，即 SWIM Ci > 0）。不適用的目標輸出 `not_applicable` 並寫原因。
5. 各測試的定義（門檻數值寫在 yaml，可調）：
   - **R1 著陸地表條件**
     - `slope`：smaller_is_better，full_at 5°、zero_at 15°，required。SkyFall 寫 100 m 坡度 < 5–15°（待定），規劃建議先取 15°。限制：地球端是 200 m 坡度在 0.1° 格內的中位數。另外回報 zero_at = 10° 時前 20 名的重疊程度（敏感度）。
     - `roughness`：`s_roughness`，required。
     - `thermal_inertia`：火星門檻是 > 100（最好 > 150），只能比相對排名。用火星 TES 分位數把 100、150 換成火星百分位 p100、p150；地球 `ati_pct` ≤ p100 → 0，≥ p150 → 1。required。
     - `barrenness`：`s_barrenness`，optional。
     - 列為無法評估：1–5 m 坡度、岩石高度與覆蓋率、雷達粗糙度。
   - **R2 視覺導航**：全球網格沒有影像紋理和沙丘比例，整項標 `not_evaluated`，原因寫「需要 Sentinel-2 紋理，留到放大階段」。不要自己編代理。
   - **R3 淺層地下冰**（只對有冰的目標）。這裡測的是「有沒有冰可以偵測」，不是比 Ci 機率。
     - `permafrost`：larger_is_better，作用在 `permafrost_frac`，zero_at 0.1、full_at 0.9，required。
     - `cold`：smaller_is_better，作用在 `lst_mean_c`，full_at −2 °C、zero_at +2 °C，required。
     - `dryness`：`s_aridity`，optional。南緯 60° 以南乾燥指數是空值，設 optional 才不會把南極乾谷排除。
     - 列為無法評估：多邊形地、地下雷達、3–5 m 深度。
   - **R4 含水礦物**（代理）
     - `lithology`：`s_lithology`，required（GLiM 大類對照，含 oxia、meridiani 的文獻覆寫）。
     - `barrenness`：optional。
     - 寫清楚 R4 只是岩性大類的代理，很粗；光譜比對（CRISM/OMEGA 對 EMIT/ASTER）列為無法評估。
   - **R5 冰緣地形**（代理，只對有冰的目標）
     - `permafrost`、`cold`（同 R3），required。
     - `slope`、`roughness`：用 `s_slope`、`s_roughness`，required。
     - `barrenness`：optional。
     - 列為無法評估：多邊形尺寸、冰河分布。
   - **R6 沙塵與近地表氣象**
     - `dust`、`temperature`、`diurnal_range`：用 `s_dust`、`s_temperature`、`s_diurnal_range`，全部 required。R6 本來就包含溫度日變化，所以這裡納入；類比剖面的環境面向維持不納入。
     - 季節時間序列列為無法評估，目前只比年平均。
6. 測試之間的權重：yaml 記下 Harris 的 ROC 權重（R1 0.408、R3 0.242、R6 0.158、R2 0.103、R4 0.061、R5 0.028）和等差權重（0.286、0.238、0.190、0.143、0.095、0.048）。這次只輸出「參考用加權總分」：對可評估、適用的測試重新正規化後做加權幾何平均。主要結果是每項測試自己的排名。
7. 排名規則（同類比剖面）：
   - 每個目標 × 測試取前 20 名，地點彼此至少相距 150 km，只用該測試可評分的陸地格。
   - 每筆附上：測試分數、各特徵分數、地球值對火星值或門檻、breaks（特徵分數 < 0.3）、是否為已知類比地（50 km 內）、最近的已知類比地與距離、地名、Worldview 連結、該格的類比剖面整體相似度（參考用）。
8. 分布統計：每個目標 × 測試記下可評分的陸地格數，以及分數 ≥ 0.8、≥ 0.9 的陸地面積比例（下一步選門檻 τ 時用）。
9. 已知類比地檢查：
   - 每個已知類比地在每項測試的分數（半徑內中位數）和全球前百分比。
   - 把 `known_analogs.csv` 的 missions 對到測試：landing → R1、rover → R1、isru_base → R3、geology → R4／R5。看標了該任務的類比地是否排在前面。這只是檢查，不是正式驗證。
10. 候選池（給下一步的集合覆蓋）：取所有「目標 × 測試」前 200 名（彼此 ≥ 50 km）的聯集，每列一個格子。欄位：`cell_id`、`lat`、`lon`、地名、已知類比地標記，以及每個「目標 × 測試」的分數 `S_<目標>_<測試>`。不適用或不可評分的留空。

## 3. 選做：新增 SkyFall 設計參考著陸點 AP-105（30 分鐘內做不完就跳過，寫進紀錄）
- 座標：北緯 43.3295°、東經 198.5228° → `lon = −161.4772`；半徑 50 km（SkyFall 著陸橢圓 100 × 25 km）；missions `[landing, isru_base]`；id `ap105`。source 寫「座標取自 nasa/docs/火星.pdf（SkyFall 任務資訊包），原始文件待補」。
- 用 IanChen 的擷取程式抽值：`nasa\IanChen\scripts\run_task_a.py point 43.3295 -161.4772 50`，或 `mars_features.build_targets`。
  - 原始資料的下載位置見 `IanChen\docs\DATA_SOURCES.md`，放在 `IanChen\data\raw\mars\{tes,swim,sim3292}`。
  - 不要改 IanChen 的程式碼。
- 這台電腦有 Norton HTTPS 掃描：
  - Python 用 truststore。
  - GDAL 讀遠端 DEM 前，先跑 `python scripts\make_ca_bundle.py` 產生 PEM，再把環境變數 `GDAL_CURL_CA_BUNDLE` 指向它。`CURL_CA_BUNDLE` 對 rasterio 內建的 GDAL 無效。
- 先重抽 Jezero（18.4, 77.5, 25），確認和 `mars_targets.json` 完全一致，再抽 AP-105。合併進 `data\processed\mars_targets.json`，合併前先備份到 `data\interim\`。
- Deuteronilus、Phlegra 等其他 SkyFall 區還沒有具體座標：不要自己編，紀錄為待補。

## 4. 輸出
- `outputs\mission_tests\TEST_SUMMARY.md`（中文，給組員看）。每個目標一節，內容：
  - 哪些測試適用、不適用、無法評估
  - 每項測試的前 10 名表
  - 分布統計
  - 已知類比地檢查
  - 限制
- `outputs\mission_tests\<目標>_tests.json`。
- `outputs\mission_tests\requirement_matrix.csv` 和 `.md`：照總覽第三節的欄位（目標地點、測試代號、特徵、目標值或門檻、特徵類型、行星端資料、地球端資料、特徵權重），從 yaml 和目標值自動產生，交給整合者。
- `outputs\mission_tests\candidate_pool.csv`。
- 圖：每個目標一張小多圖，每個可評估的測試一格全球分數地圖，標出前 5 名。沿用 `profiles.py` 的配色與 `dim_map` 風格。

## 5. 驗證（做完這些才算完成）
- 滿意度函數邊界檢查：x = full_at → 1，x = zero_at → 0，中點 → 0.5，NaN → NaN。另外挑一個格子手算一項測試分數，和程式結果核對。
- 合理性：
  - R3 前幾名應該在永凍土、年均溫 < 0 °C 的地方。
  - R1 前幾名的坡度應該 < 5°。
  - Jezero 的 R6 前幾名，應該和類比剖面「大氣與沙塵」面向的前幾名大致重疊。
  - 不合理的話：查原因並修好，或寫進限制。
- 回報每項測試前 20 名中，optional 特徵缺資料的筆數，以檢查「缺資料反而佔便宜」的問題。
- 重跑 `python scripts\make_profiles.py`，確認類比剖面的數字沒有變。這次只能新增，不能改壞既有流程。

## 6. 規則
- 先 `conda activate nasa_hackathon`，在 `hatrefish\` 底下工作。這次不需要 GEE。
- 不改 `IanChen\` 裡的任何檔案；不 commit、不 push；不動 GEE 登入。
- 要刪除的檔案改成移到 `_to_delete\`。
- 做完要更新兩份文件：
  - 在 `docs\WORKLOG_B_1114.md` 末尾加「## 10. 測試項目分數（Claude Code，11/14 下午）」，寫：做了什麼、和上面設計不同的地方與理由、結果重點（每個目標每項測試的第 1 名）、限制、待辦（集合覆蓋、R2、其他 SkyFall 區座標）。
  - 在 `docs\PROJECT_CONTEXT.md` 加一小節「3.6 測試項目分數」：定義在哪、怎麼跑、輸出在哪。
