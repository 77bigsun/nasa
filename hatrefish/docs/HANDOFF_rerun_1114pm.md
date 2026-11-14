# 交接：重抓全球資料與重跑（PROMPT_local_rerun_1114.md）進行到哪裡

> 寫於 11/14 21:45（Claude Code）。使用者要求「先暫停、存檔、寫交接」。接手的 AI 請先讀完這份，再讀 `docs\PROMPT_local_rerun_1114.md`（任務定義）和 `docs\WORKLOG_B_1114.md` 第 11、12 節。
> **第 13 節還沒寫，文件數字還沒更新。** 本檔第 6 節是寫第 13 節要用的素材。

---

## 0. 一句話現況

PROMPT 第 2 節 **第 1 步完成**。**第 2 步（全球重抓四層）只差地表溫度**；第 4 步（補資料）**只差每月地表溫度**。這兩層正在朋友電腦上跑，已經**暫停，有存檔可續傳**。第 3、5、6、7、8 步和比較、文件都還沒做。

**注意：現在的資料是新舊混合，在地表溫度抓完之前，不要跑 `run_pipeline.py --stage grid`、剖面、測試、任務版、放大。**

| 檔案 | 狀態 |
|---|---|
| `data\interim\earth_0p1\albedo.npy`、`ndvi_mean.npy`、`aridity_index.npy` | ✅ 新抓法（遮水體＋格內平均），已補完失敗的塊 |
| `data\interim\earth_0p1\lst_day_c / lst_night_c / dtr_c / lst_mean_c.npy` | ❌ **還是舊的**（04:32，金字塔取樣，有湖面問題） |
| `data\interim\earth_0p1_extra\aster_qi/ci/mi.npy`、`ndvi_p90.npy` | ✅ 新的 |
| `data\interim\earth_0p1_extra\lst_m01…12.npy` | ❌ **還是舊的**（15:31） |
| `data\processed\earth_extra.parquet` | ✅ 新的（含新 ASTER、`ndvi_p90`、冰河） |
| `data\processed\earth_monthly.parquet` | ⚠️ 沙塵是對的，地表溫月平均是舊的 |
| `data\processed\earth_grid.parquet` | ❌ 舊的（還沒重組；和備份逐位元組相同） |
| `outputs\` 全部 | ❌ 都還是重抓前的結果 |

## 1. 備份（第 1 步，已完成）

- `data\interim\before_1114pm\`：PROMPT 第 1 節列的全部檔案（保持子資料夾結構，155 個檔）。另外加備份了 `outputs\web\`（第 8 步比較要用）。
- 備份裡各結果的產生時間不同，比較時要註明：
  - 剖面：15:13（雲端第 10 節版本）
  - 測試：16:31（雲端第 12 節，新程式＋舊資料，`summer_barren` 列為待補資料）
  - 任務版：15:59（Claude Code 第 11 節，export 還沒有信心度門檻）
  - 放大：15:50（第 11 節）
  - 網頁資料：17:09
- 比較腳本**已寫好**：`data\interim\before_1114pm\compare.py`（PROMPT 第 3 節的四張表）。用目前的檔案試跑過，可以正常執行。
  ```
  python data\interim\before_1114pm\compare.py --md data\interim\before_1114pm\compare_out.md
  ```

## 2. GEE 專案狀態（重要）

| 專案 | 狀態 |
|---|---|
| `nasa-spaceapp-hackathon` | 17:35 左右用完 Community 方案額度（每月 150 EECU 小時）→ Restricted Mode。**21:25 使用者升級成 Contributor（每月 1,000 小時），已恢復正常**。實測同時 8 塊都成功、沒有警告。**之後都用這個專案。** |
| `active-venture-430707-a8` | 組員的專案，使用者的帳號有 Service Usage Consumer＋Earth Engine Resource Viewer。在上面跑了 ASTER、夏季 NDVI 和補抓，**這個月額度也用完了（Restricted Mode）**，不要再用。 |

- Restricted Mode 的表現：每個專案大約只能同時跑 5 個請求，多的回 429「Exceeded Earth Engine concurrency limit. Your project is in Restricted Mode」；50×50 一塊地表溫約 57 秒。
- 額度用得快的原因：新抓法要讀每個 1 km 像素的 10 年影像，運算量是舊法的幾十倍；加上幾次中斷，全球地表溫已經白算了約 1.8 遍。

## 3. 朋友電腦（正在跑地表溫的地方）

- 連線：`ssh pypd@100.119.21.3`（Tailscale）。Windows，預設 shell 是 cmd。
  - PowerShell 要寫完整路徑：`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
  - 帳號沒有 CIM 權限，`Get-CimInstance` 會被拒；`Get-Process` 可以用。
- **沒有 scp／sftp**（Connection closed）。檔案改用 `data\interim\rerun_1114_tools\xfer.sh`（Git Bash 執行），透過 ssh 的標準輸入／輸出傳，用 SHA-256 核對，26 MB 約 4 秒：
  ```
  bash data/interim/rerun_1114_tools/xfer.sh pull '<遠端 Windows 路徑>' <本機路徑>
  bash data/interim/rerun_1114_tools/xfer.sh push <本機路徑> '<遠端 Windows 路徑>'
  ```
- 工作資料夾：`C:\Users\pypd\hatrefish_gee\`
  - `.venv\`：Python 3.11.18、earthengine-api 1.7.52、numpy 2.4.6
    - `uv venv` 會因 Windows RedirectionGuard（不受信任的掛接點）失敗，所以改用 uv 下載的 Python 直接 `-m venv`。
  - `src\mars_analog\`：只放了 `__init__`、`paths`、`adapters\__init__`、`adapters\earth\{__init__,_gee,gee_layers,gee_extra}.py`，都是含南極修正之後的版本。
  - `data\interim\earth_0p1\land_frac.npy`：切塊用的陸地遮罩
  - `remote_fetch.py`：可續傳的下載程式，每 2 分鐘把進度存到 `ckpt\<layer>\`，重跑同一行會自動接著抓（本機也有一份：`data\interim\rerun_1114_tools\remote_fetch.py`）
  - `logs\lst.log`、`logs\lst_m.log`
- **使用者的 GEE 登入憑證**存在 `C:\Users\pypd\.config\earthengine\credentials`。使用者同意用自己的帳號，權限範圍只有 `https://www.googleapis.com/auth/earthengine`。**全部做完後要刪掉**，並提醒使用者可以到 Google 帳號的「第三方存取權」撤銷。
- 暫停時的進度（21:42 存檔）：
  - 全球地表溫 `lst`：**206／1448 塊**
  - 每月地表溫 `lst_m`：**512／1448 塊**
  - 兩層都沒有失敗。朋友電腦上速度約每 100 塊 4–5 分鐘（`lst` 比較慢），兩層同時跑，估計還要約 40–60 分鐘。

### 3.1 接著跑（續傳）

在本機 Git Bash 各開一個背景指令（ssh 連線要保持著）：
```
ssh -o BatchMode=yes -o ServerAliveInterval=30 pypd@100.119.21.3 "cd /d C:\Users\pypd\hatrefish_gee && .venv\Scripts\python.exe -u -W ignore remote_fetch.py lst --project nasa-spaceapp-hackathon --workers 16 >> logs\lst.log 2>&1"
ssh -o BatchMode=yes -o ServerAliveInterval=30 pypd@100.119.21.3 "cd /d C:\Users\pypd\hatrefish_gee && .venv\Scripts\python.exe -u -W ignore remote_fetch.py lst_m --project nasa-spaceapp-hackathon --workers 16 >> logs\lst_m.log 2>&1"
```
- 開頭會印「resume: N tiles already done」。結束時印 `DONE lst: …/1448 tiles, failed …`，並把結果寫到遠端的 `data\interim\earth_0p1\` 和 `data\interim\earth_0p1_extra\`。
- 觀察到的現象：
  - ssh 正常結束時，裡面啟動的程式會被一起結束（`Start-Process` 也一樣）。
  - 但網路造成的「Connection reset by peer」之後，程式還活著，會繼續跑。
  - 想在遠端建排程工作（`schtasks`）讓它脫離 ssh 的要求，被 Claude Code 權限檢查擋下，不要繞過。
- 看進度：`ssh pypd@100.119.21.3 "type C:\Users\pypd\hatrefish_gee\logs\lst.log"`

### 3.2 抓完之後傳回本機

```
X=data/interim/rerun_1114_tools/xfer.sh
for b in lst_day_c lst_night_c dtr_c lst_mean_c; do bash $X pull "C:/Users/pypd/hatrefish_gee/data/interim/earth_0p1/$b.npy" data/interim/earth_0p1/$b.npy; done
for m in 01 02 03 04 05 06 07 08 09 10 11 12; do bash $X pull "C:/Users/pypd/hatrefish_gee/data/interim/earth_0p1_extra/lst_m$m.npy" data/interim/earth_0p1_extra/lst_m$m.npy; done
python scripts\fetch_earth_extra_gee.py --assemble      # 重組 earth_monthly.parquet、earth_extra.parquet
```
（遠端路徑用正斜線，Windows 上的 Python 和 PowerShell 都接受；在 bash 迴圈裡用反斜線容易跳脫錯，11/14 就因此把四個檔案寫成同一個 `earth$f.py`。）
- 每個檔案都要看到 `OK`，代表雜湊一致。
- 舊的 4 層地表溫在 `data\interim\before_1114pm\data\interim\earth_0p1\`。舊的每月地表溫只備份在 `before_1114pm\data\processed\earth_monthly.parquet`。
- 傳回後先檢查：
  - 缺值比例和舊陣列比（南極應該有值）
  - McMurdo（−77.2, 161.5）、Jezero 湖邊格（48.05, 92.95，日溫差應約 21.5 K）
  - `python data\interim\rerun_1114_tools\check_grid.py`（重組網格後跑，會印東西相鄰相同比例、Jezero 格新舊值）

## 4. 剩下的步驟（照 PROMPT，順序不要變）

本機一律先 `conda activate nasa_hackathon`，在 `hatrefish\` 底下。

1. **第 3 步** `python scripts\run_pipeline.py --stage grid`，再跑 `check_grid.py`。要回報：
   - 東西相鄰相同比例：地表溫、NDVI 原本約 22%，應降到個位數
   - Jezero 格的日溫差、年均溫、NDVI 新舊值
2. **第 4 步**：ASTER、`ndvi_p90` 已完成；每月地表溫抓回來後 `--assemble` 就完成。`--test` 已經跑過（見第 6 節）。
3. **第 5 步** `python scripts\make_profiles.py`、`python scripts\make_mission_tests.py`。檢查：
   - `TEST_SUMMARY.md` 開頭不能有「待補資料」
   - Jezero R4 前 20 名在北緯 60° 以北的個數，基準是 **19 個（70° 以北 15 個）**，應該明顯下降
4. **第 6 步** `python scripts\zoom_candidates.py --test`，再 `--top 3 --refresh`（預設專案就是已升級的 `nasa-spaceapp-hackathon`）。
   - 看幾張圖，確認最佳小區沒有貼著湖岸。
   - 舊候選留下、名字沒被新結果覆蓋的 `zoom_*.png` 移到 `outputs\zoom\_old_1114\`。
5. **第 7 步** 依序 `--stage learn`、`validate`、`crosscheck`、`export`、`figures`（**不要 `--stage all`**），再 `python scripts\summarize_results.py`。
6. **第 8 步** `python scripts\export_web_seed.py --web-seed ..\..\nasa-main\data\seed --check`
   - `pulp[cbc]` 3.3.2、`pydantic` 2.14.3、`httpx` 0.28.1 已裝進 `nasa_hackathon`（照 nasa-main 的 requirements；numpy、scipy 沒動）。
   - 這支程式只讀 `nasa-main`，`--check` 會把定義檔複製到暫存資料夾跑網頁的評分程式，不會寫回 `nasa-main`。
   - 對照 `outputs\web\WEB_EXPORT.md`：Jezero R4 不應該再有北緯 70° 以北的地點。舊版在 `before_1114pm\outputs\web\WEB_EXPORT.md`。
7. **比較**：跑 `compare.py`。
8. **文件**：
   - `WORKLOG_B_1114.md` 末尾加「## 13. 重抓全球資料與重跑（Claude Code，11/14）」
   - 更新第 6.5 節的表、`WEIGHTS_EXPLAINED.md` 的數字（只改數字和地名，每個改過的表下面加「11/14 傍晚重跑後更新」）
   - `NEW_TARGETS_AND_ZOOM.md` 第 2 節
   - 第 13 節還要記 `WEB_EXPORT.md` 檢查表的新舊差別（各目標第 1 名、最少地點、無法覆蓋的任務）
9. **收尾**：刪掉朋友電腦上的 GEE 憑證；工作資料夾 `C:\Users\pypd\hatrefish_gee\`（含 venv、ckpt）跟使用者確認後清掉，裡面還有一個傳檔失誤留下的 `src\mars_analog\adapters\earth$f.py`，可以一起刪。

**本機記憶體**：15.3 GB，執行中只剩約 1.8 GB 可用（WSL、Discord、瀏覽器佔不少）。之前兩個背景下載被 Claude Code 因記憶體不足自動停掉。依規則被停掉的工作不能自己重開，要使用者同意。重的步驟一次跑一個。

## 5. 這次改過的程式（都還沒 commit）

| 檔案 | 改了什麼 | 為什麼 |
|---|---|---|
| `scripts\fetch_earth_gee.py` | `lst` 50 px／24 平行；`albedo`、`ndvi` 75 px；`aridity` 50 px | 150 px 的地表溫一塊要 5 分多鐘、接近逾時，20 分鐘只完成 23 塊；50 px 一塊約 30 秒。乾燥指數見第 6 節「Can't transform」 |
| `scripts\fetch_earth_extra_gee.py` | `lst`、`aster`、`ndvi` 改 50 px／16 平行 | 改成格內平均後運算變重，原本 150–200 px 會逾時 |
| `src\mars_analog\adapters\earth\gee_layers.py` `water_at` | 南緯 60° 以南 MOD44W 沒資料時當陸地（原本當水） | **錯誤修正**：MOD44W 不涵蓋南極，新抓法把整個南極遮掉，McMurdo 的地表溫變空值。不修的話 R3 第 1 名等南極結果全部消失。和 earth_grid 的水體規則（只用在 −60° 以北）一致 |
| 同檔 `lst_climatology`、`albedo_climatology`、`aridity_index` | 加參數 `grid_mean=True`；False 時回傳原生解析度、不遮水體的影像 | **錯誤修正**：第 12 節改成直接回傳聚合到 0.1° 的影像，放大程式再投到 0.01° 時，每個 1 km 子格都只拿到所屬 0.1° 格的值 |
| `src\mars_analog\adapters\earth\gee_zoom.py` `climate`、`surface` | 改用 `grid_mean=False` | 同上，恢復第 11 節時放大程式的行為 |

全球版的預設值不變。上面兩個錯誤修正不在 PROMPT 允許的「小錯」類別裡，但都是第 12 節改動造成的連帶錯誤，不是方法改變，第 13 節要寫清楚理由。

## 6. 寫第 13 節要用的素材（時間、錯誤、修法、數字）

**第 1 步 新抓法檢查（16:35，各約 20 秒）**
- Jezero 剖面第 1 名那一格（48.05, 92.95，湖邊）新 vs 舊：
  - 日溫差 21.48 vs 8.61 K（放大程式 1 km 值 21.75）
  - 年均溫 4.82 vs 2.29 °C（1 km 4.77）
  - 白天地表溫 15.56 vs 6.60
  - NDVI 0.074 vs 0.033（1 km 0.076）
  - 反照率 0.264 vs 0.232
  - 乾燥指數 0.076 vs 0.075
  - 這個 10×10 塊的「東西相鄰相同」比例：舊 49% → 新 0%
- Atacama 10×10 中位數新 vs 舊：
  - 年均溫 26.42 vs 26.57
  - 日溫差 34.22 vs 34.09
  - NDVI 0.083 vs 0.081
  - 反照率 0.222 vs 0.220
  - 乾燥指數 0.0008 vs 0.0008
  - 結論：沒有湖的地方新舊一致
- 補資料 `--test`：
  - 每月地表溫 Atacama 1 月 30.67（舊 30.73）
  - ASTER 0.990／0.995／0.936
  - 加拿大北極凍原（68.6°N, 96°W）`ndvi_p90` 0.427，年平均 NDVI 0.084

**第 2 步 全球重抓的經過（16:36 → 暫停 21:42，還沒完成）**
1. **150 px 太慢**：16:36 用 150 px／12 平行開始，20 分鐘只完成地表溫 23／234 塊。實測 50×50 一塊 32 秒、75×75 一塊 441 秒（中間逾時重試）。改 50／75 px 重開，地表溫約 2 塊／分鐘 → 約 5 塊／分鐘。另外開一個行程先跑 NDVI＋乾燥指數，不讓它在反照率後面排隊。
2. **額度用完**：約 17:35，`nasa-spaceapp-hackathon` 進入 Restricted Mode，大量 429，連單一極小的請求都失敗。
   - 失敗的塊：地表溫 142、反照率 119、NDVI 104。
   - 使用者讓組員把帳號加進 `active-venture-430707-a8` 的 IAM（18:39 生效）。
3. **補抓**（用 `patch_tiles.py`）：
   - NDVI 104 塊：6 分鐘
   - 反照率 119 塊：14 分鐘
   - 乾燥指數改在新專案從頭抓：18 分鐘。最上排、最下排共 43 塊失敗，錯誤是「Can't transform (x, 0.0)」：請求範圍包含南北極點時，遮水體的換投影會失敗。
     - 北邊 19 塊改用 50 px 小塊（跳過沒有陸地的 85–90°N）補抓：79 小塊，44 秒。
     - 南極 24 塊不補：乾燥指數在南緯 60° 以南本來就設成缺值。
4. **檢查**（陸地 = `land_frac` > 0.5）：
   - NDVI 缺值 0.2841 → 0.2842，多 102 格空值（遮水體後整格都是水的湖岸格）。
   - 反照率和舊值相關 0.990，但南極 605,172 格變空值。那時南極修正還沒做，不過熱慣量要求乾燥指數 < 0.65，而乾燥指數在南極是缺值，所以**不影響計分**，沒有重抓。
   - 乾燥指數：北緯 75° 以上有值格 62,246 → 62,356，新舊相關 0.9993。
5. **舊專案上的全球地表溫卡死**：做到 1440／1448 後，CPU 不再增加、只剩 1 條連線（等一個不回應的請求），19:44 停掉。程式只在整層結束才存檔，1440 塊全丟。
6. **南極被當成水**（19:5x 發現）：新抓法在 McMurdo 的地表溫全是空值（舊值 −27.9 °C）。修 `water_at` 後是 −27.91 °C，蒙古湖邊格不受影響（日溫差仍 21.48）。同時發現放大程式拿到 0.1° 聚合影像的錯誤，一起修（第 5 節）。
7. **本機記憶體不足**：約 20:1x，新專案上的全球地表溫（約 600 塊）和每月地表溫（約 300 塊）被 Claude Code 因記憶體不足停掉，進度全丟。
8. **新專案也用完額度**：約 20:50 發現 `active-venture-430707-a8` 也進入 Restricted Mode。實測同時 6 塊只有 5 塊成功，每塊 30–76 秒。
9. **換到朋友電腦＋升級**：使用者同意在朋友電腦用自己的帳號，並把 `nasa-spaceapp-hackathon` 升級成 Contributor。21:29:45 開始兩層，21:42 暫停（見第 3 節）。

**第 4 步 已完成的補資料（新專案，18:41–19:46）**
- ASTER：36 分鐘，0 失敗。
  - 缺值 3.04% → 2.48%。
  - 超出 0.7–1.3 的格子：舊 692 → 新 0。
  - 新舊排名相關：QI 0.91、CI 0.93、MI 0.98。CI 的 Pearson 只有 0.055，是被舊的極端壞值拉低的；排除舊壞值後是 0.78。
- `ndvi_p90`：28 分鐘，0 失敗，缺值 0%。
  - 和年平均的差（中位數）：全部 +0.20、年均溫 < −5 °C +0.415、> 20 °C +0.12。
  - 北緯 55° 以北、年均溫 < −5 °C、年平均 NDVI < 0.1（看起來很荒）的格子共 51,356 個，其中夏季 NDVI ≥ 0.4（`summer_barren` = 0）的有 6,706 個，≤ 0.15（滿分）的有 9,173 個。

**其他**
- 第 8 步需要的套件已裝（第 4 節）。
- 網頁 main 分支在 `C:\Users\plusl\nasa-main`。

## 7. 還沒解決／要使用者決定的

- 全球地表溫、每月地表溫還沒抓完（朋友電腦，暫停中，可續傳）。
- 反照率、NDVI、乾燥指數在南極是空值（抓的時候南極修正還沒做）。現在的計分用不到；如果之後要南極反照率，要用修正後的程式補抓南緯 60° 以南的塊。清單：`data\interim\rerun_1114_tools\antarctic_tiles.log`，308 塊（50 px）。
- `active-venture-430707-a8` 這個月都會在限速模式，記得跟組員說一聲。
- 朋友電腦上的憑證和工作資料夾要清理（第 4 節第 9 點）。
- 第 11 節列的其他待辦（缺岩性佔便宜、門檻型測試很多同分、R2 無法評估等）都還在。

---

## 8. 22:10 改計畫：少抓一點（使用者決定，時間不夠）

**決定**：(1) 不再抓每月地表溫 `lst_m`，改用新的年均推算；(2) 全球地表溫 `lst` 的平均期間從 2015–2024 十年縮成 2020–2024 五年。

**為什麼**：剩 1,242 塊地表溫＋936 塊每月地表溫。每月地表溫只供 R5/R6 的季節特徵用，主分數不用它。五年的氣候平均仍是正常的氣候平均，運算量約減半。檢查過「只重抓有水的塊」沒用：1,448 塊裡 1,175 塊有至少一個混水格，只省 19%。

**帳**：舊作法剩 1,242 塊（lst）＋936 塊（lst_m）。新作法 lst 要從頭抓 1,448 塊，但每塊約一半運算，等於約 724 塊舊工作量，不再抓 lst_m。總工作量約少 66%。`ckpt\lst`（十年版的 206 塊）**不能接**，新程式用 `ckpt\lst_2020`，從 0 開始。

### 8.1 程式改動（已寫好，都還沒 commit）

| 檔案 | 改了什麼 |
|---|---|
| `src\mars_analog\adapters\earth\gee_layers.py` | `lst_climatology(grid_mean=True, start="2015-01-01")` 加 `start`；預設不變，放大程式照舊用十年 |
| `data\interim\rerun_1114_tools\remote_fetch.py` | 加 `--start`（預設 `2020-01-01`）；checkpoint 資料夾改成 `ckpt\lst_2020`；`lst_m` 不再使用 |
| `scripts\derive_monthly_lst.py`（新） | 新每月值 = 舊每月值 +（新年均 − 舊每月平均）；新舊年均差 > 1.5 K 或日夜差差 > 3 K 的格子設空值 |

`derive_monthly_lst.py` 用合成資料測過：平移後年均等於新年均、月與月的差保持不變、超過門檻的格子被遮掉。**還沒用真資料跑過**。

### 8.2 要做的事（照順序）

1. 把兩個改過的檔案傳到朋友電腦（本機 Git Bash）：
   ```
   X=data/interim/rerun_1114_tools/xfer.sh
   bash $X push src/mars_analog/adapters/earth/gee_layers.py 'C:/Users/pypd/hatrefish_gee/src/mars_analog/adapters/earth/gee_layers.py'
   bash $X push data/interim/rerun_1114_tools/remote_fetch.py 'C:/Users/pypd/hatrefish_gee/remote_fetch.py'
   ```
2. 只開 lst（**不要再開 lst_m**）：
   ```
   ssh -o BatchMode=yes -o ServerAliveInterval=30 pypd@100.119.21.3 "cd /d C:\Users\pypd\hatrefish_gee && .venv\Scripts\python.exe -u -W ignore remote_fetch.py lst --project nasa-spaceapp-hackathon --workers 20 >> logs\lst5.log 2>&1"
   ```
   開頭應印 `lst: 1448 land tiles, 1448 to fetch, …, workers 20`（不是 resume）。
   - 20 條：之前兩層各 16 條（共 32 條同時）跑過沒有失敗，現在只剩一層，20 條在那之內。log 出現 429（concurrency limit）就停掉，改回 `--workers 16` 重跑同一行，會從存檔接著抓。
3. 抓完只傳回 4 個檔案（第 3.2 節的 lst_m 迴圈跳過）：`lst_day_c`、`lst_night_c`、`dtr_c`、`lst_mean_c`。
4. `python scripts\run_pipeline.py --stage grid`，再 `python data\interim\rerun_1114_tools\check_grid.py`。
5. `python scripts\derive_monthly_lst.py`（看統計，遮掉的比例不該太大），沒問題再加 `--write`，然後 `python scripts\fetch_earth_extra_gee.py --assemble`。（`--assemble` 要用重組後的 `earth_grid.parquet`，所以在第 4 步之後。）
6. 接 PROMPT 第 5～8 步和比較。第 5 步 `make_mission_tests.py` 之後加跑 `python scripts\make_set_cover.py`（集合覆蓋，約 1 分鐘，讀新的 `candidate_pool.csv`）。

### 8.3 第 13 節要寫清楚的限制

- 全球地表溫平均期間是 2020–2024；備份（舊）是 2015–2024。新舊比較同時含「水體遮罩」和「年份範圍」兩種差異，不能全部歸因給遮罩。
- 放大程式（1 km）仍用 2015–2024，和全球的 2020–2024 不一致；差異預期很小，但要註明。
- 每月地表溫是推算值：年均來自新資料，季節形狀來自舊資料。湖邊／海岸格的舊季節幅度偏小，這類格子（新舊差超過門檻）被設成空值，R5/R6 的季節特徵對它們不評分。記下遮掉的格子數。
- R5/R6 的季節測試標為「近似」。其他測試不受影響。
- 朋友電腦上 `ckpt\lst`（十年版）、`ckpt\lst_m` 可在收尾時一起刪。

## 9. 集合覆蓋（22:55 加，11/14 晚）

- 新程式 `scripts\make_set_cover.py`：讀 `outputs\mission_tests\candidate_pool.csv`，用整數規劃（pulp＋CBC）找「最少幾個地球地點能讓每個（火星目標, 測試）都至少有一個合格地點」，再畫每多一個地點的邊際效益曲線。規則寫在程式開頭。
- 合格規則：分數 ≥ 0.9 × 該需求在候選池的最高分。不用固定門檻，因為各測試分數範圍差很多（舊資料 Jezero R6 最高 0.76）。
- 輸出 `outputs\set_cover\`：`SET_COVER.md`、`set_cover.json`、`marginal_all.png`。
- pulp 3.3.2（本機）和 pulp 4 結果相同，約 40–50 秒。
- **現在的 `outputs\set_cover\` 是用重抓前的候選池算的**（試跑）：27 個需求，最少 5 個地點，邊際曲線 14 → 20 → 24 → 26 → 27。換門檻時地點數 3–7、具體地點變動大（敏感度表），代表「要幾個地點」比「是哪幾個」穩。其中 Jezero R4 指派到加拿大北極（76.95°N），就是 `ndvi_p90` 還沒納入的舊問題，重跑後應該消失。
- 重跑後在第 13 節記：最少地點數、曲線、敏感度表新舊對照。

## 10. 一鍵執行的 .cmd（23:10 加）

`run_1114\` 裡的檔案依序執行（雙擊或在 cmd 裡打檔名）。每個都會在出錯時停下來，畫面和 log 存在 `run_1114\logs\`。

| 檔案 | 做什麼 | 什麼時候跑 |
|---|---|---|
| `1_start_download.cmd` | 測金鑰登入 → 檢查朋友電腦有沒有舊的下載還在跑 → 傳兩個改過的檔案（`OK` 才繼續）→ 開始下載（workers 20）。**視窗要一直開著**；中斷了重跑同一個檔會接著抓 | 現在 |
| `2_status.cmd` | 讀朋友電腦的 `logs\lst5.log`：進度、每分鐘幾塊、預估完成時間、有沒有 429；列出遠端的 Python 行程 | 下載中隨時 |
| `3_pull_and_grid.cmd` | 階段 A：確認下載完成且沒有失敗 → 傳回 4 個檔案 → 重組網格 → `check_grid.py` → `derive_monthly_lst.py`（只看統計）。log：`run_1114\logs\stageA.log` | 下載完成後 |
| `4_rest.cmd` | 階段 B：每月溫度寫檔 → `--assemble` → 剖面 → R1–R6 → 集合覆蓋 → 網頁資料 → 放大（先 `--test`）→ 舊放大圖移到 `_old_1114` → `compare.py`。網頁資料、放大、比較失敗不會中斷其他步驟，最後列出來。log：`run_1114\logs\stageB.log` | Claude 看過 stageA.log 之後 |
| `5_cleanup_friend.cmd` | 刪朋友電腦上的 GEE 憑證和 `hatrefish_gee` 資料夾（每項都先問） | 階段 A 確認沒問題之後 |

- `_env.cmd`：共用設定。用 Git 內附的 bash.exe 和 ssh.exe（不用 `bash`，因為那可能是 WSL 的）。Python：`%USERPROFILE%\miniconda3`，環境 `nasa_hackathon`。
- `helper.py`：只用標準函式庫。`eta` 讀下載 log，`run` 執行一步並同時寫 log，`move_old_zoom` 把舊的放大圖移走（不刪）。
- 這些 .cmd 沒有在 Windows 上實際跑過（Claude 在雲端寫的）；`helper.py` 用假 log 測過。
- 任務版（learn、validate、crosscheck、export、figures、summarize_results）照 PROMPT 第 7 步不跑。
