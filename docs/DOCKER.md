# Windows 上如何啟動這個專案

## 第一次準備

1. 從 [Docker 官方 Windows 安裝頁](https://docs.docker.com/desktop/setup/install/windows-install/) 下載 Docker Desktop。
2. 使用 WSL 2 backend 與 Linux containers；這個專案使用 Linux 映像。
3. 若安裝程式要求安裝／更新 WSL 或重新開機，依官方引導完成。Docker Desktop 安裝完後需自行開啟，等待引擎就緒。
4. 開啟新的 PowerShell，確認：

```powershell
docker version
docker compose version
```

`docker version` 應同時顯示 Client 與 Server。只有 Client 或出現無法連線的訊息時，先確認 Docker Desktop 已啟動。若出現找不到指令，重新開啟 PowerShell。

## 第一次啟動

```powershell
cd D:\NASA
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

- `config --quiet` 檢查 Compose 設定。
- `up --build -d` 下載映像、建置程式，並在背景啟動服務。第一次需要下載 Python、Node、CBC 等依賴，時間取決於網路與電腦。
- `ps` 查看六個服務，啟動初期可能顯示 starting，待 healthcheck 完成後應為 healthy。

開啟 **http://localhost:8080**。初版仍是示範資料，請留意 placeholder 橫幅。

四個後端文件：

- http://localhost:8080/api/catalog/docs
- http://localhost:8080/api/measurements/docs
- http://localhost:8080/api/similarity/docs
- http://localhost:8080/api/planning/docs

不需要另外在主機安裝 Python 或 Node 才能用 Docker 模式；這些環境由映像提供。

## 平常會用到的指令

| 目的 | PowerShell 指令 |
|---|---|
| 看全部狀態 | `docker compose ps` |
| 持續看日誌，Ctrl+C 結束查看 | `docker compose logs -f` |
| 只看相似度與規劃服務 | `docker compose logs -f similarity planning` |
| 改程式後重新建置與啟動 | `docker compose up --build -d` |
| 暫停容器 | `docker compose stop` |
| 再次啟動既有容器 | `docker compose start` |
| 停止並移除此專案容器與網路 | `docker compose down` |

目前 seed 資料放在 `D:\NASA\data`，以唯讀方式掛進容器；正常 `down` 不會刪除這個主機資料夾。

## 修改程式時使用熱更新

先關閉一般模式，接著使用開發覆寫：

```powershell
docker compose down
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

此模式會在前景顯示日誌，Vue 使用 Vite，後端使用 uvicorn reload。新增套件後請重新建置；若前端 node_modules volume 保留舊版依賴，可用 README 的 npm ci 指令更新。

## 遇到問題先看哪裡？

- 8080 已被使用：停止先前的 `scripts/dev.py`，或複製 `.env.example` 為 `.env`，將 `PORT=8081`，重新執行 up，再開 localhost:8081。
- gateway 沒啟動：看 `docker compose ps` 哪個依賴不健康，再用 `docker compose logs 服務名稱` 查看原因。
- 改資料後仍看見舊值：執行 `docker compose restart catalog measurements similarity planning`，清除定義與量測快取並重新讀取檔案。
- 建置下載失敗：先確認 Docker Desktop 的網路及 registry 連線；將錯誤內容交給團隊處理。

可在主機已具備 Python 開發依賴時，執行真正的 HTTP 檢查：

```powershell
.\.venv\Scripts\python.exe scripts/smoke.py
```

此腳本會檢查四套 API 文件、health、月球／火星評分與規劃。它使用目前示範候選 demo-01 的時間序列，替換正式資料後需調整該測試案例。

本環境在撰寫時尚未安裝 Docker，Docker 實際建置與啟動仍待安裝後驗收。已另以四個本機 API 程序驗證服務串接。

官方參考：[Windows 安裝](https://docs.docker.com/desktop/setup/install/windows-install/)、[Compose 入門](https://docs.docker.com/compose/gettingstarted/)。
