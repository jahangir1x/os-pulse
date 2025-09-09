@echo off
echo Setting up OS-Pulse Controller...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup completed successfully!
echo.
echo To activate the environment manually, run:
echo   .venv\Scripts\activate.bat
echo.
echo To start the controller, run:
echo   python main.py --help
echo.
pause
