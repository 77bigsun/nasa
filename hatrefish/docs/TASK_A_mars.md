# 任務 A：火星端＋評估

> 給 A 本人與 A 的 AI 助手。開始前先讀 `docs/PROJECT_CONTEXT.md`，所有規格以它為準。
> 你負責：火星資料、火星特徵擷取、對照表與標註資料、驗證、權重學習、新候選標記。
> 你**不**負責：地球網格、相似度函數、計分、匯出（這些是 B 的）。

## 你的產出一覽

| 產出 | 路徑 | 誰會用 | 期限 |
|---|---|---|---|
| 火星目標清單 | `config/targets.yaml` | A、B | 11/10 |
| 火星變數讀取函式 | `src/mars_analog/adapters/mars/*.py` | A | 11/11 |
| 火星特徵擷取器 | `src/mars_analog/mars_features.py` | B、後端 | 11/11 |
| 火星端百分位參考 | `data/processed/mars_reference_pct.json` | A | 11/11 |
| 目標特徵檔 | `data/processed/mars_targets.json` | B | 11/11 晚上 |
| 岩性對照表 | `data/mappings/lithology_mars_to_glim.csv` | B | 11/11 |
| 已知類比地標註表 | `data/labels/known_analogs.csv` | A、B | 11/11 |
| 驗證模組 | `src/mars_analog/validate.py` | A | 11/12 |
| 權重學習 | `src/mars_analog/learn_weights.py` → `config/weights_learned.json` | B | 11/12 |
| 新候選標記 | `src/mars_analog/novelty.py` | B | 11/12 |
| 資料引用 | `docs/DATA_SOURCES.md`（火星部分） | 全隊 | 持續 |

---

## A1. 火星目標清單 `config/targets.yaml`

先做 2–3 個目標，主流程穩了再加。座標是概略值，**請查證後再填**（可用 NASA Mars Trek 或 USGS Gazetteer）。

```yaml
targets:
  - id: jezero
    name: Jezero Crater
    lat: 18.4        # 待查證
    lon: 77.5        # 東經，-180~180
    radius_km: 25
    note: 古湖泊三角洲、碳酸鹽，適合地質探勘
  - id: arcadia
    name: Arcadia Planitia
    lat: 47.2        # 待查證（選 SWIM 高冰一致性區域內的一點）
    lon: -175.7
    radius_km: 50
    note: 中緯度地下冰、地形平坦，載人基地候選
  - id: gale
    name: Gale Crater
    lat: -5.4        # 待查證
    lon: 137.8
    radius_km: 25
    note: 層狀沉積（Mount Sharp）
```

**驗收**：每個目標都有來源可查的座標，經度統一為 −180～180。

## A2. 火星資料下載與讀取函式

每個變數一個檔案，放在 `src/mars_analog/adapters/mars/`，用 registry 註冊（見 PROJECT_CONTEXT 第 6 節）。每個函式的介面：

```python
def load(lat: float, lon: float, radius_km: float, cfg: dict) -> dict:
    """回傳 {"value": float|str|None, "coverage": bool, "source": str, "n_pixels": int}"""
```

| 變數 | 檔案 | 資料 | 做法 | 注意 |
|---|---|---|---|---|
| slope | `slope.py` | MOLA＋HRSC 融合 DEM 200 m（USGS Astrogeology） | 裁切目標圓內，算坡度，取中位數（度） | 檔案約 11 GB，**用 rasterio window 只讀需要的範圍**，或改用 JMARS 匯出的 200 m 坡度圖 |
| roughness | `roughness.py` | 同上 | 1 km 視窗（5×5 像素）高程標準差，再取目標內中位數 | 要和 B 的地球端用**完全相同的視窗定義** |
| thermal_inertia | `thermal_inertia.py` | THEMIS 熱慣量定量版 100 m（±60°）；高緯度用 TES 3 km | 目標內中位數 | 60° 以上 THEMIS 無資料，改用 TES；兩者都沒有時 coverage = false |
| lithology | `lithology.py` | USGS 火星地質圖 SIM 3292（Shapefile） | 目標中心點所在的地質單元代碼；面積最大的單元優先 | Robinson 投影、Mars 2000 球體，讀進來先轉經緯度 |
| ice | `ice.py` | SWIM 冰一致性圖（swim.psi.edu）；中子譜儀含水量補 SWIM 範圍外 | 目標內平均，換算 p = (SWIM+1)/2 | SWIM 只有中緯度；範圍外用中子譜儀時要另外定義換算方式並寫進註解 |
| temperature | `temperature.py` | Mars Climate Database v6.1 | 目標座標的年均地表溫度（K → °C） | 先用網頁介面查值即可；有時間再用 MCD 的 Python 介面 |
| aridity | `aridity.py` | 無（定義為極乾） | 固定回傳 `{"value": "max", "coverage": true}` | |
| barrenness | `barrenness.py` | 無（定義為無植被） | 固定回傳 NDVI = 0 | |
| dust | `dust.py` | MCD 沙塵柱光學厚度（年均） | 目標座標的年均值 | |

每個 adapter 檔案開頭要寫資料來源與引用格式的註解。

**驗收**：對三個目標各跑一次所有 adapter，沒有例外錯誤；缺資料時正確回傳 coverage = false。

## A3. 火星端百分位參考 `data/processed/mars_reference_pct.json`

B 類變數（熱慣量、沙塵）要用「在火星上的百分位」。做法：

1. 在火星全球（熱慣量限 ±60°）隨機抽樣約 5,000 個點，或直接用全球網格。
2. 對每個 B 類變數存下分位點（0、1、2…100 百分位的數值）。

```json
{ "thermal_inertia": { "unit": "tiu", "quantiles": [/* 101 個值 */] },
  "dust": { "unit": "tau", "quantiles": [/* 101 個值 */] } }
```

`mars_features.py` 用這份表把目標的原始值轉成百分位 `pct`。

## A4. 火星特徵擷取器 `src/mars_analog/mars_features.py`

```python
def extract_mars_features(lat: float, lon: float, radius_km: float = 25) -> dict:
    """
    回傳：
    {
      "slope":           {"value": 2.1,  "pct": None, "coverage": True,  "source": "hrsc_mola_200m"},
      "thermal_inertia": {"value": 310,  "pct": 0.62, "coverage": True,  "source": "themis_ti"},
      "lithology":       {"value": "AHv", "glim": "vb", "coverage": True, "source": "sim3292"},
      "ice":             {"value": 0.6,  "p": 0.8,   "coverage": True,  "source": "swim"},
      ...
    }
    """

def build_targets(path="config/targets.yaml") -> None:
    """對 targets.yaml 每個目標呼叫 extract_mars_features，寫出 data/processed/mars_targets.json"""
```

- 這個函式是「任意火星座標都能判斷」的核心。後端的互動功能會直接呼叫它，所以**不能依賴手動輸入的數值**。
- 欄位名稱必須和 `config/features.yaml` 的變數名稱一致。

**驗收**：
- `build_targets()` 產出的 `mars_targets.json` 包含三個目標、9 個變數。
- 隨便輸入一個火星座標（例如 0, 0）也能回傳結果，缺資料的變數 coverage = false。

**先交假資料**：11/10 前先手寫一份格式正確的 `mars_targets.json` 給 B，讓 B 能先跑計分流程。

## A5. 岩性對照表 `data/mappings/lithology_mars_to_glim.csv`

USGS 火星地質圖的單元是「年代＋成因」分類，GLiM 是岩石類型分類，所以要做一張相似度對照表：

```csv
mars_unit_group,description,glim_class,similarity,rationale
volcanic,火山單元（玄武岩質為主）,vb,1.0,基性火山岩
volcanic,火山單元,va,0.6,酸性火山岩，化學組成不同
volcanic,火山單元,pb,0.6,基性深成岩，成分接近但產狀不同
basin_sediment,盆地與平原沉積,su,0.8,未固結沉積物
basin_sediment,盆地與平原沉積,ss,0.7,碎屑沉積岩
basin_sediment,盆地與平原沉積,ev,0.7,蒸發岩（對應鹽類沉積）
...
```

步驟：
1. 把 SIM 3292 的地質單元歸成幾個大類（火山、高地、盆地沉積、極地沉積、撞擊相關等），記錄在 `mars_unit_group` 的對照中。
2. 列出 GLiM 第一層的 16 個岩性類別。
3. 為每個「火星大類 × GLiM 類別」給 0–1 的分數，並寫一句理由。
4. 沒列出的組合預設 0.1。

**驗收**：B 能用 `(mars_unit_group, glim_class)` 查到分數；每一列都有理由。

## A6. 已知類比地標註表 `data/labels/known_analogs.csv`

這張表同時是**訓練資料、驗證基準、新候選過濾器**，是整個專案的關鍵。

```csv
site_id,name,lat,lon,radius_km,analog_for,mars_target_ids,missions,reference_url,verified
atacama_yungay,Atacama Desert (Yungay),-24.08,-69.92,30,Mars hyper-arid surface,"jezero;gale","geology;rover",<url>,false
haughton,Haughton Crater (Devon Island),75.38,-89.68,15,Mars impact crater / polar desert,"jezero;gale","geology;rover",<url>,false
mcmurdo_dry_valleys,McMurdo Dry Valleys,-77.5,162.0,50,Mars cold & dry / ground ice,"arcadia","isru_base;geology",<url>,false
mdrs_utah,Mars Desert Research Station,38.41,-110.79,20,Mars mission analog,"gale","rover",<url>,false
mauna_kea,Mauna Kea,19.82,-155.47,15,ISRU / volcanic regolith,"","isru_base",<url>,false
...
```

- 初始清單至少包含影片點名的：阿塔卡馬、南極（乾谷）、冰島、夏威夷、莫哈維、死亡谷、Haughton。再加上 Rio Tinto、斯瓦爾巴、猶他 MDRS、Black Point 熔岩流、Dhofar（Oman）等文獻常見地點。目標 25–40 筆。
- 上面的座標是概略值，**每筆都要查證，查證後把 `verified` 改成 true**，並附參考連結。
- `missions` 標註文獻中這個地點用於哪種任務，權重學習會用到。

**驗收**：至少 25 筆、全部 verified、每筆都有參考連結。

## A7. 驗證模組 `src/mars_analog/validate.py`

依賴 B 的 `similarity.py` 與 `scoring.py`（用 B 的介面，不要自己重寫計分）。

```python
def evaluate(target_id: str, mission: str, weights: dict | None = None) -> dict:
    """回傳 {"auc": float, "recall_at_1pct": float, "recall_at_5pct": float,
             "known_ranks": {site_id: rank_percentile}}"""

def leave_one_site_out(mission: str) -> dict:
    """每次拿掉一個已知類比地重新學權重，看它能否被排回前 5%"""

def sensitivity(target_id: str, mission: str, delta: float = 0.2) -> dict:
    """每個權重 ±20%，回傳前 10 名的重疊率（Jaccard）"""
```

- 正樣本：標註表中 `mars_target_ids` 包含該目標的地點（落在哪些網格就用那些格）。
- 負樣本：隨機陸地網格（正樣本數的 10 倍）＋高 NDVI 網格（雨林、農地）作為困難負樣本。
- 主要指標：AUC、已知類比地落在前 1% 與 5% 的比例。

**驗收**：輸出一份 `outputs/validation_report.json`，並在 README 寫一段結果摘要。

## A8. 權重學習 `src/mars_analog/learn_weights.py`

因為總分是加權幾何平均，ln S = Σ w_i ln s_i，所以**用 ln(s_i) 當特徵做邏輯回歸，學到的係數就能直接對應到權重**。

步驟：
1. 用 B 的 `similarity_vector()` 取得正負樣本的 9 維單項相似度，取 ln（下限 0.01）。
2. 用帶 L2 正則化的邏輯回歸，係數限制 ≥ 0（sklearn 不支援非負限制，可用 `scipy.optimize.minimize` 搭配 bounds 自己寫，或訓練完把負係數設為 0）。
3. 係數正規化成總和 1，得到「資料驅動權重」 `w_learned`。
4. 與任務先驗混合：`w_final[m] ∝ w_prior[m] ⊙ w_learned`（逐項相乘後正規化）。標註表中某任務的樣本夠多（≥ 10 筆）時，才另外學該任務專屬的權重。
5. 寫入 `config/weights_learned.json`：

```json
{ "method": "logreg_l2_nonneg_logs", "trained_at": "...", "n_pos": 30, "n_neg": 300,
  "learned_global": { "slope": 0.12, "...": "..." },
  "final": { "geology": { "...": "..." }, "rover": { "...": "..." },
             "isru_base": { "...": "..." }, "landing": { "...": "..." } } }
```

**注意**：正樣本只有幾十筆，只能用簡單模型，**不要用深度網路**。已知類比地也偏向交通方便的地點，所以學到的權重只用來修正先驗，不完全取代。

**驗收**：`final` 的每個任務權重總和 = 1；用 `final` 權重跑出來的 AUC 不低於先驗權重（若較低，報告中說明並保留先驗）。

## A9. 新候選標記 `src/mars_analog/novelty.py`

```python
def flag_known(results: pd.DataFrame, buffer_km: float = 50) -> pd.DataFrame:
    """距離任何已知類比地 buffer_km 以內的網格標 known_analog=True，並填入 name"""
```

- 前 N 名中 `known_analog = False` 的就是「新候選」。
- 對每個目標的前 3 名新候選，用 NASA Worldview 看衛星影像，確認不是資料錯誤（例如雲、水體、城市），把結論寫在 `outputs/new_candidates.md`。

## A10. 11/13 換資料

官方 Resources 公布後：
1. 列出官方清單中和火星有關的每個資料集，對照第 A2 節的 9 個變數。
2. 已在用的不動；同一變數有官方資料的，新增 adapter source、改 `features.yaml`；新變數先跟 B 討論要不要加。
3. 重跑 `build_targets()`、驗證、權重學習。

## 和 B 的協作點

| 時間 | 你交給 B | B 交給你 |
|---|---|---|
| 11/10 | 假資料版 `mars_targets.json`、`targets.yaml` | `similarity_vector()`、`aggregate()` 介面（可先回傳假值） |
| 11/11 | 真實 `mars_targets.json`、岩性對照表、標註表 | 地球網格第一版 |
| 11/12 | `weights_learned.json`、`novelty.py` | 完整計分流程 |

## 不要做的事

- 不要改 B 的檔案（`earth_grid.py`、`similarity.py`、`scoring.py`、`export.py`、`adapters/earth/`）。
- 不要自己寫另一套計分公式，一律呼叫 B 的模組。
- 缺資料不要補 0 或平均值，設 coverage = false。
- 不要把大型原始資料 commit 進 git。
