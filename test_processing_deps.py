"""
Test if document processing dependencies are working
"""
import sys
import os

print("=" * 70)
print("Testing Document Processing Dependencies")
print("=" * 70)
print()

# Test 1: Check if uploads directory exists
print("1. Checking uploads directory...")
if os.path.exists("uploads"):
    print("   ✅ uploads/ directory exists")
else:
    os.makedirs("uploads")
    print("   ✅ uploads/ directory created")

print()

# Test 2: Check OCR (Tesseract)
print("2. Testing OCR (Tesseract)...")
try:
    import pytesseract
    # Try to get version
    version = pytesseract.get_tesseract_version()
    print(f"   ✅ Tesseract installed: version {version}")
except ImportError:
    print("   ❌ pytesseract not installed")
    print("      Run: pip install pytesseract")
except Exception as e:
    print(f"   ⚠️  Tesseract found but not working: {e}")
    print("      You need to install Tesseract OCR:")
    print("      Download: https://github.com/UB-Mannheim/tesseract/wiki")

print()

# Test 3: Check OpenCV
print("3. Testing OpenCV...")
try:
    import cv2
    print(f"   ✅ OpenCV installed: version {cv2.__version__}")
except ImportError:
    print("   ❌ OpenCV not installed")
    print("      Run: pip install opencv-python")

print()

# Test 4: Check PIL/Pillow
print("4. Testing PIL/Pillow...")
try:
    from PIL import Image
    print(f"   ✅ Pillow installed")
except ImportError:
    print("   ❌ Pillow not installed")
    print("      Run: pip install Pillow")

print()

# Test 5: Check PDF libraries
print("5. Testing PDF libraries...")
try:
    import pdfplumber
    print(f"   ✅ pdfplumber installed")
except ImportError:
    print("   ❌ pdfplumber not installed")
    print("      Run: pip install pdfplumber")

try:
    import pdf2image
    print(f"   ✅ pdf2image installed")
except ImportError:
    print("   ❌ pdf2image not installed")
    print("      Run: pip install pdf2image")

print()

# Test 6: Test processing service imports
print("6. Testing processing service...")
try:
    from services.processing_service import processing_service
    print("   ✅ Processing service loaded")
except Exception as e:
    print(f"   ❌ Processing service error: {e}")

print()

# Test 7: Test individual services
print("7. Testing individual services...")
services = [
    'ocr_service',
    'classification_service',
    'quality_service',
    'signature_service',
    'metadata_service',
    'validation_service'
]

for service_name in services:
    try:
        module = __import__(f'services.{service_name}', fromlist=[service_name])
        print(f"   ✅ {service_name}")
    except Exception as e:
        print(f"   ❌ {service_name}: {e}")

print()
print("=" * 70)
print("TEST COMPLETE")
print()
print("If Tesseract is not installed:")
print("  1. Download: https://github.com/UB-Mannheim/tesseract/wiki")
print("  2. Install to: C:\\Program Files\\Tesseract-OCR")
print("  3. It should work automatically")
print("=" * 70)

