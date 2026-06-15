@echo off
REM Quick setup script for HIDCAS project

echo.
echo ========================================
echo HIDCAS - Quick Setup Script
echo ========================================
echo.

echo [1/3] Creating Python virtual environment...
python -m venv venv
echo.

echo [2/3] Activating virtual environment...
call .\venv\Scripts\activate.bat
echo.

echo [3/3] Installing dependencies...
pip install -r backend/requirements.txt
echo.

echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start PostgreSQL service
echo 2. Create database: createdb hidcas
echo 3. Run backend: cd backend && python -m uvicorn main:app --reload
echo 4. Open Frontend/index.html in browser
echo.
pause
