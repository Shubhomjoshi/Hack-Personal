"""
Simple PaddleOCR Test Module
Tests PaddleOCR functionality independently before integrating with FastAPI
"""
import os
import sys
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF

def initialize_paddleocr():
    """Initialize PaddleOCR with proper settings"""
    print("=" * 60)
    print("🔧 Initializing PaddleOCR...")
    print("=" * 60)

    try:
        # Disable OneDNN to avoid compatibility issues
        os.environ['FLAGS_use_mkldnn'] = '0'

        from paddleocr import PaddleOCR

        # Initialize PaddleOCR with CPU-only settings
        ocr = PaddleOCR(
            use_textline_orientation=True,  # Enable text direction detection (updated parameter)
            lang='en',  # English language
            enable_mkldnn=False,  # Disable OneDNN/MKLDNN
            cpu_threads=4  # Use 4 CPU threads for processing
        )

        print("✅ PaddleOCR initialized successfully!")
        print("   - Mode: CPU only")
        print("   - Language: English")
        print("   - OneDNN: Disabled")
        print()
        return ocr

    except Exception as e:
        print(f"❌ Failed to initialize PaddleOCR: {str(e)}")
        print("\n💡 Solution:")
        print("   pip install paddlepaddle paddleocr")
        return None


def extract_text_from_image(ocr, image_path):
    """Extract text from an image file"""
    print(f"📄 Processing image: {image_path}")
    print("-" * 60)

    try:
        # Run OCR using the predict method
        result = ocr.predict(image_path)

        if not result or not result[0]:
            print("⚠️  No text detected in image")
            return ""

        # Extract text from results
        extracted_text = []
        confidence_scores = []

        for line in result[0]:
            text = line[1][0]  # Extract text
            confidence = line[1][1]  # Extract confidence score
            extracted_text.append(text)
            confidence_scores.append(confidence)
            print(f"   Text: {text}")
            print(f"   Confidence: {confidence:.2%}")
            print()

        full_text = "\n".join(extracted_text)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        print(f"✅ Extraction complete!")
        print(f"   Total lines: {len(extracted_text)}")
        print(f"   Average confidence: {avg_confidence:.2%}")
        print()

        return full_text, avg_confidence

    except Exception as e:
        print(f"❌ Error during OCR: {str(e)}")
        return "", 0.0


def extract_text_from_pdf(ocr, pdf_path):
    """Extract text from a PDF file by converting pages to images"""
    print(f"📚 Processing PDF: {pdf_path}")
    print("-" * 60)

    try:
        # Open PDF
        doc = fitz.open(pdf_path)
        print(f"   Total pages: {len(doc)}")
        print()

        all_text = []
        all_confidences = []

        for page_num in range(len(doc)):
            print(f"📄 Processing page {page_num + 1}/{len(doc)}...")

            # Convert page to image
            page = doc[page_num]
            pix = page.get_pixmap(dpi=300)  # High DPI for better quality

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            from io import BytesIO
            img = Image.open(BytesIO(img_data))

            # Save temporarily
            temp_img_path = f"temp_page_{page_num}.png"
            img.save(temp_img_path)

            # Extract text using OCR
            result = ocr.predict(temp_img_path)

            # Clean up temp file
            os.remove(temp_img_path)

            if result and result[0]:
                page_text = []
                page_confidences = []

                for line in result[0]:
                    text = line[1][0]
                    confidence = line[1][1]
                    page_text.append(text)
                    page_confidences.append(confidence)

                page_text_str = "\n".join(page_text)
                avg_conf = sum(page_confidences) / len(page_confidences) if page_confidences else 0

                all_text.append(page_text_str)
                all_confidences.extend(page_confidences)

                print(f"   ✅ Page {page_num + 1}: {len(page_text)} lines extracted")
                print(f"      Confidence: {avg_conf:.2%}")
            else:
                print(f"   ⚠️  Page {page_num + 1}: No text detected")

            print()

        doc.close()

        full_text = "\n\n".join(all_text)
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0

        print(f"✅ PDF extraction complete!")
        print(f"   Total text length: {len(full_text)} characters")
        print(f"   Average confidence: {avg_confidence:.2%}")
        print()

        return full_text, avg_confidence

    except Exception as e:
        print(f"❌ Error processing PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return "", 0.0


def test_with_sample_pdf():
    """Test OCR with a PDF from the uploads folder"""
    print("\n" + "=" * 60)
    print("🧪 PADDLEOCR FUNCTIONALITY TEST")
    print("=" * 60)
    print()

    # Initialize OCR
    ocr = initialize_paddleocr()
    if not ocr:
        return

    # Check for PDFs in uploads folder
    uploads_dir = Path(__file__).parent / "uploads"

    if not uploads_dir.exists():
        print("❌ uploads folder not found!")
        return

    pdf_files = list(uploads_dir.glob("*.pdf"))

    if not pdf_files:
        print("❌ No PDF files found in uploads folder!")
        return

    # Use the first PDF
    pdf_path = str(pdf_files[0])
    print(f"📁 Found {len(pdf_files)} PDF(s) in uploads folder")
    print(f"📝 Testing with: {pdf_files[0].name}")
    print()

    # Extract text
    text, confidence = extract_text_from_pdf(ocr, pdf_path)

    # Display results
    print("=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    print(f"Text Length: {len(text)} characters")
    print(f"Confidence: {confidence:.2%}")
    print()
    print("📄 Extracted Text Preview (first 500 chars):")
    print("-" * 60)
    print(text[:500] if text else "No text extracted")
    print("-" * 60)
    print()

    # Save full text to file
    output_file = "ocr_test_output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("PaddleOCR Test Results\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Source PDF: {pdf_files[0].name}\n")
        f.write(f"Text Length: {len(text)} characters\n")
        f.write(f"Confidence: {confidence:.2%}\n\n")
        f.write("=" * 60 + "\n")
        f.write("FULL EXTRACTED TEXT\n")
        f.write("=" * 60 + "\n\n")
        f.write(text)

    print(f"💾 Full results saved to: {output_file}")
    print()
    print("✅ Test complete!")


if __name__ == "__main__":
    test_with_sample_pdf()

