@echo off
echo Starting Agent Server (Python Flask)...

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Run the Flask application
python app.py
