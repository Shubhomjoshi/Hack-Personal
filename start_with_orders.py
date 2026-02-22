"""
Start server and verify orders API is working
"""
import subprocess
import time
import sys

print("=" * 70)
print("🚀 STARTING SERVER WITH ORDERS API")
print("=" * 70)
print()

print("📝 Starting FastAPI server...")
print("   URL: http://localhost:8000")
print("   Docs: http://localhost:8000/docs")
print("   Orders API: http://localhost:8000/api/orders/")
print()
print("⚠️  Press Ctrl+C to stop the server")
print()
print("=" * 70)
print()

try:
    # Start the server
    subprocess.run([
        sys.executable, "main.py"
    ])
except KeyboardInterrupt:
    print("\n\n👋 Server stopped by user")
except Exception as e:
    print(f"\n❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()

