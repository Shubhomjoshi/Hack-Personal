"""
Complete System Check - Verify Everything is Working
"""
import sys
import os

def check_python_version():
    """Check Python version"""
    print("1. Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} - Need 3.8+")
        return False

def check_dependencies():
    """Check required dependencies"""
    print("\n2. Checking dependencies...")
    required = {
        'fastapi': 'FastAPI framework',
        'uvicorn': 'ASGI server',
        'sqlalchemy': 'Database ORM',
        'pydantic': 'Data validation',
        'jose': 'JWT tokens',
        'passlib': 'Password hashing'
    }

    all_ok = True
    for package, description in required.items():
        try:
            __import__(package)
            print(f"   ✅ {package:15} - {description}")
        except ImportError:
            print(f"   ❌ {package:15} - MISSING!")
            all_ok = False

    return all_ok

def check_files():
    """Check required files exist"""
    print("\n3. Checking required files...")
    required_files = {
        'main.py': 'Main application',
        'database.py': 'Database config',
        'models.py': 'Database models',
        'schemas.py': 'Pydantic schemas',
        'auth.py': 'Authentication',
        'requirements.txt': 'Dependencies',
        'routers/auth.py': 'Auth routes',
        'routers/documents.py': 'Document routes'
    }

    all_ok = True
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"   ✅ {file:25} - {description}")
        else:
            print(f"   ❌ {file:25} - MISSING!")
            all_ok = False

    return all_ok

def check_database():
    """Check database can be initialized"""
    print("\n4. Checking database...")
    try:
        from database import Base, engine
        import models

        # Try to create tables
        Base.metadata.create_all(bind=engine)

        # Check if database file was created
        if os.path.exists('app.db'):
            size = os.path.getsize('app.db')
            print(f"   ✅ Database file: app.db ({size} bytes)")
        else:
            print("   ⚠️  Database file not found (will be created on first run)")

        # Try to query
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()

        # Count users
        from models import User
        count = db.query(User).count()
        print(f"   ✅ Database accessible ({count} users)")
        db.close()

        return True
    except Exception as e:
        print(f"   ❌ Database error: {str(e)}")
        return False

def check_import_main():
    """Check if main app can be imported"""
    print("\n5. Checking main application...")
    try:
        from main import app
        print(f"   ✅ FastAPI app loaded")
        print(f"   ✅ Title: {app.title}")
        print(f"   ✅ Version: {app.version}")
        print(f"   ✅ Routes: {len(app.routes)}")
        return True
    except Exception as e:
        print(f"   ❌ Cannot import main: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("SYSTEM VERIFICATION CHECK")
    print("=" * 70)
    print()

    checks = [
        check_python_version(),
        check_dependencies(),
        check_files(),
        check_database(),
        check_import_main()
    ]

    print()
    print("=" * 70)

    if all(checks):
        print("✅ ALL CHECKS PASSED!")
        print()
        print("Your system is ready to run!")
        print()
        print("Start the server:")
        print("  python main.py")
        print()
        print("Or use safe starter:")
        print("  python start_server.py")
        print()
        print("Then visit:")
        print("  http://localhost:8000/docs")
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        print("Fix the issues above, then:")
        print()
        print("1. Install dependencies:")
        print("   pip install -r requirements.txt")
        print()
        print("2. Initialize database:")
        print("   python init_database.py")
        print()
        print("3. Run this check again:")
        print("   python check_system.py")

    print("=" * 70)

    return 0 if all(checks) else 1

if __name__ == "__main__":
    sys.exit(main())

