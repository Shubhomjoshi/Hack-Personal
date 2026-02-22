"""
Database migration script to add order_info table and populate with initial data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal
from models import Base, OrderInfo
from sqlalchemy import inspect


def table_exists(table_name: str) -> bool:
    """Check if table exists in database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def create_order_info_table():
    """Create the order_info table"""
    print("🔧 Creating order_info table...")

    if table_exists("order_info"):
        print("⚠️  Table 'order_info' already exists. Skipping creation.")
        return False

    # Create only the order_info table
    Base.metadata.tables['order_info'].create(engine)
    print("✅ Table 'order_info' created successfully!")
    return True


def populate_initial_data():
    """Populate order_info table with initial data"""
    print("\n📝 Populating initial order data...")

    db = SessionLocal()

    try:
        # Check if data already exists
        existing_count = db.query(OrderInfo).count()
        if existing_count > 0:
            print(f"⚠️  Table already contains {existing_count} records. Skipping data population.")
            return

        # Initial data
        orders_data = [
            {
                "order_number": "ORD-112-2025",
                "customer_code": "LLTP1",
                "bill_to_code": "HILR1"
            },
            {
                "order_number": "ORD-112-2026",
                "customer_code": "LLTP2",
                "bill_to_code": "HILR2"
            },
            {
                "order_number": "ORD-112-2027",
                "customer_code": "LLTP3",
                "bill_to_code": "HILR3"
            },
            {
                "order_number": "ORD-112-2028",
                "customer_code": "LLTP4",
                "bill_to_code": "HILR4"
            },
            {
                "order_number": "ORD-112-2029",
                "customer_code": "LLTP5",
                "bill_to_code": "HILR5"
            }
        ]

        # Insert data
        for order_data in orders_data:
            order = OrderInfo(**order_data)
            db.add(order)

        db.commit()
        print(f"✅ Successfully inserted {len(orders_data)} orders!")

        # Display inserted data
        print("\n📊 Inserted Orders:")
        print("-" * 70)
        print(f"{'Order Number':<20} {'Customer Code':<20} {'Bill To Code':<20}")
        print("-" * 70)

        for order_data in orders_data:
            print(f"{order_data['order_number']:<20} {order_data['customer_code']:<20} {order_data['bill_to_code']:<20}")

        print("-" * 70)

    except Exception as e:
        print(f"❌ Error populating data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main migration function"""
    print("=" * 70)
    print("📦 ORDER INFO TABLE MIGRATION")
    print("=" * 70)
    print()

    try:
        # Step 1: Create table
        table_created = create_order_info_table()

        # Step 2: Populate data
        populate_initial_data()

        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("📋 Next Steps:")
        print("  1. Restart your FastAPI server")
        print("  2. Access API endpoint: GET /api/orders/")
        print("  3. View Swagger docs: http://localhost:8000/docs")
        print()

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ MIGRATION FAILED: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

