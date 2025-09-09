@echo off
REM Quick test script for API integration

echo Starting OS-Pulse API Integration Test
echo =====================================

REM Set API configuration
set OSPULSE_API_ENABLED=true
set OSPULSE_API_ENDPOINT=http://localhost:8080/api/events
set OSPULSE_API_KEY=test-key
set OSPULSE_LOG_LEVEL=INFO

echo Configuration:
echo   API Enabled: %OSPULSE_API_ENABLED%
echo   API Endpoint: %OSPULSE_API_ENDPOINT%
echo   API Key: %OSPULSE_API_KEY%
echo   Log Level: %OSPULSE_LOG_LEVEL%
echo.

echo Starting Python virtual environment...
call .\.pyenv\Scripts\activate.bat

echo.
echo Testing API integration...
python test_api_integration.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ API integration test passed!
    echo.
    echo Next steps:
    echo 1. Start the test API server: python test_api_server.py
    echo 2. Run OS-Pulse with API: python main.py spawn --executable "C:\Windows\System32\notepad.exe"
    echo 3. Perform file operations in notepad to see events
) else (
    echo.
    echo ❌ API integration test failed!
    echo Check the error messages above for troubleshooting.
)

echo.
pause
