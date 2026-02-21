"""
Quick Start Server - Test Upload API
"""
import subprocess
import sys

print("=" * 70)
print("STARTING FASTAPI SERVER (PaddleOCR DISABLED)")
print("=" * 70)
print()
print("✅ PaddleOCR has been disabled")
print("✅ Using pdfplumber only (fast text extraction)")
print()
print("Server will start on: http://localhost:8000")
print("API Docs: http://localhost:8000/docs")
print()
print("Test the upload API:")
print("  POST /api/documents/upload")
print()
print("Press Ctrl+C to stop the server")
print("=" * 70)
print()

# Start server
subprocess.run([
    sys.executable,
    "-m",
    "uvicorn",
    "main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
])

