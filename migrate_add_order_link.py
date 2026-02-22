"""
Migration: Add order_info_id column to documents table
"""
print("=" * 80)
print("MIGRATION: Adding order_info_id to documents table")
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

print("   Checking for order_info_id column...")

if 'order_info_id' in column_names:
    print("✅ order_info_id column already exists!")
    print()
else:
    print("❌ order_info_id column not found")
    print()
    print("Step 3: Adding order_info_id column...")

    try:
        # Add the column using raw SQL
        with engine.connect() as conn:
            # Add column
            conn.execute(text("""
                ALTER TABLE documents 
                ADD COLUMN order_info_id INTEGER REFERENCES order_info(id)
            """))
            conn.commit()

        print("✅ order_info_id column added successfully!")
        print()

        # Verify
        inspector = inspect(engine)
        new_columns = inspector.get_columns('documents')
        new_column_names = [col['name'] for col in new_columns]

        if 'order_info_id' in new_column_names:
            print("✅ Verified: order_info_id column is now in the table")
        else:
            print("⚠️ Warning: Column may not have been added correctly")

    except Exception as e:
        print(f"❌ Error adding column: {e}")
        print()
        print("Note: If you see 'duplicate column name' error, the column already exists.")
        print()
        sys.exit(1)

print()
print("Step 4: Linking existing documents to orders (if order_number matches)...")

from database import SessionLocal
from models import Document, OrderInfo

db = SessionLocal()

try:
    # Get documents that have order_number but no order_info_id
    unlinked_docs = db.query(Document).filter(
        Document.order_number.isnot(None),
        Document.order_info_id.is_(None)
    ).all()

    print(f"   Found {len(unlinked_docs)} documents with order_number but no order link")

    if unlinked_docs:
        linked_count = 0
        for doc in unlinked_docs:
            # Find matching order
            order = db.query(OrderInfo).filter(
                OrderInfo.order_number == doc.order_number
            ).first()

            if order:
                doc.order_info_id = order.id
                linked_count += 1
                print(f"      Linked document {doc.id} to order '{order.order_number}'")

        db.commit()
        print(f"   ✅ Linked {linked_count} documents to orders!")
    else:
        print("   ℹ️ No documents to link")

except Exception as e:
    print(f"❌ Error linking documents: {e}")
    db.rollback()
finally:
    db.close()

print()
print("✅ MIGRATION COMPLETE!")
print()
print("Summary:")
print("  • order_info_id column added to documents table")
print("  • Foreign key constraint to order_info.id")
print("  • Existing documents linked to orders (where possible)")
print()
print("Next steps:")
print("  1. Restart server: python main.py")
print("  2. Test upload API with order_number or driver_user_id")
print("  3. Documents will now be automatically linked to orders")
print()

