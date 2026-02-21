"""
Test password hashing to diagnose the issue
"""
from auth import get_password_hash

# Test with the exact password from the error
test_password = "Test@1234"

print(f"Testing password: {test_password}")
print(f"Password length: {len(test_password)}")
print(f"Password bytes: {len(test_password.encode('utf-8'))}")

try:
    hashed = get_password_hash(test_password)
    print(f"✅ Hashing successful!")
    print(f"Hashed password: {hashed[:50]}...")
except Exception as e:
    print(f"❌ Hashing failed: {e}")
    import traceback
    traceback.print_exc()

