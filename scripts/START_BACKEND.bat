@echo off
echo ========================================
echo Starting Backend Server
echo ========================================
echo.
cd /d %~dp0backend
echo Current directory: %CD%
echo.
echo Checking Python...
python --version
echo.
echo Starting backend on http://localhost:8000
echo.
echo IMPORTANT: Keep this window open!
echo.
echo Waiting for backend to start...
echo You should see:
echo   - Connected to MongoDB
echo   - Created default test user
echo   - Uvicorn running
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
echo Backend stopped. Press any key to exit...
pause >nul

