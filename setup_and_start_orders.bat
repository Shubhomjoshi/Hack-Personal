@echo off
echo ====================================================================
echo ORDERS API SETUP AND START
echo ====================================================================
echo.

echo Step 1: Creating database table and adding order data...
python add_order_data.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to add order data!
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo Step 2: Starting FastAPI server...
echo ====================================================================
echo.
echo Server will start at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Orders API: http://localhost:8000/api/orders/
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

