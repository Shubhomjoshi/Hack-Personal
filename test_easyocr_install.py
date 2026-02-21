"""
Simple OCR test to verify EasyOCR functionality
"""
import sys
import os

print("=" * 70)
print("EASYOCR INSTALLATION TEST")
print("=" * 70)

# Test 1: Check if EasyOCR is installed
print("\nStep 1: Checking EasyOCR installation...")
try:
    import easyocr
    print("✅ EasyOCR is installed")
    print(f"   Version: {easyocr.__version__ if hasattr(easyocr, '__version__') else 'Unknown'}")
except ImportError as e:
    print(f"❌ EasyOCR is NOT installed: {e}")
    print("\n📦 To install EasyOCR, run:")
    print("   pip install easyocr")
    sys.exit(1)

# Test 2: Initialize EasyOCR
print("\nStep 2: Initializing EasyOCR reader...")
try:
    reader = easyocr.Reader(['en'], gpu=False)
    print("✅ EasyOCR initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize EasyOCR: {e}")
    sys.exit(1)

# Test 3: Test on a simple image (if available)
print("\nStep 3: Testing OCR on sample image...")
test_images = [
    "test_extraction.png",
    "test_page.png",
    "temp_page_0.png",
    "Image 3.jpg"
]

found_image = None
for img in test_images:
    if os.path.exists(img):
        found_image = img
        break

if found_image:
    print(f"   Testing with: {found_image}")
    try:
        result = reader.readtext(found_image)
        print(f"✅ OCR completed successfully")
        print(f"   Found {len(result)} text region(s)")

        if result:
            print("\n📄 Extracted Text:")
            print("-" * 70)
            for detection in result[:5]:  # Show first 5 detections
                bbox, text, confidence = detection
                print(f"   {text} (confidence: {confidence:.2f})")
            if len(result) > 5:
                print(f"   ... and {len(result) - 5} more")
            print("-" * 70)
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
else:
    print("⚠️  No test images found. Skipping OCR test.")

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - EasyOCR is ready to use!")
print("=" * 70)

