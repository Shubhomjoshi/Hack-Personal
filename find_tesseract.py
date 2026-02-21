"""
Find Tesseract Installation
"""
import os
import glob

print("=" * 70)
print("SEARCHING FOR TESSERACT INSTALLATION")
print("=" * 70)
print()

# Common installation directories
search_paths = [
    r'C:\Program Files\Tesseract-OCR',
    r'C:\Program Files (x86)\Tesseract-OCR',
    r'C:\Tesseract-OCR',
    r'C:\Program Files\tesseract',
    r'C:\Program Files (x86)\tesseract',
]

found_locations = []

print("Searching common installation directories...")
print()

for path in search_paths:
    exe_path = os.path.join(path, 'tesseract.exe')
    if os.path.exists(exe_path):
        print(f"✅ FOUND: {exe_path}")
        found_locations.append(exe_path)

        # Check version
        try:
            import subprocess
            result = subprocess.run([exe_path, '--version'],
                                  capture_output=True, text=True, timeout=5)
            version_info = result.stdout.split('\n')[0] if result.stdout else "Unknown"
            print(f"   Version: {version_info}")
        except Exception as e:
            print(f"   Could not get version: {e}")
        print()
    else:
        print(f"❌ Not found: {path}")

print()
print("=" * 70)

if found_locations:
    print(f"✅ Tesseract found at {len(found_locations)} location(s)")
    print()
    print("The OCR service should automatically detect it at:")
    for loc in found_locations:
        print(f"  {loc}")
    print()
    print("NEXT STEPS:")
    print("1. Restart your server: python main.py")
    print("2. Check health: http://localhost:8000/health")
    print("3. Should show: 'ocr_tesseract': 'available'")
else:
    print("❌ Tesseract NOT FOUND in standard locations")
    print()
    print("Searching entire C:\\ drive for tesseract.exe...")
    print("(This may take a minute...)")
    print()

    # Search entire C drive (may take time)
    try:
        for root, dirs, files in os.walk('C:\\'):
            if 'tesseract.exe' in files:
                full_path = os.path.join(root, 'tesseract.exe')
                print(f"✅ Found at: {full_path}")
                found_locations.append(full_path)
                break
            # Don't search Windows, System32, etc.
            dirs[:] = [d for d in dirs if d not in ['Windows', 'System32', '$Recycle.Bin', 'PerfLogs']]
    except Exception as e:
        print(f"Search error: {e}")

    if not found_locations:
        print()
        print("❌ Tesseract is NOT installed or not found")
        print()
        print("INSTALL TESSERACT:")
        print("1. Download: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install to: C:\\Program Files\\Tesseract-OCR")
        print("3. Run this script again")

print("=" * 70)

# Test with Python
print()
print("Testing with Python pytesseract...")
try:
    import pytesseract
    if found_locations:
        # Try setting path
        pytesseract.pytesseract.tesseract_cmd = found_locations[0]

    version = pytesseract.get_tesseract_version()
    print(f"✅ Python can access Tesseract: version {version}")
    print()
    print("YOUR OCR SHOULD WORK!")
except Exception as e:
    print(f"❌ Python cannot access Tesseract: {e}")
    print()
    if found_locations:
        print("Tesseract is installed but Python can't access it.")
        print(f"Try manually setting path in services/ocr_service.py:")
        print(f"pytesseract.pytesseract.tesseract_cmd = r'{found_locations[0]}'")
    else:
        print("Tesseract is not installed. Please install it first.")

print("=" * 70)

