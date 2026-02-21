"""
Simple server start without reload (for production/stable use)
This avoids the watchfiles crash from monitoring too many files
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("STARTING DOCUMENT INTELLIGENCE API SERVER")
    print("=" * 70)
    print("\n🚀 Starting server without auto-reload (stable mode)...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔧 To stop: Press CTRL+C\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # No reload - stable mode
        log_level="info"
    )

