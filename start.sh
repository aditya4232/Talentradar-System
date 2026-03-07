#!/bin/bash
set -e

echo ""
echo "  TalentRadar AI - Recruitment Platform"
echo "  ======================================"
echo ""

# Checks
command -v python3 >/dev/null 2>&1 || { echo "[ERROR] Python3 not found"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "[ERROR] Node.js not found"; exit 1; }

# Setup .env
if [ ! -f "backend/.env" ]; then
  echo "[INFO] Creating backend/.env from template..."
  cp backend/.env.example backend/.env
  echo "[WARN] Edit backend/.env and add your GROQ_API_KEY and GITHUB_TOKEN"
  echo "       GROQ (free): https://console.groq.com"
  echo ""
fi

# Backend venv
echo "[1/4] Setting up Python virtual environment..."
cd backend
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt -q
cd ..

# Frontend deps
echo "[2/4] Installing frontend dependencies..."
cd frontend
[ ! -d "node_modules" ] && npm install --silent
cd ..

# Start backend
echo "[3/4] Starting FastAPI backend on http://localhost:8000 ..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend
echo "[4/4] Starting React frontend on http://localhost:5173 ..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "  ✅ TalentRadar AI is running!"
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "  First time? Click 'Seed 100 Demo Candidates' in the Sourcing page."
echo ""
echo "  Press Ctrl+C to stop both servers."
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
