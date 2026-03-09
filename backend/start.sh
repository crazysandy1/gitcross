#!/bin/bash

echo "========================================"
echo "    GutBot - AI Health Chatbot"
echo "    Startup Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[1] Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "[2] Activating Python virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "[3] Installing backend dependencies..."
pip install -r requirements_backend.txt

# Start backend server
echo "[4] Starting backend server..."
python app_enhanced.py &
BACKEND_PID=$!

sleep 3

# Start frontend
cd frontend

echo "[5] Installing frontend dependencies..."
npm install

echo "[6] Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "========================================"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo "Health Check: http://localhost:5000/health"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
