"""
Reset Database - Delete old database and create fresh one
"""
import os
import sys

print("=" * 70)
print("DATABASE RESET")
print("=" * 70)
print()

# Check if database exists
db_file = "app.db"

if os.path.exists(db_file):
    print(f"Found existing database: {db_file}")
    print("This will DELETE the database and all data!")
    print()
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() != 'yes':
        print("Aborted.")
        sys.exit(0)

    # Delete database
    try:
        os.remove(db_file)
        print(f"✅ Deleted {db_file}")
    except Exception as e:
        print(f"❌ Error deleting database: {e}")
        sys.exit(1)
else:
    print("No existing database found.")

print()
print("Creating fresh database...")
print()

try:
    # Import database and models
    from database import Base, engine
    import models

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("✅ Database created successfully!")
    print()
    print("Tables created:")
    print("  - users (WITHOUT full_name column)")
    print("  - documents")
    print("  - validation_rules")
    print("  - document_validations")
    print("  - processing_logs")
    print()
    print("=" * 70)
    print("✅ RESET COMPLETE!")
    print()
    print("You can now start the server:")
    print("  python main.py")
    print()
    print("Or:")
    print("  python start_server.py")
    print("=" * 70)

except Exception as e:
    print(f"❌ Error creating database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

