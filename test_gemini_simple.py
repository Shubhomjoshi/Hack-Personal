"""
Simple Gemini Connection Test
"""
import os
import sys

print("=" * 80)
print("GEMINI CONNECTION TEST")
print("=" * 80)

# Set API key
os.environ['GEMINI_API_KEY'] = "AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw"

print("\n1. Testing Gemini SDK import...")
try:
    from google import genai
    from google.genai import types
    print("   ✅ Gemini SDK imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import: {e}")
    print("\n   Install with: pip install google-genai")
    sys.exit(1)

print("\n2. Testing Gemini service initialization...")
try:
    from services.gemini_service import get_gemini_analyzer

    analyzer = get_gemini_analyzer()
    print(f"   ✅ Gemini analyzer created")
    print(f"   Model: {analyzer.model}")
    print(f"   Available: {analyzer.available}")

    if not analyzer.available:
        print("   ⚠️  Gemini not available - check API key or network")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. Testing simple text analysis...")
try:
    import numpy as np
    from PIL import Image

    # Create a simple test image with text
    test_image = Image.new('RGB', (800, 200), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(test_image)

    # Draw some text
    draw.text((10, 10), "TEST DOCUMENT", fill='black')
    draw.text((10, 50), "Order Number: 12345", fill='black')
    draw.text((10, 90), "Signature: ___________", fill='black')

    # Convert to numpy
    image_np = np.array(test_image)

    print("   📤 Sending test image to Gemini...")
    result = analyzer.analyze_document(image_np, "Test OCR text")

    if "error" in result:
        print(f"   ❌ Gemini returned error: {result['error']}")
        sys.exit(1)

    print("   ✅ Gemini analysis successful!")
    print(f"   • Extracted text length: {len(result.get('extracted_text', ''))}")
    print(f"   • Signatures detected: {result.get('signatures', {}).get('count', 0)}")
    print(f"   • Confidence: {result.get('confidence', 0.0)}")

except Exception as e:
    print(f"   ❌ Analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print("\nGemini is working properly!")
print(f"Model: {analyzer.model}")
print("API Key: Configured ✅")
print("\nReady to process documents!")

