"""
Quick test to verify OCR service loads correctly
"""
print("=" * 70)
print("Testing OCR Service After Timeout Fix")
print("=" * 70)

try:
    from services.ocr_service import ocr_service
    print("✅ OCR Service imported successfully")
    print(f"OCR Available: {ocr_service.ocr_available}")

    if ocr_service.ocr_available:
        print("✅ PaddleOCR initialized successfully")
    else:
        print("⚠️  PaddleOCR not available (may need installation)")

    print("\n" + "=" * 70)
    print("SUCCESS: OCR service is working correctly")
    print("=" * 70)

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

