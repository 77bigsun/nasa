# PROMPT：11/14 夜間重跑（下載完成 → 階段 A → 階段 B → 打包交接 → 文件）

> 給本機 Claude Code。寫於 11/14 23:35（雲端 Claude）。
> 先讀這份，再讀 `docs\HANDOFF_rerun_1114pm.md` 第 8–10 節（背景、改計畫的理由、`run_1114\` 的檔案）。
> `docs\PROMPT_local_rerun_1114.md` 是原始任務定義；它第 2 節第 2–8 步的做法改成照這份。

## 0. 規則

- 工作目錄 `C:\Users\plusl\nasa\hatrefish`，Python 環境 `nasa_hackathon`（`conda activate nasa_hackathon`）。
- **不要 git commit／push**：比賽規則還沒確定程式能不能公開。
- **重的步驟一次只跑一個，不要平行。** 本機記憶體只剩約 2 GB，之前兩個背景工作因記憶體不足被停掉。被系統停掉的工作不要自己重開，先問使用者。
- 會超過 2 分鐘的步驟用背景執行，每 2–5 分鐘看一次 log。
- 每一步都用 `python run_1114/helper.py run <log> -- <script> <args...>` 執行。它會同時印到畫面和寫進 log，並回傳該步的 exit code。
  - 階段 A 的 log：`run_1114/logs/stageA.log`
  - 階段 B 的 log：`run_1114/logs/stageB.log`
- **不要執行 `run_1114\*.cmd`。** 裡面有 `pause`、`choice`，會等人按鍵，卡住你的 shell。下面列的指令就是同樣的步驟拆開來。
- 不要讀、不要複製使用者的 GEE 憑證。刪除朋友電腦上的憑證（第 5 節）要先問使用者。
- 不要跑任務版：`run_pipeline.py` 的 learn、validate、crosscheck、export、figures，以及 `summarize_results.py`，都不要跑。也不要用 `--stage all`。
- 遇到「停下來」的條件：把數字和 log 位置告訴使用者，等指示，不要自己繞過。

## 1. 等下載完成

全球地表溫度（2020–2024 五年平均，遮水體）正在朋友電腦上下載，預計 23:53 左右完成。是使用者開的 `1_start_download.cmd` 視窗在跑。**不要關那個視窗，也不要另外再開下載。**

看進度：
```
ssh -o ConnectTimeout=10 pypd@100.119.21.3 "type C:\Users\pypd\hatrefish_gee\logs\lst5.log" > /tmp/lst5.log
python run_1114/helper.py eta /tmp/lst5.log
```

依 exit code 處理：

| exit | 意思 | 做什麼 |
|---|---|---|
| 0 | 全部完成，沒有失敗 | 進第 2 節 |
| 2 | 還在跑 | 5 分鐘後再看 |
| 3 | 完成但有失敗的塊 | 停下來，請使用者重跑 `1_start_download.cmd`（只會補抓失敗的塊） |
| 4 | 讀不懂 log | 停下來，把 log 最後 20 行給使用者 |

- log 裡出現 429 或 concurrency：告訴使用者。
- 查遠端有沒有 Python 在跑（不要用 tasklist，在那台電腦上會出錯）：
  ```
  ssh pypd@100.119.21.3 "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -Command (Get-Process python -ErrorAction SilentlyContinue).Id"
  ```
  沒有完成、又沒有 Python 在跑：停下來告訴使用者。

## 2. 階段 A（約 30 分鐘）

1. **傳回 4 個檔案。** 舊檔已備份在 `data\interim\before_1114pm\`。每個檔案都要看到 `OK`。出現 MISMATCH 就重傳那一個；同一個檔連續兩次 MISMATCH，停下來。
   ```
   for b in lst_day_c lst_night_c dtr_c lst_mean_c; do bash data/interim/rerun_1114_tools/xfer.sh pull "C:/Users/pypd/hatrefish_gee/data/interim/earth_0p1/$b.npy" data/interim/earth_0p1/$b.npy; done
   ```
   遠端路徑要用正斜線。在 bash 迴圈裡用反斜線容易跳脫錯，11/14 就曾因此寫壞檔名。
2. **重組全球網格**（背景執行，10–20 分鐘）：
   ```
   python run_1114/helper.py run run_1114/logs/stageA.log -- scripts/run_pipeline.py --stage grid
   ```
3. **檢查網格：**
   ```
   python run_1114/helper.py run run_1114/logs/stageA.log -- data/interim/rerun_1114_tools/check_grid.py
   ```
4. **單格檢查。** 讀 `data/interim/earth_0p1/*.npy`，列 `iy = int((90 - lat) / 0.1)`，欄 `ix = int((lon + 180) / 0.1)`。舊值在 `before_1114pm` 裡同名的陣列。

   | 地點 | 座標 | 期望 |
   |---|---|---|
   | Jezero 湖邊格 | 48.05, 92.95 | `dtr_c` 約 21 K（舊 8.61；新抓法測試時 21.48），`lst_mean_c` 約 4.8 °C（舊 2.29） |
   | McMurdo | −77.2, 161.5 | `lst_mean_c` 有值，約 −28 °C，不能是 NaN |
   | Atacama | −24.1, −69.9 | 和舊值差不多（年均溫差 < 1 K） |

5. **每月地表溫度推算，只看統計、不寫檔：**
   ```
   python run_1114/helper.py run run_1114/logs/stageA.log -- scripts/derive_monthly_lst.py
   ```

**通過條件**：全部符合才進階段 B，任何一條不符就停下來，把數字給使用者。

- 地表溫度 4 層：陸地缺值比例比舊的增加不到 0.5 個百分點。
- 地表溫度 4 層：「東西相鄰相同」的比例明顯下降。原本約 22%，目標是個位數。
- `check_grid.py` 印出 `same cell ids: True`，列數不變。
- Jezero 湖邊格的 `dtr_c` 在 15–25 K。
- McMurdo 的 `lst_mean_c` 不是 NaN。
- `derive_monthly_lst.py` 被遮掉的比例 < 15%。

## 3. 階段 B（約 1.5–2 小時）

開始前先記下時間（第 8 步要用）：
```
python run_1114/helper.py mark run_1114/logs/stageB_start.txt
```

依序執行。每一步的指令都是 `python run_1114/helper.py run run_1114/logs/stageB.log -- <下表的指令>`。

| # | 指令 | 失敗時 | 跑完要檢查 |
|---|---|---|---|
| 1 | `scripts/derive_monthly_lst.py --write` | 停 | 印出 `written` |
| 2 | `scripts/fetch_earth_extra_gee.py --assemble` | 停 | `earth_monthly.parquet` 的缺值比例合理 |
| 3 | `scripts/make_profiles.py` | 停 | 打開 2–3 張 `outputs/profiles/board_*.png`：每格 5 個地點，底下文字沒被裁掉 |
| 4 | `scripts/make_mission_tests.py` | 停 | 見表下說明 |
| 5 | `scripts/make_set_cover.py` | 停 | 記下 `outputs/set_cover/SET_COVER.md` 的最少地點數、邊際曲線、敏感度表；Jezero R4 不應指派到 70°N 以北 |
| 6 | `scripts/export_web_seed.py --web-seed ../../nasa-main/data/seed --check` | 記錄後繼續 | `outputs/web/WEB_EXPORT.md`：Jezero R4 的候選不應有 70°N 以北的地點 |
| 7 | `scripts/zoom_candidates.py --test` | 記錄後跳過第 8 步 | 印出子格中位數，沒有錯誤 |
| 8 | `scripts/zoom_candidates.py --top 3 --refresh` | 記錄後繼續 | 會用 GEE，最久，用背景跑。看 3–4 張 `outputs/zoom/zoom_*.png`，最佳小區不應貼著湖岸 |
| 9 | `data/interim/before_1114pm/compare.py --md data/interim/before_1114pm/compare_out.md` | 記錄後繼續 | 產生 4 張新舊比較表 |

第 4 步要確認兩件事：
- `outputs/mission_tests/TEST_SUMMARY.md` 開頭不能有「待補資料」。
- `jezero_tests.json` 裡 R4 前 20 名在 60°N 以北的個數要明顯下降。基準是舊版 19 個（70°N 以北 15 個）。

第 6 步：`--check` 如果因為 pulp 之類的套件失敗，就不加 `--check` 再跑一次，並記下原因。

第 8 步跑完後（不論成功或失敗），執行：
```
python run_1114/helper.py move_old_zoom run_1114/logs/stageB_start.txt
```
它會把這次沒有覆蓋到的舊 `zoom_*.png` 移到 `outputs/zoom/_old_1114/`。是移動，不是刪除。

## 4. 打包交給網頁組

用 Python `zipfile` 做 `C:\Users\plusl\nasa\hatrefish\_handoff\handoff_web_1115.zip`，內容：

- `outputs/web/` 整個資料夾
- `outputs/set_cover/` 整個資料夾
- `outputs/profiles/`：`mars_*_profile.json`、`board_*.png`、`PROFILE_SUMMARY.md`
- `outputs/mission_tests/`：`*_tests.json`、`candidate_pool.csv`、`crosswalk_dimensions_tests.csv`、`TEST_SUMMARY.md`
- `outputs/zoom/`：`zoom_*.json`、`ZOOM_SUMMARY.md`
- `docs/OVERVIEW_PLAIN.md`

zip 裡保留原本的相對路徑。不要寄出，把 zip 的路徑和大小告訴使用者。

## 5. 收尾（每一項都先問使用者）

1. **刪朋友電腦上的 GEE 憑證和工作資料夾。** 確認階段 A、B 都不需要再從那台電腦抓資料之後，再問使用者：
   ```
   ssh pypd@100.119.21.3 "del C:\Users\pypd\.config\earthengine\credentials"
   ssh pypd@100.119.21.3 "rmdir /s /q C:\Users\pypd\hatrefish_gee"
   ```
   提醒使用者：要到 Google 帳號撤銷 Earth Engine 授權，等所有 GEE 步驟都做完再撤銷（包括放大）。撤銷後，本機的 Earth Engine 登入也會失效。
2. **修 `run_1114\1_start_download.cmd`。** 使用者確認下載視窗已經關掉之後，才能改這個檔：cmd 是一邊執行一邊讀批次檔，執行中改檔會讓它跑錯行。
   - 要改的地方：第 2/4 步的 `tasklist | findstr /i python`。
   - 改成和 `2_status.cmd` 一樣的寫法：用 `%PSC% (Get-Process python -ErrorAction SilentlyContinue).Id` 把結果寫到暫存檔，再看檔案大小判斷有沒有 Python 在跑。
   - 檔案要保持 UTF-8（無 BOM）、CRLF 換行。

## 6. 文件

1. **`docs\WORKLOG_B_1114.md` 末尾加「## 13. 重抓全球資料與重跑（11/14 晚）」。** 素材：
   - 經過與錯誤：HANDOFF 第 6 節（16:35–21:42）。
   - 改計畫的理由：第 8 節（五年平均、每月溫度用推算）。
   - 要寫清楚的限制：第 8.3 節。
   - 集合覆蓋：第 9 節。
   - 這次第 2、3 節各項檢查的數字。
   - `compare_out.md` 的 4 張表。
   - `WEB_EXPORT.md` 檢查表的新舊差別（各目標第 1 名、最少地點、無法覆蓋的任務）。舊版在 `before_1114pm\outputs\web\WEB_EXPORT.md`。
2. **`docs\PROMPT_local_rerun_1114.md` 第 5 節列的其他文件**照它寫的更新，例如 `NEW_TARGETS_AND_ZOOM.md` 第 2 節。任務版的文件（`WORKLOG` 第 6.5 節、`WEIGHTS_EXPLAINED.md`）不改。
3. **`docs\PROJECT_CONTEXT.md` 只改兩處：**
   - 第 3.2 節溫度那列註明「MODIS LST 2020–2024（11/14 晚起；放大程式仍是 2015–2024）」。
   - 第 3.6 節最後一點改成「集合覆蓋已做：`scripts/make_set_cover.py`，輸出 `outputs/set_cover/`」。
4. **新增 `docs\DATA_SOURCES.md`。** `PROJECT_CONTEXT` 第 10 節要求有這份，但它還不存在。
   - 從 `src\mars_analog\adapters\` 各檔開頭的引用註解整理，火星端和地球端都要。
   - 每個來源列：名稱、提供單位、網址或 DOI、引用格式、對應的官方入口（Earthdata、PDS、Copernicus 等）。
   - 地球端至少要有：MCD12Q1、MOD44W、GMTED2010、Copernicus GLO-30、MOD11A2／MYD11A2、MCD43A3、MOD13A2／MOD13Q1、Global Aridity Index v3、MERRA-2、ESA CCI Permafrost、GLiM、ASTER GED AG100、GLIMS、ArcticDEM、REMA、Sentinel-1、ALOS PALSAR、HLS。
   - 只寫程式裡實際有用到、而且有引用註解的。找不到引用的，列成待補，不要自己編 DOI。

## 7. 回報給使用者

全部做完（或中途停下）時，簡短列出：

- 每一步成功或失敗，log 在哪裡。
- 第 2 節的通過條件數字。
- 集合覆蓋：最少地點數、邊際曲線、敏感度。
- Jezero R4 在 60°N、70°N 以北的個數（新 vs 舊）。
- zip 的路徑。
- 還沒做的事（例如收尾的兩項還在等使用者回答）。
