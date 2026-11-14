@echo off
rem 其他 .cmd 共用的設定：朋友電腦、Git Bash、ssh、Python 的位置。
set "R=pypd@100.119.21.3"
set "W=C:\Users\pypd\hatrefish_gee"
for %%A in ("%~dp0..") do set "HF=%%~fA"
set "GB="
for %%G in ("%ProgramFiles%\Git\bin\bash.exe" "%LOCALAPPDATA%\Programs\Git\bin\bash.exe") do if not defined GB if exist %%G set "GB=%%~G"
if not defined GB for /f "delims=" %%P in ('where git 2^>nul') do if not defined GB if exist "%%~dpP..\bin\bash.exe" set "GB=%%~dpP..\bin\bash.exe"
if not defined GB (
  echo 找不到 Git Bash 的 bash.exe。請告訴 Claude Git 裝在哪裡。
  exit /b 1
)
for %%A in ("%GB%\..\..") do set "GITROOT=%%~fA"
set "SSH=%GITROOT%\usr\bin\ssh.exe"
if not exist "%SSH%" set "SSH=ssh"
set "PYBASE=%USERPROFILE%\miniconda3\python.exe"
if not exist "%PYBASE%" set "PYBASE=python"
set "ACT=%USERPROFILE%\miniconda3\Scripts\activate.bat"
exit /b 0
