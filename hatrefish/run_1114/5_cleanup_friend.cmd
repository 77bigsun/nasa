@echo off
chcp 65001 >nul
setlocal
call "%~dp0_env.cmd" || goto :end
echo 這會在朋友電腦上（每一項都會先問你）：
echo   1. 刪掉你的 Earth Engine 登入憑證  C:\Users\pypd\.config\earthengine\credentials
echo   2. 刪掉整個工作資料夾  C:\Users\pypd\hatrefish_gee（venv、存檔、下載的陣列）
echo 等階段 A 確認沒問題再刪（之後不需要再從朋友電腦抓資料）。
echo.
choice /m "1. 刪掉憑證"
if errorlevel 2 goto :skip1
"%SSH%" %R% "del C:\Users\pypd\.config\earthengine\credentials && echo 已刪除憑證"
:skip1
choice /m "2. 刪掉工作資料夾 hatrefish_gee"
if errorlevel 2 goto :skip2
"%SSH%" %R% "rmdir /s /q C:\Users\pypd\hatrefish_gee && echo 已刪除工作資料夾"
:skip2
echo.
echo 另外：Google 帳號 - 安全性 - 第三方存取權 可以撤銷 Earth Engine 的授權。
echo 但撤銷會讓你自己電腦上的 Earth Engine 登入也失效，所以等所有 GEE 步驟（包括放大）都做完再撤銷。
:end
pause
