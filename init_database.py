"""
Database Initialization Script
Run this to create/reset the database
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("Database Initialization")
print("=" * 70)
print()

try:
    # Import database components
    print("1. Importing database components...")
    from database import Base, engine, init_db
    print("   ✅ Database components imported")

    # Import all models to ensure they're registered
    print("2. Importing models...")
    from models import (
        User, Document, DocumentType, ReadabilityStatus, ValidationStatus,
        ValidationRule, DocumentValidation, ProcessingLog
    )
    print("   ✅ All models imported")

    # Check if database file exists
    db_file = "app.db"
    if os.path.exists(db_file):
        print(f"3. Database file exists: {db_file}")
        print("   ⚠️  WARNING: Old database has full_name column!")
        print("   ⚠️  This will cause 'no such column' errors!")
        response = input("   Delete and recreate? (y/n): ")
        if response.lower() == 'y':
            os.remove(db_file)
            print("   ✅ Old database removed")
        else:
            print("   ⚠️  Keeping old database - may cause errors!")
    else:
        print("3. No existing database found")

    # Create tables
    print("4. Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✅ All tables created successfully!")

    print()
    print("=" * 70)
    print("✅ Database initialized successfully!")
    print()
    print("Tables created:")
    print("  - users")
    print("  - documents")
    print("  - validation_rules")
    print("  - document_validations")
    print("  - processing_logs")
    print()
    print("You can now start the server:")
    print("  python main.py")
    print("=" * 70)

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print()
    print("Please make sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

