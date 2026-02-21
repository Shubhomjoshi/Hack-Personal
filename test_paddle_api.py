"""
Quick PaddleOCR API Test - Check the result structure
"""
import os
from pathlib import Path
from PIL import Image
import fitz

# Disable OneDNN
os.environ['FLAGS_use_mkldnn'] = '0'

from paddleocr import PaddleOCR

print("Initializing PaddleOCR...")
ocr = PaddleOCR(
    use_textline_orientation=True,
    lang='en',
    enable_mkldnn=False,
    cpu_threads=4
)

print("✅ Initialized!")
print()

# Get first PDF from uploads
uploads_dir = Path(__file__).parent / "uploads"
pdf_files = list(uploads_dir.glob("*.pdf"))

if not pdf_files:
    print("No PDFs found!")
    exit()

pdf_path = str(pdf_files[0])
print(f"Testing with: {pdf_files[0].name}")
print()

# Convert first page to image
doc = fitz.open(pdf_path)
page = doc[0]
pix = page.get_pixmap(dpi=300)

# Save as temp image
temp_img = "test_page.png"
pix.save(temp_img)

print(f"Saved temp image: {temp_img}")
print()

# Run OCR
print("Running OCR...")
result = ocr.predict(temp_img)

print()
print("=" * 60)
print("RESULT STRUCTURE:")
print("=" * 60)
print(f"Type: {type(result)}")
print(f"Content: {result}")
print()

# Try to parse it
if result:
    print("Attempting to parse...")
    if isinstance(result, dict):
        print(f"Dict keys: {result.keys()}")
        for key, value in result.items():
            print(f"  {key}: {value}")
    elif isinstance(result, list):
        print(f"List length: {len(result)}")
        if len(result) > 0:
            print(f"First item type: {type(result[0])}")
            print(f"First item: {result[0]}")

# Cleanup
os.remove(temp_img)
doc.close()

print()
print("Done!")

