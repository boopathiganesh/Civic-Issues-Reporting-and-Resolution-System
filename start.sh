#!/bin/bash
# Smart Civic Issue Resolution System - Quick Start Script
# Run this script to start the application automatically

echo "================================================"
echo "  Smart Civic Issue Resolution System"
echo "================================================"
echo ""

# Step 1: Create virtual environment if it doesn't exist
# Step 1: Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "[1/3] Creating Virtual Environment..."
    python3 -m venv backend/venv
else
    echo "[1/3] Virtual Environment found (skipping)"
fi

echo ""

# Step 2: Activate virtual environment and install dependencies
echo "[2/3] Installing Dependencies..."
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt

echo ""

# Step 3: Initialize database
echo "[3/3] Initializing Database..."
cd backend
python init_db.py
cd ..

echo ""
echo "================================================"
echo "  Starting Application..."
echo "================================================"
echo ""
echo "Application will open at: http://localhost:5000"
echo "Press Ctrl+C in terminal to stop the server"
echo ""

# Open browser after 2 seconds (macOS/Linux)
sleep 2
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:5000"
else
    xdg-open "http://localhost:5000" 2>/dev/null || echo "Please open http://localhost:5000 in your browser"
fi

# Start Flask application
cd backend
python app.py
cd ..
