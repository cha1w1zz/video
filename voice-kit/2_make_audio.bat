@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ref.wav (echo Run 1_prepare_voice.bat first. & pause & exit /b 1)
if not exist lines.txt copy lines.example.txt lines.txt >nul
echo Speaking every line in lines.txt (edit lines.txt to change the text)...
venv\Scripts\python speak_batch.py --ref ref.wav --ref-text-file ref.txt --script lines.txt --outdir out --steps 32 || (echo FAILED - copy the error text and send it to Claude & pause & exit /b 1)
start "" "%~dp0out"
pause
