# Smart Civic Issue Resolution System - Quick Start Script
# Run this script to start the application automatically

Write-Host "================================================" -ForegroundColor Green
Write-Host "  Smart Civic Issue Resolution System" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Step 1: Create virtual environment if it doesn't exist
if (!(Test-Path "backend\venv")) {
    Write-Host "[1/3] Creating Virtual Environment..." -ForegroundColor Cyan
    python -m venv backend\venv
}
else {
    Write-Host "[1/3] Virtual Environment found (skipping)" -ForegroundColor Cyan
}

Write-Host ""

# Step 2: Activate virtual environment and install dependencies
Write-Host "[2/3] Installing Dependencies..." -ForegroundColor Cyan
& ".\backend\venv\Scripts\Activate.ps1"
pip install -q -r backend\requirements.txt

Write-Host ""

# Step 3: Initialize database
Write-Host "[3/3] Initializing Database..." -ForegroundColor Cyan
Set-Location backend
python init_db.py
Set-Location ..

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Starting Application..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Application will open at: http://localhost:5000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C in terminal to stop the server" -ForegroundColor Yellow
Write-Host ""

# Open browser after 2 seconds
Start-Sleep -Seconds 2
Start-Process "http://localhost:5000"

# Start Flask application
Set-Location backend
python app.py
Set-Location ..
