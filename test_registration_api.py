"""
Test Registration API with Strong Password Validation
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("Testing Registration API with Strong Password Validation")
print("=" * 70)
print()

# Test cases
test_cases = [
    {
        "name": "Valid Password",
        "data": {
            "email": "test1@example.com",
            "username": "testuser1",
            "password": "Test@123"
        },
        "should_pass": True
    },
    {
        "name": "Missing Uppercase",
        "data": {
            "email": "test2@example.com",
            "username": "testuser2",
            "password": "test@123"
        },
        "should_pass": False,
        "expected_error": "uppercase"
    },
    {
        "name": "Missing Lowercase",
        "data": {
            "email": "test3@example.com",
            "username": "testuser3",
            "password": "TEST@123"
        },
        "should_pass": False,
        "expected_error": "lowercase"
    },
    {
        "name": "Missing Digit",
        "data": {
            "email": "test4@example.com",
            "username": "testuser4",
            "password": "Test@abc"
        },
        "should_pass": False,
        "expected_error": "digit"
    },
    {
        "name": "Missing Special Character",
        "data": {
            "email": "test5@example.com",
            "username": "testuser5",
            "password": "Test1234"
        },
        "should_pass": False,
        "expected_error": "special"
    },
    {
        "name": "Too Short",
        "data": {
            "email": "test6@example.com",
            "username": "testuser6",
            "password": "Te@1"
        },
        "should_pass": False,
        "expected_error": "8 characters"
    },
    {
        "name": "Valid Complex Password",
        "data": {
            "email": "test7@example.com",
            "username": "testuser7",
            "password": "MySecure#Pass123!"
        },
        "should_pass": True
    }
]

def test_registration(test_case):
    """Test a registration attempt"""
    print(f"Test: {test_case['name']}")
    print(f"Password: {test_case['data']['password']}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_case['data'],
            headers={"Content-Type": "application/json"}
        )

        if test_case['should_pass']:
            if response.status_code == 201:
                print("✅ PASS - Registration successful")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ FAIL - Expected success but got: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            if response.status_code in [400, 422]:
                print(f"✅ PASS - Correctly rejected (Status: {response.status_code})")
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            else:
                print(f"❌ FAIL - Expected rejection but got: {response.status_code}")
                print(f"   Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR - Could not connect to server")
        print("   Make sure the server is running: python main.py")
        return False
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False

    print()
    return True

# Run tests
print("Starting tests...")
print()

for test_case in test_cases:
    if not test_registration(test_case):
        break

print("=" * 70)
print("Testing Complete!")
print()
print("To test manually:")
print("1. Start server: python main.py")
print("2. Open Swagger UI: http://localhost:8000/docs")
print("3. Try POST /api/auth/register with different passwords")
print("=" * 70)

