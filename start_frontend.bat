@echo off
echo ========================================
echo    TalentRadar - Starting Frontend
echo ========================================
echo.

cd frontend

echo Starting HTTP server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

python -m http.server 3000

pause
