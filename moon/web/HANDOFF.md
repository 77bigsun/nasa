# 月球端資料交接（給網站）

版本：2026-11-15 16:30（台北）。溫度已改用 MODIS 地表溫度。狀態：初步結果。地名是依 1° 格點座標推出的大約位置，上線前請核對一次。

## 呈現方式（11/14 定案）

1. **第 1 步：選分支任務**
   - 任務只剩 M2、M3、M4、M6，M1、M5 已刪除。
   - 結果**按任務分別排名**，每個任務一張排行榜。
2. **第 2 步：選比較地點（月球候選基地）**
   - 共 10 個：Shackleton 連接脊，加上 9 個 Artemis III 候選區。
   - 每個地點要顯示「適合測哪些任務」，資料在 `moon_sites[].suitable_tasks`。
   - 只有 M4 的排名會隨月球地點改變。M2、M3、M6 用的是地球極端值錨點，跟月球地點無關。
3. **第 3 步：相似度結果**
   - 每個任務一張排行榜，分三段：
     - 新候選地（主角）
     - 已知類比地（驗證組）
     - 最不像的地點
   - 點進任一地點，顯示每個特徵的原始值、s 分數，以及像／部分像／不像的分類。
   - 想顯示總分的話，用勾選任務的權重重新正規化後加總（見下方）。這只是附加資訊，排名以單一任務為主。

建議用**方案 A**：網站直接讀這裡算好的分數，不要在後端重算。

## 檔案

| 檔案 | 用途 |
|---|---|
| `moon_results.json` | 主檔：任務定義、10 個月球地點與適合任務、每個任務的排名 |
| `moon_global_grid.json` | 地球儀熱度圖：19,599 個 1° 陸地格點的 M2、M3、M6 分數，以及每個月球地點的 M4 粗篩分數 |
| `global_by_task_maps.png` | 三張全球熱度圖的參考圖 |

## moon_results.json 結構

```
meta              產生時間、公式、權重、冰蓋遮罩、資料來源、AI 揭露
tasks.{M2,M3,M4,M6}
  name / name_zh / weight（ROC，四項合計 1）
  features[]      id, w（特徵權重）, c（資料適配度）, formula
  depends_on_moon_site   只有 M4 是 true
moon_sites[]      10 個月球候選基地
  id, name, lat, lon, dem_source
  terrain         relief_16km_m, slope_fraction（6 個坡度區間）, class（gentle / moderate / very steep）
  suitable_tasks  primary[], secondary[], note（團隊依文獻判斷，11/14 Canva 表）
  best_earth_analogs_by_task.{任務}   該任務在全球前 3 名的新候選地
task_rankings
  M2 / M3 / M6    { new_candidates[10], known_analogs_validation[4], least_similar[3] }
  M4.{月球地點 id} { 同上 }
```

每個地點的格式（`Candidate` 欄位）：

```
rank, lat, lon, name_en, name_zh, score（0–100）, known_analog_region（null 表示是新候選地）
features[]: feature, value（原始值）, moon_value（只有 M4 有）, s（0–1）, classification（similar / partial / different）
```

分類門檻：s ≥ 0.6 為 similar，s < 0.3 為 different，介於中間為 partial。

## 公式

- **D 型**：s = clip((x − b) / (t − b), 0, 1)
- **任務分數** = 100 × Σ(w × c × s) / Σ(w × c)；缺值的特徵直接跳過。
- **選用的總分** = Σ(W × 任務分數) / Σ W，只加總勾選的任務。

  W（ROC 權重）：M3 0.429、M4 0.280、M2 0.183、M6 0.108。

| 任務 | 特徵（w、c） |
|---|---|
| M2 | 正午太陽高度角（0.3、1.0）、低角度光照比例（0.7、1.0） |
| M3 | 最長連續黑暗（0.5、1.0）、年最低溫（0.35、0.6）、日夜溫差（0.15、0.6） |
| M4 | 30 m 坡度分布（0.7、1.0）、16 km 起伏（0.3、1.0） |
| M6 | 年均溫（0.25、0.6）、年最高溫（0.25、0.6）、冰與凍土推估（0.5、0.3） |

## 篩選規則

- **冰蓋**：NASA MODIS MCD12Q1（GIBS，2023）中「永久冰雪」佔 1° 格點 50% 以上的格點，不列入排名。
- **已知類比地**：評審點名的南極、阿他加馬、冰島、夏威夷，以及 Haughton／Devon Island、死亡谷，放在驗證組，不列入新候選地。
- **同一地區只取一個**：新候選地每 8° 緯度 × 25° 經度只取一格（M2、M3、M6），避免一個地區佔滿名單。

## 限制（網站上要寫）

- 溫度是 2023 年 NASA MODIS Terra 月平均地表溫度（經 GIBS），是單一年份的月平均值，不是多年極值；色階下限 −73 °C。
- 極區在永晝、永夜月份沒有日夜循環，日夜溫差記為 0。
- 12 個沒有 MODIS 資料的格點不列入 M3、M6 排名。
- 光照和黑暗只用緯度計算，沒有考慮地形遮蔽。所以 M2 在同一條緯度帶上會同分。
- M4 的 30 m 坡度只算了 145 個依起伏挑出的全球格點，加上 24 個指定地點；熱度圖上的 M4 是只用起伏的粗篩結果。
- 真空、1/6 重力、輻射、月塵，地球都無法重現；M5 月塵已刪除。

## 資料來源

- LRO LOLA 5 m（NASA GSFC PGDA）
- LOLA LDEM_80S_20M（NASA PDS）
- LROC NAC ROI 中心座標
- MODIS Terra 月平均地表溫度 MOD11C3（2023，經 NASA GIBS）
- MODIS MCD12Q1（NASA GIBS）
- 以 SRTM 為主的 AWS Terrain Tiles

計算程式與資料整理由 Claude（Anthropic）協助產生，提交時請在 AI 使用欄位揭露。
