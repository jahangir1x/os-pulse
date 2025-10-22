@echo off
echo Building OS-Pulse Go Controller...

REM Download dependencies
echo Downloading Go dependencies...
go mod tidy

REM Build the application
echo Building executable...
go build -o os-pulse.exe

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Build successful!
    echo.
    echo Usage examples:
    echo   .\os-pulse.exe list
    echo   .\os-pulse.exe spawn -e "C:\Windows\System32\notepad.exe"
    echo   .\os-pulse.exe attach -n notepad.exe
    echo.
    echo For API integration:
    echo   .\os-pulse.exe spawn -e "C:\Windows\System32\notepad.exe" --enable-api --api-endpoint "http://localhost:8080/api"
    echo.
) else (
    echo ❌ Build failed!
    exit /b 1
)