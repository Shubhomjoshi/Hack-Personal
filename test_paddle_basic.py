"""
Basic PaddleOCR Initialization Test
"""
import os
import sys

print("=" * 60)
print("🧪 PADDLEOCR BASIC INITIALIZATION TEST")
print("=" * 60)
print()

# Step 1: Check if PaddleOCR is installed
print("Step 1: Checking PaddleOCR installation...")
try:
    import paddleocr
    print("✅ PaddleOCR package found")
    print(f"   Location: {paddleocr.__file__}")
except ImportError as e:
    print(f"❌ PaddleOCR not installed: {e}")
    print("   Run: pip install paddlepaddle paddleocr")
    sys.exit(1)

print()

# Step 2: Check PaddlePaddle
print("Step 2: Checking PaddlePaddle...")
try:
    import paddle
    print("✅ PaddlePaddle found")
    print(f"   Version: {paddle.__version__}")
except ImportError as e:
    print(f"❌ PaddlePaddle not installed: {e}")
    sys.exit(1)

print()

# Step 3: Initialize PaddleOCR with correct parameters
print("Step 3: Initializing PaddleOCR...")
print("   Disabling OneDNN/MKLDNN to avoid errors...")

# Disable OneDNN
os.environ['FLAGS_use_mkldnn'] = '0'

try:
    from paddleocr import PaddleOCR

    print("   Creating OCR instance...")
    print("   Parameters:")
    print("     - use_angle_cls: True")
    print("     - lang: 'en'")
    print("     - enable_mkldnn: False")
    print("     - cpu_threads: 4")
    print()

    ocr = PaddleOCR(
        use_angle_cls=True,
        lang='en',
        enable_mkldnn=False,
        cpu_threads=4
    )

    print("✅ PaddleOCR initialized successfully!")
    print()

except Exception as e:
    print(f"❌ Failed to initialize PaddleOCR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print()
print("PaddleOCR is ready to use.")
print("You can now integrate it with FastAPI.")

