# 給 Claude Code 的任務：重抓全球資料並重跑全部（11/14 傍晚）

你在 `nasa\hatrefish\` 工作（NASA Space Apps 2026，火星組 B）。程式已在雲端改好（見 `docs\WORKLOG_B_1114.md` 第 12 節），**這次的工作是在本機重抓 GEE 資料、重跑所有結果、比較前後差異、更新文件數字**。全程自主完成，不要停下來問；判斷不確定時選合理的做法，並寫進工作紀錄。

## 0. 先讀
- `docs\WORKLOG_B_1114.md` 第 11、12 節。
- 這次改過的程式：`src\mars_analog\adapters\earth\gee_layers.py`（`land_mean_on_grid`、`glo30`）、`_gee.py`、`gee_extra.py`、`gee_zoom.py`、`src\mars_analog\mission_tests.py`、`config\mission_tests.yaml`、`src\mars_analog\export.py`、`src\mars_analog\zoom.py`、`scripts\fetch_earth_gee.py`、`scripts\fetch_earth_extra_gee.py`。

## 1. 先備份（之後的前後比較都用這份）
把下面複製到 `data\interim\before_1114pm\`（保持子資料夾結構）：
- `data\interim\earth_0p1\` 裡的 `lst_day_c`、`lst_night_c`、`dtr_c`、`lst_mean_c`、`albedo`、`ndvi_mean`、`aridity_index` 共 7 個 `.npy`
- `data\processed\` 的 `earth_grid.parquet`、`earth_reference_pct.json`、`earth_monthly.parquet`、`earth_extra.parquet`
- 整個 `outputs\profiles\`、`outputs\mission_tests\`、`outputs\zoom\`，以及 `outputs\` 根目錄的 `mars_*.json`、`summary_tables.md`、`new_candidates.md`、`validation_report.json`
- `config\weights_learned.json`

## 2. 依序執行（每一步看輸出，有問題先修再往下）
先 `conda activate nasa_hackathon`，在 `hatrefish\` 底下。

1. **檢查新抓法**
   ```
   python scripts\fetch_earth_gee.py --test --only lst albedo ndvi aridity --at 48.05 92.95
   python scripts\fetch_earth_gee.py --test --only lst albedo ndvi aridity
   ```
   - 第一行是 Jezero 剖面第 1 名那一格（大湖盆地湖邊）。中心格日溫差應該從舊的 8.6 K 變成接近放大程式的 1 km 值（約 20 K）；「東西相鄰相同」的比例應該明顯下降。
   - 第二行是 Atacama，數值應該和舊的差不多（那裡沒有湖）。
   - 不符合就查原因再往下。
2. **全球重抓**：`python scripts\fetch_earth_gee.py --only lst albedo ndvi aridity`
   - 可能比凌晨久（格內平均比較重）。逾時太多就把 `fetch_earth_gee.py` 裡這幾層的區塊再改小。
   - 最後檢查缺值比例有沒有比舊陣列多；多很多就找出失敗的塊重抓。
3. **重組全球網格**：`python scripts\run_pipeline.py --stage grid`
   - 檢查東西向相鄰格完全相同的比例：地表溫度、NDVI 原本約 22%，應該降到個位數。
   - 回報 Jezero 第 1 名那一格（48.05, 92.95）的日溫差、年均溫、NDVI 新舊值。
4. **補資料**
   ```
   python scripts\fetch_earth_extra_gee.py --test --only lst aster ndvi
   python scripts\fetch_earth_extra_gee.py --only lst aster ndvi --refresh
   ```
   - 每月地表溫度改了抓法、ASTER 加了範圍檢查，`ndvi_p90` 是新的一層。
   - `--test` 的 ndvi 用加拿大北極凍原檢查：夏季 NDVI（`ndvi_p90`）應該明顯高於年平均。
5. **重跑剖面與測試**：`python scripts\make_profiles.py`、`python scripts\make_mission_tests.py`
   - 測試總表開頭不能有「待補資料」。
   - Jezero 的 R4 前 20 名，北緯 60° 以北的個數應該從 19 個明顯下降。
   - 看 `outputs\profiles\board_*.png`（每個面向、每個變數各自的前 5 名）：每格都有 5 個地點、底下文字沒有被裁掉。
6. **放大**
   ```
   python scripts\zoom_candidates.py --test
   python scripts\zoom_candidates.py --top 3 --refresh
   ```
   - 地形改用新版 DEM，候選地也可能變了，所以要 `--refresh`。
   - 看幾張圖，確認最佳小區沒有貼著湖岸。
   - 舊候選留下的 `zoom_*.png`（名字不會被新結果覆蓋的）移到 `outputs\zoom\_old_1114\`。
7. **任務版不用跑**：11/14 決定任務導向只用測試項目 R1–R6，任務版（`run_pipeline.py` 的 learn、validate、crosscheck、export、figures 與 `summarize_results.py`）停用，程式保留備查。
   - 也不要用 `--stage all`：它會重組網格、又會跑任務版。
8. **給網頁整合的資料**（main 分支已經 checkout 在 `C:\Users\plusl\nasa-main`）
   ```
   pip install "pulp[cbc]"
   python scripts\export_web_seed.py --web-seed ..\..\nasa-main\data\seed --check
   ```
   - 用重跑後的 `candidate_pool.csv` 重新挑候選、重新填值，覆蓋 `outputs\web\`。
   - `--check` 會用網頁自己的評分程式跑一次；`pulp` 裝不起來就先不加 `--check`，在紀錄裡寫原因。
   - 對照 `outputs\web\WEB_EXPORT.md` 的候選清單：Jezero R4 不應該再有北緯 70° 以北的地點。

## 3. 前後比較（用第 1 步的備份）
寫一個比較腳本（放在 `scripts\` 以外的地方，例如 `data\interim\before_1114pm\compare.py`），比較：
- 類比剖面：每個目標整體前 20 名，第 1 名新舊、前 20 名在 150 km 內的重疊數；舊前 20 名裡「格內或相鄰格水體 > 10%」的有幾個、新的有幾個。
- 測試：每個目標 × 測試的第 1 名新舊。
- 放大：每個目標第 1 名的「0.1° 原分數」和「1 km 中位數」的差距，新舊各多少（湖修好後差距應該變小）。

## 4. 規則
- 只准修小錯（GEE 記憶體、逾時、區塊大小、波段名、圖的版面）。方法或門檻要改的，寫進紀錄的「建議」。
- 不改 `IanChen\` 裡的任何檔案；不 commit、不 push；不動 GEE 登入設定。
- 要刪除的檔案改成移到 `_to_delete\`。

## 5. 做完
1. 在 `docs\WORKLOG_B_1114.md` 末尾加「## 13. 重抓全球資料與重跑（Claude Code，11/14）」：每一步的時間、錯誤與修法，第 3 節的前後比較表，還沒解決的問題。
2. 任務版已停用：`docs\WORKLOG_B_1114.md` 第 6.5 節和 `docs\WEIGHTS_EXPLAINED.md` 不用更新。
3. 如果 `docs\NEW_TARGETS_AND_ZOOM.md` 第 2 節提到的地名或數字變了，也一起更新。
4. 第 13 節也記下第 2 節第 8 步 `WEB_EXPORT.md` 檢查表的新舊差別（各目標第 1 名、最少地點、無法覆蓋的任務）。
