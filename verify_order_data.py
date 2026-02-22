"""
Verify order_info table and data
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import OrderInfo


def verify_order_data():
    """Verify order info table exists and has data"""
    print("🔍 Verifying order_info table...\n")

    db = SessionLocal()

    try:
        # Query all orders
        orders = db.query(OrderInfo).all()

        if not orders:
            print("⚠️  No orders found in database")
            return

        print(f"✅ Found {len(orders)} orders in database\n")
        print("-" * 80)
        print(f"{'ID':<5} {'Order Number':<20} {'Customer Code':<20} {'Bill To Code':<20}")
        print("-" * 80)

        for order in orders:
            print(f"{order.id:<5} {order.order_number:<20} {order.customer_code:<20} {order.bill_to_code:<20}")

        print("-" * 80)
        print(f"\n✅ Verification complete! Table is ready.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    verify_order_data()

