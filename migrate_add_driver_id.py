"""
Migration script to add driver_id column to order_info table
"""
print("=" * 80)
print("MIGRATION: Adding driver_id column to order_info table")
print("=" * 80)
print()

import sys
from database import engine, SessionLocal
from models import User, OrderInfo
from sqlalchemy import inspect, text

print("Step 1: Checking if order_info table exists...")
inspector = inspect(engine)
tables = inspector.get_table_names()

if 'order_info' not in tables:
    print("❌ order_info table does not exist!")
    print("   Please run: python create_order_table_now.py first")
    sys.exit(1)

print("✅ order_info table exists")
print()

print("Step 2: Checking current columns...")
columns = inspector.get_columns('order_info')
column_names = [col['name'] for col in columns]

print("   Current columns:")
for col_name in column_names:
    print(f"      • {col_name}")
print()

if 'driver_id' in column_names:
    print("✅ driver_id column already exists!")
    print()
else:
    print("Step 3: Adding driver_id column...")

    try:
        # Add the column using raw SQL
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE order_info 
                ADD COLUMN driver_id INTEGER REFERENCES users(id)
            """))
            conn.commit()

        print("✅ driver_id column added successfully!")
        print()

        # Verify
        inspector = inspect(engine)
        new_columns = inspector.get_columns('order_info')
        new_column_names = [col['name'] for col in new_columns]

        if 'driver_id' in new_column_names:
            print("✅ Verified: driver_id column is now in the table")
        else:
            print("⚠️ Warning: Column may not have been added correctly")

    except Exception as e:
        print(f"❌ Error adding column: {e}")
        print()
        print("Alternative: Drop and recreate the table")
        print("   1. Backup your data if needed")
        print("   2. Delete app.db")
        print("   3. Run: python create_order_table_now.py")
        sys.exit(1)

print()
print("Step 4: Assigning drivers to existing orders...")
db = SessionLocal()

try:
    # Get all orders
    orders = db.query(OrderInfo).all()
    print(f"   Found {len(orders)} orders")

    if orders:
        # Get some users
        users = db.query(User).all()

        if users:
            print(f"   Found {len(users)} users to assign")

            # Assign users to orders in a round-robin fashion
            for i, order in enumerate(orders):
                if order.driver_id is None:
                    user = users[i % len(users)]
                    order.driver_id = user.id
                    print(f"      Assigned {order.order_number} to user ID {user.id} ({user.username})")

            db.commit()
            print("   ✅ Drivers assigned!")
        else:
            print("   ⚠️ No users found in database - orders will have no drivers")
    else:
        print("   ℹ️ No orders found in table")

except Exception as e:
    print(f"❌ Error assigning drivers: {e}")
    db.rollback()
finally:
    db.close()

print()
print("Step 5: Displaying updated orders...")
db = SessionLocal()

try:
    orders = db.query(OrderInfo).all()

    print()
    print("=" * 100)
    print(f"{'ID':<5} {'Order Number':<20} {'Customer Code':<20} {'Bill To Code':<20} {'Driver ID':<10}")
    print("=" * 100)

    for order in orders:
        driver_display = str(order.driver_id) if order.driver_id else "None"
        print(f"{order.id:<5} {order.order_number:<20} {order.customer_code:<20} {order.bill_to_code:<20} {driver_display:<10}")

    print("=" * 100)
    print(f"Total Orders: {len(orders)}")
    print("=" * 100)

finally:
    db.close()

print()
print("✅ MIGRATION COMPLETE!")
print()
print("Next steps:")
print("  1. Restart server: python main.py")
print("  2. Test API: GET /api/orders/")
print("  3. Response should now include 'driver_id' field")
print()

