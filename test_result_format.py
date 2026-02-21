"""
Simple test to understand PaddleOCR predict() result format
"""
import os
from PIL import Image
import numpy as np

os.environ['FLAGS_use_mkldnn'] = '0'

from paddleocr import PaddleOCR

print("Initializing...")
ocr = PaddleOCR(use_textline_orientation=True, lang='en', enable_mkldnn=False, cpu_threads=4)

# Create a simple test image with text
from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (400, 100), color='white')
d = ImageDraw.Draw(img)
d.text((10, 30), "Hello World Test", fill='black')
img.save('simple_test.png')

print("\nRunning OCR on simple test image...")
result = ocr.predict('simple_test.png')

print("\n" + "="*60)
print("RESULT:")
print("="*60)
print(f"Type: {type(result)}")

if isinstance(result, list):
    print(f"\nList length: {len(result)}")
    if len(result) > 0:
        print(f"First item type: {type(result[0])}")
        if isinstance(result[0], dict):
            print(f"First item keys: {result[0].keys()}")
            for key, value in result[0].items():
                print(f"\n{key}:")
                print(f"  Type: {type(value)}")
                if isinstance(value, (list, dict)):
                    print(f"  Length/Keys: {len(value)}")
                    if len(value) > 0:
                        print(f"  First element: {value[0] if isinstance(value, list) else list(value.items())[0]}")
                else:
                    print(f"  Value: {value}")
        else:
            print(f"First item: {result[0]}")
elif isinstance(result, dict):
    print(f"\nKeys: {result.keys()}")
    for key in result.keys():
        print(f"\n{key}:")
        print(f"  Type: {type(result[key])}")
        print(f"  Value: {result[key]}")

os.remove('simple_test.png')
print("\nDone!")

