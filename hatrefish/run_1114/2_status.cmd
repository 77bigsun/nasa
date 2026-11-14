@echo off
chcp 65001 >nul
setlocal
call "%~dp0_env.cmd" || goto :end
cd /d "%HF%"
"%SSH%" -o ConnectTimeout=10 %R% "type %W%\logs\lst5.log" > "%TEMP%\lst5.log" 2>nul
if errorlevel 1 (
  echo 讀不到朋友電腦上的 log（可能還沒開始，或連不上朋友電腦）。
  goto :end
)
"%PYBASE%" run_1114\helper.py eta "%TEMP%\lst5.log"
echo.
echo 朋友電腦上的 Python：
"%SSH%" %R% "tasklist | findstr /i python" || echo   （沒有 Python 在跑）
:end
if /i not "%~1"=="nopause" pause
