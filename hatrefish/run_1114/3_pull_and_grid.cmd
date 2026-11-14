@echo off
chcp 65001 >nul
setlocal
call "%~dp0_env.cmd" || goto :fail
cd /d "%HF%"
set "LOG=%HF%\run_1114\logs\stageA.log"
echo.
echo === 1/5 確認下載完成 ===
"%SSH%" -o ConnectTimeout=10 %R% "type %W%\logs\lst5.log" > "%TEMP%\lst5.log" || goto :fail
"%PYBASE%" run_1114\helper.py eta "%TEMP%\lst5.log"
if errorlevel 3 (echo 有失敗的塊。先重跑 1_start_download.cmd 補抓，或告訴 Claude。 & goto :fail)
if errorlevel 2 (echo 還沒抓完。 & goto :fail)
echo.
echo === 2/5 傳回 4 個地表溫度檔案（舊的已備份在 before_1114pm）===
for %%b in (lst_day_c lst_night_c dtr_c lst_mean_c) do call :pull %%b || goto :fail
echo.
echo === 3/5 重組全球網格（約 10-20 分鐘）===
echo 先關掉用不到的程式（Discord、多餘的瀏覽器分頁），記憶體比較夠。
call "%ACT%" nasa_hackathon
python -c "import sys; print('Python:', sys.prefix)"
python run_1114\helper.py run "%LOG%" -- scripts\run_pipeline.py --stage grid || goto :fail
echo.
echo === 4/5 檢查網格 ===
python run_1114\helper.py run "%LOG%" -- data\interim\rerun_1114_tools\check_grid.py || goto :fail
echo.
echo === 5/5 每月地表溫度推算：只看統計，還不寫檔 ===
python run_1114\helper.py run "%LOG%" -- scripts\derive_monthly_lst.py || goto :fail
echo.
echo 階段 A 完成。告訴 Claude「階段 A 跑完了」：Claude 會讀 run_1114\logs\stageA.log 檢查數字，
echo 沒問題再執行 4_rest.cmd。
pause
exit /b 0

:pull
"%GB%" data/interim/rerun_1114_tools/xfer.sh pull C:/Users/pypd/hatrefish_gee/data/interim/earth_0p1/%1.npy data/interim/earth_0p1/%1.npy > "%TEMP%\xfer.txt" 2>&1
type "%TEMP%\xfer.txt"
findstr /b /c:"OK " "%TEMP%\xfer.txt" >nul || (echo 傳檔失敗：%1 & exit /b 1)
exit /b 0

:fail
echo.
echo 停止。把這個視窗的內容複製給 Claude（log 也在 run_1114\logs\）。
pause
exit /b 1
