Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Download 50 Clinical Trials" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location ml_models
python download_clinicaltrials.py --search "diabetes" --max 50

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Download Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Files saved to: downloaded_trials/" -ForegroundColor Yellow
Write-Host ""
Write-Host "To upload trials, go to: http://localhost:3000/upload" -ForegroundColor Yellow
Write-Host ""

