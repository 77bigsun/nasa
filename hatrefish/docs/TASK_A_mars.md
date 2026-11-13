# 任務 A：火星端（IanChen）

> 這份文件給 IanChen 本人，也給他的 AI 助手。
> 每個任務前半段是白話說明（要做什麼、為什麼）；標著「**技術細節**」的部分是寫程式時要看的。
> 整體規格以 `docs/PROJECT_CONTEXT.md` 為準。最後更新：11/13。

---

## 一句話說明你的工作

我們要回答「地球上哪裡最像火星的某個地點」。要比較，得先知道火星那個地點是什麼樣子：坡有多陡、地面是沙還是岩石、地下有沒有冰、有多冷、沙塵多不多、是什麼岩石。

**你的工作，就是把這些火星資料從衛星資料裡讀出來，整理成一份數字表，交給 B 去跟地球比。** 另外還有兩份參考資料要整理：「岩石種類相似度表」和「已知類比地清單」。

## 分工

| 你負責 | 你不用做（B 負責） |
|---|---|
| 決定火星目標的座標 | 地球的資料和全球網格 |
| 寫火星擷取器，讀出火星各項數值 | 相似度和總分的計算 |
| 火星百分位表 | 驗證（AUC）、學權重 |
| 岩石種類相似度表 | 標記哪些是新發現的候選地 |
| 已知類比地清單 | |
| 火星資料的引用出處 | |

你之前做的 12 個地球點（`IanChen/` 資料夾）**保留當驗證用**，不用再增加地球欄位。B 會做全球網格，涵蓋整個地球。

## 這次改了什麼（11/13）

- **官方資料清單公布了**，但只列了資料網站入口（NASA 的 Earthdata、Worldview、PDS 等），沒有指定要用哪份資料。所以我們不用換資料，只要把每個資料的出處寫清楚。
- **熱慣量統一用 TES 全球圖**。目標的數值和百分位表要用同一份資料，比較才公平。
- **新增「日溫差」欄位**：先把數值算出來，要不要計分之後再決定。
- **岩石種類不再混入永凍土**：冰已經有自己的變數，岩性裡再算一次等於重複計分。
- **已知類比地要至少 20 個**，不然學權重和驗證的數字不可靠。
- **火星數值一律從資料算出來**，不要手動輸入預設值。

## 名詞小抄

| 名詞 | 意思 |
|---|---|
| 目標 | 火星上要拿來比對的地點：Jezero、Gale、Arcadia |
| 擷取器 | 一個函式：給它火星座標，它就去讀各種衛星資料，回傳那個地點的各項數值 |
| coverage | 這個變數有沒有資料。沒資料就填 `false`，**不要硬填 0** |
| 百分位 | 某個數值在整個星球上排第幾。0.9 代表比 90% 的地方高 |
| 熱慣量 | 地面溫度變化的快慢。細沙低（白天燙、晚上冰），岩石高。可以用來判斷地面是沙還是石頭 |
| DEM | 高程資料，用來算坡度和地面起伏 |
| TES | NASA 衛星做的火星全球熱慣量地圖 |
| SWIM | 火星地下冰地圖。數值 −1 代表很可能沒冰，+1 代表很可能有冰 |
| MCD | Mars Climate Database，火星氣候模型，可以查任何地點的溫度和沙塵 |
| SIM3292 | USGS 的火星全球地質圖，標出每塊區域屬於哪種地質單元 |
| GLiM | 地球全球岩性地圖，把岩石分成 16 類 |

## 任務總覽

| 編號 | 任務 | 產出檔案 | 期限 |
|---|---|---|---|
| A1 | 決定三個目標的座標 | `config/targets.yaml` | 11/13 晚上 |
| A2 | 寫火星擷取器 | `src/mars_analog/mars_features.py` 等 | 11/14 中午 |
| A3 | 做火星百分位表 | `data/processed/mars_reference_pct.json` | 11/14 中午 |
| A4 | 輸出三個目標的數值 | `data/processed/mars_targets.json` | 11/14 中午 |
| A5 | 做岩石種類相似度表 | `data/mappings/` 底下兩個 csv | 11/14 晚上 |
| A6 | 擴充已知類比地清單 | `data/labels/known_analogs.csv` | 11/14 晚上 |
| A7 | 整理火星資料出處 | `docs/DATA_SOURCES.md` | 持續更新 |
| A8 | （選做）找更細的地形資料 | 見 A8 | 11/15 |

**建議順序**：A1 → A2 → A3、A4。A5 和 A6 不需要寫程式，可以穿插著做，或在等程式跑的時候做。

---

## A1. 決定三個火星目標的座標

**要做什麼**：替 Jezero、Gale、Arcadia 各決定一個中心點座標和範圍半徑，並寫明這個座標是從哪裡來的。

**為什麼重要**：擷取器會以這個座標為中心，讀取周圍一圈的資料來算數值。**座標一換，所有數值都會跟著變**，地球端的比對結果也會跟著變。所以兩個人一定要用同一組座標。

**目前的狀況**：

| 目標 | 你的版本 | 原本 targets.yaml 的版本 | 要做的事 |
|---|---|---|---|
| Jezero | 18.38, 77.58 | 18.4, 77.5 | 只差約 5 km，選一個並寫出處 |
| Arcadia | 39.2, 172.0 | 47.2, −175.7 | **兩點相距約 700 km，是不同地點，要決定用哪個** |
| Gale | 還沒有 | −5.4, 137.8 | 要補上並查證 |

**怎麼選**：座標要能代表這個目標「想拿來比的特色」。

- **Jezero**：選古代三角洲沉積的位置，對應地質探勘任務。
- **Arcadia**：選地下淺層冰最明確的位置，對應建基地、取冰任務。建議挑 SWIM 冰地圖上數值高的點，最好引用論文裡的載人登陸候選區。
- **Gale**：選 Curiosity 探測車的探索區，或 Mount Sharp 山腳。
- **半徑**：一般用 25 km。Arcadia 是一大片平原，可以用 50 km。

**完成的標準**：三個目標都有座標、半徑和出處連結。

**技術細節**：經度統一用 −180～180（東經為正）。格式：

```yaml
targets:
  - id: jezero
    name: Jezero Crater delta
    lat: 18.38
    lon: 77.58
    radius_km: 25
    missions: [geology, rover]
    source: <出處連結>
  - id: arcadia
    name: Arcadia Planitia (shallow ice)
    lat: <待決定>
    lon: <待決定>
    radius_km: 50
    missions: [isru_base, landing]
    source: <出處連結>
  - id: gale
    name: Gale Crater
    lat: <待查證>
    lon: <待查證>
    radius_km: 25
    missions: [geology, rover]
    source: <出處連結>
```

---

## A2. 寫火星擷取器

**要做什麼**：寫一個函式，輸入火星座標和半徑，輸出這個地點的各項數值。

**為什麼重要**：題目要求「遇到新的地點也能判斷」。有了擷取器，任何火星座標丟進去都能自動算出數值，不用靠人工查。這也是後端互動功能會直接呼叫的東西。

**要讀出的數值**：

| 變數 | 代表什麼 | 資料來源 |
|---|---|---|
| 坡度 `slope` | 地面有多陡 | 火星高程資料（200 m 解析度） |
| 粗糙度 `roughness` | 地面高低起伏多不多 | 同上 |
| 熱慣量 `thermal_inertia` | 地面是細沙還是岩石 | TES 熱慣量地圖 |
| 岩性 `lithology` | 屬於哪種地質單元 | SIM3292 地質圖 |
| 冰 `ice` | 地下有沒有冰 | SWIM 冰地圖 |
| 溫度 `temperature` | 年平均地表溫度 | MCD 氣候模型 |
| 日溫差 `diurnal_range`（新增） | 一天之中最熱減最冷 | MCD 氣候模型 |
| 沙塵 `dust` | 大氣中的沙塵量 | MCD 氣候模型 |
| 乾燥度 `aridity` | 不用讀，火星固定是極乾 | — |
| 荒蕪度 `barrenness` | 不用讀，火星固定沒有植被 | — |

**用來檢查程式的參考值**（我們之前實際測過的）：

| | Jezero | Gale | Arcadia（47.2, −175.7） |
|---|---|---|---|
| 熱慣量 | 281 | 433 | 241 |
| SWIM 冰 | −0.19 | 0.06 | 0.51 |
| 年均地表溫度 | −49.5 °C | −50.9 °C | −75.9 °C |
| 沙塵（在火星排第幾） | 0.55（0.87） | 0.46（0.73） | 0.35（0.42） |

Jezero 的坡度：之前用 200 m 資料測到中位數約 1.9°，你量到的是 3.15°，差在取的範圍和算法不同。A1 決定半徑後，以擷取器算出來的為準。

**完成的標準**：
- 三個目標的每個變數都有數值，或標記為沒資料（coverage = false）。
- 隨便輸入一個座標（例如 0, 0）也能跑完不出錯。

**技術細節**：

每個變數寫成一個檔案，放在 `src/mars_analog/adapters/mars/`，統一介面：

```python
def load(lat: float, lon: float, radius_km: float, cfg: dict) -> dict:
    """回傳 {"value": float|str|None, "coverage": bool, "source": str, "n_pixels": int}"""
```

| 變數 | 讀法 | 注意事項 |
|---|---|---|
| slope | GDAL 遠端讀，不用下載 11 GB：`/vsicurl/https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif` | 座標單位是度。算坡度時，東西方向的像素距離要乘 cos(緯度)。範例在 `scripts/check_env.py`，記得先 `dem.astype("float64").filled(np.nan)` |
| roughness | 同一份 DEM。5×5 像素（1 km）視窗內的高程標準差，再取範圍內中位數 | 視窗大小要和地球端完全一樣 |
| thermal_inertia | 下載 `global_ti_night_2007.img` 和 `.lbl`：https://pds-geosciences.wustl.edu/mgs/mgs-m-tes-5-timap-v1/mgst_9001/data/ ，用 GDAL 開 `.lbl` | ⚠ repo 裡現在的 `global_ti_msk_night_2007` 是**遮罩檔**，不是熱慣量，要重新下載。投影單位是公尺：x = R·經度(弧度)，R = 3396000 |
| lithology | `data/raw/sim3292_database/` 裡的 `SIM3292_Global_Geology.shp`，欄位 `Unit` | 地圖是 Robinson 投影。先把點用 `+proj=longlat +R=3396190 +no_defs` 轉過去，再判斷落在哪個區塊。回傳 Unit 代碼和 A5 的大類 |
| ice | GDAL 遠端讀：`https://swim.psi.edu/output/SWIM4MIM/Global/Composite/SWIM4MIM_Ci_0_1.tif` | 投影單位是公尺，R = 3396190。經度範圍是 −180～180（網站寫 0–360 是錯的）。−30 代表沒資料。另外輸出 p = (數值+1)/2 |
| temperature | 用 `scripts/fetch_mcd.py`（tsurf，季節和時間都選 all） | 輸出 °C |
| diurnal_range | 同一張溫度表：每個季節取最高減最低，再對所有季節取平均 | 先算出來，計分權重暫時是 0 |
| dust | `fetch_mcd.py` 已經有沙塵年平均 | 同時輸出原始數值和火星百分位 |
| aridity | 固定回傳 `{"value": "max", "coverage": true}` | |
| barrenness | 固定回傳 NDVI = 0 | |

每個檔案開頭用註解寫上資料來源和引用格式。

---

## A3. 做火星百分位表

**要做什麼**：算出「熱慣量」和「沙塵」在整個火星上的分布，存成一張表，之後就能查任何數值在火星上排第幾。

**為什麼需要**：火星和地球的熱慣量是用不同方法量的，單位不同，不能直接相減。所以改比「在各自星球上排第幾」。例如 Jezero 的熱慣量如果比火星 55% 的地方高，就去找地球上也比 55% 的地方高的位置。

**只有這兩個變數需要**。溫度、日溫差、乾燥度不需要，因為火星比地球任何地方都冷、都乾，直接找地球上最冷、最乾的地方就好。

**技術細節**：
- 熱慣量：用 TES 全球圖所有有資料的像素。越靠近兩極，一格代表的面積越小，所以每格要乘 cos(緯度) 當權重，排名才公平。
- 沙塵：`fetch_mcd.py` 已經算好全球的面積加權百分位，直接轉存。
- 格式：

```json
{ "thermal_inertia": { "unit": "tiu", "source": "tes_night_2007", "quantiles": [/* 第 0 到第 100 百分位，共 101 個數字 */] },
  "dust": { "unit": "tau", "source": "mcd_v6.2_tauref_annual", "quantiles": [/* 101 個數字 */] } }
```

---

## A4. 輸出三個目標的數值

**要做什麼**：用擷取器跑完三個目標，把結果存成一個檔案交給 B。B 的比對程式會直接讀這個檔案。

**完成的標準**：檔案裡有三個目標，每個目標都有 10 個欄位（9 個變數加上日溫差）。

**技術細節**：

```python
def extract_mars_features(lat: float, lon: float, radius_km: float = 25) -> dict: ...
def build_targets(path="config/targets.yaml") -> None:
    """對 targets.yaml 每個目標呼叫 extract_mars_features，寫出 data/processed/mars_targets.json"""
```

- 每個變數至少要有 `value`、`coverage`、`source`。
- 熱慣量和沙塵另外加 `pct`（火星百分位），冰另外加 `p`，岩性另外加 `group`（A5 的大類）。
- 變數名稱要和 `config/features.yaml` 一致。

---

## A5. 做岩石種類相似度表

**要做什麼**：做一張表，寫出「某種火星岩石」和「某種地球岩石」有多像，分數從 0 到 1，每一格附一句理由。

**為什麼需要**：坡度這種數字可以直接相減比較，但岩石種類是類別，「玄武岩」減「砂岩」沒有意義。所以要事先定好每一對有多像。例如火星的玄武岩對地球的玄武岩是 1.0，對地球的碳酸鹽岩只有 0.1。

**為什麼要拿掉永凍土**：你原本的分類有 `basalt_permafrost`、`clastic_permafrost`。但冰已經有自己的變數了，岩性裡再算一次，冰就被重複計分。所以岩性只管岩石，冰交給冰的變數。

**步驟**：
1. **把火星地質單元分成幾個大類**：SIM3292 地質圖有很多地質單元代碼，把每個代碼歸到一個大類。大類名稱可以沿用你原本的詞彙（拿掉 `_permafrost`），例如：玄武岩 `basalt`、碎屑岩 `clastic`、泥岩 `mudstone_clastic`、硫酸鹽蒸發岩 `evaporite_sulfate_clastic`、撞擊角礫岩 `impact_breccia_carbonate`、碳酸鹽黏土沉積 `sedimentary_carbonate_clay`、熱液硫酸鹽 `hydrothermal_sulfate`。需要的話加極地層狀沉積 `polar_layered`。
2. **給每一對打分數**：每個火星大類對 GLiM 的每個地球類別，給 0–1 的分數和一句理由。沒寫到的組合預設 0.1。

GLiM 的 16 個地球岩石類別：

| 代碼 | 意思 | 代碼 | 意思 |
|---|---|---|---|
| su | 未固結沉積物 | pa | 酸性深成岩 |
| ss | 碎屑沉積岩 | pi | 中性深成岩 |
| sm | 混合沉積岩 | pb | 基性深成岩 |
| sc | 碳酸鹽沉積岩 | va | 酸性火山岩 |
| py | 火山碎屑岩 | vi | 中性火山岩 |
| ev | 蒸發岩 | vb | 基性火山岩（玄武岩） |
| mt | 變質岩 | ig | 冰與冰川 |
| wb | 水體 | nd | 無資料 |

GLiM 分得沒有你的分類那麼細（例如分不出硫酸鹽和碳酸鹽黏土），細的類別就對到最接近的 GLiM 類別，並在理由裡說明。

**完成的標準**：任一組「火星大類＋地球類別」都查得到分數，而且每一列都有理由。

**技術細節**：兩個檔案。

`data/mappings/sim3292_unit_groups.csv`（地質單元 → 大類）：

```csv
unit,unit_desc,mars_group
<SIM3292 的 Unit 代碼>,<UnitDesc>,basalt
...
```

`data/mappings/lithology_mars_to_glim.csv`（大類 × 地球類別 → 分數）：

```csv
mars_group,glim_class,similarity,rationale
basalt,vb,1.0,同為基性火山岩
basalt,pb,0.6,成分接近，但是深成岩
sedimentary_carbonate_clay,sm,0.8,混合沉積岩，可含碳酸鹽與黏土
sedimentary_carbonate_clay,sc,0.7,碳酸鹽沉積岩
evaporite_sulfate_clastic,ev,0.9,蒸發岩
...
```

---

## A6. 擴充已知類比地清單

**要做什麼**：整理一份清單，列出科學家已經公認、或已經拿來做過火星測試的地球地點，至少 20 個，每個都附參考資料。

**為什麼重要**：這份清單有三個用途。
1. **檢查我們的方法準不準**：如果方法是對的，這些公認的類比地應該會排在前面。
2. **學權重**：從這些地點學出哪些變數比較重要。
3. **找出新地點**：排名前面、但不在清單上的，就是我們「新發現」的候選地，這正是題目最想看到的。

**怎麼做**：
- 先放你已經有的 6 個：Atacama、McMurdo 乾谷、Haughton 隕石坑、MDRS 猶他、Black Point 熔岩流、冰島 Askja。
- 再從論文、NASA 網頁補充。可以從這些查起：Rio Tinto（西班牙）、Svalbard（挪威）、Mauna Kea（夏威夷）、Lanzarote（西班牙）、Pilbara（澳洲）、Death Valley、Mojave（美國）、Lonar 隕石坑（印度）、Ries 隕石坑（德國）、Dhofar（阿曼）。**每個都要自己確認**有文獻支持。
- 寫出每個地點被用來模擬什麼、適合哪種任務。

不像火星的「反例地點」（例如雨林、農田）由 B 從地球網格隨機抽，你不用做。

**完成的標準**：至少 20 筆，每筆都有參考連結，而且都確認過（`verified` = true）。

**技術細節**：欄位如下：

```csv
site_id,name,lat,lon,radius_km,analog_for,mars_target_ids,missions,reference_url,verified
atacama_yungay,Atacama Desert (Yungay),-24.08,-69.92,30,hyper-arid surface,"jezero;gale","geology;rover",<url>,true
```

`missions` 填 `geology`（地質探勘）、`rover`（探測車測試）、`isru_base`（基地／取冰）、`landing`（著陸測試）之中的一或多個，用分號隔開。

---

## A7. 整理火星資料出處

**要做什麼**：在 `docs/DATA_SOURCES.md` 寫下每份火星資料的名稱、提供單位、網址和引用格式。

**為什麼**：比賽規定用到的所有資料都要標出處，沒標可能被取消資格。能寫的話，也標出它對應官方資料清單上的哪個入口（火星資料多半是 PDS）。

---

## A8. （選做）找更細的地形資料

**要做什麼**：幫兩個目標準備比 200 m 更細的地形資料。

**為什麼**：火星全球最細的地形資料只有 200 m，看不出小尺度的地形。我們的做法是「先粗後細」：全球先用 200 m 篩出前幾名，再用細的資料重新排一次。

- **Jezero**：20 m（USGS 提供，可自由使用）：https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif 。範圍更大的版本在 USGS 網站，名稱是「Mars 2020 Science Investigation CTX DEM Mosaic」。
- **Gale**：30 m：https://zenodo.org/record/5808354
- **Arcadia**：沒有現成的細資料，維持 200 m，在結果裡註明。

---

## 時程與交接

| 時間 | 你交給 B | B 交給你 |
|---|---|---|
| 11/13 晚上 | 三個目標的座標（A1） | 地球資料的欄位清單 |
| 11/14 中午 | 三個目標的數值（A4）、火星百分位表（A3） | 第一版排名，讓你檢查火星數值合不合理 |
| 11/14 晚上 | 岩石相似度表（A5）、已知類比地清單（A6） | 驗證結果 |
| 11/15 | 細地形資料（A8，選做）、資料出處（A7） | 最終結果 |

## 請不要做的事

- **不要再增加地球欄位**：B 的全球網格會涵蓋整個地球，12 個點留著當驗證就好。
- **不要自己寫比對或計分的程式**：統一用 B 的，不然兩邊結果會對不起來。
- **沒資料就標沒資料**：設 coverage = false，不要填 0 或猜一個數字。填 0 會被當成真的數值，結果就錯了。
- **不要手動輸入火星數值**：一律由擷取器從資料算出來，這樣換任何地點都能用。
- **不要把原始資料 commit 進 git**：檔案太大。`data/raw/`、`.tif`、`.cub`、`.nc` 已經設定成不會被加入。
