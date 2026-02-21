"""
PDF Reader Script
Extracts text content from PDF files
"""
import sys

def read_pdf_pypdf2(pdf_path):
    """Read PDF using PyPDF2"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = []
            print(f"Total pages: {len(pdf_reader.pages)}\n")
            print("=" * 80)
            for i, page in enumerate(pdf_reader.pages):
                print(f"\n--- Page {i + 1} ---\n")
                page_text = page.extract_text()
                print(page_text)
                text.append(page_text)
            return "\n\n".join(text)
    except ImportError:
        print("PyPDF2 not installed. Install with: pip install PyPDF2")
        return None
    except Exception as e:
        print(f"Error reading PDF with PyPDF2: {e}")
        return None

def read_pdf_pdfplumber(pdf_path):
    """Read PDF using pdfplumber (better text extraction)"""
    try:
        import pdfplumber
        text = []
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}\n")
            print("=" * 80)
            for i, page in enumerate(pdf.pages):
                print(f"\n--- Page {i + 1} ---\n")
                page_text = page.extract_text()
                print(page_text)
                text.append(page_text)
        return "\n\n".join(text)
    except ImportError:
        print("pdfplumber not installed. Install with: pip install pdfplumber")
        return None
    except Exception as e:
        print(f"Error reading PDF with pdfplumber: {e}")
        return None

if __name__ == "__main__":
    pdf_file = "Ai-powered Document Intelligence For Trucking Industry.pdf"

    print("Attempting to read PDF...\n")

    # Try pdfplumber first (usually better)
    result = read_pdf_pdfplumber(pdf_file)

    # If pdfplumber fails, try PyPDF2
    if result is None:
        print("\n" + "=" * 80)
        print("Trying alternative method (PyPDF2)...")
        print("=" * 80 + "\n")
        result = read_pdf_pypdf2(pdf_file)

    if result is None:
        print("\n❌ Could not read PDF. Please install one of these:")
        print("   pip install pdfplumber")
        print("   pip install PyPDF2")

