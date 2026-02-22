@echo off
echo ================================================================================
echo COMPLETE SETUP: ORDER INFO TABLE WITH DRIVER ASSIGNMENT
echo ================================================================================
echo.

echo This script will:
echo   1. Create/update order_info table with driver_id column
echo   2. Add 5 sample orders
echo   3. Assign drivers to orders
echo   4. Start the FastAPI server
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo ================================================================================
echo STEP 1: Setting up order_info table with driver_id...
echo ================================================================================
echo.

python create_order_table_now.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to create table!
    echo.
    echo Trying migration approach...
    python migrate_add_driver_id.py
    if errorlevel 1 (
        echo.
        echo ERROR: Both methods failed!
        echo.
        echo Manual fix:
        echo   1. Delete app.db
        echo   2. Run: python create_order_table_now.py
        pause
        exit /b 1
    )
)

echo.
echo ================================================================================
echo STEP 2: Starting FastAPI server...
echo ================================================================================
echo.
echo Server will start at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Orders API: http://localhost:8000/api/orders/
echo.
echo API Response will include 'driver_id' field!
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

