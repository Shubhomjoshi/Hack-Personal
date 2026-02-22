"""
Fix script: Clear hardcoded order_number values from existing documents
This will reset order_number to NULL for documents with hardcoded 'ORD-2026-001'
"""
print("=" * 80)
print("FIXING HARDCODED ORDER_NUMBER VALUES")
print("=" * 80)
print()

from database import SessionLocal
from models import Document

db = SessionLocal()

try:
    print("📊 Step 1: Finding documents with hardcoded values...")
    print()

    # Find documents with hardcoded order_number
    hardcoded_docs = db.query(Document).filter(
        Document.order_number == "ORD-2026-001"
    ).all()

    if not hardcoded_docs:
        print("✅ No hardcoded values found!")
        print("   All documents are clean.")
        print()
    else:
        print(f"Found {len(hardcoded_docs)} document(s) with hardcoded 'ORD-2026-001'")
        print()

        print("Documents to fix:")
        for doc in hardcoded_docs:
            print(f"   • Doc {doc.id}: {doc.original_filename}")
            print(f"     Current order_number: {doc.order_number}")
            print(f"     selected_order_number: {doc.selected_order_number or 'N/A'}")
        print()

        # Ask for confirmation
        print("=" * 80)
        print("⚠️  WARNING: This will reset order_number to NULL for these documents")
        print("=" * 80)
        print()
        print("Options:")
        print("  1. The documents will need to be re-processed to extract order_number")
        print("  2. OR you can manually set order_number from selected_order_number")
        print()

        response = input("Do you want to proceed? (yes/no): ").strip().lower()
        print()

        if response in ['yes', 'y']:
            print("📝 Step 2: Clearing hardcoded values...")
            print()

            fixed_count = 0
            for doc in hardcoded_docs:
                old_value = doc.order_number
                doc.order_number = None
                fixed_count += 1
                print(f"   ✅ Doc {doc.id}: '{old_value}' → NULL")

            db.commit()

            print()
            print(f"✅ Fixed {fixed_count} document(s)")
            print()

            print("📋 Next Steps:")
            print("  1. These documents now have order_number = NULL")
            print("  2. Upload new documents to test extraction")
            print("  3. Check logs to see if Gemini extracts order_number correctly")
            print("  4. If Gemini doesn't extract, check Gemini response format")
            print()
        else:
            print("❌ Operation cancelled")
            print()

    print("=" * 80)
    print("✅ DONE")
    print("=" * 80)
    print()

    # Show summary
    print("📊 Current Database State:")
    all_docs = db.query(Document).all()
    hardcoded = len([d for d in all_docs if d.order_number == "ORD-2026-001"])
    extracted = len([d for d in all_docs if d.order_number and d.order_number != "ORD-2026-001"])
    null_count = len([d for d in all_docs if not d.order_number])

    print(f"   Total documents: {len(all_docs)}")
    print(f"   Hardcoded (ORD-2026-001): {hardcoded}")
    print(f"   Extracted from OCR/Gemini: {extracted}")
    print(f"   NULL (pending extraction): {null_count}")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()

finally:
    db.close()

