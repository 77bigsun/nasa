# Moon：月球南極基地的地球類比（最終版）

更新：2026-11-15 16:30（台北）｜Suicide Squad 月球組

## 怎麼看這個資料夾

| 路徑 | 給誰 | 內容 |
|---|---|---|
| `web/` | 網站（學長） | `moon_results.json`、`moon_global_grid.json`、`HANDOFF.md`、熱度圖。**網站只需要這個資料夾** |
| `月球類比_公式原理_月球篩選地_資料來源.pdf` | 隊友、評審 | 每個特徵的公式與原理、篩選流程、10 個月球地點與適配任務、所有資料連結 |
| `global/` | 隊友 | 全球掃描的全部結果與資料集 |
| `code/` | 隊友 | 所有計算程式，可重算每一步 |
| `results/`、`moon_reference/`、`earth_data/` | 參考 | 早期 12 個驗證點、M5（已刪除）的資料 |
| `archive/` | 參考 | 已被取代的舊版結果 |

## 方法摘要

- **任務**：M2 低太陽角光照、M3 長時間黑暗與極寒、M4 陡坡地形、M6 冷陷冰資源。M1、M5 已刪除。
- **呈現**：每個任務各自排名；每個月球候選基地列出適配任務與地球最佳類比。只有 M4 會隨月球地點改變。
- **任務分數** = 100 × Σ(w·c·s) / Σ(w·c)
- **任務權重（ROC）**：M3 0.429、M4 0.280、M2 0.183、M6 0.108
- **特徵權重**：
  - M2：正午高度角 0.3、低角度光照 0.7
  - M3：最長黑暗 0.5、年最低溫 0.35、日夜溫差 0.15
  - M4：30 m 坡度分布 0.7、16 km 起伏 0.3
  - M6：年均溫 0.25、年最高溫 0.25、冰凍土推估 0.5

## 資料來源

| 用途 | 資料 | 比賽清單內 |
|---|---|---|
| 月球地形 | LRO LOLA 5 m（PGDA）、LOLA LDEM_80S_20M（PDS） | 是 |
| 月球候選區座標 | LROC NAC ROI；Nobile Rim 1、Slater Plain 用文獻座標 | 是（部分） |
| 地球溫度 | MODIS Terra 月平均地表溫度 2023（Worldview／GIBS） | 是 |
| 冰蓋判定 | MODIS MCD12Q1 地表覆蓋 2023（Worldview／GIBS） | 是 |
| 地球地形 | AWS Terrain Tiles（南北緯 60° 內為 NASA SRTM） | 否；NASADEM 下載被 S3 跨網站限制擋住 |

詳細連結見 PDF 第 5 節。

## 重要檔案

- `global/global_by_task.csv`：19,599 個 1° 陸地格點的所有原始值、s 分數、各任務分數、冰蓋與已知類比地標記
- `global/modis_lst_2023_1deg.csv`：MODIS 地表溫度的年統計值
- `global/m4_global_by_moonsite.csv`：169 個有 30 m 坡度的地點，對 10 個月球地點的 M4 分數
- `global/moon10_reference_sites.json`：10 個月球地點的座標、起伏、坡度分布
- `global/final_rankings.json`：各任務排名
- `global/global_by_task_POWER_backup.csv`：改用 MODIS 前的版本（NASA POWER 氣溫），供比對

## 重跑順序

`global_screen.py` → `global_by_task.py` → `apply_ice.py` → `apply_lst.py` → `m4_global.py` → `final_rank.py` → `build_handoff.py`

計算程式與資料整理由 Claude（Anthropic）協助產生；點子、任務、權重由團隊決定。
