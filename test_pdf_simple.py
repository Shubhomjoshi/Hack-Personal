"""
Simple EasyOCR Test for 40352_44853_BOL.pdf
"""
print("Starting EasyOCR test...")

import os
import sys

# Check file
pdf_file = "40352_44853_BOL.pdf"
if not os.path.exists(pdf_file):
    print(f"ERROR: {pdf_file} not found!")
    sys.exit(1)

print(f"Found PDF: {pdf_file} ({os.path.getsize(pdf_file):,} bytes)")

# Import service
print("Loading EasyOCR service...")
from services.easyocr_service import easyocr_service

print(f"OCR Available: {easyocr_service.ocr_available}")
print(f"Using Tesseract: {easyocr_service.use_tesseract_fallback}")

# Extract
print("\nExtracting text (this may take 30-60 seconds)...")
import time
start = time.time()

try:
    text, confidence = easyocr_service.extract_text(pdf_file, "pdf")
    elapsed = time.time() - start

    print(f"\nExtraction complete in {elapsed:.2f} seconds!")
    print(f"Confidence: {confidence:.4f}")
    print(f"Text length: {len(text) if text else 0} characters")

    if text and len(text) > 0:
        print("\n" + "="*80)
        print("EXTRACTED TEXT:")
        print("="*80)
        print(text)
        print("="*80)

        # Save to file
        with open("extracted_text_output.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\nSaved to: extracted_text_output.txt")
    else:
        print("\nWARNING: No text extracted!")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")

