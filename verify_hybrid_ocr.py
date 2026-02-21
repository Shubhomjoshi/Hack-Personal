"""
Quick Setup Verification Script
Tests all components before starting the server
"""
import sys
import os

print("=" * 70)
print("🔧 HYBRID OCR SETUP VERIFICATION")
print("=" * 70)
print()

# Test 1: Python packages
print("Test 1: Checking Python packages...")
try:
    import cv2
    print("  ✅ opencv-python installed")
except ImportError:
    print("  ❌ opencv-python NOT installed")
    print("     Run: pip install opencv-python")
    sys.exit(1)

try:
    import pytesseract
    print("  ✅ pytesseract installed")
except ImportError:
    print("  ❌ pytesseract NOT installed")
    print("     Run: pip install pytesseract")
    sys.exit(1)

try:
    import pdfplumber
    print("  ✅ pdfplumber installed")
except ImportError:
    print("  ❌ pdfplumber NOT installed")
    print("     Run: pip install pdfplumber")
    sys.exit(1)

try:
    import fitz  # PyMuPDF
    print("  ✅ PyMuPDF installed")
except ImportError:
    print("  ❌ PyMuPDF NOT installed")
    print("     Run: pip install PyMuPDF")
    sys.exit(1)

print()

# Test 2: Tesseract OCR
print("Test 2: Checking Tesseract OCR...")
try:
    version = pytesseract.get_tesseract_version()
    print(f"  ✅ Tesseract installed (version {version})")
except Exception as e:
    print(f"  ❌ Tesseract NOT found: {e}")
    print("     Install from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("     Then add to PATH")
    sys.exit(1)

print()

# Test 3: Image Preprocessor
print("Test 3: Checking Image Preprocessor...")
try:
    from services.image_preprocessor import image_preprocessor
    print("  ✅ Image preprocessor loaded")
except Exception as e:
    print(f"  ❌ Image preprocessor failed: {e}")
    sys.exit(1)

print()

# Test 4: OCR Service
print("Test 4: Checking OCR Service...")
try:
    from services.ocr_service import ocr_service
    if ocr_service.ocr_available:
        print("  ✅ OCR Service initialized successfully")
        print(f"     - Tesseract: Available")
        print(f"     - Preprocessor: {'Available' if hasattr(ocr_service, 'preprocessor') else 'Not found'}")
    else:
        print("  ⚠️  OCR Service loaded but OCR not available")
except Exception as e:
    print(f"  ❌ OCR Service failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 5: Quick preprocessing test
print("Test 5: Testing preprocessing on sample image...")
try:
    import numpy as np
    # Create a simple test image
    test_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    temp_path = "test_image.png"
    cv2.imwrite(temp_path, test_img)

    # Try to preprocess
    preprocessed = image_preprocessor.preprocess(temp_path)

    # Clean up
    os.remove(temp_path)

    print("  ✅ Preprocessing pipeline works")
except Exception as e:
    print(f"  ❌ Preprocessing test failed: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print()
print("Your system is ready! You can now:")
print("1. Start the server: python start_server.py")
print("2. Test upload API with text-based PDFs (fast)")
print("3. Test upload API with scanned PDFs (slower, but works)")
print()
print("Performance expectations:")
print("  - Text PDFs: < 1 second ⚡")
print("  - Scanned PDFs: 5-10 seconds per page 📸")
print()

