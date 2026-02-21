"""
Test API imports and basic functionality
"""
import sys
import os

print("=" * 70)
print("Testing API Components")
print("=" * 70)

all_passed = True

# Test 1: Import main modules
print("\n[Test 1] Importing core modules...")
try:
    import main
    print("✅ main.py imported successfully")
except Exception as e:
    print(f"❌ main.py import failed: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False

# Test 2: Import routers
print("\n[Test 2] Importing routers...")
try:
    from routers import documents, auth, analytics, validation_rules
    print("✅ All routers imported successfully")
except Exception as e:
    print(f"❌ Router import failed: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False

# Test 3: Import services
print("\n[Test 3] Importing services...")
try:
    from services.ocr_service import ocr_service
    from services.processing_service import processing_service
    print(f"✅ Services imported successfully")
    print(f"   - OCR Available: {ocr_service.ocr_available}")
except Exception as e:
    print(f"❌ Service import failed: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False

# Test 4: Check concurrent.futures
print("\n[Test 4] Testing concurrent.futures...")
try:
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

    def test_func():
        return "success"

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(test_func)
        result = future.result(timeout=5)

    print("✅ ThreadPoolExecutor working correctly")
except Exception as e:
    print(f"❌ concurrent.futures test failed: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False

# Test 5: Database
print("\n[Test 5] Testing database...")
try:
    from database import get_db, init_db
    init_db()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"❌ Database test failed: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False

# Summary
print("\n" + "=" * 70)
if all_passed:
    print("✅ ALL TESTS PASSED - API should work correctly")
    print("\nYou can now start the server with:")
    print("  python start_server.py")
    print("  OR")
    print("  python start_debug.py  (for detailed logging)")
else:
    print("❌ SOME TESTS FAILED - Check errors above")
    print("\nThe 500 error is likely caused by one of the failed tests above.")

print("=" * 70)

