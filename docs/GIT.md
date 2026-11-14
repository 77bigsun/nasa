# 這個資料夾與 GitHub 的關係

`D:\NASA` 已初始化為 Git working tree。

- 遠端名稱：`origin`
- 遠端網址：`https://github.com/77bigsun/nasa.git`
- 本機分支：`main`
- 追蹤分支：`origin/main`
- 綁定時遠端內容：初始 README，commit `d150af2`。

設定時保留了本機網站檔案，並將本機 main 接到遠端既有歷史。這份專案目前是未提交的工作目錄變更，未執行 push。

確認連結：

```powershell
cd D:\NASA
git remote -v
git branch -vv
git status
```

`.gitignore` 已排除 `.venv`、`node_modules`、dist、`.env`、暫存與日誌。套件 lockfile、示範資料、NASA 貼圖及原始碼會納入版本控制。

準備好上傳時，可在確認 `git status` 的檔案清單後執行：

```powershell
git add .
git commit -m "Add Earth Analog Finder prototype and service boundaries"
git push -u origin main
```

GitHub 若要求登入，請用你自己的帳號完成驗證。若 Git 要求 user.name / user.email，請設定你希望提交紀錄顯示的身分；此任務沒有替你猜測或更改 Git 身分。

之後的變更可透過自己的 feature 分支處理，再開 PR 回 main。服務集中於同一個 repo，仍可按資料夾分工與審查。
