"""
Safe Database Initialization and Startup
"""
import sys
import os

print("=" * 70)
print("Starting FastAPI Application")
print("=" * 70)
print()

# Step 1: Check dependencies
print("Step 1: Checking dependencies...")
required_packages = ['fastapi', 'sqlalchemy', 'pydantic', 'uvicorn']
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f"  ✅ {package}")
    except ImportError:
        print(f"  ❌ {package} - NOT INSTALLED")
        missing_packages.append(package)

if missing_packages:
    print()
    print("❌ Missing packages detected!")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

print()

# Step 2: Initialize database
print("Step 2: Initializing database...")
try:
    from database import Base, engine
    import models  # Import models to register them

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("  ✅ Database tables created/verified")

except Exception as e:
    print(f"  ❌ Database initialization failed: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("Try running: python init_database.py")
    sys.exit(1)

print()

# Step 3: Start FastAPI
print("Step 3: Starting FastAPI server...")
print()
print("Server will start at: http://localhost:8000")
print("API Documentation: http://localhost:8000/docs")
print()
print("=" * 70)
print()

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

