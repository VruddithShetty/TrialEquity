@echo off
echo ========================================
echo Download 50 Clinical Trials
echo ========================================
echo.

cd ml_models
python download_clinicaltrials.py --search "diabetes" --max 50

echo.
echo ========================================
echo Download Complete!
echo ========================================
echo.
echo Files saved to: downloaded_trials/
echo.
echo To upload trials, go to: http://localhost:3000/upload
echo.
pause

