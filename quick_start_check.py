"""
Quick Start Script - Upload API Test
"""
import sys
import os

print("=" * 70)
print("UPLOAD API - QUICK START CHECK")
print("=" * 70)

# Check 1: EasyOCR
print("\n[1/5] Checking EasyOCR...")
try:
    from services.easyocr_service import easyocr_service
    if easyocr_service.ocr_available:
        engine = "EasyOCR" if not easyocr_service.use_tesseract_fallback else "Tesseract"
        print(f"    ✅ OCR Engine: {engine}")
    else:
        print("    ❌ No OCR engine available")
        sys.exit(1)
except Exception as e:
    print(f"    ❌ Error: {e}")
    sys.exit(1)

# Check 2: Background Processor
print("\n[2/5] Checking Background Processor...")
try:
    from services.background_processor import background_processor
    print("    ✅ Background processor loaded")
except Exception as e:
    print(f"    ❌ Error: {e}")
    sys.exit(1)

# Check 3: Documents Router
print("\n[3/5] Checking Documents Router...")
try:
    from routers.documents import router
    print("    ✅ Documents router loaded")
except Exception as e:
    print(f"    ❌ Error: {e}")
    sys.exit(1)

# Check 4: Database
print("\n[4/5] Checking Database...")
try:
    from database import SessionLocal
    from models import Document
    db = SessionLocal()
    count = db.query(Document).count()
    db.close()
    print(f"    ✅ Database connected ({count} documents)")
except Exception as e:
    print(f"    ❌ Error: {e}")
    sys.exit(1)

# Check 5: Upload Directory
print("\n[5/5] Checking Upload Directory...")
if os.path.exists("uploads"):
    files = len([f for f in os.listdir("uploads") if os.path.isfile(os.path.join("uploads", f))])
    print(f"    ✅ Upload directory exists ({files} files)")
else:
    print("    ⚠️  Upload directory doesn't exist (will be created)")
    os.makedirs("uploads", exist_ok=True)
    print("    ✅ Created upload directory")

print("\n" + "=" * 70)
print("✅ ALL CHECKS PASSED - READY TO START SERVER!")
print("=" * 70)
print("\nTo start the server, run:")
print("  python start_server.py")
print("\nAPI will be available at:")
print("  http://localhost:8000")
print("  http://localhost:8000/docs (Swagger UI)")
print("\nUpload endpoint:")
print("  POST /api/documents/upload")
print("=" * 70)

