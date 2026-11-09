# 專案總覽（火星組）— 給所有成員與 AI 的共同背景

> 這份文件是火星組的「單一事實來源」。A、B 的任務文件（`TASK_A_mars.md`、`TASK_B_earth.md`）都以本文件的規格為準。
> 規格有變更時，先改這份文件，再通知對方。

## 1. 題目

- 競賽：NASA Space Apps Challenge 2026（黑客松 2026-11-14～15）
- 題目：**Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars**
- 出題者（NASA Earth Science Division）在說明影片中的重點：
  1. 用科學角度比較，不只是「長得像」：地質與礦物、極端溫度、冰與永凍土、沙塵過程、火山地形、洞穴等。
  2. 也可以從任務角度出發：著陸、導航、移動、機器人、建造、就地資源利用、人員作業。
  3. 沒有完美的類比地。要說清楚**哪裡類比成立、成立到什麼程度、哪裡不成立**。
  4. 不要只找已知的類比地（阿塔卡馬、南極、冰島、夏威夷、莫哈維、死亡谷、Haughton），要**系統性搜尋地球、找出還沒被發現的類比地**。相似度指標、互動應用、機器學習方法都是被鼓勵的做法。
- 本組範圍：**地球 vs. 火星**。月球組另外進行，兩組不共用程式。

## 2. 我們要做出什麼

輸入一個火星目標（預設目標或任意座標）與任務類型，輸出：

1. 全球陸地每一格的**相似度總分（0–100）**與熱度圖。
2. 前 N 名類比地，每個地點附：
   - 9 個變數各自的**單項相似度（0–1）**
   - 依任務加權後的**總分**
   - **信心度**（缺資料的變數越多，信心度越低）
   - 是否為**已知類比地**（不是的話就是「新候選」）
   - 地球無法複製的落差清單（重力、氣壓、輻射等）

最終交付給負責前後端的成員（見第 7 節）。

## 3. 時程

| 日期 | 內容 |
|---|---|
| 11/9–11/12 | 用現有公開資料完成整條流程（A、B 平行開發） |
| 11/12 晚上 | 內部 v1：完整跑通一次，產出真實結果檔 |
| 11/13 | 官方題目 Resources、提交指南、評審指南公布 → 對照官方資料清單，替換資料來源並重跑 |
| 11/14–15 | 黑客松：最終版本、分批交付給前後端 |

> 11/13 一定要讀評審指南，確認評分標準，以及有沒有賽前準備的相關規定。

## 4. 變數規格（9 個）

詳細參數在 `config/features.yaml`。三種比較類型：

- **A 類（可直接比）**：同一個物理量，用高斯核比數值差。
- **B 類（地球到不了，或單位不同）**：各自轉成「在自己星球上的百分位」再比，或比地球端的極端程度。
- **C 類（有或沒有）**：比機率或比例。

| 變數 | 類型 | 火星資料（目前） | 地球資料（目前） | 單項相似度公式 |
|---|---|---|---|---|
| `slope` 坡度 | A | MOLA＋HRSC 融合 DEM 200 m | Copernicus DEM GLO-30，重採樣到 200 m | `exp(-(x-t)^2 / (2σ^2))`，σ = 3° |
| `roughness` 粗糙度 | A | 同上，1 km 視窗內高程標準差 | 同上 | 高斯核，σ = 地球陸地分布標準差 × 0.5 |
| `thermal_inertia` 熱慣量 | B | THEMIS 100 m（±60°）；TES 3 km 補高緯度 | MODIS 推算表觀熱慣量 ATI = (1−反照率)/(日溫−夜溫) | `1 − |p_mars − p_earth|`，p = 各自星球上的百分位 |
| `lithology` 岩性 | 類別 | USGS 火星地質圖 SIM 3292 | GLiM 全球岩性圖 | 查表 `data/mappings/lithology_mars_to_glim.csv`（0–1） |
| `ice` 地下冰 | C | SWIM 冰一致性（−1～+1）；中子譜儀含水量補高緯度 | ESA CCI 永凍土比例（僅北半球 30°N 以北） | `1 − |p_earth − p_mars|`，p_mars = (SWIM+1)/2 |
| `temperature` 溫度 | B | Mars Climate Database 地表溫度 | MODIS 地表溫度年均、ERA5 | 地球端「有多冷」的百分位（越冷越接近 1） |
| `aridity` 乾燥度 | B | 定義為極乾 | 全球乾燥指數；ERA5 降雨 | 地球端「有多乾」的百分位 |
| `barrenness` 荒蕪度 | C | 定義為無植被 | MODIS NDVI 年均 | `clip(1 − NDVI/0.3, 0, 1)` |
| `dust` 沙塵活動 | B | MCD 沙塵柱光學厚度 | MODIS 氣膠光學厚度（MCD19A2）、MERRA-2 沙塵 | `1 − |p_mars − p_earth|` |

### 缺資料規則（兩人都要遵守）

- 每個變數都要有 `coverage`（true/false）。資料缺漏時 **coverage = false，不要補 0**。
- 計分時只用 coverage = true 的變數，權重在這些變數之間重新正規化。
- 信心度 `confidence` = 有資料的變數原始權重總和（0–1）。

## 5. 計分公式

單項相似度 s_i ∈ [0, 1]，任務權重 w_i（每個任務總和 = 1，見 `config/missions.json`）。

```
有效集合 V = { i | coverage_i = true 且 w_i > 0 }
w'_i = w_i / Σ_{j∈V} w_j                       # 重新正規化
總分 S = 100 × exp( Σ_{i∈V} w'_i × ln(max(s_i, 0.01)) )   # 加權幾何平均，0.01 避免 log(0)
信心度 C = Σ_{i∈V} w_i
```

用幾何平均而不是算術平均：任一關鍵變數很差時，總分會明顯下降。例如取冰任務中，冰的分數很低的地點不該拿高分。

## 6. Repo 結構與檔案負責人

```
.
├─ README.md                         # 共同（B 先建）
├─ environment.yml                   # 共同（B 先建）
├─ .gitignore                        # 共同：忽略 data/raw/、大型 tif、.env
├─ docs/
│  ├─ PROJECT_CONTEXT.md             # 本文件（共同）
│  ├─ TASK_A_mars.md                 # A 的任務
│  ├─ TASK_B_earth.md                # B 的任務
│  └─ DATA_SOURCES.md                # 資料來源與引用清單（A、B 各自補自己的）
├─ config/
│  ├─ features.yaml                  # 變數規格（共同，改動需雙方同意）
│  ├─ missions.json                  # 任務權重先驗（共同）
│  ├─ targets.yaml                   # 火星目標清單（A）
│  └─ weights_learned.json           # 學習後權重（A 產出）
├─ data/
│  ├─ raw/                           # 原始下載檔，不進 git
│  ├─ processed/
│  │  ├─ mars_targets.json           # A 產出
│  │  ├─ mars_reference_pct.json     # A 產出：火星端百分位參考分布
│  │  └─ earth_grid.parquet          # B 產出（大檔不進 git，放共用雲端）
│  ├─ labels/known_analogs.csv       # A 產出
│  └─ mappings/lithology_mars_to_glim.csv   # A 產出
├─ src/mars_analog/
│  ├─ __init__.py                    # B：對外的 score() 介面
│  ├─ config.py                      # B：讀 features.yaml / missions.json
│  ├─ adapters/
│  │  ├─ mars/                       # A：每個火星變數一個讀取函式
│  │  └─ earth/                      # B：每個地球變數一個讀取函式
│  ├─ mars_features.py               # A
│  ├─ earth_grid.py                  # B
│  ├─ similarity.py                  # B
│  ├─ scoring.py                     # B
│  ├─ validate.py                    # A
│  ├─ learn_weights.py               # A
│  ├─ novelty.py                     # A
│  └─ export.py                      # B
├─ scripts/run_pipeline.py           # B：一鍵重跑全流程
├─ notebooks/                        # 各自探索用，檔名加前綴 a_ / b_
├─ outputs/                          # 交付給前後端的結果檔
└─ tests/                            # 各自負責自己模組的測試
```

**規則**：每個檔案只有一個負責人，只改自己的檔案。要動對方的檔案，先開 issue 或直接溝通。共同檔案（`features.yaml`、`missions.json`、本文件）改動需雙方同意。

### 資料轉接層（為 11/13 換資料做準備）

每個變數的資料讀取都寫成 `src/mars_analog/adapters/{mars|earth}/{variable}.py`，並註冊到 registry：

```python
# adapters/earth/slope.py
from ..registry import register

@register(body="earth", variable="slope", source="copernicus_glo30")
def load(region_or_grid, cfg): ...
```

`features.yaml` 裡寫明每個變數目前用哪個 `source`。11/13 換成官方資料時，**新增一個 source、改設定檔即可**，評分與訓練程式不動。

## 7. 交付給前後端的格式

### 7.1 結果檔：`outputs/mars_{target_id}_{mission}.json`

```json
{
  "body": "mars",
  "version": "v1",
  "generated_at": "2026-11-12T20:00:00+08:00",
  "target": { "id": "arcadia", "name": "Arcadia Planitia", "lat": 47.2, "lon": -175.7 },
  "mission": "isru_base",
  "variables": ["slope", "roughness", "thermal_inertia", "lithology", "ice",
                "temperature", "aridity", "barrenness", "dust"],
  "weights": { "slope": 0.10, "roughness": 0.05, "...": "..." },
  "results": [
    {
      "rank": 1,
      "cell_id": "e_123456",
      "lat": -77.5, "lon": 162.0,
      "name": "McMurdo Dry Valleys",
      "total": 81.3,
      "confidence": 0.78,
      "scores":   { "slope": 0.92, "ice": 0.40, "...": "..." },
      "coverage": { "slope": true, "ice": false, "...": true },
      "known_analog": true,
      "gaps": ["gravity", "pressure", "radiation"]
    }
  ],
  "heatmap": "mars_arcadia_isru_base.png"
}
```

- `variables` 由各組自行定義，前端依此清單畫圖。這樣前端能用同一個介面處理月球組與火星組。
- **欄位定案後不刪不改名，只能往後加。**
- `name`：已知類比地用標註表的名稱；新候選可留空，或用反向地理編碼得到的地名。

### 7.2 評分模組（給後端呼叫）

```python
from mars_analog import score
result = score(target_lat=47.2, target_lon=-175.7, radius_km=25,
               mission="isru_base",   # 或 weights={...} 自訂權重
               top_n=20)              # 回傳與 7.1 同格式的 dict
```

### 7.3 交付時程

| 時間 | 交付內容 |
|---|---|
| 立刻 | 假資料版結果檔（格式正確，數字隨便），讓前後端先開工 |
| 11/12 | 真實資料 v1 |
| 11/14 開賽 +6 h | 官方資料試跑版 |
| 開賽 +24 h | 第一版正式結果 |
| 開賽 +30 h | 評分模組第一版 |
| 開賽 +36 h | 最終版；之後只修 bug、不改格式 |

## 8. 任務類型與權重先驗

見 `config/missions.json`。四種任務：`geology`（地質探勘）、`rover`（探測車測試）、`isru_base`（基地／取冰）、`landing`（著陸測試）。數值是依任務需求設定的初始假設，之後由 A 用已知類比地學習修正，並做 ±20% 敏感度分析。

## 9. 地球無法複製的落差（固定列出，不計分）

`gravity`（月 0.17 g、火 0.38 g）、`pressure`（火星地表約為地球 0.6%）、`radiation`（無磁場、大氣保護）、`atmosphere_composition`（火星約 95% CO₂）。

## 10. 引用

官方條款要求：用到的每個資料或程式來源都要引用（即使是開源或免費的），原創內容需公開或採用開源授權。每個 adapter 檔案開頭都要用註解寫出資料來源與引用格式，並同步更新 `docs/DATA_SOURCES.md`。
