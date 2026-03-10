@echo off
echo ========================================
echo    TalentRadar - Starting Backend
echo ========================================
echo.

cd backend

echo Activating virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using global Python.
)

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API Docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
