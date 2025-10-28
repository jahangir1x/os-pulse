@echo off
echo Starting OS-Pulse Backend...

REM Set default environment variables if not set
if "%DATABASE_URL%"=="" set DATABASE_URL=postgres://postgres:password@localhost:5432/ospulse?sslmode=disable
if "%AGENT_SERVICE_URL%"=="" set AGENT_SERVICE_URL=http://localhost:7000
if "%PORT%"=="" set PORT=3003

echo Database URL: %DATABASE_URL%
echo Agent Service URL: %AGENT_SERVICE_URL%
echo Port: %PORT%
echo.

go run main.go