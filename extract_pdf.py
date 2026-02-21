"""
Simple PDF to Text Extractor
"""
try:
    import pdfplumber

    pdf_path = "Ai-powered Document Intelligence For Trucking Industry.pdf"
    output_path = "pdf_content.txt"

    with open(output_path, 'w', encoding='utf-8') as output_file:
        with pdfplumber.open(pdf_path) as pdf:
            output_file.write(f"PDF: {pdf_path}\n")
            output_file.write(f"Total Pages: {len(pdf.pages)}\n")
            output_file.write("=" * 80 + "\n\n")

            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                output_file.write(f"--- PAGE {i} ---\n\n")
                output_file.write(text if text else "[No text found]")
                output_file.write("\n\n" + "=" * 80 + "\n\n")

    print(f"✅ PDF content extracted to: {output_path}")

    # Also print to console
    with open(output_path, 'r', encoding='utf-8') as f:
        print(f.read())

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

