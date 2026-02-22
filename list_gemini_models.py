"""
List available Gemini models
"""
from google import genai

# Hardcoded API key (as per user requirement)
api_key = "AIzaSyBB4zqR0mf6xToxUdYzZ6rkrFJumwWGVE0"

print(f"API Key: {api_key[:10]}...")
print("\nListing available Gemini models...\n")

try:
    client = genai.Client(api_key=api_key)

    # List all available models
    models = client.models.list()

    print("Available models:")
    print("="*60)
    for model in models:
        print(f"  - {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"    Methods: {model.supported_generation_methods}")

except Exception as e:
    print(f"Error listing models: {e}")

