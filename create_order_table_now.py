"""
FORCE CREATE order_info table and add data
"""
print("=" * 80)
print("CREATING ORDER_INFO TABLE AND ADDING DATA")
print("=" * 80)
print()

import sys
import os

# Ensure we're in the right directory
print(f"Working directory: {os.getcwd()}")
print(f"Database path: app.db")
print()

try:
    # Import required modules
    print("Step 1: Importing modules...")
    from database import engine, SessionLocal, Base
    from models import OrderInfo
    from sqlalchemy import inspect
    print("✅ Modules imported")
    print()

    # Create all tables
    print("Step 2: Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created/verified")
    print()

    # Check if table exists
    print("Step 3: Verifying order_info table...")
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()

    if 'order_info' in all_tables:
        print("✅ order_info table exists!")

        # Show table columns
        columns = inspector.get_columns('order_info')
        print("\n   Table columns:")
        for col in columns:
            print(f"      • {col['name']} ({col['type']})")
    else:
        print("❌ order_info table NOT FOUND!")
        print("\n   Available tables:")
        for table in all_tables:
            print(f"      • {table}")
        sys.exit(1)
    print()

    # Add data
    print("Step 4: Adding order data...")
    db = SessionLocal()

    try:
        # Check existing data
        existing_count = db.query(OrderInfo).count()
        print(f"   Current records: {existing_count}")

        if existing_count == 0:
            print("   Adding 5 orders...")

            # Get some user IDs to assign as drivers (if users exist)
            from models import User
            users = db.query(User).limit(5).all()
            user_ids = [user.id for user in users] if users else [None, None, None, None, None]

            if users:
                print(f"   Found {len(users)} users to assign as drivers")
            else:
                print("   No users found - orders will be created without drivers")

            orders_data = [
                ("ORD-112-2025", "LLTP1", "HILR1", user_ids[0]),
                ("ORD-112-2026", "LLTP2", "HILR2", user_ids[1]),
                ("ORD-112-2027", "LLTP3", "HILR3", user_ids[2]),
                ("ORD-112-2028", "LLTP4", "HILR4", user_ids[3]),
                ("ORD-112-2029", "LLTP5", "HILR5", user_ids[4]),
            ]

            for order_num, cust_code, bill_code, driver_id in orders_data:
                order = OrderInfo(
                    order_number=order_num,
                    customer_code=cust_code,
                    bill_to_code=bill_code,
                    driver_id=driver_id
                )
                db.add(order)
                driver_info = f" (Driver ID: {driver_id})" if driver_id else " (No driver)"
                print(f"      Added: {order_num}{driver_info}")

            db.commit()
            print("   ✅ All orders added!")
        else:
            print("   ℹ️  Orders already exist, skipping insertion")

        # Display all orders
        print()
        print("Step 5: Displaying all orders...")
        all_orders = db.query(OrderInfo).all()
        print()
        print("=" * 95)
        print(f"{'ID':<5} {'Order Number':<20} {'Customer Code':<20} {'Bill To Code':<20} {'Driver ID':<10}")
        print("=" * 95)

        for order in all_orders:
            driver_display = str(order.driver_id) if order.driver_id else "None"
            print(f"{order.id:<5} {order.order_number:<20} {order.customer_code:<20} {order.bill_to_code:<20} {driver_display:<10}")

        print("=" * 95)
        print(f"Total Orders: {len(all_orders)}")
        print("=" * 95)

    except Exception as e:
        print(f"❌ Error with data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

    print()
    print("✅ SUCCESS! Order data is ready.")
    print()
    print("Next steps:")
    print("  1. Start server: python main.py")
    print("  2. Access API: http://localhost:8000/docs")
    print("  3. Test endpoint: GET /api/orders/")
    print()

except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

