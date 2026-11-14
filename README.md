# Earth Analog Finder · 地球類比探索

依 [原始規格](docs/SPEC.md) 建立的 NASA Space Apps Challenge 2026 團隊原型。專案直接位於 `D:\NASA`，沒有另外包一層 analog-finder 資料夾。

後續已依團隊管理需求拆成 6 個服務（4 個後端 API）。先看 [服務分工與流程圖](docs/SERVICES.md)、[Docker 操作教學](docs/DOCKER.md)、[GitHub 綁定狀態](docs/GIT.md)。原始 SPEC 留作需求來源，最新服務邊界以 SERVICES 為準。

**目前所有目標與地球候選特徵值都是示範資料。網站的分數由程式計算，但不是基於真實觀測的科學結果，也不代表 NASA 確認的場址。**

## 啟動

安裝 Docker Desktop 並啟動 Linux containers 後，在專案根目錄執行：

```powershell
docker compose up --build
```

開啟 **http://localhost:8080**。

- Catalog OpenAPI：http://localhost:8080/api/catalog/docs
- Measurements OpenAPI：http://localhost:8080/api/measurements/docs
- Similarity OpenAPI：http://localhost:8080/api/similarity/docs
- Planning OpenAPI：http://localhost:8080/api/planning/docs
- Gateway health：http://localhost:8080/health

`.env.example` 列出可調設定。預設不用複製；如需換埠可複製為 `.env` 再修改 PORT。後端的 ROOT_PATH 由 Compose 設定，資料與文件唯讀掛載。Python image 為 3.12，前端建置使用 Node 26 LTS。

開發模式（Vite + uvicorn reload）：

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

停止：`docker compose down`。前端新增依賴後，如現有 frontend_modules volume 仍保留舊套件，可執行 `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps frontend npm ci` 更新後再啟動。

### 不使用 Docker 的 Windows 本機模式

需求：Python 3.12 以上（最低 3.11，依目前套件支援範圍）、Node 22 以上。建置驗證環境為 Python 3.13.1 / Node 26.13.0。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Set-Location frontend
npm.cmd ci
Set-Location ..
.\.venv\Scripts\python.exe scripts/dev.py
```

同樣開啟 **http://localhost:8080**。啟動器會管理 catalog (8001)、similarity (8002)、measurements (8003)、planning (8004) 與 Vite (8080)。按 Ctrl+C 一起停止，日誌在忽略追蹤的 `.runtime/`。`PORT` 只覆寫前端埠；8001–8004 請保持可用。前端預設熱更新；後端改動後重新啟動，可選 `scripts/dev.py --reload` 開啟 uvicorn 檔案監看。

此工作環境已安裝 `.venv` 與 `frontend/node_modules`，可以直接執行最後一行。這些本機依賴不應提交到 Git。

## 可使用的功能

- `/`：NASA Blue Marble 地球、任務選單、地球／月球／火星資料對照。WebGL 不可用時採靜態地球替代。太陽日與恆星日有區別，來源附在表格旁。
- `/moon`、`/mars`：六項任務勾選 → 單一目標選擇 → 結果；狀態存於 Pinia 與 URL query，支援重新載入及分享。
- 各任務前十名、整體排名、可點選候選的特徵詳情、相似／差異／不可重現條件、來源與代理指標標示。
- 相位疊圖、ECDF、Wasserstein；Leaflet 地球候選地圖優先 NASA GIBS，圖磚錯誤切換 OSM。火星目標採純經緯度圖示意，避免誤用地球地理底圖。
- τ、ROC／等差／自訂權重、排除已知類比場址；最小集合覆蓋、覆蓋表、uncoverable、固定 k 邊際效益與 Dirichlet 敏感度分析。
- `/method`：由 catalog 讀取 docs/METHOD.md，公式以 KaTeX 顯示。
- `/data`：11 項官方 Resources 與 11 項補充來源，列出 used_by 特徵。official 指競賽 Resources 清單，不表示所有補充來源都非官方機構。
- 繁體中文／英文介面切換，內容缺英文時回退中文；原始注意事項與方法正文目前保留中文為主。
- placeholder 與缺資料會明示；不會把示範排名當成真實發現。

## 結構與修改位置

```text
gateway/                       Nginx 正式 / 開發反向代理
frontend/src/pages/            首頁、任務精靈、方法、資料來源
frontend/src/components/       地球、地圖、圖表、詳情抽屜
services/catalog/app/          Pydantic 模型、FileRepository、內容 API
services/measurements/app/     候選與目標量測的唯一讀取服務
services/similarity/app/core/   小型純函式：評分、聚合、權重、穩健性、序列
services/similarity/app/engine.py  組合定義與量測資料，不在 Vue 計算相似度
services/planning/app/core/     最小集合覆蓋、邊際效益、權重敏感度
services/shared/               共用 API 契約與內容 HTTP client
services/similarity/tests/      核心方法、服務邊界、跨服務 API 整合測試
services/ingest/                未來下載處理 worker 說明（尚未實作）
data/seed/                     12 任務、36 特徵、17 目標、20 示範候選
scripts/generate_seed.py        固定種子重建示範資料（會覆寫 seed）
scripts/dev.py                 無 Docker 本機啟動器
scripts/smoke.py               真正 HTTP 服務串接與入口路由檢查
docs/SPEC.md                   使用者原始規格
docs/METHOD.md                 方法、假設、限制與參考來源
docs/VALIDATION.md             驗證結果與未驗收項目
docs/SERVICES.md               六個服務的責任、修改對照與資料流
docs/DOCKER.md                 Windows Docker 操作與排錯
docs/GIT.md                    GitHub 綁定與提交方式
```

如何替換資料、欄位格式、如何新增特徵與任務：見 [data/README.md](data/README.md)。方法說明與修改位置：見 [docs/METHOD.md](docs/METHOD.md)。

catalog 管理定義，measurements 讀取量測；similarity 透過 HTTP 向兩者取資料並快取（預設 60 秒）。planning 再向 similarity 取得分數，以計算地點組合。similarity 與 planning 不掛載 data 目錄。兩個資料擁有者的 repository 邊界可替換成資料庫。資料變更後重啟四個後端，使量測與定義一起更新。

## 驗證

```powershell
.\.venv\Scripts\python.exe -m pytest -q
Set-Location frontend
npm.cmd test
npm.cmd run build
```

2026-11-14：拆分後端後 27 tests passed；前端 5 tests passed；TypeScript / Vite 正式建置通過。HTTP 測試涵蓋四套 health／OpenAPI／docs、月球與火星的 score／optimize／sensitivity、時間序列與舊規劃 API 轉送。NASA GIBS 公開 WMTS 圖磚先前已確認為 200 image/jpeg。

**驗證限制：此環境沒有 Docker；未實際執行 Docker build / Compose。瀏覽器控制 host 不可用，原生 Edge 授權逾時，未完成畫面、WebGL、響應式與圖表的真人瀏覽器驗收。元件測試是 DOM 模擬，不等同視覺驗收。** 詳細紀錄見 docs/VALIDATION.md。

## 團隊後續需補的資料

月球座標全部保留 todo；火星 AP-105 座標、工程限制、NASA 技術缺口排名沿用團隊規格，未逐項核對原始文獻。行星時程不作已確認承諾。尚需確認實際資料版本、來源產品、覆蓋範圍、跨感測器尺度、光譜波段對齊與不確定度。

TOST 僅提供獨立差值的探索性核心函式；時間序列 block bootstrap 尚未實作，也未用來宣稱統計等效。固定 k 最大覆蓋與敏感度採 20 個候選的精確枚舉，大量候選需換 MILP。ingest 依規格只保留說明，沒有登入、資料庫或雲端部署。

Blue Marble 素材來源與 NASA credit 見 [textures/README.md](frontend/public/textures/README.md)。
