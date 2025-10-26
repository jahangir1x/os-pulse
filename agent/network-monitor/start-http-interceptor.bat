@echo off
REM Start mitmproxy with HTTP interceptor

echo Starting mitmproxy HTTP/HTTPS interceptor...
echo.
echo Proxy will be available on: 127.0.0.1:8080
echo API endpoint: http://127.0.0.1:3003/network-monitor/events
echo.
echo Configure your applications to use proxy:
echo   HTTP Proxy: 127.0.0.1:8080
echo   HTTPS Proxy: 127.0.0.1:8080
echo.
echo For HTTPS interception, visit http://mitm.it to install certificate
echo.

REM Check if virtual environment exists and activate
if exist ".pyenv\Scripts\activate.bat" (
    call .pyenv\Scripts\activate.bat
)

REM Start mitmproxy with the interceptor
mitmdump -s http_interceptor.py --set confdir=%USERPROFILE%\.mitmproxy -v