"""
Start server with detailed error logging
"""
import sys
import traceback

print("=" * 70)
print("Starting FastAPI Server with Debug Info")
print("=" * 70)

try:
    print("\n1. Testing imports...")
    from services.ocr_service import ocr_service
    print(f"   ✅ OCR Service loaded (Available: {ocr_service.ocr_available})")
    
    from services.processing_service import processing_service
    print("   ✅ Processing Service loaded")
    
    from database import init_db
    print("   ✅ Database module loaded")
    
    print("\n2. Initializing database...")
    init_db()
    print("   ✅ Database initialized")
    
    print("\n3. Starting FastAPI server...")
    print("   Server will start on: http://127.0.0.1:8000")
    print("   Swagger docs at: http://127.0.0.1:8000/docs")
    print("-" * 70)
    
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    
except KeyboardInterrupt:
    print("\n\n✅ Server stopped by user")
    sys.exit(0)
    
except Exception as e:
    print("\n" + "=" * 70)
    print("❌ STARTUP ERROR:")
    print("=" * 70)
    print(f"\nError: {str(e)}\n")
    print("Full traceback:")
    traceback.print_exc()
    print("\n" + "=" * 70)
    print("\nTroubleshooting:")
    print("1. Check if all dependencies are installed: pip install -r requirements.txt")
    print("2. Check if PaddleOCR is properly installed")
    print("3. Review the error message above")
    print("=" * 70)
    sys.exit(1)

