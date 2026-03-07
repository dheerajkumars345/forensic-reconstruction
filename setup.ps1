# Crime Scene Reconstruction System - Setup Script

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Crime Scene Reconstruction System" -ForegroundColor Cyan
Write-Host "Setup Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.9 or higher." -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found. Please install Node.js 18 or higher." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Backend Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Setup Backend
Set-Location backend

Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Frontend Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Setup Frontend
Set-Location frontend

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Backend:" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""
Write-Host "2. Start Frontend (in a new terminal):" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "3. Open browser:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
