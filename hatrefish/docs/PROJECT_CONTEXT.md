# 專案總覽（火星組）：給所有成員與 AI 的共同背景

> 這份文件是火星組的「共同規格」。`TASK_A_mars.md`（IanChen）和 `TASK_B_earth.md`（B）都以這份為準。
> 規格要改時，先改這份文件，再通知對方。最後更新：11/13。

---

## 1. 題目

- 競賽：NASA Space Apps Challenge 2026（黑客松 2026-11-14～15）
- 題目：**Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars**
- 本組範圍：**地球 vs. 火星**。月球組另外進行，兩組不共用程式。
- 出題者在說明影片中的重點：
  1. 要用科學角度比較，不只是「長得像」：地質與礦物、極端溫度、冰與永凍土、沙塵、火山地形等。
  2. 也可以從任務角度出發：著陸、移動、機器人、建造、就地取用資源、人員作業。
  3. 沒有完美的類比地。要說清楚**哪裡像、像到什麼程度、哪裡不像**。
  4. 不要只列已知的類比地（阿塔卡馬、南極、冰島、夏威夷、莫哈維、死亡谷、Haughton），要**系統性搜尋整個地球，找出還沒被發現的類比地**。
- **官方資料清單（11/13 公布）**：只列資料網站入口，沒有指定資料集。
  - 地球：NASA Earthdata Search、NASA Worldview
  - 月球與火星：NASA PDS、LRO、LRO Diviner
  - 夥伴機構：CSA（RADARSAT 雷達資料）、ESA（Copernicus、Open Science Catalog）、JAXA（G-Portal）

  我們的資料不用換，但每個資料都要寫清楚出處，並盡量對應到上面的入口。

## 2. 我們要做出什麼

輸入一個火星地點（預設目標或任意座標）和任務類型，輸出：

1. 全球陸地每一格的**相似度總分（0–100）**，和一張全球熱度圖。
2. 前 N 名的地球地點，每個地點附：
   - 每個變數的**單項相似度（0–1）**
   - 依任務加權後的**總分**
   - **信心度**：缺資料的變數越多，信心度越低
   - 是不是**已知類比地**。不是的話，就是我們的「新候選地」
   - **哪裡不像**：分數低的變數，和火星差多少（例如「仍比 Jezero 暖 23 °C」）
   - 地球無法模擬的項目：重力、氣壓、輻射、大氣成分
3. 驗證結果：證明這套方法能把已知類比地排在前面。

**先粗後細**：全球先用 200 m 尺度初篩。有更細火星地形資料的目標（Jezero 20 m、Gale 30 m），前 50 名再用細尺度重新排一次。

## 3. 變數規格

詳細參數在 `config/features.yaml`。

### 3.1 五種比較方式

| 方式 | 代碼 | 白話 | 用在 |
|---|---|---|---|
| 直接比數值 | `gaussian` | 單位相同，差越少越像 | 坡度、粗糙度 |
| 比「排第幾」 | `abs_pct_diff` | 兩邊量法或單位不同，所以比「在自己星球上排第幾」 | 熱慣量、沙塵 |
| 比「有多極端」 | `earth_extreme_pct` | 火星比地球任何地方都冷、都乾，所以地球上越極端的地方分數越高 | 溫度、日溫差、乾燥度 |
| 查表 | `lookup` | 類別不能相減，事先定好每一對有多像 | 岩性 |
| 比例 | `abs_prob_diff`、`ndvi_linear` | 比機率或比例 | 冰、荒蕪度 |

驗證時會比較幾種不同做法（見 TASK_B 的 B6），選最好的。上表是目前的預設。

### 3.2 變數一覽

| 變數 | 代表什麼 | 比較方式 | 火星資料 | 地球資料 | 單項相似度 |
|---|---|---|---|---|---|
| `slope` 坡度 | 地面有多陡 | 直接比數值 | HRSC-MOLA 融合高程 200 m | Copernicus DEM 30 m，**先粗化到 200 m 再算** | `exp(-(x-t)² / (2σ²))`，σ = 3° |
| `roughness` 粗糙度 | 地面起伏 | 直接比數值 | 同上，5×5 像素（1 km）視窗內高程標準差 | 同上，視窗完全一樣 | 同上，σ = 地球陸地分布標準差 × 0.5 |
| `thermal_inertia` 熱慣量 | 地面是細沙還是岩石 | 比排第幾 | TES 全球熱慣量圖（夜間，2007） | MODIS 表觀熱慣量 ATI = (1−反照率)/(日溫−夜溫) | `1 − \|p_mars − p_earth\|` |
| `lithology` 岩性 | 岩石種類 | 查表 | USGS 火星地質圖 SIM3292 → 火星大類 | GLiM 全球岩性圖 | 查 `data/mappings/lithology_mars_to_glim.csv`，查不到 0.1 |
| `ice` 地下冰 | 有沒有冰 | 比例 | SWIM 冰地圖（−1～+1） | ESA CCI 永凍土比例 | `1 − \|p_earth − p_mars\|`，p_mars = (SWIM+1)/2 |
| `temperature` 溫度 | 年平均地表溫度 | 比有多極端 | Mars Climate Database（MCD）v6.2 | MODIS 地表溫度 | `cold_pct`（比多少陸地冷） |
| `diurnal_range` 日溫差（新增） | 一天最熱減最冷 | 比有多極端 | MCD：每季日最高減日最低，再平均 | MODIS 日溫減夜溫 | `dtr_pct`。**權重暫時是 0**，看驗證結果再決定 |
| `aridity` 乾燥度 | 有多乾 | 比有多極端 | 固定為極乾 | 全球乾燥指數（不用 CHIRPS 雨量） | `arid_pct`（比多少陸地乾） |
| `barrenness` 荒蕪度 | 植被多少 | 比例 | 固定為無植被 | MODIS NDVI | `clip(1 − NDVI/0.3, 0, 1)` |
| `dust` 沙塵 | 大氣沙塵量 | 比排第幾 | MCD 沙塵光學厚度年平均 | MERRA-2 沙塵光學厚度 | `1 − \|p_mars − p_earth\|` |

### 3.3 特別規則

- **熱慣量**：火星的目標值和火星百分位表都用 TES，同一份資料比較才公平。THEMIS 100 m 只當局部檢查。地球的 ATI 在潮濕地區不準，日夜溫差太小的格子設沒資料。
- **岩性不混入永凍土**：冰只由 `ice` 表示，不然會重複計分。
- **永凍土資料範圍**：ESA CCI 只涵蓋北緯 25°～85° 和南極（南緯 60°～85°）。範圍外的低海拔地區當作 0（沒有永凍土）；範圍外的高山（暫定海拔 3500 m 以上）設沒資料。
- **SWIM 範圍外**：火星端冰設沒資料。
- **百分位怎麼算**：
  - 地球：扣掉冰蓋的陸地格（南極乾谷這種無冰地區要保留）。
  - 火星：TES 全球所有有資料的像素。
  - 兩邊都要做面積加權：越靠近兩極，一格代表的面積越小，所以每格乘 cos(緯度)。

### 3.4 缺資料規則（兩人都要遵守）

- 每個變數都要有 `coverage`（true/false）。沒資料就是 **coverage = false，不要補 0**。補 0 會被當成真的數值，結果就錯了。
- 計分時只用 coverage = true 的變數，權重在這些變數之間重新分配。
- 信心度 = 有資料的變數原始權重加總（0–1）。

## 4. 計分公式

單項相似度 s_i（0–1），任務權重 w_i（每個任務加總 = 1，見 `config/missions.json`）。

```
有效集合 V = { i | coverage_i = true 且 w_i > 0 }
w'_i = w_i / Σ_{j∈V} w_j                                  # 權重重新分配
總分 S = 100 × exp( Σ_{i∈V} w'_i × ln(max(s_i, 0.01)) )   # 加權幾何平均；0.01 避免 log(0)
信心度 C = Σ_{i∈V} w_i
```

**為什麼用幾何平均**：任何一項很差，總分就會被明顯拉低。例如取冰任務中，沒有冰的地方不該拿高分；坡度完美但長滿植物，也不能拿來測漫遊車。

**權重從哪來**：先用 `missions.json` 的手動設定（先驗）。B 再用已知類比地學出修正值，寫到 `config/weights_learned.json`；學出來的只用來修正，不完全取代。

## 5. 程式結構與交接檔案

```
hatrefish/
  config/      features.yaml、missions.json、targets.yaml、weights_learned.json
  src/mars_analog/
    adapters/registry.py
    adapters/mars/    # IanChen
    adapters/earth/   # B
    mars_features.py  # IanChen
    earth_grid.py  similarity.py  scoring.py  validate.py
    learn_weights.py  novelty.py  refine.py  export.py   # B
  data/
    raw/         # 原始資料，不進 git
    processed/   # mars_targets.json、mars_reference_pct.json、earth_grid.parquet、earth_reference_pct.json
    mappings/    # sim3292_unit_groups.csv、lithology_mars_to_glim.csv（IanChen）
    labels/      # known_analogs.csv（IanChen）
  outputs/       # 結果檔、熱度圖、驗證報告
  scripts/       # check_env.py、fetch_mcd.py、run_pipeline.py
```

**資料轉接層**：每個變數的讀取程式寫成一個 adapter，並註冊到 registry。要換資料來源時，新增一個 adapter、改 `features.yaml` 就好，計分和驗證程式都不用動。

```python
# adapters/earth/slope.py
from ..registry import register

@register(body="earth", variable="slope", source="copernicus_glo30_200m")
def load(grid_spec, cfg): ...
```

**交接檔案一覽**：

| 檔案 | 誰做 | 誰用 | 格式在哪 |
|---|---|---|---|
| `config/targets.yaml` | IanChen | 兩人 | TASK_A 的 A1 |
| `data/processed/mars_targets.json` | IanChen | B | TASK_A 的 A4 |
| `data/processed/mars_reference_pct.json` | IanChen | B | TASK_A 的 A3 |
| `data/mappings/*.csv` | IanChen | B | TASK_A 的 A5 |
| `data/labels/known_analogs.csv` | IanChen | B | TASK_A 的 A6 |
| `data/processed/earth_grid.parquet` | B | B、後端 | TASK_B 的 B3 |
| `outputs/mars_{target}_{mission}.json` | B | 前後端、簡報 | 本文件第 7 節 |

## 6. 分工與時程

| | IanChen（A） | B |
|---|---|---|
| 負責 | 火星目標座標、火星擷取器、火星百分位表、岩石相似度表、已知類比地清單、火星資料出處 | 程式骨架、地球網格、相似度與計分、驗證、學權重、新候選標記、先粗後細、輸出、簡報規劃 |
| 文件 | `TASK_A_mars.md` | `TASK_B_earth.md` |

| 時間 | A 交給 B | B 交給 A |
|---|---|---|
| 11/13 晚上 | 三個目標的座標 | 地球網格的欄位清單 |
| 11/14 中午 | 三個目標的數值、火星百分位表 | 第一版排名 |
| 11/14 晚上 | 岩石相似度表、已知類比地清單 | 驗證結果 |
| 11/15 | 細地形資料（選做）、火星資料出處 | 最終結果 |

## 7. 交付給前後端的格式

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
      "breaks": [
        { "variable": "temperature", "earth": 27.0, "mars": -49.5, "unit": "C" }
      ],
      "gaps": ["gravity", "pressure", "radiation", "atmosphere_composition"],
      "worldview_url": "https://worldview.earthdata.nasa.gov/..."
    }
  ],
  "heatmap": "mars_jezero_geology.png"
}
```

- `variables` 由各組自己定義，前端依這個清單畫圖。這樣前端能用同一個介面處理月球組和火星組。
- `breaks`：單項分數低於 0.3 的變數，附上兩邊的實際數值，用來說明「哪裡不像」。
- `name`：已知類比地用清單上的名稱；新候選地可以留空，或用反向地理編碼得到的地名。
- **欄位定案後不刪不改名，只能往後加。**

### 7.2 評分模組（給後端呼叫）

```python
from mars_analog import score
result = score(target_lat=18.38, target_lon=77.58, radius_km=25,
               mission="geology",   # 或 weights={...} 自訂權重
               top_n=20)            # 回傳和 7.1 同格式的 dict
```

## 8. 任務類型與權重

四種任務，權重在 `config/missions.json`：

| 代碼 | 任務 | 最重視的變數 |
|---|---|---|
| `geology` | 地質探勘 | 岩性、荒蕪度 |
| `rover` | 探測車測試 | 坡度、粗糙度、熱慣量 |
| `isru_base` | 建基地、取冰 | 冰、溫度 |
| `landing` | 著陸測試 | 坡度、粗糙度 |

這些數值是依任務需求設定的初始假設。B 會用已知類比地學出修正值，並做 ±20% 的敏感度分析。日溫差的權重目前都是 0。

## 9. 地球無法模擬的項目（固定列出，不計分）

| 項目 | 火星 | 地球 |
|---|---|---|
| `gravity` 重力 | 0.38 g | 1 g |
| `pressure` 氣壓 | 約為地球的 0.6% | 1 大氣壓 |
| `radiation` 輻射 | 沒有磁場和厚大氣保護 | 有保護 |
| `atmosphere_composition` 大氣成分 | 約 95% CO₂ | 氮氣、氧氣為主 |

## 10. 引用

- 官方條款要求：用到的每個資料或程式來源都要引用，即使是開源或免費的。原創內容要公開或採用開源授權。
- 每個 adapter 開頭用註解寫出資料來源和引用格式。
- `docs/DATA_SOURCES.md` 列出所有資料：名稱、提供單位、網址、引用格式、對應官方清單的哪個入口（PDS、Earthdata、Copernicus 等）。
