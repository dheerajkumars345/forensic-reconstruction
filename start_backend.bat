@echo off
echo ============================================
echo   STARTING BACKEND SERVER
echo ============================================
echo.
cd /d "%~dp0backend"
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting backend server on port 8000...
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn main:app --reload --port 8000
pause
