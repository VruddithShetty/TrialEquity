# PowerShell script to start backend with error visibility
Write-Host "========================================"
Write-Host "Starting Clinical Trials Backend Server"
Write-Host "========================================"
Write-Host ""

cd $PSScriptRoot

Write-Host "Checking Python..."
python --version
Write-Host ""

Write-Host "Starting backend server..."
Write-Host "Press Ctrl+C to stop"
Write-Host ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

