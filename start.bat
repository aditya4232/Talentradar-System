@echo off
echo.
echo  ████████╗ █████╗ ██╗     ███████╗███╗   ██╗████████╗
echo  ╚══██╔══╝██╔══██╗██║     ██╔════╝████╗  ██║╚══██╔══╝
echo     ██║   ███████║██║     █████╗  ██╔██╗ ██║   ██║
echo     ██║   ██╔══██║██║     ██╔══╝  ██║╚██╗██║   ██║
echo     ██║   ██║  ██║███████╗███████╗██║ ╚████║   ██║
echo     ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝
echo          RADAR  -  AI Recruitment Platform
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Install from https://nodejs.org
    pause
    exit /b 1
)

:: Setup backend .env
if not exist "backend\.env" (
    echo [INFO] Creating backend\.env from template...
    copy "backend\.env.example" "backend\.env"
    echo [WARN] Please edit backend\.env and add your GROQ_API_KEY and GITHUB_TOKEN
    echo        Get GROQ key free at: https://console.groq.com
    echo        Get GitHub token at: https://github.com/settings/tokens
    echo.
)

:: Install backend dependencies
echo [1/4] Installing backend Python dependencies...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
cd ..

:: Install frontend dependencies
echo [2/4] Installing frontend Node dependencies...
cd frontend
if not exist "node_modules" (
    npm install --silent
)
cd ..

:: Start backend
echo [3/4] Starting FastAPI backend on http://localhost:8000 ...
start "TalentRadar Backend" cmd /k "cd backend && venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
echo [4/4] Starting React frontend on http://localhost:5173 ...
start "TalentRadar Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo  ✅ TalentRadar AI is starting up!
echo.
echo  Frontend:  http://localhost:5173
echo  Backend:   http://localhost:8000
echo  API Docs:  http://localhost:8000/docs
echo.
echo  First time? Click "Seed 100 Demo Candidates" in the Sourcing page.
echo.
pause
