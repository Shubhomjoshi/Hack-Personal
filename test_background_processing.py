"""
Test Background Processing - Verify all fields are updated correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Document, ValidationStatus, ReadabilityStatus
import time


def test_document_processing():
    """Test that background processing updates all required fields"""

    print("=" * 70)
    print("TESTING BACKGROUND PROCESSING FIELD UPDATES")
    print("=" * 70)

    db = SessionLocal()

    try:
        # Get the most recent document
        document = db.query(Document).order_by(Document.id.desc()).first()

        if not document:
            print("❌ No documents found in database")
            return

        print(f"\n📄 Testing Document ID: {document.id}")
        print(f"   Filename: {document.original_filename}")
        print(f"   Uploaded: {document.created_at}")
        print(f"   Last Updated: {document.updated_at}")

        # Check required fields
        fields_to_check = {
            "ocr_text": document.ocr_text,
            "quality_score": document.quality_score,
            "readability_status": document.readability_status,
            "is_blurry": document.is_blurry,
            "is_skewed": document.is_skewed,
            "uploaded_by": document.uploaded_by,
            "updated_at": document.updated_at,
        }

        print("\n" + "=" * 70)
        print("REQUIRED FIELD STATUS:")
        print("=" * 70)

        all_good = True
        for field_name, field_value in fields_to_check.items():
            status = "✅" if field_value is not None else "❌"
            print(f"{status} {field_name:20s}: {field_value}")
            if field_value is None:
                all_good = False

        print("\n" + "=" * 70)
        print("PROCESSING STATUS:")
        print("=" * 70)
        print(f"   Is Processed: {document.is_processed}")
        print(f"   Validation Status: {document.validation_status}")
        print(f"   Processing Error: {document.processing_error or 'None'}")

        # Check quality threshold
        print("\n" + "=" * 70)
        print("QUALITY THRESHOLD CHECK:")
        print("=" * 70)

        if document.quality_score is not None:
            if document.quality_score < 6:
                print(f"⚠️  QUALITY TOO LOW: {document.quality_score}% (threshold: 6%)")
                print(f"   Expected: Processing should stop")
                print(f"   Actual Status: {document.validation_status}")

                if document.validation_status == ValidationStatus.NEEDS_REVIEW:
                    print("   ✅ Correct: Status set to NEEDS_REVIEW")
                else:
                    print("   ❌ Error: Status should be NEEDS_REVIEW")
                    all_good = False

                if not document.is_processed:
                    print("   ✅ Correct: is_processed is False")
                else:
                    print("   ❌ Error: is_processed should be False")
                    all_good = False
            else:
                print(f"✅ QUALITY ACCEPTABLE: {document.quality_score}% (threshold: 6%)")
                print(f"   Processing should continue normally")
        else:
            print("⚠️  Quality score not yet calculated")

        # Additional fields (updated if quality >= 6)
        print("\n" + "=" * 70)
        print("OPTIONAL FIELDS (if quality >= 6):")
        print("=" * 70)

        optional_fields = {
            "document_type": document.document_type,
            "classification_confidence": document.classification_confidence,
            "has_signature": document.has_signature,
            "signature_count": document.signature_count,
            "order_number": document.order_number,
            "extracted_metadata": document.extracted_metadata
        }

        for field_name, field_value in optional_fields.items():
            status = "✅" if field_value is not None else "⚠️ "
            print(f"{status} {field_name:25s}: {field_value}")

        print("\n" + "=" * 70)
        print("OVERALL RESULT:")
        print("=" * 70)

        if all_good:
            print("✅ ALL REQUIRED FIELDS ARE UPDATED CORRECTLY")
        else:
            print("❌ SOME REQUIRED FIELDS ARE MISSING OR INCORRECT")

        print("=" * 70)

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🧪 Starting Background Processing Test...\n")
    test_document_processing()
    print("\n✅ Test Complete!\n")

