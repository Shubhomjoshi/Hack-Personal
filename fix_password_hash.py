"""
Quick fix for password hashing issue
Run this to reinstall dependencies and test
"""
import subprocess
import sys

print("=" * 70)
print("FIXING PASSWORD HASHING ISSUE")
print("=" * 70)
print()

print("Step 1: Reinstalling passlib and bcrypt...")
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", "passlib==1.7.4", "bcrypt==4.0.1"], check=True)
    print("✅ Dependencies reinstalled")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()
print("Step 2: Testing password hashing...")
try:
    from auth import get_password_hash
    test_pwd = "Test@1234"
    hashed = get_password_hash(test_pwd)
    print(f"✅ Password hashing works!")
    print(f"   Test password: {test_pwd}")
    print(f"   Hashed: {hashed[:50]}...")
except Exception as e:
    print(f"❌ Still failing: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("✅ FIX COMPLETE - Restart your server now!")
print("   python start_server.py")
print("=" * 70)

