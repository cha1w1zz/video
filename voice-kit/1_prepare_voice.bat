@echo off
chcp 65001 >nul
cd /d "%~dp0"
set SRC=%~1
if "%SRC%"=="" for %%f in (*.m4a *.wav *.mp3) do if not defined SRC set SRC=%%f
if "%SRC%"=="" (echo Put your recording (.m4a/.wav/.mp3) in this folder first. & pause & exit /b 1)
echo Using: %SRC%
venv\Scripts\python prep_ref.py "%SRC%" || (echo FAILED - copy the error text and send it to Claude & pause & exit /b 1)
echo.
echo === Opening ref.txt: CHECK the words and fix any mistakes, save, close. Then run 2_make_audio.bat ===
notepad ref.txt
pause
