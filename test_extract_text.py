"""
Complete PaddleOCR Test - Extract and Display Text
"""
import os
from pathlib import Path
from PIL import Image
import fitz

# Disable OneDNN
os.environ['FLAGS_use_mkldnn'] = '0'

print("=" * 70)
print("PADDLEOCR TEXT EXTRACTION TEST")
print("=" * 70)
print()

print("Step 1: Initializing PaddleOCR...")
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_textline_orientation=True, lang='en', enable_mkldnn=False, cpu_threads=4)
print("[OK] Initialized!")
print()

# Get first PDF from uploads
uploads_dir = Path(__file__).parent / "uploads"
pdf_files = list(uploads_dir.glob("*.pdf"))

if not pdf_files:
    print("[ERROR] No PDFs found!")
    exit()

pdf_path = str(pdf_files[0])
print(f"Step 2: Processing PDF: {pdf_files[0].name}")
print()

# Convert first page to image
doc = fitz.open(pdf_path)
print(f"Total pages: {doc.page_count}")
page = doc[0]
pix = page.get_pixmap(dpi=300)

# Save as temp image
temp_img = "test_extraction.png"
pix.save(temp_img)
print("[OK] Converted page 1 to image")
print()

# Run OCR
print("Step 3: Running OCR...")
result = ocr.predict(temp_img)
print("[OK] OCR Complete!")
print()

# Parse results
print("=" * 70)
print("EXTRACTION RESULTS")
print("=" * 70)
print()

if result and len(result) > 0:
    ocr_result = result[0]

    # Get texts and scores
    texts = ocr_result['rec_texts'] if 'rec_texts' in ocr_result else []
    scores = ocr_result['rec_scores'] if 'rec_scores' in ocr_result else []

    print(f"Lines detected: {len(texts)}")
    print(f"Average confidence: {sum(scores)/len(scores)*100:.1f}%" if scores else "N/A")
    print()
    print("-" * 70)
    print("EXTRACTED TEXT:")
    print("-" * 70)

    if texts:
        for i, (text, score) in enumerate(zip(texts, scores), 1):
            print(f"{i:3d}. [{score*100:5.1f}%] {text}")
    else:
        print("(No text detected)")

    print("-" * 70)
    print()

    # Combined text
    full_text = "\n".join(texts)
    print("FULL TEXT (Combined):")
    print("-" * 70)
    print(full_text if full_text else "(empty)")
    print("-" * 70)
    print()
    print(f"Total characters: {len(full_text)}")

else:
    print("[ERROR] No results from OCR")

# Cleanup
os.remove(temp_img)
doc.close()

print()
print("=" * 70)
print("TEST COMPLETE!")
print("=" * 70)

