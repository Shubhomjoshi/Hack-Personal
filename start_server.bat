@echo off
REM FastAPI Server Startup Script (Windows)
REM AI-Powered Document Intelligence Backend

echo.
echo ========================================================================
echo   AI-Powered Document Intelligence API - Server Startup
echo ========================================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please create virtual environment first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if main.py exists
if not exist "main.py" (
    echo [ERROR] main.py not found!
    echo Please ensure you're in the correct directory.
    pause
    exit /b 1
)

REM Start the server
echo [INFO] Starting FastAPI server...
echo.
python start_server.py

pause

