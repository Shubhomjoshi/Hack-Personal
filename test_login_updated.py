"""
Example: Testing the Updated Login API
"""
import requests
import json
# Base URL
BASE_URL = "http://localhost:8000/api"
def test_login_api():
    """"""
    Test the updated login API that returns complete user details
    """"""
    # Login credentials
    login_data = {
        "username": "your_username",
        "password": "your_password"
    }
    print("🔐 Testing Login API...")
    print(f"POST {BASE_URL}/auth/login")
    print(f"Request: {json.dumps(login_data, indent=2)}")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data
        )
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Login Successful!")
            print("\n📋 Complete Response:")
            print(json.dumps(data, indent=2))
            print("\n🎯 Available Fields:")
            print(f"  • Access Token: {data['access_token'][:50]}...")
            print(f"  • Token Type: {data['token_type']}")
            print(f"  • User ID: {data['id']}")
            print(f"  • Email: {data['email']}")
            print(f"  • Username: {data['username']}")
            print(f"  • Is Active: {data['is_active']}")
            print(f"  • Is Admin: {data['is_admin']}")
            print(f"  • Created At: {data['created_at']}")
            print(f"  • Updated At: {data['updated_at']}")
            print("\n💡 Frontend Usage:")
            print("  // Store token")
            print(f"  localStorage.setItem('token', '{data['access_token'][:20]}...');")
            print("  // Store user details")
            print(f"  const user = {{")
            print(f"    id: {data['id']},")
            print(f"    email: '{data['email']}',")
            print(f"    username: '{data['username']}',")
            print(f"    isActive: {str(data['is_active']).lower()},")
            print(f"    isAdmin: {str(data['is_admin']).lower()}")
            print(f"  }};")
            print(f"  localStorage.setItem('user', JSON.stringify(user));")
            return data
        else:
            print(f"\n❌ Login Failed: {response.status_code}")
            print(response.json())
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Server not running!")
        print("Start the server with: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
if __name__ == "__main__":
    print("=" * 60)
    print("UPDATED LOGIN API TEST")
    print("=" * 60)
    test_login_api()
