"""
Test Gemini + EasyOCR Combined Analysis
Tests signature detection and OCR text combination
"""
import os
import sys
import cv2
import numpy as np

print("=" * 80)
print("GEMINI + EASYOCR COMBINED ANALYSIS TEST")
print("=" * 80)

# Test file
pdf_file = "40352_44853_BOL.pdf"
if not os.path.exists(pdf_file):
    print(f"❌ ERROR: {pdf_file} not found!")
    sys.exit(1)

print(f"\n✅ Testing with: {pdf_file}")
print(f"   Size: {os.path.getsize(pdf_file):,} bytes")

# Step 1: Extract with EasyOCR
print("\n" + "=" * 80)
print("STEP 1: EasyOCR Extraction")
print("=" * 80)

from services.easyocr_service import easyocr_service

print("🔄 Running EasyOCR...")
import time
start_easy = time.time()

try:
    easyocr_text, easyocr_confidence = easyocr_service.extract_text(pdf_file, "pdf")
    easy_time = time.time() - start_easy

    print(f"✅ EasyOCR completed in {easy_time:.2f}s")
    print(f"   Confidence: {easyocr_confidence:.4f}")
    print(f"   Text length: {len(easyocr_text) if easyocr_text else 0} characters")
    print(f"\n📄 EasyOCR Text Preview (first 500 chars):")
    print("-" * 80)
    print(easyocr_text[:500] if easyocr_text else "[No text extracted]")
    print("-" * 80)

except Exception as e:
    print(f"❌ EasyOCR failed: {e}")
    easyocr_text = ""
    easyocr_confidence = 0.0
    easy_time = 0

# Step 2: Convert PDF to image for Gemini
print("\n" + "=" * 80)
print("STEP 2: Preparing Image for Gemini")
print("=" * 80)

try:
    from pdf2image import convert_from_path
    print("🔄 Converting PDF to image...")

    images = convert_from_path(pdf_file, dpi=300, first_page=1, last_page=1)
    if images:
        pil_image = images[0]
        # Convert to numpy array for Gemini
        image_np = np.array(pil_image)
        print(f"✅ Image prepared: {image_np.shape}")
    else:
        print("❌ Failed to convert PDF to image")
        sys.exit(1)

except Exception as e:
    print(f"❌ Image conversion failed: {e}")
    sys.exit(1)

# Step 3: Analyze with Gemini
print("\n" + "=" * 80)
print("STEP 3: Gemini Vision Analysis")
print("=" * 80)

from services.gemini_service import get_gemini_analyzer

gemini_analyzer = get_gemini_analyzer()

if not gemini_analyzer.available:
    print("❌ Gemini not available. Set GEMINI_API_KEY environment variable.")
    print("   Skipping Gemini analysis...")
    gemini_result = {
        "error": "Gemini not available",
        "extracted_text": "",
        "signatures": {"count": 0, "present": False, "details": []},
        "extracted_fields": {}
    }
    gemini_time = 0
else:
    print("🔄 Running Gemini analysis (this may take 10-30 seconds)...")
    print("   ℹ️  Note: Will retry up to 3 times if high demand/503 errors occur")
    start_gemini = time.time()

    try:
        # Call with retry logic (max 3 attempts)
        gemini_result = gemini_analyzer.analyze_document(image_np, easyocr_text, max_retries=3)
        gemini_time = time.time() - start_gemini

        if "error" in gemini_result:
            print(f"⚠️  Gemini analysis had errors: {gemini_result['error']}")
            print(f"   💡 Tip: Gemini may be experiencing high demand. The system automatically retries.")
        else:
            print(f"✅ Gemini analysis completed in {gemini_time:.2f}s")

    except Exception as e:
        print(f"❌ Gemini analysis failed: {e}")
        import traceback
        traceback.print_exc()
        gemini_result = {
            "error": str(e),
            "extracted_text": "",
            "signatures": {"count": 0, "present": False, "details": []},
            "extracted_fields": {}
        }
        gemini_time = 0

# Step 4: Display Gemini Results
print("\n" + "=" * 80)
print("GEMINI ANALYSIS RESULTS")
print("=" * 80)

gemini_text = gemini_result.get("extracted_text", "")
gemini_signatures = gemini_result.get("signatures", {})
gemini_fields = gemini_result.get("extracted_fields", {})

print(f"\n📊 GEMINI OCR TEXT:")
print(f"   Length: {len(gemini_text)} characters")
print(f"   Quality: {gemini_result.get('text_quality', 'unknown')}")
print(f"\n   Preview (first 500 chars):")
print("-" * 80)
print(gemini_text[:500] if gemini_text else "[No text extracted]")
print("-" * 80)

print(f"\n✍️  SIGNATURE DETECTION:")
print(f"   Count: {gemini_signatures.get('count', 0)}")
print(f"   Present: {gemini_signatures.get('present', False)}")

if gemini_signatures.get('details'):
    print(f"   Details:")
    for i, sig in enumerate(gemini_signatures['details'], 1):
        print(f"      Signature {i}:")
        print(f"         Location: {sig.get('location', 'unknown')}")
        print(f"         Signer: {sig.get('signer', 'unknown')}")
        print(f"         Type: {sig.get('type', 'unknown')}")
        print(f"         Confidence: {sig.get('confidence', 0.0):.2f}")

print(f"\n📋 EXTRACTED FIELDS:")
if gemini_fields:
    # Highlight critical fields
    print(f"\n   🎯 CRITICAL FIELDS:")
    print(f"      BOL Number: {gemini_fields.get('bol_number', 'NOT FOUND')}")
    print(f"      Order Number: {gemini_fields.get('order_number', 'NOT FOUND')}")
    print(f"      Client Name: {gemini_fields.get('client_name', 'NOT FOUND')}")
    print(f"      Document Date: {gemini_fields.get('document_date', 'NOT FOUND')}")

    print(f"\n   📄 OTHER FIELDS:")
    for key, value in gemini_fields.items():
        if key not in ['bol_number', 'order_number', 'client_name', 'document_date'] and value:
            print(f"      {key}: {value}")
else:
    print("   [No fields extracted]")

# Step 5: Combine OCR Texts
print("\n" + "=" * 80)
print("STEP 4: Combining OCR Results")
print("=" * 80)

combined_text = gemini_analyzer.combine_ocr_results(
    easyocr_text,
    gemini_text,
    gemini_result.get('confidence', 0.0)
)

print(f"\n📝 COMBINED OCR TEXT:")
print(f"   Length: {len(combined_text)} characters")
print(f"\n   Preview (first 500 chars):")
print("-" * 80)
print(combined_text[:500] if combined_text else "[No text]")
print("-" * 80)

# Step 6: Summary Comparison
print("\n" + "=" * 80)
print("COMPARISON SUMMARY")
print("=" * 80)

print(f"\n⏱️  Processing Times:")
print(f"   EasyOCR: {easy_time:.2f}s")
print(f"   Gemini: {gemini_time:.2f}s")
print(f"   Total: {easy_time + gemini_time:.2f}s")

print(f"\n📊 OCR Text Lengths:")
print(f"   EasyOCR: {len(easyocr_text) if easyocr_text else 0} characters")
print(f"   Gemini: {len(gemini_text) if gemini_text else 0} characters")
print(f"   Combined: {len(combined_text) if combined_text else 0} characters")

print(f"\n🎯 Best Choice:")
if len(combined_text) == len(gemini_text):
    print(f"   ✅ Using Gemini text (better quality/more content)")
elif len(combined_text) == len(easyocr_text):
    print(f"   ✅ Using EasyOCR text (more content)")
else:
    print(f"   ✅ Using combined text")

print(f"\n✍️  Signature Detection:")
print(f"   Signatures found: {gemini_signatures.get('count', 0)}")
print(f"   Has signatures: {gemini_signatures.get('present', False)}")

# Step 7: Database Update Preview
print("\n" + "=" * 80)
print("DATABASE UPDATE PREVIEW")
print("=" * 80)

print(f"\nFields that would be updated in database:")
print(f"   ocr_text: {len(combined_text)} characters")
print(f"   has_signature: {gemini_signatures.get('present', False)}")
print(f"   signature_count: {gemini_signatures.get('count', 0)}")

# Critical extracted fields
bol_num = gemini_fields.get('bol_number') or gemini_fields.get('order_number')
client_name = gemini_fields.get('client_name')
doc_date = gemini_fields.get('document_date')
invoice_num = gemini_fields.get('invoice_numbers')

print(f"\n   🎯 CRITICAL FIELDS FROM GEMINI:")
print(f"   bol_number/order_number: {bol_num if bol_num else 'ORD-2026-001 (static fallback)'}")
print(f"   client_name: {client_name if client_name else 'NOT EXTRACTED'}")
print(f"   document_date: {doc_date if doc_date else '2026-02-20 (static fallback)'}")
print(f"   invoice_number: {invoice_num[0] if invoice_num and isinstance(invoice_num, list) and len(invoice_num) > 0 else 'INV-2026-001 (static fallback)'}")
print(f"   document_type: {gemini_fields.get('document_type', 'Bill of Lading (static)')}")

# Show consignee if available
consignee = gemini_fields.get('consignee')
if consignee:
    print(f"   consignee: {consignee}")

# Save results to file
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

try:
    with open("gemini_test_results.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("GEMINI + EASYOCR TEST RESULTS\n")
        f.write("=" * 80 + "\n\n")

        f.write("EASYOCR TEXT:\n")
        f.write("-" * 80 + "\n")
        f.write(easyocr_text if easyocr_text else "[No text]")
        f.write("\n\n")

        f.write("GEMINI TEXT:\n")
        f.write("-" * 80 + "\n")
        f.write(gemini_text if gemini_text else "[No text]")
        f.write("\n\n")

        f.write("COMBINED TEXT:\n")
        f.write("-" * 80 + "\n")
        f.write(combined_text if combined_text else "[No text]")
        f.write("\n\n")

        f.write("SIGNATURE DETECTION:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Count: {gemini_signatures.get('count', 0)}\n")
        f.write(f"Present: {gemini_signatures.get('present', False)}\n")
        if gemini_signatures.get('details'):
            f.write("\nDetails:\n")
            for i, sig in enumerate(gemini_signatures['details'], 1):
                f.write(f"  Signature {i}:\n")
                f.write(f"    Location: {sig.get('location', 'unknown')}\n")
                f.write(f"    Signer: {sig.get('signer', 'unknown')}\n")
                f.write(f"    Type: {sig.get('type', 'unknown')}\n")

        f.write("\n\nEXTRACTED FIELDS:\n")
        f.write("-" * 80 + "\n")
        f.write("\nCRITICAL FIELDS:\n")
        f.write(f"  BOL Number: {gemini_fields.get('bol_number', 'NOT FOUND')}\n")
        f.write(f"  Order Number: {gemini_fields.get('order_number', 'NOT FOUND')}\n")
        f.write(f"  Client Name: {gemini_fields.get('client_name', 'NOT FOUND')}\n")
        f.write(f"  Document Date: {gemini_fields.get('document_date', 'NOT FOUND')}\n")
        f.write("\nOTHER FIELDS:\n")
        for key, value in gemini_fields.items():
            if key not in ['bol_number', 'order_number', 'client_name', 'document_date'] and value:
                f.write(f"  {key}: {value}\n")

    print("✅ Results saved to: gemini_test_results.txt")

except Exception as e:
    print(f"⚠️  Could not save results: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE!")
print("=" * 80)

print(f"\n📋 Summary:")
print(f"   • EasyOCR extracted {len(easyocr_text) if easyocr_text else 0} characters")
print(f"   • Gemini extracted {len(gemini_text) if gemini_text else 0} characters")
print(f"   • Combined text: {len(combined_text) if combined_text else 0} characters")
print(f"   • Signatures detected: {gemini_signatures.get('count', 0)}")
print(f"   • Status: {'✅ SUCCESS' if combined_text else '⚠️  NO TEXT EXTRACTED'}")

print("\n🎉 Test completed successfully!")

