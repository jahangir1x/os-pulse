@echo off
REM Quick launcher for attaching to existing notepad process

echo Starting OS-Pulse Controller - Attaching to Notepad...
@REM call .venv\Scripts\activate.bat
python main.py attach --process-name "notepad.exe" --interactive
