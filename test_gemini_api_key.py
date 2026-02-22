"""
Quick test to verify Gemini API key is working
"""
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test if Gemini API key is valid and working"""

    print("\n" + "="*60)
    print("GEMINI API KEY TEST")
    print("="*60 + "\n")

    # Hardcoded API key (as per user requirement)
    api_key = "AIzaSyBB4zqR0mf6xToxUdYzZ6rkrFJumwWGVE0"

    print(f"✅ API Key (hardcoded): {api_key[:10]}...{api_key[-5:]}")
    print(f"   Full length: {len(api_key)} characters")

    # Test API key validity
    try:
        print("\n🔄 Testing API key with Gemini...")

        client = genai.Client(api_key=api_key)

        # Try to generate simple content
        response = client.models.generate_content(
            model='gemini-3-flash-preview',  # Using gemini-3-flash-preview as required
            contents='Say "API key is working" if you can read this.'
        )

        print(f"✅ API Key is VALID!")
        print(f"   Model: gemini-3-flash-preview")
        print(f"   Response: {response.text[:100]}")

        return True

    except Exception as e:
        print(f"❌ API Key test FAILED!")
        print(f"   Error: {e}")

        # Check for common error types
        error_str = str(e)
        if "API_KEY_INVALID" in error_str:
            print("\n💡 Suggestion: Your API key appears to be invalid or expired")
            print("   Please check:")
            print("   1. Visit https://aistudio.google.com/app/apikey")
            print("   2. Generate a new API key")
            print("   3. Update your .env file with the new key")
        elif "INVALID_ARGUMENT" in error_str:
            print("\n💡 Suggestion: API key format might be incorrect")
            print("   Expected format: AIzaSy... (starts with AIza)")
        elif "503" in error_str or "UNAVAILABLE" in error_str:
            print("\n💡 Suggestion: Gemini service is temporarily unavailable")
            print("   This is usually temporary - try again in a few minutes")

        return False

if __name__ == "__main__":
    success = test_gemini_api()

    print("\n" + "="*60)
    if success:
        print("✅ TEST PASSED - Gemini API is ready to use!")
    else:
        print("❌ TEST FAILED - Please fix the API key issue")
    print("="*60 + "\n")

