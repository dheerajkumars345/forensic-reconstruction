@echo off
echo ============================================
echo   STARTING FRONTEND (WEB INTERFACE)
echo ============================================
echo.
cd /d "%~dp0frontend"
echo Installing dependencies...
call npm install
echo.
echo Starting frontend on port 5173...
echo Open http://localhost:5173 in your browser
echo Press Ctrl+C to stop the server
echo.
call npm run dev
pause
