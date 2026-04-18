@echo off
cd /d "%~dp0"
if not exist "dino_env\" (
    echo First time setup - Creating virtual environment...
    python -m venv dino_env
    echo.
    echo Installing MediaPipe, OpenCV, PyAutoGUI, NumPy...
    call dino_env\Scripts\activate.bat
    pip install mediapipe==0.10.9 opencv-python pyautogui numpy
    echo.
    echo Setup complete!
) else (
    call dino_env\Scripts\activate.bat
)
echo Starting game controller...
python dino_controller.py
pause