@echo off
chcp 65001 >nul
setlocal
call "%~dp0_env.cmd" || goto :fail
cd /d "%HF%"
echo.
echo === 1/4 測試登入朋友電腦（金鑰登入）===
"%SSH%" -o BatchMode=yes -o ConnectTimeout=10 %R% "echo ok" >nul 2>&1
if errorlevel 1 (
  echo 金鑰登入失敗。請在這個視窗輸入：  ssh %R%
  echo 如果它要密碼，告訴 Claude（傳檔程式需要金鑰登入，不要把密碼貼給 Claude）。
  goto :fail
)
echo OK
echo.
echo === 2/4 檢查朋友電腦上有沒有還在跑的 Python ===
rem tasklist 在朋友電腦上會出錯，改用 PowerShell 的 Get-Process；沒有 Python 時輸出是空的。
set "PSC=C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -Command"
"%SSH%" %R% "%PSC% (Get-Process python -ErrorAction SilentlyContinue).Id" > "%TEMP%\pyids.txt" 2>nul
if errorlevel 255 (echo 連不上朋友電腦。& goto :fail)
set "PYSZ=0"
for %%S in ("%TEMP%\pyids.txt") do set "PYSZ=%%~zS"
if not "%PYSZ%"=="0" (
  echo 朋友電腦上 Python 的行程編號：
  type "%TEMP%\pyids.txt"
  echo 上面有 Python 在跑。如果是之前的下載還活著，不要再開一個，改用 2_status.cmd 看進度。
  choice /m "確定要再開一個下載嗎"
  if errorlevel 2 goto :fail
) else (
  echo 沒有，可以開始。
)
echo.
echo === 3/4 把兩個改過的檔案傳到朋友電腦 ===
call :push src/mars_analog/adapters/earth/gee_layers.py C:/Users/pypd/hatrefish_gee/src/mars_analog/adapters/earth/gee_layers.py || goto :fail
call :push data/interim/rerun_1114_tools/remote_fetch.py C:/Users/pypd/hatrefish_gee/remote_fetch.py || goto :fail
echo.
echo === 4/4 開始下載全球地表溫度（2020-2024，workers 20）===
echo 這個視窗要一直開著，電腦不要睡眠。大約 35-70 分鐘。
echo 看進度：另開一個視窗，執行 run_1114\2_status.cmd
echo.
"%SSH%" -o ServerAliveInterval=30 %R% "cd /d %W% && .venv\Scripts\python.exe -u -W ignore remote_fetch.py lst --project nasa-spaceapp-hackathon --workers 20 >> logs\lst5.log 2>&1"
echo.
echo ssh 結束了。目前狀態：
call "%~dp02_status.cmd" nopause
echo.
echo 如果上面說「全部完成」：執行 3_pull_and_grid.cmd。
echo 如果還沒完成而且朋友電腦上沒有 Python 在跑：重跑這個檔案，會從存檔接著抓。
pause
exit /b 0

:push
"%GB%" data/interim/rerun_1114_tools/xfer.sh push %1 %2 > "%TEMP%\xfer.txt" 2>&1
type "%TEMP%\xfer.txt"
findstr /b /c:"OK " "%TEMP%\xfer.txt" >nul || (echo 傳檔失敗：%1 & exit /b 1)
exit /b 0

:fail
echo.
echo 停止。把這個視窗的內容複製給 Claude。
pause
exit /b 1
