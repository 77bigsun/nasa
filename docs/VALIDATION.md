# 驗證紀錄 · 2026-11-14

環境：Windows、Python 3.13.1、Node 26.13.0、Vite 8.3.8、FastAPI 0.162.7、PuLP 4.2.0 + cbcbox 2.929。Docker 設計目標為 python:3.12-slim / node:26-alpine。

## 已執行

| 檢查 | 結果 |
|---|---|
| pytest：公式邊界、ROC／等差、幾何平均、SAM、百分位、時間序列 | 通過 |
| pytest：最少集合覆蓋、次階段品質取捨、uncoverable、固定種子敏感度 | 通過 |
| pytest：seed schema、來源引用、月球／火星 score／optimize／sensitivity／series | 通過 |
| pytest：無效任務、跨星球 site、缺目標 fallback、排除已知場址、placeholder | 通過 |
| 後端測試總數（拆分後新增服務邊界與依賴失敗案例） | 27 passed |
| Vitest：分享 URL 還原／驗證、精靈選擇→目標→結果、零任務阻擋、詳情與序列載入、語系切換 | 5 passed |
| vue-tsc + Vite production build | 通過 |
| 本機四個 FastAPI + Vite 啟動器 | 成功，port 8001／8002／8003／8004／8080 |
| HTTP GET `/` `/moon` `/mars` `/method` `/data` | 全部 200（路由可服務，非畫面驗證） |
| HTTP catalog／measurements／similarity／planning 的 health、docs 與 OpenAPI | 四套 API 均成功；規劃與評分分開運行，保留代理前綴 |
| 透過本機代理 POST 月球／火星 score、optimize、sensitivity | similarity 評分、planning 規劃均成功，舊 API 別名保留轉送 |
| NASA Blue Marble 本機資產 | 已下載公開鏡像，HTTP 200 |
| NASA GIBS WMTS Level8 範例圖磚 | 200 image/jpeg，17,819 bytes |

## 尚未實測

- Docker build／Compose 正式與開發模式：主機沒有 docker 指令，僅提供設定與 YAML 結構檢查。
- 真人瀏覽器視覺與互動：browser access host unavailable；原生 Edge 的 app approval timed out。未以其他未授權瀏覽器控制技術繞過。
- WebGL 實際旋轉、Leaflet 實際繪製與 fallback、ECharts/KaTeX 視覺、手機斷點、鍵盤焦點與螢幕閱讀器均待人工驗收。
- 真實資料下載、光譜重採樣、時間序列自相關 bootstrap 與科學效度：原型未實作／未驗證。

## 對照原規格驗收清單

1. 首頁與 Compose：程式已實作；HTTP／正式前端建置通過；Docker 與畫面待實測。
2. 月球任務卡、來源、權重、注意事項與限制表：已實作，catalog 資料契約通過。
3. 任務選擇、Shackleton、排名與詳情地圖：API／精靈元件通過；地圖與抽屜視覺待實測。
4. τ／權重／排除、集合覆蓋、邊際效益、敏感度：API／核心通過；圖表視覺待實測。
5. 火星流程、R1 threshold、工程表：API／核心通過；視覺待實測。
6. placeholder 橫幅：API flag 與精靈元件測試通過。
7. zh-TW／en：介面字串與切換已實作；內容缺翻譯回退中文，待人工瀏覽器確認。
8. 兩個代理前綴 docs：本機 Vite 代理實測通過；Nginx Compose 待實測。
9. pytest／README／資料替換／新增特徵與方法位置：完成。

目前沒有任何經真實觀測支持的場址發現。NASA 工程條件、來源版本與技術缺口排名的細節仍待團隊確認。
