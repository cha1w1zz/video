@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === STEP 0: one-time setup (RTX 3060 Ti / CUDA 12.4) ===
where nvidia-smi >nul 2>nul || (echo NVIDIA driver not found. Install the latest Game Ready driver from nvidia.com, restart, run this again. & pause & exit /b 1)
nvidia-smi
where ffmpeg >nul 2>nul || (echo Installing ffmpeg... & winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements & echo ffmpeg installed. CLOSE this window and run 0_setup.bat again. & pause & exit /b 0)
py -3.11 --version >nul 2>nul || (echo Installing Python 3.11... & winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements & echo Python installed. CLOSE this window and run 0_setup.bat again. & pause & exit /b 0)
if not exist venv py -3.11 -m venv venv
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\pip install numpy==1.26.4
venv\Scripts\pip install torch==2.4.0+cu124 torchaudio==2.4.0+cu124 --extra-index-url https://download.pytorch.org/whl/cu124
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python -c "import torch;print('GPU:',torch.cuda.get_device_name(0)) if torch.cuda.is_available() else print('!! CUDA NOT AVAILABLE - tell Claude')"
echo === Setup done. Next: put your recording (e.g. Cleanmark.m4a) in this folder and run 1_prepare_voice.bat ===
pause
