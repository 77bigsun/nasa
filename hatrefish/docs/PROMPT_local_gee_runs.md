# 給 Claude Code 的任務：在本機跑 GEE 補資料、放大與重跑（11/14 下午）

你在 `nasa\hatrefish\` 工作（NASA Space Apps 2026，火星組 B）。程式都已經寫好、在雲端用合成資料測過，**這次的工作是在本機實際跑 Google Earth Engine 的部分、檢查結果、修小錯**。全程自主完成，不要停下來問；判斷不確定時選合理的做法，並寫進工作紀錄。

## 0. 先讀
- `docs\WORKLOG_B_1114.md` 第 8–10 節（今天做了什麼）、`docs\NEW_TARGETS_AND_ZOOM.md`、`config\mission_tests.yaml`。
- 程式：`scripts\fetch_earth_extra_gee.py`、`src\mars_analog\adapters\earth\gee_extra.py`、`scripts\zoom_candidates.py`、`src\mars_analog\zoom.py`、`src\mars_analog\adapters\earth\gee_zoom.py`、`scripts\make_mission_tests.py`。

## 1. 依序執行（每一步看輸出，有問題先修再往下）
先 `conda activate nasa_hackathon`，在 `hatrefish\` 底下。

1. `python scripts\fetch_earth_extra_gee.py --test`
   - 檢查：每月沙塵 `dust_m` 約 0.001–0.5；每月地表溫 `lst_m` 在 Atacama 約 5–35 °C；冰河 `glacier_frac` 在 Juneau 冰原 > 0；ASTER 指標 `aster_qi/ci/mi` 約 0.9–1.2。
   - 常見錯誤：
     - GLIMS 資產編號不對：查 Earth Engine 資料目錄的現行編號，改 `gee_extra.GLIMS_IDS`。
     - ASTER GED 波段名稱不同：`--test` 會印出波段名，照著改 `gee_extra.aster_indices` 的比對規則。
2. `python scripts\fetch_earth_extra_gee.py`（全球；可能要數十分鐘）
   - 結束時會自動產生 `data\processed\earth_monthly.parquet` 和 `earth_extra.parquet`。
   - 中斷就重跑同一行，會跳過已抓好的層。
   - 看最後印出的缺值比例；有整片塊失敗（NaN）就重跑那一層：`--only <層> --refresh`。
3. `python scripts\make_mission_tests.py`
   - 檢查 `outputs\mission_tests\TEST_SUMMARY.md` 開頭不再列「待補資料」。
   - R6：季節形狀分數不是全部擠在同一個值；回報每個目標 R6 第 1 名有沒有變。
   - R5：Protonilus 的 `glacier_distance` 有分數；前幾名在冰河附近。
   - R4：Jezero（碳酸鹽＋鎂鐵質）、Arcadia／AP-105（鎂鐵質）的 `mineral_signature` 有分數；同分的情況應該變少。
   - 冰河比例會併進「無冰覆蓋」：看 R1、R4 前幾名有沒有冰河格子。
4. `python scripts\zoom_candidates.py --test`
   - 檢查子格中位數和 0.1° 格的值大致一致。
   - 檢查有沒有底圖來源（HLS 或陰影圖），以及「地點細節」有坡度和雷達數值。
5. `python scripts\zoom_candidates.py --top 3`
   - 全部 7 個目標，每個目標前 3 名。
   - 看幾張 `outputs\zoom\zoom_*.png`：底圖、子格分數、面向比較三格都正常，沒有文字重疊。
   - 地點細節失敗的話，`ZOOM_SUMMARY.md` 會顯示「—」，原因記在 json 的 `site_details.error`。
6. `python scripts\run_pipeline.py --stage all`
   - 冰的算法 11/14 上午改過，任務版結果要重跑才會一致。

## 2. 規則
- 只准修上面列的程式裡的小錯（資產編號、波段名、逾時重試、圖的版面）。設計或門檻要改的話，寫進紀錄的「建議」，不要自己改。
- 不改 `IanChen\` 裡的任何檔案；不 commit、不 push；不動 GEE 登入設定。
- 要刪除的檔案改成移到 `_to_delete\`。

## 3. 做完
在 `docs\WORKLOG_B_1114.md` 末尾加「## 11. 本機 GEE 執行（Claude Code，11/14）」，內容：
- 每一步花多久、遇到什麼錯、怎麼修
- 補資料前後每個目標各測試第 1 名的變化
- 放大結果的重點（每個目標第 1 名的最佳 1 km 小區、它的高解析坡度 p90）
- 還沒解決的問題
