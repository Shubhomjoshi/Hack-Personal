"""
Quick verification script - Check if all components are importable
"""
import sys
print("=" * 70)
print("Document Intelligence API - Component Verification")
print("=" * 70)
print()

errors = []

# Test 1: Core modules
print("✓ Testing core modules...")
try:
    from database import Base, engine, get_db, init_db
    print("  ✅ database.py")
except Exception as e:
    errors.append(f"database.py: {e}")
    print(f"  ❌ database.py: {e}")

try:
    from models import User, Document, ValidationRule, DocumentValidation, ProcessingLog
    print("  ✅ models.py")
except Exception as e:
    errors.append(f"models.py: {e}")
    print(f"  ❌ models.py: {e}")

try:
    from schemas import UserRegister, DocumentUploadResponse, ValidationRuleCreate
    print("  ✅ schemas.py")
except Exception as e:
    errors.append(f"schemas.py: {e}")
    print(f"  ❌ schemas.py: {e}")

try:
    from auth import get_password_hash, verify_password, create_access_token
    print("  ✅ auth.py")
except Exception as e:
    errors.append(f"auth.py: {e}")
    print(f"  ❌ auth.py: {e}")

print()

# Test 2: Routers
print("✓ Testing routers...")
try:
    from routers import auth, documents, validation_rules, analytics
    print("  ✅ All routers imported")
except Exception as e:
    errors.append(f"routers: {e}")
    print(f"  ❌ routers: {e}")

print()

# Test 3: Services
print("✓ Testing services...")
services_list = [
    'ocr_service',
    'classification_service',
    'quality_service',
    'signature_service',
    'metadata_service',
    'validation_service',
    'processing_service'
]

for service_name in services_list:
    try:
        module = __import__(f'services.{service_name}', fromlist=[service_name])
        print(f"  ✅ {service_name}.py")
    except Exception as e:
        errors.append(f"{service_name}: {e}")
        print(f"  ❌ {service_name}.py: {e}")

print()

# Test 4: Main application
print("✓ Testing main application...")
try:
    from main import app
    print("  ✅ main.py - FastAPI app loaded")
    print(f"  ✅ API Title: {app.title}")
    print(f"  ✅ API Version: {app.version}")
    print(f"  ✅ Total Routes: {len(app.routes)}")
except Exception as e:
    errors.append(f"main.py: {e}")
    print(f"  ❌ main.py: {e}")

print()
print("=" * 70)

if errors:
    print(f"❌ Verification FAILED with {len(errors)} error(s):")
    for error in errors:
        print(f"   - {error}")
else:
    print("✅ All components verified successfully!")
    print()
    print("🚀 System is ready to run!")
    print()
    print("To start the server:")
    print("  python main.py")
    print()
    print("Or:")
    print("  uvicorn main:app --reload")
    print()
    print("Then visit: http://localhost:8000/docs")

print("=" * 70)

