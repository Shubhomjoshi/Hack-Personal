"""
Quick verification that all fixes are applied correctly
"""
import sys

print("=" * 70)
print("VERIFICATION: Checking All Fixes Applied Correctly")
print("=" * 70)

all_checks_passed = True

# Check 1: Verify concurrent.futures import at top
print("\n[Check 1] Verifying concurrent.futures import location...")
try:
    with open('services/ocr_service.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Check first 15 lines for the import
        top_lines = ''.join(lines[:15])
        if 'from concurrent.futures import ThreadPoolExecutor' in top_lines:
            print("✅ concurrent.futures imported at top of file")
        else:
            print("❌ concurrent.futures import not found at top")
            all_checks_passed = False
except Exception as e:
    print(f"❌ Error reading file: {e}")
    all_checks_passed = False

# Check 2: Verify no cls=False in ocr() calls
print("\n[Check 2] Verifying no invalid cls=False parameters...")
try:
    with open('services/ocr_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'cls=False' in content:
            print("❌ Found cls=False parameter (should be removed)")
            all_checks_passed = False
        else:
            print("✅ No cls=False parameters found")
except Exception as e:
    print(f"❌ Error reading file: {e}")
    all_checks_passed = False

# Check 3: Verify timeout protection exists
print("\n[Check 3] Verifying timeout protection is in place...")
try:
    with open('services/ocr_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'timeout=30' in content and 'ThreadPoolExecutor' in content:
            print("✅ Timeout protection found (30 seconds)")
        else:
            print("❌ Timeout protection not found")
            all_checks_passed = False
except Exception as e:
    print(f"❌ Error reading file: {e}")
    all_checks_passed = False

# Check 4: Verify page limit exists
print("\n[Check 4] Verifying page limit protection...")
try:
    with open('services/ocr_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'MAX_PAGES' in content or 'page_count > 10' in content:
            print("✅ Page limit protection found")
        else:
            print("⚠️  Page limit might not be set (optional)")
except Exception as e:
    print(f"❌ Error reading file: {e}")

# Check 5: Try importing the module
print("\n[Check 5] Testing module import...")
try:
    from services.ocr_service import ocr_service
    print(f"✅ OCR Service imported successfully")
    print(f"   - OCR Available: {ocr_service.ocr_available}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    all_checks_passed = False

# Check 6: Test ThreadPoolExecutor functionality
print("\n[Check 6] Testing ThreadPoolExecutor...")
try:
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

    def test_task():
        return "success"

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(test_task)
        result = future.result(timeout=5)

    if result == "success":
        print("✅ ThreadPoolExecutor works correctly")
    else:
        print("❌ ThreadPoolExecutor returned unexpected result")
        all_checks_passed = False
except Exception as e:
    print(f"❌ ThreadPoolExecutor test failed: {e}")
    all_checks_passed = False

# Summary
print("\n" + "=" * 70)
if all_checks_passed:
    print("✅✅✅ ALL CHECKS PASSED ✅✅✅")
    print("\nThe 500 error fix has been successfully applied!")
    print("\nNext steps:")
    print("1. Start the server: python start_server.py")
    print("2. Test upload API at: http://localhost:8000/docs")
    print("3. Upload a document and verify it returns 201 (not 500)")
else:
    print("❌ SOME CHECKS FAILED")
    print("\nPlease review the errors above.")
    sys.exit(1)

print("=" * 70)

