"""
Quick test to verify extract_text_from_file method exists
"""
import sys
import os

print("=" * 70)
print("Testing EasyOCR Service Fix")
print("=" * 70)
print()

try:
    # Import the service
    print("1. Importing easyocr_service...")
    from services.easyocr_service import easyocr_service
    print("   ✅ Import successful")
    print()

    # Check if method exists
    print("2. Checking extract_text_from_file method...")
    if hasattr(easyocr_service, 'extract_text_from_file'):
        print("   ✅ Method exists!")
    else:
        print("   ❌ Method NOT found!")
        sys.exit(1)
    print()

    # Check if method is callable
    print("3. Checking if method is callable...")
    if callable(getattr(easyocr_service, 'extract_text_from_file')):
        print("   ✅ Method is callable!")
    else:
        print("   ❌ Method is not callable!")
        sys.exit(1)
    print()

    # List all public methods
    print("4. Available methods in EasyOCRService:")
    methods = [m for m in dir(easyocr_service) if not m.startswith('_') and callable(getattr(easyocr_service, m))]
    for method in sorted(methods):
        print(f"   • {method}")
    print()

    print("=" * 70)
    print("✅ ALL TESTS PASSED - extract_text_from_file is ready!")
    print("=" * 70)
    print()
    print("The /api/samples/upload endpoint should now work correctly.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

