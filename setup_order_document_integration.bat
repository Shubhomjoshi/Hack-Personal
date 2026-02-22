@echo off
echo ================================================================================
echo COMPLETE SETUP: ORDER-DOCUMENT INTEGRATION
echo ================================================================================
echo.

echo This script will:
echo   1. Create/update order_info table with driver_id column
echo   2. Add order_info_id column to documents table
echo   3. Add 5 sample orders with drivers assigned
echo   4. Link existing documents to orders
echo   5. Start the FastAPI server
echo.
echo After setup, you can upload documents with:
echo   - Desktop app: order_number parameter
echo   - Mobile app: driver_user_id parameter
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo ================================================================================
echo STEP 1: Setting up order_info table with driver assignments...
echo ================================================================================
echo.

python create_order_table_now.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to create order_info table!
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo STEP 2: Adding order_info_id to documents table...
echo ================================================================================
echo.

python migrate_add_order_link.py
if errorlevel 1 (
    echo.
    echo Note: If you see 'duplicate column' error, the column already exists.
    echo This is normal if you've run this script before.
    echo.
)

echo.
echo ================================================================================
echo STEP 3: Starting FastAPI server...
echo ================================================================================
echo.
echo Server will start at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Upload API: POST /api/documents/upload
echo   Desktop app: ?order_number=ORD-112-2025
echo   Mobile app:  ?driver_user_id=3
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

