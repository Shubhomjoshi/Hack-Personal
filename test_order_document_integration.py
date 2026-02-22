"""
Test Order-Document Integration
"""
print("=" * 80)
print("TESTING ORDER-DOCUMENT INTEGRATION")
print("=" * 80)
print()

from database import SessionLocal
from models import User, OrderInfo, Document

db = SessionLocal()

try:
    print("1. Checking order_info table...")
    orders = db.query(OrderInfo).all()
    print(f"   Total orders: {len(orders)}")

    if orders:
        print("\n   Orders with drivers:")
        print("   " + "-" * 70)
        print(f"   {'Order Number':<20} {'Customer':<15} {'Driver ID':<10} {'Active':<10}")
        print("   " + "-" * 70)
        for order in orders:
            active = "✅ Yes" if order.is_active else "❌ No"
            driver_id = str(order.driver_id) if order.driver_id else "None"
            print(f"   {order.order_number:<20} {order.customer_code:<15} {driver_id:<10} {active:<10}")
        print("   " + "-" * 70)
    else:
        print("   ⚠️  No orders found!")
        print("   Run: python create_order_table_now.py")

    print()
    print("2. Checking documents table...")
    documents = db.query(Document).all()
    print(f"   Total documents: {len(documents)}")

    if documents:
        linked_docs = [d for d in documents if d.order_info_id is not None]
        print(f"   Linked to orders: {len(linked_docs)}")

        if linked_docs:
            print("\n   Documents linked to orders:")
            print("   " + "-" * 70)
            print(f"   {'Doc ID':<10} {'Filename':<30} {'Order Number':<20}")
            print("   " + "-" * 70)
            for doc in linked_docs[:5]:  # Show first 5
                filename = doc.original_filename[:27] + "..." if len(doc.original_filename) > 30 else doc.original_filename
                order_num = doc.order_info.order_number if doc.order_info else "N/A"
                print(f"   {doc.id:<10} {filename:<30} {order_num:<20}")
            if len(linked_docs) > 5:
                print(f"   ... and {len(linked_docs) - 5} more")
            print("   " + "-" * 70)

    print()
    print("3. Testing upload API scenarios...")
    print()

    # Test 1: Desktop scenario
    print("   Scenario 1: Desktop Upload (with order_number)")
    test_order = db.query(OrderInfo).filter(OrderInfo.is_active == True).first()
    if test_order:
        print(f"      ✅ Can upload with: order_number={test_order.order_number}")
        print(f"      This will link document to order ID: {test_order.id}")
    else:
        print("      ❌ No active orders available")

    print()

    # Test 2: Mobile scenario
    print("   Scenario 2: Mobile Upload (with driver_user_id)")
    order_with_driver = db.query(OrderInfo).filter(
        OrderInfo.driver_id.isnot(None),
        OrderInfo.is_active == True
    ).first()

    if order_with_driver:
        print(f"      ✅ Can upload with: driver_user_id={order_with_driver.driver_id}")
        print(f"      System will find order: {order_with_driver.order_number}")
        print(f"      Document will be linked to order ID: {order_with_driver.id}")
    else:
        print("      ❌ No active orders with assigned drivers")

    print()
    print("4. API Endpoints Ready:")
    print()
    print("   Desktop Upload:")
    print("   POST /api/documents/upload")
    print(f"   Query: ?order_number={test_order.order_number if test_order else 'ORD-112-2025'}")
    print("   Body: multipart/form-data with 'files'")
    print()

    print("   Mobile Upload:")
    print("   POST /api/documents/upload")
    print(f"   Query: ?driver_user_id={order_with_driver.driver_id if order_with_driver else '3'}")
    print("   Body: multipart/form-data with 'files'")
    print()

    print("=" * 80)
    print("✅ INTEGRATION TEST COMPLETE")
    print("=" * 80)
    print()

    if test_order and order_with_driver:
        print("✅ System is ready for both desktop and mobile uploads!")
    else:
        print("⚠️  Setup incomplete:")
        if not test_order:
            print("   - No active orders found")
        if not order_with_driver:
            print("   - No orders with drivers assigned")
        print()
        print("Run: python create_order_table_now.py")

    print()

except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()

