@echo off
echo ========================================
echo GORM Database Test Utility
echo ========================================
echo.

echo Checking if running from correct directory...
if not exist "go.mod" (
    echo Error: Please run this from the backend directory
    echo Usage: .\cmd\test_gorm\run-test.bat
    pause
    exit /b 1
)

echo.
echo Running GORM test...
echo.

go run cmd/test_gorm/main.go

echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo Test completed successfully!
    echo ========================================
) else (
    echo ========================================
    echo Test failed! Check error messages above.
    echo ========================================
    echo.
    echo Common issues:
    echo 1. PostgreSQL not running - Run: docker-compose up -d
    echo 2. Wrong credentials in .env file
    echo 3. Database 'ospulse' doesn't exist
)

pause
