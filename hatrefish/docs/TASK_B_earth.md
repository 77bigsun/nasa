# 任務 B：地球端、比對引擎、驗證與呈現

> 這份文件給 B 本人，也給 B 的 AI 助手。
> 每個任務前半段是白話說明（要做什麼、為什麼）；標著「**技術細節**」的部分是寫程式時要看的。
> 整體規格以 `docs/PROJECT_CONTEXT.md` 為準。最後更新：11/13。

---

## 一句話說明你的工作

IanChen 會把火星目標的各項數值整理好（坡度、熱慣量、冰、溫度……）。**你的工作是把整個地球切成小格子，算出每一格的同樣數值，再拿來跟火星比，算出每一格「有多像」的分數並排名。** 接著檢查這套方法準不準、從已知類比地學出比較好的權重、標出新發現的候選地，最後規劃怎麼呈現給評審。

## 分工

| 你負責 | 你不用做（IanChen 負責） |
|---|---|
| 專案程式骨架 | 火星目標座標 |
| 地球資料與全球網格 | 火星擷取器、火星數值 |
| 相似度和總分的計算 | 火星百分位表 |
| 驗證方法準不準、比較不同算法 | 岩石種類相似度表 |
| 學權重 | 已知類比地清單 |
| 標記新候選地、先粗後細重排 | 火星資料出處 |
| 輸出結果檔、規劃最後的呈現 | |

## 這次改了什麼（11/13）

- **分工調整**：驗證、學權重、標記新候選地，原本在 A，現在改由你負責。
- **官方資料清單**只列資料網站入口（Earthdata、Worldview、Copernicus 等），沒有指定資料集。所以不用換資料，但每個資料要寫清楚出處，地球資料盡量走 NASA Earthdata 或 ESA Copernicus。
- **相似度分三種算法**，依變數決定（見 B4）。另外要用驗證結果比較幾種做法，選最好的。
- **乾燥度改用乾燥指數**，不用 CHIRPS 雨量。CHIRPS 在 Atacama 算出 161 mm/年，實際不到 2 mm。
- **新增「日溫差」欄位**：先算出來，權重暫時是 0，之後看驗證結果決定要不要納入。
- **新增「先粗後細」**：全球先用 200 m 尺度初篩，前幾名再用更細的地形重排。
- **結果要寫出「哪裡不像」**：除了分數，也要寫出每個地點和火星差多少（例如「仍比 Jezero 暖 23 °C」）。

## 名詞小抄

| 名詞 | 意思 |
|---|---|
| 網格 | 把地球陸地切成 0.1° × 0.1° 的小格（赤道附近約 11 km），每格算一組數值 |
| 單項相似度 | 某一個變數有多像，0 到 1。1 代表完全一樣 |
| 總分 | 依任務權重把單項相似度合起來，0 到 100 |
| 信心度 | 有資料的變數佔多少權重。缺資料越多，信心度越低 |
| coverage | 這一格這個變數有沒有資料。沒資料就是 `false`，**不要填 0** |
| 百分位 | 某個數值在全球陸地排第幾。0.9 代表比 90% 的陸地高 |
| ATI | 表觀熱慣量，地球上用衛星溫度和反照率估算的熱慣量 |
| AUC | 驗證分數。把已知類比地和普通地點混在一起，看我們的排名能不能把類比地排在前面。1 是完美，0.5 等於亂猜 |
| GEE | Google Earth Engine，在雲端處理衛星資料，不用自己下載 |

## 任務總覽

| 編號 | 任務 | 產出 | 期限 |
|---|---|---|---|
| B1 | 建立程式骨架 | `src/mars_analog/` | 11/13 晚上 |
| B2 | 讀取地球資料 | `src/mars_analog/adapters/earth/` | 11/14 上午 |
| B3 | 建立全球網格 | `data/processed/earth_grid.parquet` | 11/14 上午 |
| B4 | 算單項相似度 | `similarity.py` | 11/14 中午 |
| B5 | 算總分和排名 | `scoring.py` | 11/14 中午 |
| B6 | 驗證、比較算法 | `validate.py`、`outputs/validation_report.json` | 11/14 下午 |
| B7 | 學權重 | `learn_weights.py`、`config/weights_learned.json` | 11/14 晚上 |
| B8 | 標記新候選地 | `novelty.py` | 11/14 晚上 |
| B9 | 先粗後細重排 | `refine.py` | 11/15 上午 |
| B10 | 輸出結果檔 | `export.py`、`outputs/` | 11/15 上午 |
| B11 | 規劃最後的呈現 | 簡報大綱、展示用圖 | 11/15 |
| B12 | （選做）加分項目 | 見 B12 | 有空再做 |

**最小可交付版本（一定要先完成）**：B1 到 B5 跑通，加上 B6 的基本驗證和 B10 的輸出。有了這些就有完整的結果可以展示，其他都是加分。

**火星數值還沒好之前**：先用 `TASK_A_mars.md` 裡 A2 的參考值表，手寫一份臨時的 `mars_targets.json` 來測試，等 IanChen 的版本好了再換。

---

## B1. 建立程式骨架

**要做什麼**：建立程式的資料夾和共用工具，讓兩個人的程式能接在一起。

**完成的標準**：在 `hatrefish/` 底下 `pip install -e .` 之後，`import mars_analog` 成功。

**技術細節**：

```
hatrefish/
  pyproject.toml
  src/mars_analog/
    __init__.py          # 對外的 score() 介面（B10）
    config.py            # 讀 features.yaml、missions.json、weights_learned.json（沒有就用 missions.json）
    adapters/registry.py
    adapters/earth/      # 你的
    adapters/mars/       # IanChen 的
    earth_grid.py  similarity.py  scoring.py  validate.py
    learn_weights.py  novelty.py  refine.py  export.py
  scripts/run_pipeline.py
```

`registry.py`：

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

---

## B2. 讀取地球資料

**要做什麼**：寫好讀取每個地球變數的程式，能算出每一格的數值。

**為什麼這樣做**：地球資料量很大，所以盡量在 GEE 雲端算完，只把每格的結果下載回來。

**每個變數用什麼資料**：

| 變數 | 代表什麼 | 資料 | 出處 |
|---|---|---|---|
| 坡度 | 地面有多陡 | Copernicus DEM 30 m | ESA |
| 粗糙度 | 地面起伏多不多 | 同上 | ESA |
| 熱慣量 | 地面是沙還是岩石 | MODIS 日夜地表溫度加反照率，算 ATI | NASA Earthdata |
| 岩性 | 岩石種類 | GLiM 全球岩性圖 | 學術資料（PANGAEA） |
| 冰 | 有沒有永凍土 | ESA CCI 永凍土 | ESA |
| 溫度 | 年平均地表溫度 | MODIS 地表溫度 | NASA Earthdata |
| 日溫差（新增） | 白天減晚上 | 同上 | NASA Earthdata |
| 乾燥度 | 有多乾 | 全球乾燥指數 | CGIAR |
| 荒蕪度 | 植被多少 | MODIS NDVI | NASA Earthdata |
| 沙塵 | 大氣沙塵量 | MERRA-2 沙塵光學厚度 | NASA Earthdata |
| 陸地、冰蓋遮罩 | 排除海、湖、冰蓋 | ESA WorldCover | ESA |

**幾個要特別注意的地方（白話）**：
- **坡度一定要先把地形資料粗化到 200 m 再算**。火星的地形資料是 200 m，同一片地用 30 m 算出來的坡度會比用 200 m 算的陡很多，這樣就不公平。
- **永凍土資料只涵蓋部分地區**：北緯 25°～85°，和南極（南緯 60°～85°）。範圍外的低海拔地區可以當作「沒有永凍土」（0）；範圍外的高山（暫定海拔 3500 m 以上）可能有永凍土但沒資料，要設沒資料。
- **熱慣量在潮濕地區不準**，因為水分蒸發會影響日夜溫差。乾燥地區最準，剛好是我們最在意的地方。日夜溫差太小（水體、雲多）的格子設沒資料。
- **乾燥指數要確認南極有沒有值**。沒有的話，南極那幾格的乾燥度設沒資料。

**完成的標準**：在小範圍（例如智利北部）每個變數都能算出合理的值。Atacama 應該很乾、NDVI 很低。

**技術細節**：

每個 adapter 的介面：

```python
def load(grid_spec: dict, cfg: dict) -> pd.DataFrame:
    """回傳 DataFrame[cell_id, <變數欄位...>, cov_<變數>]"""
```

| 變數 | GEE 資料（ID 以實際查到的為準） | 做法 |
|---|---|---|
| slope | `COPERNICUS/DEM/GLO30`（band `DEM`） | `mosaic()` 之後要 `setDefaultProjection`，否則 `ee.Terrain.slope` 會算錯。先 reduceResolution 到 200 m，再算坡度，最後對 0.1° 格取中位數 |
| roughness | 同上 | 200 m 下 5×5 視窗的高程標準差，再取格內中位數。視窗要和火星端完全一樣 |
| thermal_inertia | `MODIS/061/MOD11A2`、`MODIS/061/MYD11A2`（LST_Day、LST_Night）、`MODIS/061/MCD43A3`（Albedo_WSA_shortwave） | ATI = (1 − 反照率) / (日溫 − 夜溫)，取多年中位數。日夜溫差 < 5 K 設沒資料 |
| lithology | GLiM（PANGAEA 10.1594/PANGAEA.788537 有 0.5° 格網版；完整向量版另外下載） | 先用 0.5° 版跑通，有空再換向量版。取格內面積最大的第一層類別 |
| ice | ESA CCI Permafrost v5（北半球、南極兩個 .nc，從 CEDA 下載） | 本機處理：`PFR` 是百分比，`ds.PFR.isel(time=0).coarsen(lat=10, lon=10, boundary="trim").mean()/100`。範圍外依上面規則處理 |
| temperature | MOD11A2 / MYD11A2 | 日、夜平均的多年平均，轉 °C |
| diurnal_range | 同上 | 日溫減夜溫的多年平均 |
| aridity | `projects/sat-io/open-datasets/global_ai/global_ai_yearly` | 注意數值可能有放大倍數，以資料說明為準 |
| barrenness | `MODIS/061/MOD13A2`（NDVI，倍數 0.0001） | 多年平均 |
| dust | `NASA/GSFC/MERRA/aer/2`（DUEXTTAU） | 多年平均 |
| 遮罩 | `ESA/WorldCover/v200` | 水體（80）比例 > 50% 的格子排除；冰雪（70）比例 > 50% 的格子排除 |

每個 adapter 開頭用註解寫上資料來源和引用格式。

---

## B3. 建立全球網格

**要做什麼**：把 B2 的所有變數算到全球每一格，合併成一張大表，之後比對都直接讀這張表。

**為什麼要先做好存起來**：全球算一次要很久，但比對時只要讀表，幾秒就能算完。這樣換任何火星目標都很快。

**還要做「地球百分位表」**：溫度、乾燥度、熱慣量、沙塵、日溫差都要知道「在全球陸地排第幾」。做法跟火星端一樣：越靠近兩極格子面積越小，所以每格乘 cos(緯度) 當權重。參考範圍是「扣掉冰蓋的陸地」（南極乾谷這種無冰的地方要保留）。

**完成的標準**：全球網格產生成功；抽查幾個已知地點的數值合理。

**技術細節**：
- 先在小範圍（智利北部）跑通，再跑全球。
- 每個變數在 GEE 算成 0.1° 的影像（3600 × 1800），分塊下載成 numpy，不用經過 Google Drive。最後只保留陸地格，存成 parquet。
- 輸出欄位（只能增加，不刪不改名）：

```
cell_id, lat, lon,
slope_deg, roughness_m, ati, ati_pct, glim_class, permafrost_frac,
lst_mean_c, cold_pct, dtr_c, dtr_pct, aridity_index, arid_pct,
ndvi_mean, dust_aod, dust_pct,
cov_slope, cov_roughness, cov_thermal_inertia, cov_lithology, cov_ice,
cov_temperature, cov_diurnal_range, cov_aridity, cov_barrenness, cov_dust
```

- 地球百分位表存成 `data/processed/earth_reference_pct.json`。

---

## B4. 算單項相似度

**要做什麼**：對每一格、每個變數，算出跟火星目標有多像（0 到 1）。

**三種算法，依變數決定**：

| 算法 | 用在 | 白話 |
|---|---|---|
| 直接比數值 | 坡度、粗糙度 | 單位相同，差越少越像。漫遊車爬 15° 的坡，在哪個星球都是 15° |
| 比「排第幾」 | 熱慣量、沙塵 | 兩個星球量法或單位不同，所以比「在自己星球上排第幾」。火星排前 30%，就找地球上也排前 30% 的地方 |
| 比「有多極端」 | 溫度、日溫差、乾燥度 | 火星比地球任何地方都冷、都乾，所以地球上越冷、越乾的地方分數越高 |
| 查表 | 岩性 | 用 IanChen 做的岩石相似度表 |
| 比例 | 冰、植被 | 冰比永凍土比例；植被越少越像 |

**沒資料的處理**：火星或地球任一邊沒資料，這一項就標成沒資料，計分時跳過，不要當成 0 分。

**完成的標準**：
- 數值完全一樣時分數是 1。
- 沒資料時分數是空值、coverage 是 false。

**技術細節**：

```python
def similarity_vector(target: dict, grid: pd.DataFrame, spec: dict) -> pd.DataFrame:
    """回傳 DataFrame[cell_id, s_<變數>..., cov_<變數>...]"""
```

| 變數 | 公式 |
|---|---|
| slope、roughness | `exp(-(x - t)^2 / (2σ^2))`，σ 從 `features.yaml` 讀 |
| thermal_inertia、dust | `1 - abs(p_mars - p_earth)` |
| temperature | `cold_pct` |
| diurnal_range | `dtr_pct`（日溫差越大越接近 1） |
| aridity | `arid_pct` |
| lithology | 先用 `sim3292_unit_groups.csv` 把火星 Unit 轉成大類，再查 `lithology_mars_to_glim.csv`，查不到給 0.1 |
| ice | `1 - abs(permafrost_frac - p_mars)`，p_mars = (SWIM+1)/2 |
| barrenness | `clip(1 - ndvi_mean / 0.3, 0, 1)` |

同時算每一項的「絕對差距」（例如溫度差幾 °C），給 B10 寫「哪裡不像」用。

---

## B5. 算總分和排名

**要做什麼**：依任務權重把單項相似度合成總分，排出前幾名。

**為什麼用幾何平均**：任何一項很差，總分就會被明顯拉低。例如坡度完美但長滿植物，也不能拿來測漫遊車。這比加總平均更符合實際。

**四種任務**：地質探勘、探測車測試、建基地取冰、著陸測試。每種任務重視的變數不同，權重在 `config/missions.json`。

**完成的標準**：用下面的手算範例檢查，四個任務的總分要一樣。

單項分數依序是坡度 0.92、粗糙度 0.85、熱慣量 0.60、岩性 0.70、冰 0.20、溫度 0.45、乾燥度 0.90、荒蕪度 0.98、沙塵 0.55。正確總分：著陸 78.2、探測車 75.0、地質 69.8、取冰 43.0。

**技術細節**：

```python
def aggregate(sim: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """回傳 DataFrame[cell_id, total, confidence]，公式見 PROJECT_CONTEXT 第 4 節"""

def rank(target_id: str, mission: str, weights: dict | None = None, top_n: int = 20) -> pd.DataFrame:
    """weights=None 時用 weights_learned.json，沒有就用 missions.json"""
```

`diurnal_range` 在 `missions.json` 裡的權重目前都是 0。

---

## B6. 驗證、比較算法

**要做什麼**：檢查我們的方法能不能把「公認的類比地」排在前面，並比較幾種算法哪個最好。

**為什麼重要**：這是證明「方法可信」的唯一證據，也是簡報最有說服力的部分。題目要求遇到新地點也能判斷，驗證就是在證明這件事。

**怎麼做**：
1. **基本驗證**：把已知類比地（IanChen 的清單）和隨機的普通陸地格混在一起，看排名能不能把類比地排在前面，算 AUC。
2. **留一個出來測**：每次拿掉一個已知類比地，用剩下的學權重，看被拿掉的那個還能不能排進前 5%。這最接近「遇到沒看過的地點」。
3. **權重敏感度**：每個權重增減 20%，看前 10 名變動多少。變動小代表結果穩定。
4. **比較算法**，每種都算 AUC，選最好的，並寫進簡報：
   - 做法 A：全部都直接比數值
   - 做法 B：照 B4 的分類（目前的預設）
   - 做法 C：先把火星目標值「拉回」地球範圍內（例如溫度直接設成地球最冷的值），再直接比數值
   - 另外試：日溫差納入或不納入、沙塵用直接比數值或比排名

**快速檢查**：在已知類比地清單還沒好之前，先用 `IanChen/` 的 12 個點檢查：6 個已知類比地應該排在台灣點和負樣本前面。

**完成的標準**：產出 `outputs/validation_report.json`，並寫一段白話結果摘要。

**技術細節**：

```python
def evaluate(target_id: str, mission: str, weights: dict | None = None, method: str = "B") -> dict:
    """回傳 {"auc", "recall_at_1pct", "recall_at_5pct", "known_ranks": {site_id: 排名百分位}}"""
def leave_one_site_out(mission: str) -> dict: ...
def sensitivity(target_id: str, mission: str, delta: float = 0.2) -> dict:
    """回傳前 10 名的重疊率（Jaccard）"""
```

- 正樣本：`known_analogs.csv` 中 `mars_target_ids` 包含該目標的地點，所在的網格。
- 負樣本：隨機陸地格（正樣本的 10 倍）＋高 NDVI 格（雨林、農地）。

---

## B7. 學權重

**要做什麼**：從已知類比地學出「哪些變數比較重要」，用來修正手動設定的權重。

**為什麼不完全用學出來的**：已知類比地只有二、三十個，而且偏向交通方便的地方。學出來的權重只用來修正原本的設定，不完全取代。**不要用深度學習**，資料太少一定會過擬合。

**怎麼做（白話）**：用邏輯迴歸，讓模型學「什麼樣的單項分數組合，會是已知類比地」。因為總分是幾何平均，取 log 之後剛好是加權總和，所以模型學到的係數可以直接當權重。

**完成的標準**：
- 每個任務的權重加起來等於 1。
- 用新權重跑出來的 AUC 不低於原本的；如果比較低，就保留原本的並在報告裡說明。

**技術細節**：
1. 特徵是 ln(max(s_i, 0.01))，係數限制 ≥ 0，加 L2 正則化（用 `scipy.optimize.minimize` 加 bounds 實作）。
2. 係數正規化成總和 1，得到 `w_learned`。
3. 和任務先驗混合：`w_final[m] ∝ w_prior[m] × w_learned`（逐項相乘後正規化）。
4. 已知類比地少於 20 個時先不學，直接用先驗。
5. 寫入 `config/weights_learned.json`：

```json
{ "method": "logreg_l2_nonneg_logs", "trained_at": "...", "n_pos": 25, "n_neg": 250,
  "learned_global": { "slope": 0.12, "...": "..." },
  "final": { "geology": {}, "rover": {}, "isru_base": {}, "landing": {} } }
```

---

## B8. 標記新候選地

**要做什麼**：把排名前面的地點分成「已知類比地」和「新候選地」。

**為什麼重要**：題目明確說不要只找已知的類比地，要找出還沒被發現的。新候選地就是我們的主要成果。

**怎麼做**：
- 離任何已知類比地 50 km 以內的，標成已知；其他是新候選。
- 每個目標的前 3 名新候選，用 NASA Worldview 看衛星影像，確認不是資料出錯（例如雲、湖、城市），把結論寫在 `outputs/new_candidates.md`。

**技術細節**：

```python
def flag_known(results: pd.DataFrame, buffer_km: float = 50) -> pd.DataFrame:
    """距離已知類比地 buffer_km 內的標 known_analog=True，並填入 name"""
```

---

## B9. 先粗後細重排

**要做什麼**：全球用 200 m 尺度選出前 50 名之後，對有細地形資料的目標，用更細的尺度重新算坡度和粗糙度，再排一次。

**為什麼**：火星全球最細只有 200 m，看不出小尺度地形。但 Jezero 有 20 m、Gale 有 30 m 的地形資料，可以只對前幾名做細的比較。這樣「任何地點都能算」和「重點地點更精確」兩邊都顧到。

**怎麼做**：
- 火星端用 IanChen 準備的細地形（見 TASK_A 的 A8）。
- 地球端把前 50 名的 Copernicus 30 m 地形，粗化到和火星相同的尺度（約 20～30 m），重算坡度、粗糙度，其他變數不變，重新算總分。
- Arcadia 沒有細地形，維持 200 m，在結果裡註明。

---

## B10. 輸出結果檔

**要做什麼**：把每個目標、每種任務的結果存成固定格式的檔案，之後交給負責前後端的成員，也是簡報的素材。

**每個地點要附**：總分、信心度、每一項的單項分數、是不是已知類比地、**哪裡不像**（例如「仍比 Jezero 暖 23 °C」），以及地球無法模擬的項目（重力、氣壓、輻射、大氣成分）。

**技術細節**：
- 格式照 `PROJECT_CONTEXT.md` 第 7.1 節。其中這兩個欄位是這次新增的：
  - `breaks`：單項分數低於 0.3 的變數，附絕對差距，例如 `{"variable": "temperature", "earth": -26.7, "mars": -49.5, "unit": "C"}`
  - `worldview_url`：這個地點的 NASA Worldview 連結
- 熱度圖：全球網格總分，PNG 給前端顯示，GeoTIFF 視需要。
- 對外介面（給後端）：

```python
def score(target_lat: float, target_lon: float, radius_km: float = 25,
          mission: str | None = "geology", weights: dict | None = None, top_n: int = 20) -> dict:
    """任意火星座標 → IanChen 的 extract_mars_features → similarity_vector → aggregate → 7.1 格式"""
```

- 一鍵流程：

```
python scripts/run_pipeline.py --stage earth     # 重建地球網格
python scripts/run_pipeline.py --stage mars      # 呼叫 IanChen 的 build_targets
python scripts/run_pipeline.py --stage validate  # 驗證、比較算法
python scripts/run_pipeline.py --stage learn     # 學權重
python scripts/run_pipeline.py --stage export    # 所有目標 × 任務輸出
python scripts/run_pipeline.py --stage all
```

---

## B11. 規劃最後的呈現

**要做什麼**：決定簡報要放什麼，並準備展示用的圖。

**建議放的內容**：
1. **問題**：為什麼需要地球類比地，為什麼現在多半「憑名氣」挑。
2. **方法**：一張流程圖（地球網格、火星目標 → 單項相似度 → 依任務加權 → 驗證），說明哪裡是數字計算、哪裡用到機器學習。
3. **結果**：Jezero、Arcadia 各一張全球熱度圖，加上前 5 名的單項分數拆解（哪裡像、哪裡不像）。
4. **新發現**：前幾名新候選地的 Worldview 衛星影像。
5. **可信度**：AUC、留一法、算法比較的結果。
6. **限制**：地球無法模擬的項目（重力、氣壓、輻射），以及 200 m 解析度的限制。

---

## B12. （選做）加分項目

主流程完成後才做：
- **地形外觀相似度**：用預訓練的影像模型（例如 DINOv2，不用訓練）把地形影像轉成向量，比相似度，當成額外一個變數。火星用 5 m 的 CTX 全球影像，地球用 Sentinel-2 或 Landsat。只對前幾百名計算。
- **反向查詢**：輸入地球座標，回傳它最像火星的哪些地方。
- **雷達影像展示**：官方夥伴資料很強調 SAR 雷達（CSA RADARSAT、ESA Sentinel-1）。可以拿來展示前幾名候選地，但火星沒有對應的全球雷達影像，所以不當計分變數。

---

## 時程與交接

| 時間 | 你交給 IanChen | IanChen 交給你 |
|---|---|---|
| 11/13 晚上 | 地球網格的欄位清單 | 三個目標的座標 |
| 11/14 中午 | 第一版排名，讓他檢查火星數值合不合理 | 三個目標的數值、火星百分位表 |
| 11/14 晚上 | 驗證結果 | 岩石相似度表、已知類比地清單 |
| 11/15 | 最終結果 | 細地形資料（選做）、火星資料出處 |

## 請不要做的事

- **不要改 IanChen 的檔案**：`mars_features.py`、`adapters/mars/`、`data/labels/`、`data/mappings/`。有問題直接跟他講。
- **輸出格式定案後，欄位不刪不改名**，只能往後加，不然前端會壞。
- **沒資料就標沒資料**：設 coverage = false，不要填 0。
- **不要用深度學習學權重**：資料太少。
- **不要把大檔案 commit 進 git**：parquet、tif 已經設定成不會被加入。
