"""
Simple script to add order data to database
"""
from database import engine, SessionLocal, Base
from models import OrderInfo
from sqlalchemy import inspect

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Tables created!")

print("\nAdding order data...")
db = SessionLocal()

try:
    # Check if data exists
    count = db.query(OrderInfo).count()
    print(f"Current order count: {count}")

    if count == 0:
        # Add orders
        orders = [
            OrderInfo(order_number="ORD-112-2025", customer_code="LLTP1", bill_to_code="HILR1"),
            OrderInfo(order_number="ORD-112-2026", customer_code="LLTP2", bill_to_code="HILR2"),
            OrderInfo(order_number="ORD-112-2027", customer_code="LLTP3", bill_to_code="HILR3"),
            OrderInfo(order_number="ORD-112-2028", customer_code="LLTP4", bill_to_code="HILR4"),
            OrderInfo(order_number="ORD-112-2029", customer_code="LLTP5", bill_to_code="HILR5"),
        ]

        for order in orders:
            db.add(order)

        db.commit()
        print(f"✅ Added {len(orders)} orders!")
    else:
        print("Orders already exist!")

    # Display all orders
    print("\n📊 All Orders:")
    print("-" * 70)
    all_orders = db.query(OrderInfo).all()
    for order in all_orders:
        print(f"ID: {order.id} | {order.order_number} | {order.customer_code} | {order.bill_to_code}")
    print("-" * 70)
    print(f"\nTotal: {len(all_orders)} orders")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ Done!")

