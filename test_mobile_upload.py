"""
Test script for mobile upload - simulates React Native FormData
"""
import requests
import json

# Configuration
API_URL = "http://localhost:8000/documents/upload"
TOKEN = "YOUR_TOKEN_HERE"  # Replace with actual token

def test_mobile_upload_correct():
    """Test with correct format"""
    print("\n" + "="*70)
    print("TEST 1: Correct Format (should work)")
    print("="*70)

    # This is how it SHOULD be sent
    files = {
        'files': ('test.jpg', open('debug_test_docs/test.jpg', 'rb') if os.path.exists('debug_test_docs/test.jpg') else b'fake_image_data', 'image/jpeg')
    }

    data = {
        'driver_user_id': '8'  # Send as STRING
    }

    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }

    try:
        response = requests.post(API_URL, files=files, data=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


def test_mobile_upload_as_int():
    """Test with integer (might fail)"""
    print("\n" + "="*70)
    print("TEST 2: Integer Format (React Native issue)")
    print("="*70)

    files = {
        'files': ('test.jpg', b'fake_image_data', 'image/jpeg')
    }

    data = {
        'driver_user_id': 8  # Send as INTEGER
    }

    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }

    try:
        response = requests.post(API_URL, files=files, data=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


def print_react_native_fix():
    """Print the fix for React Native developers"""
    print("\n" + "="*70)
    print("REACT NATIVE FIX")
    print("="*70)
    print("""
The issue is that React Native FormData sends integers differently.

❌ WRONG (causes the error):
    formData.append('driver_user_id', 8);  // Number
    
✅ CORRECT:
    formData.append('driver_user_id', '8');  // String
    // OR
    formData.append('driver_user_id', driverUserId.toString());

Complete working example:

const formData = new FormData();

// Add file
formData.append('files', {
    uri: fileUri,
    name: '1000000026.jpg',
    type: 'image/jpeg'
});

// Add driver_user_id as STRING (CRITICAL!)
formData.append('driver_user_id', driverUserId.toString());

// Send request
const response = await fetch('http://your-api/documents/upload', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
    },
    body: formData
});
""")


if __name__ == "__main__":
    import os
    import sys

    print("\n🔍 MOBILE UPLOAD DEBUG TOOL")
    print("="*70)

    if TOKEN == "YOUR_TOKEN_HERE":
        print("\n⚠️  Please update TOKEN in the script first!")
        print("   Get your token by logging in via /api/auth/login")
        sys.exit(1)

    # Run tests
    test_mobile_upload_correct()
    test_mobile_upload_as_int()
    print_react_native_fix()

    print("\n" + "="*70)
    print("✅ Tests Complete")
    print("="*70)

