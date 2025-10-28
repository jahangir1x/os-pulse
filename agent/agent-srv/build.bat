@echo off
echo Building agent-srv...
go build -o agent-srv.exe .
if %errorlevel% equ 0 (
    echo Build successful!
    echo Run with: .\agent-srv.exe
) else (
    echo Build failed!
)
pause
