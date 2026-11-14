@echo off
chcp 65001 >nul
setlocal
call "%~dp0_env.cmd" || goto :fail
cd /d "%HF%"
set "LOG=%HF%\run_1114\logs\stageB.log"
set "SOFT="
echo 階段 B：每月溫度、剖面、R1-R6、集合覆蓋、網頁資料、放大、新舊比較。大約 1.5-2 小時。
echo 一步跑完才跑下一步。先關掉用不到的程式。
call "%ACT%" nasa_hackathon
python run_1114\helper.py mark run_1114\logs\stageB_start.txt
call :step 1 "每月地表溫度推算（寫檔）" scripts\derive_monthly_lst.py --write || goto :fail
call :step 2 "重組 earth_monthly / earth_extra" scripts\fetch_earth_extra_gee.py --assemble || goto :fail
call :step 3 "類比剖面" scripts\make_profiles.py || goto :fail
call :step 4 "測試項目 R1-R6" scripts\make_mission_tests.py || goto :fail
call :step 5 "集合覆蓋" scripts\make_set_cover.py || goto :fail
call :step 6 "網頁資料" scripts\export_web_seed.py --web-seed ..\..\nasa-main\data\seed --check || set "SOFT=%SOFT% 網頁資料"
call :step 7 "放大：先試一個方框" scripts\zoom_candidates.py --test
if errorlevel 1 (
  set "SOFT=%SOFT% 放大"
  echo 放大的測試失敗，跳過完整放大。
) else (
  call :step 8 "放大：每個目標前 3 名（會用 GEE，最久）" scripts\zoom_candidates.py --top 3 --refresh || set "SOFT=%SOFT% 放大"
)
python run_1114\helper.py move_old_zoom run_1114\logs\stageB_start.txt
call :step 9 "新舊比較" data\interim\before_1114pm\compare.py --md data\interim\before_1114pm\compare_out.md || set "SOFT=%SOFT% 比較"
echo.
if defined SOFT (
  echo 階段 B 跑完，但這幾步失敗：%SOFT%
) else (
  echo 階段 B 全部完成。
)
echo 告訴 Claude「階段 B 跑完了」：Claude 會讀 run_1114\logs\stageB.log，寫 WORKLOG 第 13 節、更新文件。
echo 之後執行 5_cleanup_friend.cmd 清掉朋友電腦上的憑證。
pause
exit /b 0

:step
set "N=%~1"
set "T=%~2"
shift
shift
echo.
echo === 第 %N%/9 步：%T% ===
set "ARGS="
:collect
if "%~1"=="" goto :go
set "ARGS=%ARGS% %1"
shift
goto :collect
:go
python run_1114\helper.py run "%LOG%" -- %ARGS%
exit /b %errorlevel%

:fail
echo.
echo 停止。把這個視窗的內容複製給 Claude（log 在 run_1114\logs\stageB.log）。
pause
exit /b 1
