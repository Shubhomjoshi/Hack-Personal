"""
Migration: Add selected_order_number column to documents table
"""
print("=" * 80)
print("MIGRATION: Adding selected_order_number to documents table")
print("=" * 80)
print()

import sys
from database import engine
from sqlalchemy import inspect, text

print("Step 1: Checking if documents table exists...")
inspector = inspect(engine)
tables = inspector.get_table_names()

if 'documents' not in tables:
    print("❌ documents table does not exist!")
    sys.exit(1)

print("✅ documents table exists")
print()

print("Step 2: Checking current columns...")
columns = inspector.get_columns('documents')
column_names = [col['name'] for col in columns]

print("   Checking for selected_order_number column...")

if 'selected_order_number' in column_names:
    print("✅ selected_order_number column already exists!")
    print()
else:
    print("❌ selected_order_number column not found")
    print()
    print("Step 3: Adding selected_order_number column...")

    try:
        # Add the column using raw SQL
        with engine.connect() as conn:
            # Add column
            conn.execute(text("""
                ALTER TABLE documents 
                ADD COLUMN selected_order_number VARCHAR(255)
            """))
            conn.commit()

        print("✅ selected_order_number column added successfully!")
        print()

        # Verify
        inspector = inspect(engine)
        new_columns = inspector.get_columns('documents')
        new_column_names = [col['name'] for col in new_columns]

        if 'selected_order_number' in new_column_names:
            print("✅ Verified: selected_order_number column is now in the table")
        else:
            print("⚠️ Warning: Column may not have been added correctly")

    except Exception as e:
        print(f"❌ Error adding column: {e}")
        print()
        print("Note: If you see 'duplicate column name' error, the column already exists.")
        print()
        sys.exit(1)

print()
print("Step 4: Copying order_number to selected_order_number for existing records...")

from database import SessionLocal
from models import Document

db = SessionLocal()

try:
    # Get documents that have order_info_id but no selected_order_number
    docs_to_update = db.query(Document).filter(
        Document.order_info_id.isnot(None),
        Document.selected_order_number.is_(None)
    ).all()

    print(f"   Found {len(docs_to_update)} documents to update")

    if docs_to_update:
        updated_count = 0
        for doc in docs_to_update:
            # Copy from order_info relationship
            if doc.order_info:
                doc.selected_order_number = doc.order_info.order_number
                updated_count += 1
                print(f"      Set selected_order_number for doc {doc.id} to '{doc.order_info.order_number}'")

        db.commit()
        print(f"   ✅ Updated {updated_count} documents!")
    else:
        print("   ℹ️ No documents to update")

except Exception as e:
    print(f"❌ Error updating documents: {e}")
    db.rollback()
finally:
    db.close()

print()
print("✅ MIGRATION COMPLETE!")
print()
print("Summary:")
print("  • selected_order_number column added to documents table")
print("  • Stores order number from upload parameters (driver_id or order_number)")
print("  • order_number column remains for OCR-extracted order numbers")
print("  • Existing documents updated with selected_order_number")
print()
print("Column Purpose:")
print("  • order_number: Extracted from document OCR/AI processing")
print("  • selected_order_number: Selected at upload time (from params)")
print()
print("Next steps:")
print("  1. Restart server: python main.py")
print("  2. Test upload API with order_number or driver_user_id")
print("  3. Check response includes selected_order_number field")
print()

