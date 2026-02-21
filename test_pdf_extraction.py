"""
Test PDF text extraction directly
"""
import sys
import os

print("=" * 70)
print("Testing PDF Text Extraction")
print("=" * 70)
print()

# Ask for PDF path
if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
else:
    pdf_path = input("Enter PDF file path (or drag & drop): ").strip('"')

if not os.path.exists(pdf_path):
    print(f"❌ File not found: {pdf_path}")
    sys.exit(1)

print(f"Testing: {pdf_path}")
print()

# Test 1: pdfplumber
print("Method 1: pdfplumber (direct text extraction)")
print("-" * 70)
try:
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        print()

        all_text = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"Page {i+1}:")
            if text and text.strip():
                print(f"  ✅ Extracted {len(text.strip())} characters")
                print(f"  Preview: {text.strip()[:100]}...")
                all_text.append(text.strip())
            else:
                print(f"  ❌ No text found")

        print()
        if all_text:
            combined = "\n\n".join(all_text)
            print(f"✅ SUCCESS: Total {len(combined)} characters extracted")
            print()
            print("First 500 characters:")
            print("-" * 70)
            print(combined[:500])
            print("-" * 70)
        else:
            print("❌ FAILED: No text extracted from any page")
            print()
            print("This PDF appears to be:")
            print("  - Scanned/image-based PDF")
            print("  - Or has text rendering issues")
            print()
            print("Try:")
            print("  1. Open the PDF and check if you can select/copy text")
            print("  2. If yes, it's likely an extraction issue")
            print("  3. If no, it's a scanned PDF (needs OCR)")

except ImportError:
    print("❌ pdfplumber not installed")
    print("Run: pip install pdfplumber")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)

# Test 2: PyPDF2 (alternative)
print()
print("Method 2: PyPDF2 (alternative extraction)")
print("-" * 70)
try:
    import PyPDF2

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        print(f"Total pages: {len(pdf_reader.pages)}")
        print()

        all_text = []
        for i, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            print(f"Page {i+1}:")
            if text and text.strip():
                print(f"  ✅ Extracted {len(text.strip())} characters")
                all_text.append(text.strip())
            else:
                print(f"  ❌ No text found")

        print()
        if all_text:
            combined = "\n\n".join(all_text)
            print(f"✅ SUCCESS: Total {len(combined)} characters extracted")
        else:
            print("❌ FAILED: No text extracted")

except ImportError:
    print("⚠️  PyPDF2 not installed (optional)")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 70)
print()
print("SUMMARY:")
print("If both methods failed to extract text:")
print("  → Your PDF is likely scanned/image-based")
print("  → You need Tesseract + Poppler for OCR")
print()
print("If one method worked:")
print("  → We can update the code to use that method")
print()
print("=" * 70)

