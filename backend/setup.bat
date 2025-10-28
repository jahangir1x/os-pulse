@echo off
echo Setting up OS-Pulse Backend...

echo Installing Go dependencies...
go mod tidy

echo.
echo Setup complete!
echo.
echo To run the backend:
echo   go run main.go
echo.
echo Make sure PostgreSQL is running and configure DATABASE_URL in environment
echo Default: postgres://postgres:password@localhost:5432/ospulse?sslmode=disable