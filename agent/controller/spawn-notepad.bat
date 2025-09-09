@echo off
REM Quick launcher for spawning notepad with monitoring

echo Starting OS-Pulse Controller - Spawning Notepad...
call .venv\Scripts\activate.bat
python main.py spawn --executable "C:\Windows\System32\notepad.exe" --interactive
