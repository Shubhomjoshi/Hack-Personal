"""
Validation Test - Check if all required fields are being updated correctly
"""
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Document

print("=" * 80)
print("FIELD UPDATE VALIDATION TEST")
print("=" * 80)

# Connect to database
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("\n1. Checking Document model structure...")
inspector = inspect(engine)
columns = inspector.get_columns('documents')

# Check required columns exist
required_columns = {
    'is_blurry': 'BOOLEAN',
    'is_skewed': 'BOOLEAN',
    'has_signature': 'BOOLEAN',
    'ocr_text': 'TEXT'
}

print("\nChecking required columns:")
for col in columns:
    col_name = col['name']
    if col_name in required_columns:
        col_type = str(col['type'])
        print(f"   ✅ {col_name}: {col_type}")

print("\n2. Checking recent documents with processing...")
try:
    # Get most recent processed document
    recent_doc = db.query(Document).filter(
        Document.is_processed == True
    ).order_by(Document.id.desc()).first()

    if not recent_doc:
        print("   ⚠️  No processed documents found")
        print("   💡 Upload a document and run processing first")
        sys.exit(0)

    print(f"\n   Found document ID: {recent_doc.id}")
    print(f"   Filename: {recent_doc.filename}")
    print(f"   Processed: {recent_doc.is_processed}")

    print("\n3. Validating field types and values:")

    # Check is_blurry
    print(f"\n   is_blurry:")
    print(f"      Value: {recent_doc.is_blurry}")
    print(f"      Type: {type(recent_doc.is_blurry).__name__}")
    if isinstance(recent_doc.is_blurry, bool):
        print(f"      ✅ Correct type (bool)")
    else:
        print(f"      ❌ Wrong type (expected bool, got {type(recent_doc.is_blurry).__name__})")

    # Check is_skewed
    print(f"\n   is_skewed:")
    print(f"      Value: {recent_doc.is_skewed}")
    print(f"      Type: {type(recent_doc.is_skewed).__name__}")
    if isinstance(recent_doc.is_skewed, bool):
        print(f"      ✅ Correct type (bool)")
    else:
        print(f"      ❌ Wrong type (expected bool, got {type(recent_doc.is_skewed).__name__})")

    # Check has_signature
    print(f"\n   has_signature:")
    print(f"      Value: {recent_doc.has_signature}")
    print(f"      Type: {type(recent_doc.has_signature).__name__}")
    if isinstance(recent_doc.has_signature, bool):
        print(f"      ✅ Correct type (bool)")
    else:
        print(f"      ❌ Wrong type (expected bool, got {type(recent_doc.has_signature).__name__})")

    # Check ocr_text
    print(f"\n   ocr_text:")
    if recent_doc.ocr_text:
        ocr_length = len(recent_doc.ocr_text)
        print(f"      Length: {ocr_length} characters")
        print(f"      Type: {type(recent_doc.ocr_text).__name__}")
        print(f"      First 100 chars: {recent_doc.ocr_text[:100]}")

        # Check if it contains expected content
        if ocr_length > 10:
            print(f"      ✅ Contains text (combined EasyOCR + Gemini)")
        else:
            print(f"      ⚠️  Very short text (may be error message)")

        # Check if it's an error message
        if recent_doc.ocr_text.startswith("ERROR:"):
            print(f"      ⚠️  Contains error message")
        else:
            print(f"      ✅ Valid extracted text")
    else:
        print(f"      ❌ OCR text is empty or None")

    print("\n4. Additional field checks:")

    # Quality score
    print(f"\n   quality_score: {recent_doc.quality_score}%")
    print(f"   readability_status: {recent_doc.readability_status}")

    # Signature count
    print(f"   signature_count: {recent_doc.signature_count}")
    print(f"   signature_count type: {type(recent_doc.signature_count).__name__}")

    # Metadata
    if recent_doc.extracted_metadata:
        print(f"\n   extracted_metadata keys: {list(recent_doc.extracted_metadata.keys())}")
        if 'client_name' in recent_doc.extracted_metadata:
            print(f"      client_name: {recent_doc.extracted_metadata['client_name']}")
        if 'signature_details' in recent_doc.extracted_metadata:
            sig_details = recent_doc.extracted_metadata['signature_details']
            print(f"      signature_details: {len(sig_details) if isinstance(sig_details, list) else 'present'}")

    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    # Summary
    checks = []

    if isinstance(recent_doc.is_blurry, bool):
        checks.append("✅ is_blurry: Boolean")
    else:
        checks.append("❌ is_blurry: Not Boolean")

    if isinstance(recent_doc.is_skewed, bool):
        checks.append("✅ is_skewed: Boolean")
    else:
        checks.append("❌ is_skewed: Not Boolean")

    if isinstance(recent_doc.has_signature, bool):
        checks.append("✅ has_signature: Boolean")
    else:
        checks.append("❌ has_signature: Not Boolean")

    if recent_doc.ocr_text and len(recent_doc.ocr_text) > 10 and not recent_doc.ocr_text.startswith("ERROR:"):
        checks.append("✅ ocr_text: Valid combined text")
    else:
        checks.append("❌ ocr_text: Missing or invalid")

    print()
    for check in checks:
        print(f"   {check}")

    # Overall status
    all_passed = all("✅" in check for check in checks)

    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED!")
    else:
        print("⚠️  SOME VALIDATIONS FAILED")
        print("\nRecommendations:")
        print("1. Upload a new document")
        print("2. Ensure Gemini API key is set")
        print("3. Check server logs for errors")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ Validation failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

