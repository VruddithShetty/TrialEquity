@echo off
echo ========================================
echo Starting Frontend Server
echo ========================================
echo.
cd frontend
echo Installing dependencies (if needed)...
call npm install
echo.
echo Starting frontend on http://localhost:3000
echo.
echo Keep this window open!
echo.
call npm run dev
pause

