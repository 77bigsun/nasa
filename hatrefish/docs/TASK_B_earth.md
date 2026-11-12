# 任務 B：地球端＋評分引擎

> 給 B 本人與 B 的 AI 助手。開始前先讀 `docs/PROJECT_CONTEXT.md`，所有規格以它為準。
> 你負責：專案骨架、地球資料與全球網格、相似度函數、計分、一鍵流程、交付給前後端的結果檔與評分模組。
> 你**不**負責：火星資料、對照表與標註表、驗證、權重學習（這些是 A 的）。

## 你的產出一覽

| 產出 | 路徑 | 誰會用 | 期限 |
|---|---|---|---|
| 專案骨架、環境、registry | `environment.yml`、`.gitignore`、`src/mars_analog/adapters/registry.py`、`config.py` | 全隊 | 11/9 |
| 假資料版結果檔 | `outputs/mars_*_*.json` | 前後端 | 11/10 |
| 地球變數讀取函式 | `src/mars_analog/adapters/earth/*.py` | B | 11/11 |
| 全球地球網格 | `data/processed/earth_grid.parquet` | A、B | 11/11 |
| 相似度函數 | `src/mars_analog/similarity.py` | A | 11/10 介面、11/11 完成 |
| 計分 | `src/mars_analog/scoring.py` | A | 11/10 介面、11/11 完成 |
| 匯出 | `src/mars_analog/export.py` → `outputs/` | 前後端 | 11/12 |
| 對外介面 | `src/mars_analog/__init__.py` 的 `score()` | 後端 | 11/12 |
| 一鍵流程 | `scripts/run_pipeline.py` | 全隊 | 11/12 |
| 資料引用 | `docs/DATA_SOURCES.md`（地球部分） | 全隊 | 持續 |

---

## B1. 專案骨架（第一天先做）

1. 依 PROJECT_CONTEXT 第 6 節建立資料夾。
2. `environment.yml`（conda-forge）：python 3.11、gdal、rasterio、rioxarray、xarray、geopandas、shapely、pyproj、numpy、scipy、scikit-learn、pandas、pyarrow、pyyaml、matplotlib、earthengine-api、geemap、earthaccess、jupyterlab、pytest。
3. `.gitignore`：`data/raw/`、`*.tif`、`*.cub`、`*.parquet`（大檔放共用雲端）、`.env`。
4. `src/mars_analog/adapters/registry.py`：

```python
_REGISTRY = {}
def register(body: str, variable: str, source: str):
    def deco(fn):
        _REGISTRY[(body, variable, source)] = fn
        return fn
    return deco
def get_loader(body: str, variable: str, source: str):
    return _REGISTRY[(body, variable, source)]
```

5. `src/mars_analog/config.py`：讀 `config/features.yaml`、`config/missions.json`、`config/weights_learned.json`（不存在時退回先驗）。

**驗收**：`pip install -e .` 後 `import mars_analog` 成功，A 能直接在 registry 註冊火星 adapter。

## B2. 假資料版結果檔（立刻交給前後端）

依 PROJECT_CONTEXT 第 7.1 節的格式，對 3 個目標 × 4 個任務各產生一個 JSON，數值隨機但格式完全正確（含 `coverage`、`known_analog`、`gaps`）。附一張假的熱度圖 PNG。

**驗收**：前後端確認能讀取並顯示。

## B3. 地球變數讀取函式 `src/mars_analog/adapters/earth/`

盡量在 Google Earth Engine 上算完，只匯出每格的統計值。每個函式：

```python
def load(grid: "ee.FeatureCollection | gpd.GeoDataFrame", cfg: dict) -> pd.DataFrame:
    """回傳 DataFrame[cell_id, <variable 欄位...>, cov_<variable>]"""
```

| 變數 | 資料 | 每格要算的值 | 注意 |
|---|---|---|---|
| slope | Copernicus DEM GLO-30 | 先重採樣到 **200 m**（與火星 DEM 同尺度），算坡度，取格內中位數（度） | 不能直接用 30 m 算坡度，否則會比火星陡很多 |
| roughness | 同上 | 200 m 下 5×5 視窗高程標準差，取格內中位數 | 視窗定義和 A 完全一致 |
| thermal_inertia | MODIS 地表溫度（MOD11A2 日／夜）＋ MODIS 反照率（MCD43A3） | ATI = (1 − 反照率) / (日溫 − 夜溫)，取多年中位數；再算 `ati_pct`（在地球陸地上的百分位） | 日夜溫差很小（水體、雲多）時設 coverage = false |
| lithology | GLiM（向量，需上傳到 Earth Engine 或在本機處理） | 格內面積最大的 GLiM 第一層類別代碼 | |
| ice | ESA CCI 永凍土比例 | 格內平均永凍土比例 `permafrost_frac`（0–1） | **只涵蓋北半球 30°N 以北**；其他地區 coverage = false（不要設 0） |
| temperature | MODIS 地表溫度年均（＋ ERA5 補缺） | `lst_mean_c`，再算 `cold_pct`（比多少比例的陸地冷） | |
| aridity | 全球乾燥指數（或 ERA5 降雨） | `aridity_index`，再算 `arid_pct`（比多少比例的陸地乾） | CHIRPS 只到 ±50°，高緯度用 ERA5 |
| barrenness | MODIS NDVI（MOD13A2）多年平均 | `ndvi_mean` | |
| dust | MODIS 氣膠光學厚度（MCD19A2）；MERRA-2 沙塵 | `dust_aod` 多年平均，再算 `dust_pct` | |

每個 adapter 檔案開頭寫資料來源與引用格式。

## B4. 全球地球網格 `src/mars_analog/earth_grid.py`

```python
def build_grid(cell_deg: float = 0.1) -> gpd.GeoDataFrame:
    """建立全球陸地網格（排除海洋、大型水體、格陵蘭與南極冰蓋內部可選）"""

def build_earth_grid(cfg) -> None:
    """依 features.yaml 每個變數的 source 呼叫 adapter，合併成 data/processed/earth_grid.parquet"""

def load_earth_grid() -> pd.DataFrame: ...
```

輸出欄位：

```
cell_id, lat, lon,
slope_deg, roughness_m, ati, ati_pct, glim_class, permafrost_frac,
lst_mean_c, cold_pct, aridity_index, arid_pct, ndvi_mean, dust_aod, dust_pct,
cov_slope, cov_roughness, cov_thermal_inertia, cov_lithology, cov_ice,
cov_temperature, cov_aridity, cov_barrenness, cov_dust
```

- 全球先用 **0.1°**（約 10 km）。先用一個小區域（例如智利北部）測試整條流程，再跑全球。
- 前幾名候選之後可再用高解析度細算（加分項目）。

**驗收**：全球陸地網格產出成功；在 QGIS 打開抽查幾個已知地點（阿塔卡馬應該很乾、NDVI 很低）。

## B5. 相似度函數 `src/mars_analog/similarity.py`

依 PROJECT_CONTEXT 第 4 節與 `config/features.yaml` 實作：

```python
def similarity_vector(target: dict, grid: pd.DataFrame, spec: dict) -> pd.DataFrame:
    """
    target：mars_targets.json 中單一目標的特徵 dict（A 產出）
    回傳 DataFrame[cell_id, s_slope, ..., s_dust, cov_slope, ..., cov_dust]
    目標或地球任一端 coverage=false 時，該項 cov=false、s=NaN
    """
```

| 變數 | 公式 |
|---|---|
| slope、roughness | `exp(-(x - t)^2 / (2σ^2))`，σ 從 `features.yaml` 讀 |
| thermal_inertia、dust | `1 - abs(p_mars - p_earth)` |
| lithology | 查 A 的 `lithology_mars_to_glim.csv`，查不到給 0.1 |
| ice | `1 - abs(p_earth - p_mars)`，p_earth = permafrost_frac，p_mars = (SWIM+1)/2 |
| temperature | `cold_pct` |
| aridity | `arid_pct` |
| barrenness | `clip(1 - ndvi_mean / 0.3, 0, 1)` |

**先交介面**：11/10 前先讓函式能回傳正確格式（可以是假值），A 才能開始寫驗證與權重學習。

**驗收**：單元測試涵蓋每個公式的邊界情況（x = t 時為 1、缺資料時為 NaN 且 cov = false）。

## B6. 計分 `src/mars_analog/scoring.py`

```python
def aggregate(sim: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """回傳 DataFrame[cell_id, total, confidence]，公式見 PROJECT_CONTEXT 第 5 節"""

def rank(target_id: str, mission: str, weights: dict | None = None, top_n: int = 20) -> pd.DataFrame:
    """讀網格與目標 → similarity_vector → aggregate → 排序；weights=None 時用 weights_learned.json 的 final，沒有就用 missions.json 先驗"""
```

**驗收**：用以下手算範例驗證（單項分數 0.92/0.85/0.60/0.70/0.20/0.45/0.90/0.98/0.55，四個任務總分應為：著陸 78.2、探測車 75.0、地質 69.8、取冰 43.0）。

## B7. 匯出 `src/mars_analog/export.py`

```python
def export_results(target_id: str, mission: str, top_n: int = 50) -> str:
    """產出 outputs/mars_{target_id}_{mission}.json（PROJECT_CONTEXT 7.1 格式）與熱度圖 PNG/GeoTIFF"""
```

- 呼叫 A 的 `novelty.flag_known()` 填入 `known_analog` 與 `name`。
- `gaps` 固定填 `["gravity", "pressure", "radiation", "atmosphere_composition"]`。
- 熱度圖：全球網格的總分，PNG（給前端直接顯示）＋ GeoTIFF（給需要的話）。

## B8. 對外介面 `src/mars_analog/__init__.py`

```python
def score(target_lat: float, target_lon: float, radius_km: float = 25,
          mission: str | None = "geology", weights: dict | None = None,
          top_n: int = 20) -> dict:
    """任意火星座標 → 呼叫 A 的 extract_mars_features → similarity_vector → aggregate → 回傳 7.1 格式 dict"""
```

後端會用它做「點擊任意火星地點」與「自訂權重」兩個互動功能。地球網格要能快速載入（parquet，必要時只載入需要的欄位）。

**驗收**：單次呼叫在一般筆電上 10 秒內回傳。

## B9. 一鍵流程 `scripts/run_pipeline.py`

```
python scripts/run_pipeline.py --stage earth      # 重建地球網格
python scripts/run_pipeline.py --stage mars       # 呼叫 A 的 build_targets
python scripts/run_pipeline.py --stage learn      # 呼叫 A 的 learn_weights
python scripts/run_pipeline.py --stage export     # 所有目標 × 任務匯出
python scripts/run_pipeline.py --stage all
```

11/13 換資料後，只要改 `features.yaml` 再跑 `--stage all`。

## B10. 加分項目（主流程完成後才做）

- **地貌 embedding**：用預訓練 ViT（例如 DINOv2，不微調）把**DEM 山陰圖**切片轉成向量。兩個星球都用 200 m 比例尺、同大小切片，計算 cosine similarity 作為第 10 個變數 `morphology`。只對前幾百名候選計算，用來重新排序。
- **反向查詢**：輸入地球座標，回傳它最像火星的哪些地方。

## B11. 11/13 換資料

官方 Resources 公布後，和 A 一起對照官方清單：已在用的不動；同一變數有官方資料的，新增 adapter source、改 `features.yaml`；新變數討論後再決定。然後跑 `--stage all`。

## 和 A 的協作點

| 時間 | 你交給 A | A 交給你 |
|---|---|---|
| 11/9 | 專案骨架、registry | — |
| 11/10 | `similarity_vector()`、`aggregate()` 介面 | 假資料 `mars_targets.json`、`targets.yaml` |
| 11/11 | 地球網格第一版 | 真實 `mars_targets.json`、岩性對照表、標註表 |
| 11/12 | 完整計分流程 | `weights_learned.json`、`novelty.py` |

## 不要做的事

- 不要改 A 的檔案（`mars_features.py`、`adapters/mars/`、`validate.py`、`learn_weights.py`、`novelty.py`、`data/labels/`、`data/mappings/`）。
- 交付格式定案後，**不刪不改名欄位**，只能往後加。
- 缺資料不要補 0，設 coverage = false。
- 不要把大型 parquet、tif commit 進 git。
