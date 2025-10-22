@echo off
echo Starting OS-Pulse Go Controller with API integration test...

REM Set API configuration
set API_ENDPOINT=http://localhost:8080/api
set API_KEY=test-key

echo.
echo 🌐 API Configuration:
echo   Endpoint: %API_ENDPOINT%
echo   Key: %API_KEY%
echo.

REM Start with notepad and API enabled
echo 🚀 Starting notepad.exe with monitoring and API forwarding...
.\os-pulse.exe spawn --executable "C:\Windows\System32\notepad.exe" --enable-api --api-endpoint "%API_ENDPOINT%" --api-key "%API_KEY%"

echo.
echo Test completed.