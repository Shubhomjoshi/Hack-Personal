"""
Check and create order_info table in app.db
"""
import os
from database import engine, SessionLocal, Base
from models import OrderInfo
from sqlalchemy import inspect, text

print("=" * 70)
print("CHECKING ORDER_INFO TABLE IN DATABASE")
print("=" * 70)
print()

# Check database file
db_path = "app.db"
if os.path.exists(db_path):
    print(f"✅ Database file exists: {db_path}")
    print(f"   Size: {os.path.getsize(db_path)} bytes")
else:
    print(f"❌ Database file not found: {db_path}")
print()

# Check existing tables
print("📊 Existing Tables:")
inspector = inspect(engine)
tables = inspector.get_table_names()
for table in tables:
    print(f"   • {table}")
print(f"\nTotal tables: {len(tables)}")
print()

# Check if order_info exists
if 'order_info' in tables:
    print("✅ order_info table EXISTS")

    # Check data
    db = SessionLocal()
    try:
        count = db.query(OrderInfo).count()
        print(f"   Records in table: {count}")

        if count > 0:
            print("\n📋 Existing Orders:")
            orders = db.query(OrderInfo).all()
            for order in orders:
                print(f"      {order.id}. {order.order_number} → {order.customer_code} → {order.bill_to_code}")
        else:
            print("   ⚠️  Table is empty!")
    except Exception as e:
        print(f"   ❌ Error reading data: {e}")
    finally:
        db.close()
else:
    print("❌ order_info table DOES NOT EXIST")
    print("\n🔧 Creating table now...")

    try:
        # Create all tables (will only create missing ones)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created!")

        # Verify creation
        inspector = inspect(engine)
        if 'order_info' in inspector.get_table_names():
            print("✅ order_info table created successfully!")
        else:
            print("❌ Failed to create order_info table")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 70)

