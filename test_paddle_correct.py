"""
Correct PaddleOCR Implementation with Image Preprocessing
Following the proper architecture for scanned PDFs
"""
import os
import cv2
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

# Disable OneDNN
os.environ['FLAGS_use_mkldnn'] = '0'

print("=" * 70)
print("CORRECT PADDLEOCR IMPLEMENTATION")
print("=" * 70)
print()

# Step 1: Initialize PaddleOCR
print("Step 1: Initializing PaddleOCR...")
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_textline_orientation=True, lang='en', enable_mkldnn=False, cpu_threads=4)
print("[OK] Initialized!")
print()

# Step 2: Get PDF
uploads_dir = Path(__file__).parent / "uploads"
pdf_files = list(uploads_dir.glob("*.pdf"))

if not pdf_files:
    print("[ERROR] No PDFs found!")
    exit()

pdf_path = str(pdf_files[0])
print(f"Step 2: Processing PDF: {pdf_files[0].name}")
print()

# Step 3: Convert PDF to Image (300 DPI minimum)
print("Step 3: Converting PDF to images (300 DPI)...")
try:
    pages = convert_from_path(pdf_path, dpi=300)
    print(f"[OK] Converted {len(pages)} page(s)")
    page_image = pages[0]  # First page
except Exception as e:
    print(f"[ERROR] PDF conversion failed: {e}")
    print("Install poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
    exit()

print()

# Step 4: Preprocess Image (VERY IMPORTANT for accuracy)
print("Step 4: Preprocessing image...")

# Convert PIL to OpenCV format
img_cv = cv2.cvtColor(np.array(page_image), cv2.COLOR_RGB2BGR)

# 4.1 Grayscale
gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
print("  - Converted to grayscale")

# 4.2 CLAHE contrast enhancement
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
enhanced = clahe.apply(gray)
print("  - Applied CLAHE contrast enhancement")

# 4.3 Denoise
denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
print("  - Denoised image")

# 4.4 Adaptive threshold
thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 11, 2)
print("  - Applied adaptive threshold")

print("[OK] Preprocessing complete!")
print()

# Save preprocessed image for inspection
preprocessed_path = "preprocessed_image.png"
cv2.imwrite(preprocessed_path, thresh)
print(f"Preprocessed image saved: {preprocessed_path}")
print()

# Step 5: Run PaddleOCR on preprocessed image (NOT raw PDF)
print("Step 5: Running OCR on preprocessed image...")
result = ocr.predict(preprocessed_path)
print("[OK] OCR Complete!")
print()

# Step 6: Extract results
print("=" * 70)
print("EXTRACTION RESULTS")
print("=" * 70)
print()

if result and len(result) > 0:
    ocr_result = result[0]
    texts = ocr_result.get('rec_texts', [])
    scores = ocr_result.get('rec_scores', [])

    print(f"Lines detected: {len(texts)}")
    print()
    print("-" * 70)
    print("EXTRACTED TEXT:")
    print("-" * 70)

    for i, (text, confidence) in enumerate(zip(texts, scores), 1):
        print(f"{i:3d}. [{confidence*100:5.1f}%] {text}")

    print("-" * 70)
    print()

    # Combined text
    full_text = "\n".join(texts)
    print("FULL TEXT (Combined):")
    print("-" * 70)
    print(full_text)
    print("-" * 70)
    print()
    print(f"Total characters: {len(full_text)}")

else:
    print("[WARNING] No text detected")

# Cleanup
os.remove(preprocessed_path)

print()
print("=" * 70)
print("TEST COMPLETE!")
print("=" * 70)
print()
print("Key Takeaways:")
print("1. Convert PDF to image first (300 DPI minimum)")
print("2. Preprocess image (grayscale, CLAHE, denoise, threshold)")
print("3. Run OCR on preprocessed image (NOT raw PDF)")
print("4. This approach is MUCH faster and more accurate!")

