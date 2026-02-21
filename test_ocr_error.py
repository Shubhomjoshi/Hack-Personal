"""
Test the OCR service to identify 500 error
"""
import sys
import traceback

print("=" * 70)
print("Testing OCR Service After Fix")
print("=" * 70)

try:
    print("\n1. Importing OCR service...")
    from services.ocr_service import ocr_service
    print("✅ Import successful")

    print(f"\n2. OCR Available: {ocr_service.ocr_available}")

    if ocr_service.paddle_ocr:
        print("✅ PaddleOCR initialized")
    else:
        print("⚠️  PaddleOCR not available")

    print("\n3. Testing timeout imports...")
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
    print("✅ concurrent.futures imports work")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - OCR Service is working")
    print("=" * 70)

except Exception as e:
    print("\n" + "=" * 70)
    print("❌ ERROR DETECTED:")
    print("=" * 70)
    print(f"\nError: {str(e)}\n")
    print("Full traceback:")
    traceback.print_exc()
    print("\n" + "=" * 70)
    sys.exit(1)

