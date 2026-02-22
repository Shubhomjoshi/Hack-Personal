"""
Test to verify order_number is extracted from OCR/Gemini, not hardcoded
"""
print("=" * 80)
print("TESTING ORDER_NUMBER EXTRACTION FROM OCR/GEMINI")
print("=" * 80)
print()

from database import SessionLocal
from models import Document

db = SessionLocal()

try:
    print("📊 Checking Recent Documents:")
    print()

    # Get latest 10 documents
    recent_docs = db.query(Document).order_by(Document.created_at.desc()).limit(10).all()

    if not recent_docs:
        print("⚠️  No documents found in database")
        print()
    else:
        print(f"Found {len(recent_docs)} recent document(s)")
        print()

        # Check for hardcoded values
        hardcoded_count = 0
        extracted_count = 0
        null_count = 0

        print("┌──────┬─────────────────────────────┬──────────────────────┬─────────────┐")
        print("│ ID   │ Filename                    │ order_number         │ Status      │")
        print("├──────┼─────────────────────────────┼──────────────────────┼─────────────┤")

        for doc in recent_docs:
            filename = doc.original_filename[:24] + "..." if len(doc.original_filename) > 27 else doc.original_filename
            order_num = doc.order_number or "NULL"

            # Check status
            if doc.order_number == "ORD-2026-001":
                status = "❌ HARDCODED"
                hardcoded_count += 1
            elif doc.order_number is None:
                status = "⏳ PENDING"
                null_count += 1
            else:
                status = "✅ EXTRACTED"
                extracted_count += 1

            print(f"│ {doc.id:<4} │ {filename:<27} │ {order_num:<20} │ {status:<11} │")

        print("└──────┴─────────────────────────────┴──────────────────────┴─────────────┘")
        print()

        # Summary
        print("📊 Summary:")
        print(f"   Total documents: {len(recent_docs)}")
        print(f"   Hardcoded (ORD-2026-001): {hardcoded_count}")
        print(f"   Extracted from document: {extracted_count}")
        print(f"   NULL (pending/not found): {null_count}")
        print()

        # Analysis
        if hardcoded_count > 0:
            print("❌ ISSUE DETECTED!")
            print(f"   {hardcoded_count} document(s) have hardcoded order_number = 'ORD-2026-001'")
            print()
            print("   This means:")
            print("   • OCR/Gemini extraction is not working properly")
            print("   • OR fallback to static values is happening")
            print()
            print("   Check:")
            print("   • services/background_processor.py lines with 'ORD-2026-001'")
            print("   • Gemini extraction results")
            print("   • Error logs during processing")
            print()
        else:
            print("✅ GOOD!")
            print("   No hardcoded values detected")
            print()
            if extracted_count > 0:
                print(f"   ✅ {extracted_count} document(s) have extracted order numbers")
            if null_count > 0:
                print(f"   ℹ️  {null_count} document(s) have NULL (waiting for OCR or not found)")
            print()

        # Show examples
        if extracted_count > 0:
            print("📋 Examples of Extracted Order Numbers:")
            extracted_docs = [d for d in recent_docs if d.order_number and d.order_number != "ORD-2026-001"][:3]
            for doc in extracted_docs:
                print(f"   • Doc {doc.id}: {doc.original_filename}")
                print(f"     order_number: {doc.order_number}")
                print(f"     selected_order_number: {doc.selected_order_number or 'N/A'}")
                if doc.selected_order_number == doc.order_number:
                    print(f"     Status: ✅ MATCH - Order verified!")
                elif doc.selected_order_number and doc.order_number:
                    print(f"     Status: ⚠️ MISMATCH - Needs review")
                print()

    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print()

    print("📖 Expected Behavior:")
    print()
    print("After Upload (Before OCR):")
    print("  • selected_order_number = Order from upload params ✅")
    print("  • order_number = NULL ✅")
    print()

    print("After OCR/Gemini Processing:")
    print("  • order_number = Value extracted from document ✅")
    print("  • OR order_number = NULL if not found in document ✅")
    print()

    print("NEVER:")
    print("  • order_number = 'ORD-2026-001' (hardcoded) ❌")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()

print()
print("To fix hardcoded values:")
print("1. Remove all instances of 'ORD-2026-001' in background_processor.py")
print("2. Let order_number stay NULL if Gemini doesn't extract it")
print("3. Upload a new document and check if it extracts correctly")
print()

