# Test FastAPI Installation and Project Setup
# Run this file to verify everything is working

import sys
import os

print("=" * 70)
print("FastAPI Project Verification Script")
print("=" * 70)
print()

# Test 1: Python Version
print("✓ Testing Python Version...")
print(f"  Python {sys.version}")
print()

# Test 2: Import Dependencies
print("✓ Testing Dependencies...")
try:
    import fastapi
    print(f"  ✅ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"  ❌ FastAPI not found: {e}")

try:
    import uvicorn
    print(f"  ✅ Uvicorn installed")
except ImportError as e:
    print(f"  ❌ Uvicorn not found: {e}")

try:
    import sqlalchemy
    print(f"  ✅ SQLAlchemy {sqlalchemy.__version__}")
except ImportError as e:
    print(f"  ❌ SQLAlchemy not found: {e}")

try:
    import pydantic
    print(f"  ✅ Pydantic {pydantic.__version__}")
except ImportError as e:
    print(f"  ❌ Pydantic not found: {e}")

print()

# Test 3: Import Project Modules
print("✓ Testing Project Modules...")
sys.path.insert(0, os.path.dirname(__file__))

try:
    from database import Base, engine, get_db
    print("  ✅ Database module loaded")
except Exception as e:
    print(f"  ❌ Database module error: {e}")

try:
    from models import User, Item
    print("  ✅ Models module loaded")
except Exception as e:
    print(f"  ❌ Models module error: {e}")

try:
    from schemas import UserCreate, UserResponse, ItemCreate, ItemResponse
    print("  ✅ Schemas module loaded")
except Exception as e:
    print(f"  ❌ Schemas module error: {e}")

try:
    from routers import users, items
    print("  ✅ Routers loaded")
except Exception as e:
    print(f"  ❌ Routers error: {e}")

try:
    from main import app
    print("  ✅ Main application loaded")
except Exception as e:
    print(f"  ❌ Main application error: {e}")

print()

# Test 4: Database Connection
print("✓ Testing Database Connection...")
try:
    from database import init_db
    init_db()
    print("  ✅ Database initialized successfully")
    if os.path.exists("app.db"):
        size = os.path.getsize("app.db")
        print(f"  ✅ Database file created (app.db - {size} bytes)")
except Exception as e:
    print(f"  ❌ Database initialization error: {e}")

print()

# Test 5: FastAPI App
print("✓ Testing FastAPI Application...")
try:
    from main import app
    routes = [route.path for route in app.routes]
    print(f"  ✅ Application has {len(routes)} routes")
    print("  ✅ Available endpoints:")
    for route in routes:
        if hasattr(route, 'methods'):
            print(f"     {route}")
except Exception as e:
    print(f"  ❌ Application error: {e}")

print()
print("=" * 70)
print("Verification Complete!")
print("=" * 70)
print()
print("To start the server, run:")
print("  python main.py")
print()
print("Then open your browser to:")
print("  http://localhost:8000/docs")
print()

