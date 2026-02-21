"""
Direct EasyOCR Test - Extract text from 40352_44853_BOL.pdf
"""
import os
import sys

print("=" * 80)
print("DIRECT EASYOCR TEST ON: 40352_44853_BOL.pdf")
print("=" * 80)

# Check if file exists
pdf_file = "40352_44853_BOL.pdf"
if not os.path.exists(pdf_file):
    # Try in uploads directory
    pdf_file = os.path.join("uploads", "40352_44853_BOL.pdf")
    if not os.path.exists(pdf_file):
        print(f"\n❌ ERROR: PDF file not found!")
        print(f"   Tried: ./40352_44853_BOL.pdf")
        print(f"   Tried: ./uploads/40352_44853_BOL.pdf")
        print(f"\nAvailable files in current directory:")
        for f in os.listdir("."):
            if f.endswith(".pdf"):
                print(f"   - {f}")
        if os.path.exists("uploads"):
            print(f"\nAvailable files in uploads directory:")
            for f in os.listdir("uploads"):
                if f.endswith(".pdf"):
                    print(f"   - {f}")
        sys.exit(1)

print(f"\n✅ Found PDF file: {pdf_file}")
print(f"   Size: {os.path.getsize(pdf_file):,} bytes")

# Import EasyOCR service
print("\n" + "=" * 80)
print("STEP 1: Loading EasyOCR Service")
print("=" * 80)

try:
    from services.easyocr_service import easyocr_service
    print("✅ EasyOCR service imported successfully")
    print(f"   OCR Available: {easyocr_service.ocr_available}")
    print(f"   Using Tesseract Fallback: {easyocr_service.use_tesseract_fallback}")
except Exception as e:
    print(f"❌ Failed to import EasyOCR service: {e}")
    sys.exit(1)

# Extract text from PDF
print("\n" + "=" * 80)
print("STEP 2: Extracting Text from PDF")
print("=" * 80)

try:
    print(f"🔄 Processing: {pdf_file}")
    print("   This may take a minute on first run (downloading models)...")

    import time
    start_time = time.time()

    # Extract text
    text, confidence = easyocr_service.extract_text(pdf_file, "pdf")

    elapsed_time = time.time() - start_time

    print(f"\n✅ Extraction completed in {elapsed_time:.2f} seconds")
    print(f"   Confidence: {confidence:.4f}")
    print(f"   Text length: {len(text) if text else 0} characters")

except Exception as e:
    print(f"\n❌ Extraction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Display results
print("\n" + "=" * 80)
print("STEP 3: Extraction Results")
print("=" * 80)

if text and len(text.strip()) > 0:
    print(f"\n📄 EXTRACTED TEXT ({len(text)} characters):")
    print("=" * 80)
    print(text)
    print("=" * 80)

    # Show statistics
    print(f"\n📊 TEXT STATISTICS:")
    print(f"   Total characters: {len(text)}")
    print(f"   Total words: {len(text.split())}")
    print(f"   Total lines: {len(text.splitlines())}")

    # Check for BOL keywords
    print(f"\n🔍 BILL OF LADING KEYWORDS FOUND:")
    keywords = ["bill of lading", "bol", "shipper", "consignee", "carrier",
                "freight", "weight", "pieces", "description", "origin", "destination"]
    found_keywords = []
    text_lower = text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
            print(f"   ✅ '{keyword}'")

    if not found_keywords:
        print("   ⚠️  No BOL keywords found (may be scanned/unclear)")

    # Save to file
    output_file = "extracted_text_output.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("EXTRACTED TEXT FROM: 40352_44853_BOL.pdf\n")
            f.write("=" * 80 + "\n\n")
            f.write(text)
            f.write("\n\n" + "=" * 80 + "\n")
            f.write(f"Extraction date: 2026-02-20\n")
            f.write(f"Confidence: {confidence:.4f}\n")
            f.write(f"Character count: {len(text)}\n")
        print(f"\n💾 Full text saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save to file: {e}")

else:
    print("\n⚠️  WARNING: No text extracted from PDF!")
    print("   Possible reasons:")
    print("   - PDF is blank or contains only images")
    print("   - PDF is scanned with very poor quality")
    print("   - OCR models not fully loaded")
    print("   - File is corrupted")

    # Check if it's a scanned PDF
    print("\n🔍 Attempting to analyze PDF structure...")
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_file)
        print(f"   PDF Pages: {len(doc)}")

        for page_num, page in enumerate(doc, 1):
            text_content = page.get_text()
            has_images = len(page.get_images()) > 0
            print(f"   Page {page_num}: {len(text_content)} chars, Images: {has_images}")

        if len(doc) > 0 and len(doc[0].get_text()) == 0:
            print("\n   ℹ️  This appears to be a scanned/image-based PDF")
            print("   OCR should have extracted text from images")
            print("   Check if EasyOCR models are properly installed")
    except Exception as e:
        print(f"   ⚠️  Could not analyze PDF: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

# Summary
print(f"\n📋 SUMMARY:")
print(f"   File: {pdf_file}")
print(f"   OCR Engine: {'EasyOCR' if not easyocr_service.use_tesseract_fallback else 'Tesseract'}")
print(f"   Text Extracted: {'Yes' if text and len(text) > 0 else 'No'}")
print(f"   Confidence: {confidence:.4f}")
print(f"   Status: {'✅ SUCCESS' if text and len(text) > 0 else '⚠️  NO TEXT EXTRACTED'}")

print("\n✅ Direct EasyOCR test completed!")

