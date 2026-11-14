# Agent Prompt：Earth Analog Finder 網站初版（Vue 3 + FastAPI + Docker）

> 使用方式：把整份檔案交給 coding agent（可放在 repo 根目錄的 `docs/SPEC.md`，並告訴 agent「依 docs/SPEC.md 實作」）。

---

## 0. 你的角色與任務

你是資深全端工程師。請依本規格，從零建立一個可在 **localhost** 執行的網站初版：

- 前端：**Vue 3 + Vite + TypeScript**
- 後端：**FastAPI**（Python），拆成多個微服務
- 部署：**Docker Compose** 管理所有服務，一行指令啟動

這是 NASA Space Apps Challenge 2026 的參賽作品原型。**相似度方法是初版，團隊之後會修改**，所以方法程式碼必須集中、模組化、可替換；所有內容（任務、特徵、地點、權重、門檻）都必須來自設定檔，不可寫死在元件裡。

請依第 9 節的順序分階段實作，每完成一個階段就確認可以執行再進下一階段。

---

## 1. 專案背景（理解領域用）

**競賽題目**：Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars。用 NASA 及其他太空機構的公開資料，在地球上找出可作為「月球永久基地候選地」或「火星登陸與探索地點」類比的地點，並說明：

1. 找出哪些地球地點（identify）
2. 用資料說明為什麼相似（characterize）
3. 哪裡類比強、哪裡**不成立**（地球無法重現低重力、真空、稀薄大氣、輻射）
4. 這些地點如何幫助探索任務（連結 NASA 需求）

評審重點：新穎性（避開南極、阿他加馬、冰島、夏威夷、霍頓隕石坑、死亡谷等已知場址）、資料驅動、誠實說明差異、與任務連結、小尺度具體地點。

**我們的做法**：

- 以 NASA 公布的月球基地需求（Moon Base User's Guide）與火星著陸條件（SkyFall 任務）為基準。
- 每個月球／火星**目標地點**底下有 6 項**分支任務（測試項目）**，每項測試由數個**特徵**組成。
- 對地球候選地點逐一計算相似度 → 依 NASA 技術缺口排名加權 → 用**集合覆蓋最佳化**找出「最少地點數」就能涵蓋最多測試的組合。
- 同時輸出「地球無法重現」清單。

---

## 2. 技術架構與 Repo 結構

### 2.1 服務

| 服務 | 技術 | 職責 | 內部埠 |
|---|---|---|---|
| `gateway` | Nginx | 反向代理：`/` → frontend、`/api/catalog/` → catalog、`/api/similarity/` → similarity | 對外 **8080** |
| `frontend` | Vue 3 + Vite + TS | 網站介面 | 80（正式）／5173（開發） |
| `catalog` | FastAPI | 唯一的內容來源：任務、分支任務、特徵、目標地點、地球限制、資料來源、地球基本資料 | 8000 |
| `similarity` | FastAPI + numpy/scipy/pandas/PuLP | 相似度計算、權重、集合覆蓋最佳化、敏感度分析；任務與特徵定義向 `catalog` 取得（HTTP，快取） | 8000 |
| `ingest`（先不實作） | Python worker | 未來下載與處理衛星資料（earthaccess、openEO）。只建立資料夾與 README，compose 中以註解保留 | — |

- 兩個後端服務以唯讀方式掛載 `./data`（`/data:ro`）。
- 不需要資料庫與登入功能。資料存取層請抽象化（repository pattern），日後可換成 PostgreSQL/PostGIS。
- 每個服務都要有 `GET /health`。
- FastAPI 透過 gateway 提供 OpenAPI：`/api/catalog/docs`、`/api/similarity/docs`（設定 `root_path`）。

### 2.2 版本

- Python 3.12（最低 3.11）；Node.js 目前的 LTS（22 以上）。
- 前端套件：vue、vue-router、pinia、vue-i18n、axios、globe.gl（three.js）、leaflet、echarts + vue-echarts。
- 後端套件：fastapi、uvicorn、pydantic v2、numpy、scipy、pandas、pulp、pyyaml、httpx、pytest。
- 使用各套件目前的穩定版本。

### 2.3 Repo 結構

```
analog-finder/
├─ docker-compose.yml              # 正式模式（frontend 打包後由 nginx 提供）
├─ docker-compose.dev.yml          # 開發覆寫：vite dev server、uvicorn --reload、bind mount
├─ .env.example
├─ README.md
├─ docs/
│  ├─ SPEC.md                      # 本檔
│  └─ METHOD.md                    # 相似度方法說明（給團隊與評審）
├─ gateway/nginx.conf
├─ frontend/
├─ services/
│  ├─ catalog/app/{main.py, routers/, models.py, repository.py}
│  ├─ similarity/app/
│  │  ├─ main.py
│  │  ├─ core/                     # ★ 方法全部集中在這裡，團隊之後會改
│  │  │  ├─ scoring.py             # 各特徵類型的相似度函式 + 註冊表
│  │  │  ├─ aggregate.py           # 幾何平均、整體分數
│  │  │  ├─ weights.py             # ROC、等差、自訂
│  │  │  ├─ optimize.py            # 集合覆蓋、最大覆蓋（邊際效益曲線）
│  │  │  ├─ sensitivity.py         # Dirichlet 權重抽樣
│  │  │  ├─ robustness.py          # 馬氏距離交叉檢查
│  │  │  └─ timeseries.py          # 統計量萃取、Wasserstein、TOST
│  │  └─ tests/
│  └─ ingest/README.md
└─ data/
   ├─ README.md                    # 團隊如何替換示範資料
   └─ seed/
      ├─ missions.yaml
      ├─ tasks_moon.yaml
      ├─ tasks_mars.yaml
      ├─ target_sites.yaml
      ├─ earth_limits.yaml
      ├─ data_sources.yaml
      ├─ earth_facts.yaml
      ├─ categorical_tables.yaml
      ├─ method.yaml               # τ、σ、權重方案等預設值
      ├─ target_values.demo.yaml   # 目標地點的特徵值（示範）
      └─ earth_candidates.demo.json# 地球候選地點與特徵值（示範）
```

---

## 3. 使用者流程與頁面

整體風格：深色太空主題、乾淨、易讀，響應式（手機也能用）。介面文字預設**繁體中文**，用 vue-i18n 建立 `zh-TW` 與 `en` 兩種語系（評審可能看英文），右上角可切換。內容字串來自 seed 檔，提供 `name` 與 `name_en` 欄位，缺英文時顯示中文。

### 3.1 主頁 `/`

- **Hero**：自動緩慢旋轉的 3D 地球（globe.gl），使用 NASA Blue Marble 貼圖（公有領域；下載到 `frontend/public/textures/`，標註「Imagery: NASA」）。背景星空。
- 標語：「地球是探索月球與火星最容易取得的實驗室」。
- **地球、月球、火星基本資料對照**（來自 `earth_facts.yaml`，請對照 NASA Planetary Fact Sheet 確認數值並附來源連結：https://nssdc.gsfc.nasa.gov/planetary/factsheet/）：

| 項目 | 地球 | 月球 | 火星 |
|---|---|---|---|
| 重力 | 1 g | 約 0.166 g | 約 0.38 g |
| 一天長度 | 24 小時 | 約 29.5 地球日 | 約 24 小時 39 分 |
| 地表氣壓 | 約 1013 hPa | 幾乎真空 | 約 6 hPa（不到地球 1%） |
| 地表溫度 | 平均約 15°C | 陰影區可低於 -230°C，向陽處超過 100°C | 平均約 -60°C |
| 全球磁場 | 有 | 無 | 無 |

- 簡短說明「類比場址」概念與競賽的四項必要任務。
- 兩張大卡片選單：**月球 Moon**、**火星 Mars** → 點擊進入任務頁。

### 3.2 任務頁 `/:mission`（`moon` 或 `mars`）— 三步驟精靈

頁首顯示：任務目標、NASA 依據摘要、步驟指示器 ① 選分支任務 → ② 選比較地點 → ③ 相似度結果。選擇狀態存在 Pinia，並同步到 URL query（`?tasks=M1,M3&site=moon-scr&tau=0.7&weights=roc`），網址可分享。

**步驟 ①：選分支任務**

- 以卡片列出 6 項分支任務（M1–M6 或 R1–R6），每張卡片顯示：代號與名稱、要驗證什麼、NASA 依據、技術缺口排名與等級、權重（ROC／等差）、手動調整標記（*）與理由、特徵數量、資料來源徽章（✅ 官方 Resources／➕ 補充）。
- 卡片可勾選（預設全選），可展開看特徵清單與注意事項。
- 頁面下方顯示該星球的「地球無法重現的條件」表格。

**步驟 ②：選主要比較的月球／火星地點**

- 列表顯示目標地點：名稱、來源、說明、座標（若有）。有座標的在小地圖上標出；沒有座標的顯示「座標待月球組／火星組填入」。
- 只能選一個作為主要比較地點。
- 若某地點缺少目標特徵值，顯示提示並允許繼續（使用示範值）。

**步驟 ③：相似度結果**

控制列：相似度門檻 τ 滑桿、權重方案切換（ROC／等差／自訂滑桿）、「排除已知類比場址」開關。

1. **各分支任務排名**：每項選中的分支任務一個區塊，列出前 10 名地球候選地點與相似度（0–1），附長條圖。
2. **地點詳情抽屜**：點擊候選地點後顯示：
   - 每個特徵：目標值、候選值、方法類型、分數、資料來源（行星端／地球端、官方或補充）、注意事項
   - **相似之處**（分數 ≥ 0.7）、**不同之處**（分數 < 0.4）、**地球無法重現**（地球限制表 + 超出範圍的特徵）
   - 時間序列特徵：平均週期疊圖（目標 vs 候選，橫軸為相位）與累積分布圖（ECDF），並顯示 Wasserstein 距離
3. **整體排名**：加權整體分數排名 + 地圖（Leaflet，底圖優先用 NASA GIBS 影像圖磚，失敗時改用 OpenStreetMap；請自行確認 GIBS 圖磚網址格式），點的顏色代表分數。
4. **最少測試地點組合**（集合覆蓋）：顯示「最少需要 N 個地點即可涵蓋 X / Y 項分支任務」、地點清單、覆蓋度表（每項任務由哪個地點涵蓋、分數多少）、無法涵蓋的任務。
5. **邊際效益曲線**：k = 1, 2, 3… 個地點的加權涵蓋率折線圖。
6. **敏感度分析**：按鈕觸發，顯示每個地點在隨機權重下被選入的比例（長條圖）。
7. 所有結果區塊旁顯示 NASA 依據連結，對應競賽必要任務 4。

### 3.3 其他頁面

- `/method`：方法說明（從 `docs/METHOD.md` 內容整理成頁面，含公式，用 KaTeX 呈現）。
- `/data`：資料來源總覽（官方 11 項 Resources + 補充來源），標示各資料用在哪些特徵。

### 3.4 示範資料警示

只要任何結果用到 `is_placeholder: true` 的資料，頁面頂端顯示醒目但不刺眼的橫幅：「目前顯示的是示範資料（placeholder），不是真實計算結果」。**不可把示範數值呈現成真實發現。**

---

## 4. 資料模型與種子資料

### 4.1 Schema（Pydantic 模型，YAML/JSON 依此撰寫）

```yaml
# missions.yaml
- id: moon
  name: 月球：永久基地候選地
  name_en: "Moon: Permanent Base Candidates"
  goal: 找出能涵蓋月球南極基地 6 項測試的最少地球地點
  nasa_sources: [{title: ..., url: ...}]

# tasks_moon.yaml（tasks_mars.yaml 同格式）
- id: M1
  mission: moon
  name: 精準安全降落
  verify: 在岩塊、坑洞、陰影中辨識安全著陸點
  nasa_basis: "Moon Base User's Guide「Landing Safely and Accurately」"
  tech_gap: {rank: 27, bin: 3}        # 沒有時為 null
  order: 6                             # 權重排序（1 最重要）
  manual_adjust: null                  # 或 {reason: "..."}
  notes: ["..."]                       # 注意事項，介面要顯示
  features:
    - id: m1_slope
      name: 多尺度坡度、粗糙度
      type: profile                    # threshold | profile | categorical | spectral | timeseries
      compare_mode: absolute           # absolute | relative_rank
      unit: deg
      weight: 1.0                      # 測試內特徵權重（預設相等，團隊之後調整）
      threshold: null                  # threshold 類型用：{ideal_max: 5, zero_at: 15} 或 {zero_at: 100, ideal_min: 150}
      planet_threshold: null           # 只用來檢查目標地點是否合格，不用於地球評分
      out_of_earth_range: false        # true → 不評分，列入「無法重現」
      earth_proxy: false               # 地球端是代理指標時為 true
      planet_data: [{name: LOLA, official: true}]
      earth_data: [{name: Copernicus DEM, official: true}]
      notes: []

# target_sites.yaml
- id: moon-scr
  mission: moon
  name: Shackleton 連接脊
  name_en: Shackleton Connecting Ridge
  source: Moon Base I 目的地（最快 2026 年秋季發射）
  description: 與永久基地關係最直接
  lat: null
  lon: null                            # 東經 0–360 存放；地圖顯示時轉為 -180–180
  coords_status: todo                  # todo | approx | exact

# target_values.demo.yaml
moon-scr:
  is_placeholder: true
  values: {m1_slope: 12.0, ...}        # relative_rank 特徵填百分位 0–1
  spectra: {m5_vswir_mineral: [...]}   # spectral 特徵
  series: {m3_surface_temp: {...}}     # timeseries 特徵

# earth_candidates.demo.json
[{ "id": "demo-01", "name": "Demo-01", "lat": ..., "lon": ...,
   "known_analog": false, "is_placeholder": true,
   "values": {...}, "categories": {...}, "spectra": {...}, "series": {...} }]
```

**示範資料規則**：

- 產生約 20 個地球候選地點，名稱為 `Demo-01`…`Demo-20`，座標落在陸地上，其中約 4 個標 `known_analog: true`（測試排除開關）。
- 數值用固定亂數種子產生、落在合理範圍；時間序列產生簡單的日／季節週期。
- 所有目標值與候選值都標 `is_placeholder: true`。
- `data/README.md` 說明團隊如何用真實資料替換（CSV 或 JSON 格式皆可，附欄位說明）。

### 4.2 月球（mission: `moon`）

**目標地點**（座標全部 `todo`，由月球組填入）

| id | 名稱 | 來源 |
|---|---|---|
| moon-scr | Shackleton 連接脊（Shackleton Connecting Ridge） | Moon Base I 目的地 |
| moon-cabeus-b-peak | Peak near Cabeus B | 阿提米絲候選著陸區（2024 年 10 月） |
| moon-haworth | Haworth | 同上 |
| moon-malapert | Malapert Massif | 同上 |
| moon-mouton-plateau | Mons Mouton Plateau | 同上 |
| moon-mouton | Mons Mouton | 同上 |
| moon-nobile-1 | Nobile Rim 1 | 同上 |
| moon-nobile-2 | Nobile Rim 2 | 同上 |
| moon-degerlache-2 | de Gerlache Rim 2 | 同上 |
| moon-slater | Slater Plain | 同上 |

**NASA 依據摘要**：南極選址理由（架構決策 LD-03-L）為同時接觸近乎連續日照與連續黑暗、古老地形、尚未探索；第一階段能力目標為 5 kW 發電與儲能、撐過 120 小時以上黑暗、時速 10 公里大型探測車、整地展示。

**分支任務**（技術缺口排名來自 NASA《Moon to Mars Architecture Definition Document》Rev C 附錄 D.2，共 57 項、6 等級）

| id | 名稱 | 要驗證什麼 | NASA 依據 | 排名（等級） | order | 手動調整 |
|---|---|---|---|---|---|---|
| M1 | 精準安全降落 | 在岩塊、坑洞、陰影中辨識安全著陸點 | User's Guide「Landing Safely and Accurately」 | 27（3） | 6 | — |
| M2 | 低太陽角光照與太陽能 | 太陽貼近地平線時的發電與長陰影影響 | User's Guide「Lighting」；5 kW 目標 | 13（2） | 4 | — |
| M3 | 長時間黑暗與極寒 | 撐過 120 小時以上黑暗、極端溫度下運作 | User's Guide「Long Durations」 | 2、3（1） | 2 | — |
| M4 | 陡坡與極端地形移動 | 上下陡坡、進出隕石坑 | User's Guide「Terrain」；FN-M-302 L、FN-M-304 L | 8（2）、19（3） | 3 | — |
| M5 | 月塵與風化層作業 | 防塵、挖掘、壓實、整地 | User's Guide「Manipulating Regolith」 | 1（1）、29–30（3） | 1 | — |
| M6 | 冷陷冰資源探勘 | 在長期陰影的冷陷中偵測與開採冰 | User's Guide「ISRU」；LD-03-L | 55（6） | 5 | 上調：資源辨識已移至資料缺口；LD-03-L 選址理由；官方 Resources 特別點名 Diviner 極區資源產品 |

**特徵**（✅ 官方 Resources 內，➕ 補充來源）

| task | feature id | 名稱 | type | compare_mode | 月球資料 | 地球資料 | 備註 |
|---|---|---|---|---|---|---|---|
| M1 | m1_slope | 多尺度坡度、粗糙度 | profile | absolute | LOLA ✅ | Copernicus DEM ✅ | 門檻待補文獻 |
| M1 | m1_rock_proxy | 岩塊覆蓋（代理） | profile | relative_rank | Diviner 岩石覆蓋率 ✅ | 表觀熱慣量（MODIS 推算）✅ | earth_proxy |
| M1 | m1_radar_rough | 公分級雷達粗糙度 | profile | relative_rank | Mini-RF ✅ | Sentinel-1、PALSAR ✅ | 波段不同，只比相對排名 |
| M2 | m2_illum_fraction | 光照比例 | timeseries | absolute | LOLA + SPICE 自算 ✅；PGDA ➕ | Copernicus DEM + 太陽位置計算 ✅ | |
| M2 | m2_sun_elevation | 太陽高度角分布 | timeseries | absolute | 同上 | 同上 | |
| M2 | m2_horizon | 地平線遮蔽 | profile | absolute | LOLA ✅ | Copernicus DEM ✅ | |
| M3 | m3_diurnal_range | 日夜溫差 | timeseries | relative_rank | Diviner 極區累積產品（240 m）✅ | MODIS MOD11A1 ✅；SGLI ✅ | |
| M3 | m3_cold_hours | 低於門檻的累積時數 | timeseries | relative_rank | 同上 | 同上 | |
| M3 | m3_max_dark | 最長連續黑暗 | timeseries | absolute | 由 M2 光照計算 | 由 M2 光照計算 | |
| M3 | m3_abs_temp | 絕對表面溫度 | profile | absolute | Diviner ✅ | MODIS ✅ | **out_of_earth_range: true** |
| M4 | m4_slope_dist | 坡度分布、起伏 | profile | absolute | LOLA ✅ | Copernicus DEM ✅ | 門檻待補文獻 |
| M4 | m4_looseness | 表面鬆散程度 | profile | relative_rank | Diviner 岩石覆蓋率、土壤溫度 ✅ | 表觀熱慣量 ✅ | earth_proxy |
| M4 | m4_radar_rough | 雷達粗糙度 | profile | relative_rank | Mini-RF ✅ | Sentinel-1、PALSAR ✅ | |
| M5 | m5_tir_mineral | 熱紅外礦物特徵 | profile | absolute | Diviner Christiansen 特徵 ✅ | ASTER GED（100 m）✅ | 同為 8 微米附近，原理相同 |
| M5 | m5_vswir_mineral | 可見光–短波紅外礦物 | spectral | absolute | Chandrayaan-1 M3 ✅ | EMIT ✅ | EMIT 只涵蓋乾旱區、北緯 52° 以南 |
| M5 | m5_grain_proxy | 顆粒大小代理 | profile | relative_rank | Diviner 土壤溫度 ✅ | 表觀熱慣量 ✅ | earth_proxy |
| M6 | m6_ice_depth | 冰的深度 | profile | absolute | Diviner 極區資源產品：冰永凍層深度 ✅ | 永凍土活動層厚度 ESA CCI ➕ | ESA CCI 只涵蓋北緯 30° 以北 |
| M6 | m6_annual_temp | 年均、年最高溫 | profile | relative_rank | Diviner 極區資源產品 ✅ | MODIS 年統計 ✅ | |
| M6 | m6_permafrost | 永凍土有無 | categorical | absolute | Diviner 極區資源產品 ✅ | MODIS 年均地表溫 < 0°C ✅ | |
| M6 | m6_hydrogen | 含氫或冰訊號 | profile | relative_rank | LEND、Mini-RF ✅ | Sentinel-1 ✅ | |
| M6 | m6_cold_trap | 冷陷地形 | profile | absolute | LOLA + 光照計算 ✅ | Copernicus DEM + 光照計算 ✅ | |

**月球任務層級注意事項**（放入各任務 `notes`）：

- M1、M4 的坡度與岩石門檻 NASA 文件未給數值，暫用剖面比對。
- 月球一天約地球 29.5 天，時間序列先換成當地太陽時相位再比。
- 地形一律用 Copernicus DEM（SRTM 不涵蓋北緯 60° 以北，而月球類比很可能在高緯度）。
- M4 與 M6 在月球上是同一趟任務（移動到陰影坑內採冰），最佳化可給同地加分（見 5.6）。

**地球無法重現的條件（earth_limits，mission: moon）**

| 條件 | 月球 | 可否模擬 | 處理方式 |
|---|---|---|---|
| 重力 | 地球的 1/6 | 否 | 列入無法重現清單 |
| 大氣 | 幾乎真空，無風、無天氣 | 否 | 列入無法重現清單 |
| 溫度 | 陰影區可低於 -230°C，向陽處超過 100°C | 否（絕對值） | 只比相對特徵 |
| 光照 | 太陽貼近地平線、長陰影 | 部分（高緯度） | 納入 M2 |
| 輻射 | 無磁場、無大氣保護 | 否 | 列入無法重現清單 |
| 月塵 | 尖銳、帶靜電、未受風化 | 部分（火山碎屑） | 納入 M5，標註靜電特性無法模擬 |
| 地質 | 無水、無生命作用 | 部分 | 在地點描述中說明 |

### 4.3 火星（mission: `mars`）

**目標地點**

| id | 名稱 | 座標 | coords_status | 來源與說明 |
|---|---|---|---|---|
| mars-ap105 | Arcadia Planitia（AP-105） | 北緯 43.3295°、東經 198.5228° | exact | SkyFall 設計參考著陸點；多邊形地形、岩石極少 |
| mars-deuteronilus | Deuteronilus Mensae | null | todo | SkyFall 評估的北緯 30–45° 區域 |
| mars-utopia | Utopia Planitia | null | todo | 同上 |
| mars-phlegra | Phlegra Montes | null | todo | 同上 |
| mars-erebus | Erebus Montes | null | todo | 同上 |
| mars-jezero | Jezero 隕石坑（選用） | 約北緯 18.4°、東經 77.5° | approx | 毅力號地點，有地面實測，可作方法驗證 |
| mars-gale | Gale 隕石坑（選用） | 約南緯 5.4°、東經 137.8° | approx | 好奇號地點，同上 |

**NASA 依據摘要**：SkyFall 為 3 架直升機，2028 年 11–12 月隨 SR-1 Freedom 發射，約 2030 年 9 月北半球春季抵達以避開沙塵暴；著陸橢圓 100 × 25 公里；每架飛行 50–300 公里。探索區概念為中央著陸點周圍約 100 公里內的多個興趣區（2015 年研討會 47 個提案）。載人選址重視地下冰取水、海拔、科學目標。核分裂為火星主要電力（架構決策 MD-07），主因是不受沙塵暴影響。

**SkyFall 著陸工程限制**（在任務頁以表格顯示；緯度、海拔只用來篩選火星目標，不用於地球評分）

| 條件 | 要求 | 地球可否類比 |
|---|---|---|
| 緯度 | 赤道到北緯 45° | 不適用 |
| 海拔 | 低於 MOLA 基準面 -3 公里 | 不適用 |
| 100 m 坡度 | < 5–15°（待定） | 可（R1） |
| 1–5 m 坡度 | < 15° | 可（R1） |
| 岩石 | 高度 < 11 公分、覆蓋率 < 5% | 可（R1，地球用代理） |
| 熱慣量 | > 100（最好 > 150）J m⁻² K⁻¹ s⁻½ | 只比相對排名（R1） |
| 地表特徵 | 需有影像特徵供導航，避開大片沙丘、沙原 | 可（R2） |
| 季節 | 北半球春季抵達 | 參考（R6） |

**分支任務**

| id | 名稱 | 要驗證什麼 | NASA 依據 | 排名（等級） | order | 手動調整 |
|---|---|---|---|---|---|---|
| R1 | 著陸地表條件 | 坡度、岩石、承重是否適合降落 | SkyFall 工程限制 V.e–g | 10（2）、37（5） | 1 | — |
| R2 | 視覺導航可行性 | 直升機靠影像特徵導航 | SkyFall 工程限制 V.h | null | 4 | 手動排入：SkyFall 工程限制 |
| R3 | 淺層地下冰 | 透地雷達偵測 3–5 公尺內的分層與埋藏冰 | SkyFall 透地雷達；載人選址重視取水 | 52（6） | 2 | 上調：SkyFall 重點、取水為關鍵 |
| R4 | 含水礦物辨識 | 近紅外辨識含水礦物與變質產物 | SkyFall 近紅外相機；生命起源科學目標 | null | 5 | 手動排入：科學目標 |
| R5 | 冰河與冰緣地形 | 多邊形地等地貌與地下冰的關係 | SkyFall 彩色相機 | null | 6 | 手動排入：科學目標 |
| R6 | 沙塵與近地表氣象 | 塵埃揚起、風、近地表溫度日變化 | SkyFall 氣象感測；MD-07 | 35（4） | 3 | — |

**特徵**

| task | feature id | 名稱 | type | compare_mode | 火星資料 | 地球資料 | 門檻／備註 |
|---|---|---|---|---|---|---|---|
| R1 | r1_slope_100m | 100 m 坡度 | threshold | absolute | CTX 或 HRSC 地形 ➕（MOLA 約 463 m 太粗） | Copernicus DEM ✅ | `{ideal_max: 5, zero_at: 15}`（待定） |
| R1 | r1_slope_1_5m | 1–5 m 坡度 | threshold | absolute | HiRISE 地形模型 ✅（覆蓋有限） | 無全球資料，用 30 m 坡度 + 雷達代理 | `{ideal_max: 12, zero_at: 15}`；earth_proxy |
| R1 | r1_rock | 岩石覆蓋率 | threshold | relative_rank | TES／THEMIS 岩石覆蓋 ✅ | 表觀熱慣量 + Sentinel-1／PALSAR ✅ | planet_threshold `{max: 0.05}`；earth_proxy |
| R1 | r1_thermal_inertia | 熱慣量 | threshold | relative_rank | THEMIS 熱慣量（約 100 m）✅ | 表觀熱慣量 ✅ | planet_threshold `{zero_at: 100, ideal_min: 150}`；地球單位不同只比相對排名 |
| R2 | r2_texture | 影像紋理豐富度 | profile | relative_rank | CTX（6 m）、HiRISE ✅ | Sentinel-2（10 m）✅ | HLS 30 m 太粗 |
| R2 | r2_dune_fraction | 沙丘與沙原比例 | threshold | absolute | 火星全球沙丘資料庫 ➕ | Sentinel-2 ✅ | 越低越好 `{ideal_max: 0.05, zero_at: 0.3}`（暫定） |
| R3 | r3_ground_ice | 地下冰分布與深度 | profile | relative_rank | Odyssey 中子／伽瑪射線、SHARAD ✅；SWIM ➕ | MODIS 年均地表溫 < 0°C ✅；ESA CCI 永凍土 ➕ | 地球沒有 3–5 m 深度的全球資料 |
| R3 | r3_polygons | 多邊形地 | categorical | absolute | HiRISE、CTX ✅ | Sentinel-2 ✅ | |
| R3 | r3_subsurface_radar | 地表下雷達 | profile | relative_rank | SHARAD ✅ | PALSAR L 波段 ✅ | 僅極乾沙地可穿透表層 |
| R4 | r4_hydrated_spectra | 含水礦物光譜 | spectral | absolute | CRISM、OMEGA ✅ | EMIT ✅；ASTER 短波紅外 ✅ | ASTER 短波紅外 2008 年 4 月故障，只用之前資料；EMIT 只涵蓋乾旱區、北緯 52° 以南 |
| R5 | r5_landform | 地貌類型 | categorical | absolute | HiRISE、CTX ✅ | Sentinel-2、Copernicus DEM ✅；RGI 冰河分布 ➕ | |
| R5 | r5_polygon_size | 多邊形尺寸 | profile | absolute | HiRISE、CTX ✅ | Sentinel-2 ✅ | 地球冰楔多邊形約 10–30 m，10 m 解析度勉強 |
| R5 | r5_roughness | 地表粗糙度 | profile | relative_rank | HiRISE ✅ | Copernicus DEM ✅；RADARSAT-1 長期變化 ✅ | |
| R6 | r6_dust | 沙塵頻率與季節性 | timeseries | relative_rank | MCS、MARCI、TES ✅；火星氣候資料庫 MCD ➕ | MODIS 氣膠、MERRA-2 沙塵、Sentinel-5P ✅ | SkyFall 五區無著陸器實測 |
| R6 | r6_wind_temp | 風、近地表溫度日變化 | timeseries | relative_rank | MCD ➕；REMS、MEDA ✅（僅兩點） | MERRA-2 ✅ | |

**火星任務層級注意事項**（放入各任務 `notes`）：

- 火星一天約 24 小時 39 分、一年約 687 地球日，時間序列先換成當地時間與太陽經度 Ls 再比。
- 五區地形差異大（平原、台地、山區），可能需要比月球更多地球地點。
- 官方 Resources 的火星資料只有 PDS，可用 Mars ODE、Mars Trek 依經緯度搜尋。

**地球無法重現的條件（earth_limits，mission: mars）**

| 條件 | 火星 | 可否模擬 | 處理方式 |
|---|---|---|---|
| 大氣 | 氣壓不到地球 1%，主要是 CO₂ | 否 | 列入無法重現清單 |
| 著陸海拔 | 需低於 -3 公里 | 不適用 | 不評分，在地點描述中說明 |
| 重力 | 約地球的 38% | 否 | 列入無法重現清單 |
| 輻射 | 無全球磁場、大氣薄；SkyFall 劑量計要量測的就是這項 | 否 | 列入無法重現清單 |
| 溫度 | 平均約 -60°C，日夜溫差大 | 部分（極地、高山） | 比相對特徵 |
| 水 | 地表無液態水，只有冰與含水礦物 | 部分（極乾沙漠、永凍土） | 納入 R3、R4 |
| 土壤化學 | 含過氯酸鹽等氧化性物質 | 部分 | 在地點描述中說明 |
| 沙塵 | 有全球性沙塵暴 | 部分（規模與成因不同） | 納入 R6 |
| 地質 | 火山、隕石坑、河道、冰緣地貌 | 可 | 地球類比最豐富的部分 |

### 4.4 資料來源（data_sources.yaml）

每筆：`name`、`portal`、`official`（布林）、`url`、`used_by`（feature id 清單）。

**官方 Resources（official: true）**：NASA Earthdata Search、NASA Worldview、NASA Planetary Data System（PDS）、NASA LRO、NASA LRO Diviner Lunar Data、Copernicus Data Space Ecosystem、ESA Open Science Catalog、JAXA G-Portal、CSA RADARSAT Constellation Mission（RCM）、CSA RADARSAT-1、CSA SAR Python Tutorial。

**補充來源（official: false）**：NASA PGDA、Moon Trek／Mars Trek、Caltech CTX 全球鑲嵌、ASU THEMIS 熱慣量、SWIM 地下冰圖、火星氣候資料庫 MCD（LMD）、NASA POWER、ESA CCI 永凍土、ShadowCam、火星全球沙丘資料庫（USGS）、RGI 冰河清冊。

網址可先留空並標 TODO，團隊會補上。

### 4.5 categorical_tables.yaml（示範）

```yaml
m6_permafrost:   {yes: {yes: 1.0, no: 0.0, unknown: 0.5}, no: {yes: 0.0, no: 1.0, unknown: 0.5}}
r3_polygons:     {present: {present: 1.0, absent: 0.0}, absent: {present: 0.0, absent: 1.0}}
r5_landform:     # 類型間相似度，團隊之後依地質文獻調整
  polygonal_terrain: {polygonal_terrain: 1.0, patterned_ground: 0.7, debris_apron: 0.4, plain: 0.3}
  ...
```

### 4.6 method.yaml（預設值，團隊待定）

```yaml
tau: 0.7                 # 相似度門檻：達到才算「涵蓋」
sigma: 1.0               # 高斯核尺度（標準化單位）
sigma_rank: 0.15         # relative_rank 特徵的高斯核尺度（百分位差）
epsilon: 1.0e-6          # 幾何平均取對數時的下限
similar_cutoff: 0.7      # 「相似之處」
different_cutoff: 0.4    # 「不同之處」
weight_scheme: roc       # roc | rank_sum | custom
sensitivity: {n_samples: 500, alpha: 1.0, seed: 42}
integration_bonus:       # 同地整合加分（只用於同分時取捨）
  - {tasks: [M4, M6], bonus: 0.05}
```

---

## 5. 相似度與最佳化方法（初版，全部放在 `services/similarity/app/core/`）

**設計要求**：每種特徵類型一個函式，用註冊表（`SCORERS = {"threshold": ..., "profile": ...}`）分派，團隊之後可替換或新增方法而不動其他程式。每個函式寫 docstring，註明方法名稱與文獻。另寫 `docs/METHOD.md` 說明。

### 5.1 特徵分數（每個特徵 → 0–1）

| 類型 | 方法 | 文獻 |
|---|---|---|
| threshold | 梯形滿意度函數：`{ideal_max, zero_at}` → 值 ≤ ideal_max 為 1，線性降到 zero_at 為 0；`{zero_at, ideal_min}` 反向 | Derringer & Suich 1980 |
| profile（absolute） | 以地球候選池的平均與標準差做 z-score（目標值用同一組統計量），`s = exp(-(z_c - z_t)² / (2σ²))` | — |
| profile（relative_rank） | 候選值在地球池中的百分位 vs 目標值給定的百分位，`s = exp(-(p_c - p_t)² / (2σ_rank²))`；用於單位不同或代理指標 | — |
| categorical | 查 `categorical_tables.yaml`；之後可擴充 Gower 距離處理混合型 | Gower 1971 |
| spectral | 光譜角度法 `θ = arccos(a·b / (‖a‖‖b‖))`，`s = 1 - θ / (π/2)`（截在 0–1）；需相同波段格網，真實資料的重採樣先留 TODO | Kruse et al. 1993 |
| timeseries | 先萃取統計量（光照比例、日夜溫差、最長連續黑暗、低於門檻時數、沙塵事件頻率等，於特徵設定 `stat`），再依 compare_mode 當 profile 評分；另計算 Wasserstein 距離供圖表顯示 | Ramdas et al. 2017 |
| out_of_earth_range | 不評分，列入「無法重現」 | — |

若目標值超出地球候選池範圍超過 3 個標準差，回傳 `warning: target_outside_earth_range`。

### 5.2 分支任務分數（同一任務內合併）

加權幾何平均（任一關鍵特徵接近 0 會把總分拉低）：

```
S_task = exp( Σ_i w_i · ln(max(s_i, ε)) ) ，Σ w_i = 1（只計入有評分的特徵）
```

### 5.3 權重

- **ROC**（Barron & Barrett 1996）：`w_k = (1/n) Σ_{i=k}^{n} 1/i`，k 為 `order`。n = 6 時應得 0.408、0.242、0.158、0.103、0.061、0.028。
- **等差（rank sum）**：`w_k = (n - k + 1) / Σ`，n = 6 時為 0.286、0.238、0.190、0.143、0.095、0.048。
- **自訂**：使用者滑桿，自動正規化。
- 只選部分任務時，在選中的任務之間重新正規化。
- 整體分數：`S_overall = Σ_k w_k · S_task_k`。

### 5.4 穩健性檢查

任務內有 2 個以上 profile 特徵時，另用馬氏距離（地球池共變異矩陣，加微小正則化）排名，回傳與主排名的 Spearman 相關係數（Mahalanobis 1936）。

### 5.5 時間序列統計（第二優先，可先做簡版）

- `wasserstein(a, b)`：scipy。
- `tost_equivalence(diff, margin)`：等價性檢定（Schuirmann 1987），用區塊自助法估計信賴區間（Künsch 1989）。
- 回應中以效果量為主、檢定為輔。

### 5.6 最佳化

- **集合覆蓋**（Toregas et al. 1971）：需求 i = 選中的每項分支任務（之後可擴充為多個目標地點 × 任務）。候選 j 涵蓋 i 的條件為 `S_ij ≥ τ`。
  - 兩階段整數規劃（PuLP + CBC）：先求 `min Σ x_j`；再固定地點數，最大化「各需求最佳分數加權總和 + 同地整合加分」。
  - 沒有任何候選達到 τ 的任務，不進入最佳化，列為 `uncoverable`。
- **邊際效益曲線**：最大覆蓋問題（Church & ReVelle 1974），k = 1…K，最大化 `Σ w_i y_i`，限制 `y_i ≤ Σ_{j 涵蓋 i} x_j`、`Σ x_j = k`。
- **敏感度分析**：從 Dirichlet(α) 抽 N 組權重，每組以 k = 集合覆蓋最小地點數跑一次最大覆蓋，統計每個地點被選入的比例（SMAA 接受度指標，Lahdelma et al. 1998）。固定亂數種子。
- `exclude_known: true` 時排除 `known_analog` 候選。

---

## 6. API 規格

### catalog（前綴 `/api/catalog`）

| 方法 | 路徑 | 回傳 |
|---|---|---|
| GET | `/missions` | 任務清單 |
| GET | `/missions/{mission}` | 任務詳情（含 NASA 依據） |
| GET | `/missions/{mission}/tasks` | 分支任務與特徵（含計算後的 ROC、等差權重） |
| GET | `/missions/{mission}/sites` | 目標地點 |
| GET | `/missions/{mission}/limits` | 地球無法重現的條件 |
| GET | `/missions/{mission}/constraints` | 著陸工程限制（火星） |
| GET | `/data-sources` | 資料來源 |
| GET | `/earth-facts` | 主頁對照表 |
| GET | `/health` | |

### similarity（前綴 `/api/similarity`）

共同請求欄位：

```json
{ "mission": "moon", "site_id": "moon-scr", "task_ids": ["M1","M3"],
  "weight_scheme": "roc", "custom_weights": null,
  "exclude_known": false, "tau": 0.7 }
```

| 方法 | 路徑 | 說明 |
|---|---|---|
| POST | `/score` | 各任務排名（含每個特徵分數、相似／不同／無法重現、警告）、整體排名、穩健性、`uses_placeholder` |
| POST | `/optimize` | 集合覆蓋結果、覆蓋度表、uncoverable、邊際效益曲線 |
| POST | `/sensitivity` | 加上 `n_samples`、`seed`；回傳各地點被選入比例 |
| GET | `/candidates/{id}/series/{feature_id}` | 時間序列圖表資料（目標與候選） |
| GET | `/health` | |

回應的 Pydantic 模型請明確定義，前端用 TypeScript 型別對應（可由 OpenAPI 產生）。

---

## 7. Docker 與執行

- 每個 Python 服務：`python:3.12-slim`，非 root 使用者執行。
- 前端正式模式：多階段建置（node 建置 → nginx 提供靜態檔）。
- 開發模式：`docker compose -f docker-compose.yml -f docker-compose.dev.yml up` → vite dev server 熱更新、uvicorn `--reload`、原始碼 bind mount。
- 所有服務設 healthcheck；`similarity` 依賴 `catalog` 健康後再啟動。
- `.env.example` 列出埠號與設定。
- 啟動後：http://localhost:8080 。

---

## 8. 測試與驗收標準

### 單元測試（pytest，`services/similarity/tests/`）

- ROC 權重 n = 6 四捨五入到小數三位等於 `[0.408, 0.242, 0.158, 0.103, 0.061, 0.028]`；等差權重等於 `[0.286, 0.238, 0.190, 0.143, 0.095, 0.048]`。
- 梯形函數邊界值（ideal、zero_at、中點）。
- 光譜角度：相同向量 = 1，正交向量 = 0。
- 幾何平均：任一特徵為 0 時總分接近 0；`out_of_earth_range` 特徵不影響分數。
- 集合覆蓋：手算的小例子（3 個任務、4 個候選）得到正確最少地點數與 uncoverable。
- catalog 載入所有 seed 檔不報錯，且每個 feature 都屬於存在的 task。

### 驗收清單

1. `docker compose up --build` 後，http://localhost:8080 顯示旋轉地球主頁與對照表。
2. 選「月球」→ 看到 M1–M6 卡片（NASA 依據、排名、權重、資料徽章、注意事項）與地球無法重現表。
3. 勾選任務 → 選 Shackleton 連接脊 → 看到各任務排名、地點詳情（相似／不同／無法重現）、整體地圖。
4. 調整 τ、權重方案、排除已知場址，結果即時更新；集合覆蓋顯示最少地點數與無法涵蓋的任務；邊際效益曲線與敏感度分析可執行。
5. 「火星」流程同樣可用，R1 門檻型特徵正確套用滿意度函數；工程限制表顯示。
6. 使用示範資料時一定顯示示範資料橫幅。
7. zh-TW／en 切換可用（介面文字；內容缺英文時顯示中文）。
8. `/api/catalog/docs`、`/api/similarity/docs` 可透過 gateway 開啟。
9. pytest 全部通過；README 說明啟動方式、如何替換示範資料、如何新增特徵或任務、方法程式碼位置。

---

## 9. 實作順序與注意事項

**順序**

1. Repo 骨架、Docker Compose、gateway、兩個後端的 `/health`、前端空殼，確認 `docker compose up` 可跑。
2. catalog 服務 + 全部 seed 檔（依第 4 節內容）+ 示範資料產生腳本。
3. similarity 核心方法 + 單元測試 + `/score`。
4. 前端主頁、任務頁三步驟、結果頁（排名、詳情抽屜、地圖）。
5. `/optimize`、`/sensitivity` 與對應圖表；時間序列圖表。
6. `/method`、`/data` 頁面、i18n、README、`docs/METHOD.md`。

**注意事項**

- 內容一律從 catalog API 讀取，不可寫死在 Vue 元件。
- 不可編造真實世界的相似度結果；示範資料一律標記並顯示橫幅。
- 不確定的數值（座標、門檻、目標值）留 `null` 或 TODO，不要自行猜測。
- 方法集中在 `core/`，函式小而純粹（輸入陣列、輸出分數），方便團隊替換與測試。
- 先求能跑、結構清楚，不要過度設計（不做登入、資料庫、雲端部署）。
- 介面要讓評審一眼看懂：每個相似度都能點開看到「根據哪些資料、哪裡像、哪裡不像、對應哪個 NASA 需求」。
- 完成後回報：啟動指令、已完成的驗收項目、尚未完成或有疑慮的地方。
