"""
Quick validation test for updated background processor
"""
import sys
import os

print("=" * 70)
print("VALIDATING UPDATED BACKGROUND PROCESSOR")
print("=" * 70)

try:
    # Test imports
    print("\n1. Testing imports...")
    from services.background_processor import background_processor
    print("   ✅ Background processor imported successfully")

    from models import DocumentType, ReadabilityStatus, ValidationStatus
    print("   ✅ Models imported successfully")

    # Check if new methods exist
    print("\n2. Checking new static methods...")
    assert hasattr(background_processor, '_set_static_classification'), "Missing _set_static_classification"
    print("   ✅ _set_static_classification method exists")

    assert hasattr(background_processor, '_set_static_signature'), "Missing _set_static_signature"
    print("   ✅ _set_static_signature method exists")

    assert hasattr(background_processor, '_set_static_metadata'), "Missing _set_static_metadata"
    print("   ✅ _set_static_metadata method exists")

    # Check DocumentType has BILL_OF_LADING
    print("\n3. Checking DocumentType enum...")
    assert hasattr(DocumentType, 'BILL_OF_LADING'), "Missing BILL_OF_LADING in DocumentType"
    print("   ✅ DocumentType.BILL_OF_LADING exists")
    print(f"   Value: {DocumentType.BILL_OF_LADING.value}")

    print("\n4. Checking quality service...")
    from services.quality_service import quality_service
    assert hasattr(quality_service, 'assess_quality'), "Missing assess_quality method"
    print("   ✅ Quality service assess_quality method exists")

    print("\n5. Checking EasyOCR service...")
    from services.easyocr_service import easyocr_service
    assert hasattr(easyocr_service, 'extract_text'), "Missing extract_text method"
    print("   ✅ EasyOCR service extract_text method exists")

    print("\n" + "=" * 70)
    print("✅ ALL VALIDATIONS PASSED!")
    print("=" * 70)

    print("\n📋 Expected Behavior:")
    print("   • Quality threshold: < 55.0% triggers reupload")
    print("   • Document type: Bill of Lading (static)")
    print("   • Classification confidence: 1.0 (static)")
    print("   • Signature count: 1 (static)")
    print("   • has_signature: True (static)")
    print("   • Order number: ORD-2026-001 (static)")
    print("   • Invoice number: INV-2026-001 (static)")
    print("   • Document date: 2026-02-20 (static)")
    print("   • Load number: None (removed)")
    print("   • Completion log message: Added")

    print("\n🚀 Ready to start server and test!")
    print("   Run: python start_server.py")

except Exception as e:
    print(f"\n❌ VALIDATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

