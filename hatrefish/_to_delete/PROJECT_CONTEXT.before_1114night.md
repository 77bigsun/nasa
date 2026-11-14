# 專案總覽（火星組）— 給所有成員與 AI 的共同背景

> 這份文件是火星組的「單一事實來源」。`TASK_A_mars.md`（A：IanChen）、`TASK_B_earth.md`（B）都以本文件的規格為準。
> 規格有變更時，先改這份文件，再通知對方。最後更新：2026-11-13。

## 1. 題目

- 競賽：NASA Space Apps Challenge 2026（黑客松 2026-11-14～15）
- 題目：**Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars**
- 出題者（NASA Earth Science Division）在說明影片中的重點：
  1. 用科學角度比較，不只是「長得像」：地質與礦物、極端溫度、冰與永凍土、沙塵過程、火山地形、洞穴等。
  2. 也可以從任務角度出發：著陸、導航、移動、機器人、建造、就地資源利用、人員作業。
  3. 沒有完美的類比地。要說清楚**哪裡類比成立、成立到什麼程度、哪裡不成立**。
  4. 不要只找已知的類比地（阿塔卡馬、南極、冰島、夏威夷、莫哈維、死亡谷、Haughton），要**系統性搜尋地球、找出還沒被發現的類比地**。
- 本組範圍：**地球 vs. 火星**。月球組另外進行，兩組不共用程式。
- 官方 Resources（11/13 公布）只列資料入口，未指定資料集：
  - Earth：NASA Earthdata Search、NASA Worldview
  - Moon & Mars：NASA PDS、LRO、LRO Diviner
  - Partners：CSA（RCM、RADARSAT-1、SAR 教學）、ESA（Copernicus Data Space、Open Science Catalog）、JAXA（G-Portal）
  - 對策：不換資料；所有來源標明出處，並對應到上述入口（見第 10 節）。

## 2. 產出

輸入一個火星目標（預設目標或任意座標）與任務類型，輸出：

1. 全球陸地每一格的**相似度總分（0–100）**與熱度圖。
2. 前 N 名類比地，每個地點附：
   - 各變數的**單項相似度（0–1）**
   - 依任務加權後的**總分**
   - **信心度**（缺資料的變數越多，信心度越低）
   - 是否為**已知類比地**（不是的話就是「新候選」）
   - `breaks`：單項分數低於門檻的變數與兩端實際數值（類比不成立之處）
   - 地球無法複製的落差清單（重力、氣壓、輻射、大氣成分）
3. 驗證報告（AUC、留一法、敏感度、算法比較）。

**先粗後細**：全球在 200 m 尺度初篩；有高解析火星 DEM 的目標（Jezero 20 m、Gale 30 m）對前 50 名重算坡度與粗糙度後重排。

**放大（11/14）**：地球端候選地從 0.1° 格放大到 0.01° 子格（約 1 km）重算地形、溫度、乾燥度、NDVI、熱慣量，找框內最像的 1 km 小區（`scripts/zoom_candidates.py`，說明見 `docs/NEW_TARGETS_AND_ZOOM.md` 第 4 節）。

## 3. 變數規格

詳細參數在 `config/features.yaml`。

### 3.1 比較方式（`compare`）

| 代碼 | 公式 | 適用 |
|---|---|---|
| `gaussian` | `exp(-(x-t)^2 / (2σ^2))` | 同物理量、數值範圍重疊 |
| `abs_pct_diff` | `1 - \|p_mars - p_earth\|`，p = 各自星球上的百分位 | 單位或量測方式不同 |
| `earth_extreme_pct` | 地球端在火星方向上的極端百分位（越冷／越乾 → 越接近 1） | 火星超出地球範圍 |
| `lookup` | 查表 | 類別變數 |
| `abs_prob_diff` | `1 - \|p_earth - p_mars\|` | 機率／比例 |
| `ndvi_linear` | `clip(1 - NDVI / ndvi_max, 0, 1)` | 植被 |

上表為預設（方法 B）。B 在驗證階段比較其他做法（全部 `gaussian`；目標值夾到地球範圍再 `gaussian`），依 AUC 決定最終方法。

### 3.2 變數

| 變數 | compare | 火星資料 | 地球資料 | 備註 |
|---|---|---|---|---|
| `slope` | gaussian（σ = 3°） | HRSC-MOLA blend DEM 200 m | Copernicus DEM GLO-30，重採樣到 200 m | 不可直接用 30 m 算坡度 |
| `roughness` | gaussian（σ = 地球陸地標準差 × 0.5） | 同上，5×5 像素（1 km）視窗高程標準差 | 同上，同視窗 | |
| `thermal_inertia` | abs_pct_diff | TES 全球夜間 TI（2007） | MODIS ATI = (1−albedo)/(T_day−T_night) | 火星目標值與百分位表都用 TES；THEMIS 僅局部檢查 |
| `lithology` | lookup | USGS SIM3292 → 火星大類 | GLiM 第一層 | `sim3292_unit_groups.csv` + `lithology_mars_to_glim.csv`，預設 0.1 |
| `ice` | abs_prob_diff | SWIM Ci（−1～+1），目標 = clip(Ci, 0, 1) | ESA CCI Permafrost v5 比例 | 規則見 3.3（11/14 修正） |
| `temperature` | earth_extreme_pct（`cold_pct`） | MCD v6.2 tsurf 年均 | MODIS LST 年均 | MODIS LST 2020–2024（11/14 晚起；放大程式仍是 2015–2024） |
| `diurnal_range` | earth_extreme_pct（`dtr_pct`） | MCD tsurf：各 Ls 日最高−日最低，取平均 | MODIS LST 日−夜 | 新增；權重暫為 0 |
| `aridity` | earth_extreme_pct（`arid_pct`） | 固定極乾 | Global Aridity Index | 不用 CHIRPS（Atacama 偏差大） |
| `barrenness` | ndvi_linear（ndvi_max = 0.3） | 固定 NDVI = 0 | MODIS NDVI 多年平均 | |
| `dust` | abs_pct_diff | MCD tauref 年均 | MERRA-2 DUEXTTAU 多年平均 | 驗證時另試 gaussian |

### 3.3 特別規則

- 岩性不含永凍土；冰只由 `ice` 表示，避免重複計分。
- ESA CCI 永凍土涵蓋 25–85°N 與 60–85°S。範圍外：低海拔 = 0；海拔 ≥ 3500 m（暫定）→ coverage = false。
- SWIM 範圍外：火星端 `ice` coverage = false。
- 冰的目標值（11/14 修正）：SWIM Ci 是「冰跡象的一致性」，不是冰的比例。Ci ≤ 0 視為沒有冰（目標 0，找無冰的地方）；Ci > 0 時目標 = Ci。舊版 (Ci+1)/2 會讓 Jezero（Ci = −0.21）去找 40% 永凍土的地方。IanChen 檔案裡的 `p` 欄位不再使用。
- 地球 ATI：日夜溫差 < 5 K 的格子 coverage = false。
- 百分位參考分布：
  - 地球：扣除冰蓋的陸地格（無冰的南極乾谷保留），面積權重 cos(lat)。
  - 火星：TES 全球有效像素，面積權重 cos(lat)。
  - 分別存於 `data/processed/earth_reference_pct.json`、`data/processed/mars_reference_pct.json`。

### 3.4 類比剖面（類比面向，11/14 新增）

面向定義在 `config/dimensions.yaml`，程式在 `src/mars_analog/profiles.py`，執行 `python scripts/make_profiles.py`，輸出在 `outputs/profiles/`。

| 面向 | 變數 |
|---|---|
| terrain 地形 | slope、roughness |
| surface 地表物質與裸露 | lithology、thermal_inertia、barrenness（無植被） |
| environment 環境極端 | temperature、aridity |
| water_ice 水與冰 | ice |
| atmosphere_dust 大氣與沙塵 | dust |
| biology 生物與棲息性 | 無（待補：土壤有機碳、土壤鹽度） |
| subsurface 洞穴與地下 | 無（沒有全球資料） |

- 面向分數 = 面向內有資料變數的等權重幾何平均；整體相似度 = 有分數面向的等權重幾何平均 × 100。不依任務加權。
- `diurnal_range` 不計入任何面向（火星日溫差主要來自稀薄大氣，地球無法模擬），只在 breaks 當參考。
- 排名只用面向和變數都至少 80% 有資料的格子；每個面向的前幾名只用該面向變數全部有資料的格子；地點彼此至少相距 150 km。
- 目標（11/14 起 7 個）：jezero、gale、arcadia（IanChen）＋ oxia、meridiani、protonilus、ap105（SkyFall 設計參考著陸點；B 用 IanChen 的擷取程式新增，見 `docs/NEW_TARGETS_AND_ZOOM.md`）。oxia、meridiani 的岩性類別用文獻覆寫（`lithology.group_source = literature_override`）。
- 沒有已知類比地標給某目標時，總表與雷達圖改列全部已知類比地中全球排名最前的 8 個。
- 每個變數也有自己的前 5 名（`top_by_variable`，同分時整體相似度高的優先），例如「溫度最像的 5 個地方」。和每個面向的前 5 名一起畫在 `outputs/profiles/board_{目標}.png`，總表也列出地球值和火星值。只有一個變數的面向（水與冰、沙塵）變數排名和面向相同。

### 3.5 缺資料規則（兩人都要遵守）

- 每個變數都要有 `coverage`（true/false）。資料缺漏時 **coverage = false，不要補 0**。
- 計分時只用 coverage = true 的變數，權重在這些變數之間重新正規化。
- 信心度 `confidence` = 有資料的變數原始權重總和（0–1）。

### 3.6 測試項目分數 R1–R6（11/14 新增）

測試定義來自整合者 Harris 的規劃（`nasa/docs/火星.pdf`），特徵、門檻、適用性、面向 × 測試交叉表寫在 `config/mission_tests.yaml`；程式 `src/mars_analog/mission_tests.py`；執行 `python scripts/make_mission_tests.py`；輸出 `outputs/mission_tests/`（總表、需求矩陣、候選池）。

- 測試分數 = 測試內特徵的等權重幾何平均（下限 0.01）。特徵有三類：跟火星目標比（沿用單項相似度）、門檻型滿意度函數（梯形）、季節曲線與礦物指標。
- 特徵全部是必要的：缺資料就不評分。只有在 `fill` 指定的範圍補值（南緯 60° 以南的乾燥指數與 NDVI 補 1）。
- R3、R5 只對 SWIM Ci ≥ 0.1 的目標適用；R2 全球沒有資料，標為無法評估。
- 季節曲線（R6）、冰河距離（R5）、礦物指標（R4）需要 `scripts/fetch_earth_extra_gee.py` 產生的補資料；沒有時列為「待補資料」。
- 集合覆蓋已做：`scripts/make_set_cover.py`，輸出 `outputs/set_cover/`

## 4. 計分公式

> **11/14 決定：任務版停用。** 四種任務（geology、rover、isru_base、landing）加權與學習權重（本節後半、第 7.1 節、第 8 節、`docs/WEIGHTS_EXPLAINED.md`）不再更新；任務導向只用第 3.6 節的測試項目 R1–R6。程式與文件保留備查。比較方式選方法 B 的驗證結論仍然有效（類比剖面、測試項目都用它）。

單項相似度 s_i ∈ [0, 1]，任務權重 w_i（每個任務總和 = 1，見 `config/missions.json`）。

```
有效集合 V = { i | coverage_i = true 且 w_i > 0 }
w'_i = w_i / Σ_{j∈V} w_j                                  # 重新正規化
總分 S = 100 × exp( Σ_{i∈V} w'_i × ln(max(s_i, 0.01)) )   # 加權幾何平均，0.01 避免 log(0)
信心度 C = Σ_{i∈V} w_i
```

用幾何平均而不是算術平均：任一關鍵變數很差時，總分會明顯下降。

權重：預設用 `missions.json` 先驗；B 以已知類比地學習（非負 L2 邏輯迴歸，特徵為 ln s_i），與先驗逐項相乘後正規化，寫入 `config/weights_learned.json`。正樣本 < 20 時不學習。

## 5. 程式結構與資料轉接層

```
hatrefish/
  config/      features.yaml  missions.json  targets.yaml  weights_learned.json
  src/mars_analog/
    __init__.py                     # score()
    config.py
    adapters/registry.py
    adapters/mars/                  # A
    adapters/earth/                 # B
    mars_features.py                # A
    earth_grid.py  similarity.py  scoring.py  validate.py
    learn_weights.py  novelty.py  refine.py  export.py     # B
  data/
    raw/        # 不進 git
    processed/  # mars_targets.json  mars_reference_pct.json  earth_grid.parquet  earth_reference_pct.json
    mappings/   # sim3292_unit_groups.csv  lithology_mars_to_glim.csv
    labels/     # known_analogs.csv
  outputs/
  scripts/      # check_env.py  fetch_mcd.py  run_pipeline.py
```

每個變數的資料讀取寫成 `src/mars_analog/adapters/{mars|earth}/{variable}.py`，並註冊到 registry：

```python
# adapters/earth/slope.py
from ..registry import register

@register(body="earth", variable="slope", source="copernicus_glo30_200m")
def load(grid_spec, cfg): ...
```

`features.yaml` 寫明每個變數目前用哪個 `source`。換資料來源時新增 adapter、改設定檔即可，評分與訓練程式不動。

交接檔案：

| 檔案 | 產出 | 使用 | 格式 |
|---|---|---|---|
| `config/targets.yaml` | A | A、B | TASK_A A1 |
| `data/processed/mars_targets.json` | A | B | TASK_A A4 |
| `data/processed/mars_reference_pct.json` | A | B | TASK_A A3 |
| `data/mappings/*.csv` | A | B | TASK_A A5 |
| `data/labels/known_analogs.csv` | A | B | TASK_A A6 |
| `data/processed/earth_grid.parquet` | B | B、後端 | TASK_B B3 |
| `outputs/mars_{target_id}_{mission}.json` | B | 前後端 | 第 7.1 節 |

## 6. 分工與時程

| | 負責 | 任務文件 |
|---|---|---|
| A（IanChen） | 目標座標、火星擷取器、火星百分位表、岩性對照、已知類比地標註、火星資料引用 | `TASK_A_mars.md` |
| B | 骨架、地球網格、相似度、計分、驗證、權重學習、新候選標記、先粗後細、匯出、簡報規劃 | `TASK_B_earth.md` |

| 時間 | A → B | B → A |
|---|---|---|
| 11/13 晚 | `targets.yaml` | 地球網格欄位清單 |
| 11/14 中午 | `mars_targets.json`、`mars_reference_pct.json` | 第一版排名 |
| 11/14 晚 | 岩性對照、`known_analogs.csv` | 驗證報告 |
| 11/15 | 高解析 DEM（選做）、資料引用 | 最終輸出 |

## 7. 交付給前後端的格式

> 11/14 起：網頁整合用網頁 repo（77bigsun/nasa main）的 `data/seed` 格式，由 `scripts/export_web_seed.py` 產生，見 `outputs/web/WEB_EXPORT.md`。網頁目前的排名方法是暫時的，本隊的方法不用配合它調整。第 7.1 節的任務版結果檔已停用。

### 7.1 結果檔：`outputs/mars_{target_id}_{mission}.json`

```json
{
  "body": "mars",
  "version": "v1",
  "generated_at": "2026-11-15T12:00:00+08:00",
  "target": { "id": "jezero", "name": "Jezero Crater delta", "lat": 18.38, "lon": 77.58 },
  "mission": "geology",
  "method": "B",
  "variables": ["slope", "roughness", "thermal_inertia", "lithology", "ice",
                "temperature", "diurnal_range", "aridity", "barrenness", "dust"],
  "weights": { "slope": 0.05, "roughness": 0.10, "...": "..." },
  "results": [
    {
      "rank": 1,
      "cell_id": "e_123456",
      "lat": -24.08, "lon": -69.92,
      "name": "Atacama Desert (Yungay)",
      "total": 81.3,
      "confidence": 0.95,
      "scores":   { "slope": 0.92, "temperature": 0.21, "...": "..." },
      "coverage": { "slope": true, "ice": true, "...": true },
      "known_analog": true,
      "breaks": [ { "variable": "temperature", "earth": 27.0, "mars": -49.5, "unit": "C" } ],
      "gaps": ["gravity", "pressure", "radiation", "atmosphere_composition"],
      "worldview_url": "https://worldview.earthdata.nasa.gov/..."
    }
  ],
  "heatmap": "mars_jezero_geology.png"
}
```

- `variables` 由各組自行定義，前端依此清單畫圖。這樣前端能用同一個介面處理月球組與火星組。
- `breaks`：單項分數 < `breaks_threshold`（0.3）的變數。
- `name`：已知類比地用標註表的名稱；新候選可留空，或用反向地理編碼得到的地名。
- **欄位定案後不刪不改名，只能往後加。**

### 7.2 評分模組（給後端呼叫）

```python
from mars_analog import score
result = score(target_lat=18.38, target_lon=77.58, radius_km=25,
               mission="geology",   # 或 weights={...} 自訂權重
               top_n=20)            # 回傳與 7.1 同格式的 dict
```

## 8. 任務類型與權重先驗

見 `config/missions.json`。四種任務：`geology`（地質探勘）、`rover`（探測車測試）、`isru_base`（基地／取冰）、`landing`（著陸測試）。數值是依任務需求設定的初始假設，之後由 B 用已知類比地學習修正，並做 ±20% 敏感度分析。`diurnal_range` 權重暫為 0。

## 9. 地球無法複製的落差（固定列出，不計分）

`gravity`（月 0.17 g、火 0.38 g）、`pressure`（火星地表約為地球 0.6%）、`radiation`（無磁場、大氣保護）、`atmosphere_composition`（火星約 95% CO₂）。

## 10. 引用

官方條款要求：用到的每個資料或程式來源都要引用（即使是開源或免費的），原創內容需公開或採用開源授權。每個 adapter 檔案開頭用註解寫出資料來源與引用格式，並同步更新 `docs/DATA_SOURCES.md`（名稱、提供單位、網址、引用格式、對應的官方入口：PDS／Earthdata／Copernicus 等）。
