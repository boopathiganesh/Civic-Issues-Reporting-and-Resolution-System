@echo off
REM Smart Civic Issue Resolution System - Quick Start Script
REM Run this file to start the application automatically

title Smart Civic System - Starting...
color 0A

echo.
echo ================================================
echo  Smart Civic Issue Resolution System
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "backend\venv\" (
    echo [1/3] Creating Virtual Environment...
    python -m venv backend\venv
) else (
    echo [1/3] Virtual Environment found (skipping)
)

echo.
echo [2/3] Installing Dependencies...
call backend\venv\Scripts\activate.bat
pip install -q -r backend\requirements.txt

echo.
echo [3/3] Initializing Database...
pushd backend
python init_db.py
popd

echo.
echo ================================================
echo  Starting Application...
echo ================================================
echo.
echo Opening browser... (Press Ctrl+C in terminal to stop server)
echo.
timeout /t 2 /nobreak

REM Open browser
start http://localhost:5000

REM Start Flask application
pushd backend
python app.py
popd

pause
