@echo off
REM Batch script to start all services
REM Clinical Trials Blockchain Platform

echo ========================================
echo Starting Clinical Trials Platform
echo ========================================
echo.

REM Check if MongoDB is running
echo Checking MongoDB...
netstat -an | findstr "27017" >nul
if %errorlevel% == 0 (
    echo [OK] MongoDB is running on port 27017
) else (
    echo [WARNING] MongoDB is not running on port 27017
    echo Please start MongoDB:
    echo   - Install MongoDB: https://www.mongodb.com/try/download/community
    echo   - Or use Docker: docker run -d -p 27017:27017 mongo:7.0
    echo.
    set /p startMongo="Do you want to continue anyway? (y/n): "
    if /i not "%startMongo%"=="y" exit
)

REM Check if .env file exists
echo.
echo Checking environment configuration...
if not exist "backend\.env" (
    echo [WARNING] backend\.env not found. Creating from template...
    copy "backend\.env.example" "backend\.env" >nul 2>&1
    echo [OK] Created backend\.env - Please update with your settings
)

REM Start backend
echo.
echo Starting Backend Server...
echo    Backend will be available at: http://localhost:8000
echo    API Docs will be at: http://localhost:8000/docs
echo.

cd backend
start "Clinical Trials Backend" python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
cd ..

echo.
echo [OK] Backend server starting...
echo.
echo ========================================
echo Services Status:
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo To start frontend:
echo   cd frontend
echo   npm install
echo   npm run dev
echo ========================================
pause

