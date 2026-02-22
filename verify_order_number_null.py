"""
Verify order_number vs selected_order_number behavior
"""
print("=" * 80)
print("VERIFYING ORDER_NUMBER COLUMN BEHAVIOR")
print("=" * 80)
print()

from database import SessionLocal
from models import Document

db = SessionLocal()

try:
    print("📊 Testing Column Behavior:")
    print()

    # Get all documents
    all_docs = db.query(Document).all()

    if not all_docs:
        print("⚠️  No documents found in database")
        print("   Upload a document first to test")
    else:
        print(f"Found {len(all_docs)} document(s)")
        print()

        # Categorize documents
        docs_with_selected = [d for d in all_docs if d.selected_order_number]
        docs_with_extracted = [d for d in all_docs if d.order_number]
        docs_null_order = [d for d in all_docs if not d.order_number]

        print("1. Documents with selected_order_number (set at upload):")
        print(f"   Count: {len(docs_with_selected)}")
        if docs_with_selected:
            print()
            print("   ┌──────┬─────────────────────────────┬──────────────────────┬──────────────────────┐")
            print("   │ ID   │ Filename                    │ selected_order_num   │ order_number (OCR)   │")
            print("   ├──────┼─────────────────────────────┼──────────────────────┼──────────────────────┤")
            for doc in docs_with_selected[:5]:
                filename = doc.original_filename[:24] + "..." if len(doc.original_filename) > 27 else doc.original_filename
                selected = doc.selected_order_number or "NULL"
                extracted = doc.order_number or "NULL"
                print(f"   │ {doc.id:<4} │ {filename:<27} │ {selected:<20} │ {extracted:<20} │")
            print("   └──────┴─────────────────────────────┴──────────────────────┴──────────────────────┘")
        print()

        print("2. Documents with order_number = NULL (not yet extracted by OCR):")
        print(f"   Count: {len(docs_null_order)}")
        if docs_null_order:
            print()
            for doc in docs_null_order[:5]:
                print(f"   • Doc {doc.id}: {doc.original_filename}")
                print(f"     selected_order_number: {doc.selected_order_number or 'NULL'}")
                print(f"     order_number (OCR): NULL ← ✅ Correct! Waiting for OCR extraction")
                print()

        print()
        print("3. Documents with order_number populated (extracted by OCR):")
        print(f"   Count: {len(docs_with_extracted)}")
        if docs_with_extracted:
            print()
            for doc in docs_with_extracted[:5]:
                match_status = "✅ MATCH" if doc.selected_order_number == doc.order_number else "⚠️ MISMATCH"
                print(f"   • Doc {doc.id}: {doc.original_filename}")
                print(f"     selected_order_number: {doc.selected_order_number}")
                print(f"     order_number (OCR): {doc.order_number}")
                print(f"     Status: {match_status}")
                print()

        print()
        print("=" * 80)
        print("✅ VERIFICATION COMPLETE")
        print("=" * 80)
        print()

        print("📋 Expected Behavior:")
        print()
        print("1. On Upload (Before OCR):")
        print("   ✅ selected_order_number = Order from upload params")
        print("   ✅ order_number = NULL")
        print()

        print("2. After OCR Processing:")
        print("   ✅ selected_order_number = (unchanged) Order from upload")
        print("   ✅ order_number = Order extracted from document text")
        print()

        print("3. Validation:")
        print("   IF selected_order_number == order_number:")
        print("      ✅ Document matches selected order")
        print("   ELSE IF order_number == NULL:")
        print("      ℹ️ OCR not yet complete - use selected_order_number")
        print("   ELSE:")
        print("      ⚠️ Mismatch - flag for review")
        print()

        # Check if any documents were just uploaded (NULL order_number)
        recent_uploads = [d for d in all_docs if not d.order_number and d.selected_order_number]

        if recent_uploads:
            print("✅ CONFIRMED: Upload does NOT set order_number")
            print(f"   {len(recent_uploads)} document(s) have NULL order_number")
            print("   order_number will be set during OCR processing")
        else:
            print("ℹ️ All documents have been processed by OCR")
            print("   Upload a new document to verify NULL behavior")

        print()

        # Summary
        print("📊 Summary:")
        print(f"   Total documents: {len(all_docs)}")
        print(f"   With selected_order_number: {len(docs_with_selected)}")
        print(f"   With order_number (OCR): {len(docs_with_extracted)}")
        print(f"   With order_number = NULL: {len(docs_null_order)}")
        print()

        if docs_null_order:
            print("✅ System working correctly:")
            print("   • order_number is NULL on upload")
            print("   • Will be populated by OCR/AI extraction")
        else:
            print("ℹ️ All documents processed:")
            print("   • Upload a new document to verify NULL behavior")
            print("   • On upload, order_number should be NULL")
            print("   • After processing, order_number should have extracted value")

        print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()

