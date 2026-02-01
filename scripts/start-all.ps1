# PowerShell script to start all services
# Clinical Trials Blockchain Platform

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Clinical Trials Platform" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if MongoDB is running
Write-Host "Checking MongoDB..." -ForegroundColor Yellow
try {
    $mongoCheck = Test-NetConnection -ComputerName localhost -Port 27017 -WarningAction SilentlyContinue
    if ($mongoCheck.TcpTestSucceeded) {
        Write-Host "✅ MongoDB is running on port 27017" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MongoDB is not running on port 27017" -ForegroundColor Yellow
        Write-Host "   Please start MongoDB:" -ForegroundColor Yellow
        Write-Host "   - Install MongoDB: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
        Write-Host "   - Or use Docker: docker run -d -p 27017:27017 mongo:7.0" -ForegroundColor Yellow
        Write-Host ""
        $startMongo = Read-Host "Do you want to continue anyway? (y/n)"
        if ($startMongo -ne "y") {
            exit
        }
    }
} catch {
    Write-Host "⚠️  Could not check MongoDB connection" -ForegroundColor Yellow
}

# Check if .env file exists
Write-Host ""
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  backend\.env not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env" -ErrorAction SilentlyContinue
    Write-Host "✅ Created backend\.env - Please update with your settings" -ForegroundColor Green
}

# Start backend
Write-Host ""
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Write-Host "   Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs will be at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

Set-Location backend
Start-Process python -ArgumentList "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -WindowStyle Normal

Write-Host ""
Write-Host "✅ Backend server starting..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Services Status:" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "To start frontend:" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm install" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

