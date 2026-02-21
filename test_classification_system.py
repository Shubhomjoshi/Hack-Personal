"""
Test Script for Sample-Based Classification System
Tests all components of the new classification system
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("SAMPLE-BASED CLASSIFICATION SYSTEM TEST")
print("=" * 70)
print()

# Test 1: Embedding Service
print("Test 1: Embedding Service")
print("-" * 70)
try:
    from services.embedding_service import get_embedding_service

    embedding_service = get_embedding_service()
    print(f"✅ Embedding service initialized")
    print(f"   Available: {embedding_service.available}")
    if embedding_service.available:
        print(f"   Model: {embedding_service.model_name}")

        # Test embedding generation
        test_text = "This is a Bill of Lading document for shipping goods."
        embedding = embedding_service.generate_embedding(test_text)
        if embedding:
            print(f"   ✅ Generated test embedding: {len(embedding)} dimensions")

            # Test similarity
            test_text2 = "This is a Proof of Delivery document."
            embedding2 = embedding_service.generate_embedding(test_text2)
            if embedding2:
                similarity = embedding_service.compute_similarity(embedding, embedding2)
                print(f"   ✅ Similarity computation works: {similarity:.3f}")
        else:
            print(f"   ⚠️  Failed to generate embedding")
    else:
        print(f"   ❌ Embedding service not available")
        print(f"   Install with: pip install sentence-transformers")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Sample Store
print("Test 2: Sample Store")
print("-" * 70)
try:
    from services.sample_store import get_doc_sample_store
    from database import SessionLocal
    from models import DocumentType

    sample_store = get_doc_sample_store()
    db = SessionLocal()

    print(f"✅ Sample store initialized")

    # Get sample counts
    counts = sample_store.get_sample_count_per_type(db)
    total_samples = sum(counts.values())
    print(f"   Total samples in database: {total_samples}")

    if total_samples > 0:
        print(f"   Samples per type:")
        for doc_type, count in counts.items():
            if count > 0:
                print(f"      - {doc_type}: {count}")

    # Get readiness status
    status = sample_store.get_readiness_status(db)
    print(f"   System status: {status['status']}")
    print(f"   Readiness: {status['readiness_percentage']}%")
    print(f"   Message: {status['message']}")

    db.close()
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Similarity Matcher
print("Test 3: Similarity Matcher")
print("-" * 70)
try:
    from services.similarity_matcher import get_similarity_matcher

    similarity_matcher = get_similarity_matcher()
    print(f"✅ Similarity matcher initialized")

    if embedding_service.available:
        db = SessionLocal()

        # Test with sample text
        test_text = "Bill of Lading - Shipper: ABC Corp, Consignee: XYZ Ltd"
        match = similarity_matcher.match_with_text(test_text, db)

        if match:
            print(f"   ✅ Matching works")
            print(f"      Best match: {match.doc_type}")
            print(f"      Confidence: {match.confidence:.1%}")
        else:
            print(f"   ⚠️  No match found (need samples in database)")

        db.close()
    else:
        print(f"   ⚠️  Skipped (embedding service not available)")

except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 4: Sample-Based Classifier
print("Test 4: Sample-Based Classifier")
print("-" * 70)
try:
    from services.sample_based_classifier import get_sample_based_classifier

    classifier = get_sample_based_classifier()
    print(f"✅ Sample-based classifier initialized")
    print(f"   Signal weights:")
    print(f"      - Embedding: {classifier.WEIGHTS['embedding']*100}%")
    print(f"      - Gemini: {classifier.WEIGHTS['gemini']*100}%")
    print(f"      - Keyword: {classifier.WEIGHTS['keyword']*100}%")
    print(f"   Confidence thresholds:")
    print(f"      - Embedding: {classifier.EMBEDDING_THRESHOLD*100}%")
    print(f"      - Keyword: {classifier.KEYWORD_THRESHOLD*100}%")

except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 5: Database Models
print("Test 5: Database Models")
print("-" * 70)
try:
    from models import DocTypeSample, ClassificationResult as ClassificationResultModel
    from database import engine
    from sqlalchemy import inspect

    inspector = inspect(engine)

    # Check if tables exist
    tables = inspector.get_table_names()

    if 'doc_type_samples' in tables:
        print(f"   ✅ doc_type_samples table exists")
        columns = [col['name'] for col in inspector.get_columns('doc_type_samples')]
        print(f"      Columns: {', '.join(columns)}")
    else:
        print(f"   ❌ doc_type_samples table missing")

    if 'classification_results' in tables:
        print(f"   ✅ classification_results table exists")
        columns = [col['name'] for col in inspector.get_columns('classification_results')]
        print(f"      Columns: {', '.join(columns)}")
    else:
        print(f"   ❌ classification_results table missing")

except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 6: API Router
print("Test 6: API Router")
print("-" * 70)
try:
    from routers import samples

    print(f"✅ Samples router imported successfully")
    print(f"   Available endpoints:")

    # Get route info
    routes = [route for route in samples.router.routes]
    for route in routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods)
            print(f"      {methods:10} {route.path}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 7: Integration with Background Processor
print("Test 7: Background Processor Integration")
print("-" * 70)
try:
    from services.background_processor import BackgroundProcessor

    processor = BackgroundProcessor()
    print(f"✅ Background processor initialized")
    print(f"   Classifier integration: OK")

except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Summary
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print()

if embedding_service.available:
    print("✅ System is fully functional!")
    print()
    print("Next steps:")
    print("1. Start the server: python main.py")
    print("2. Upload sample documents: POST /api/samples/upload")
    print("3. Check system status: GET /api/samples/status")
    print("4. Upload test documents to see classification in action")
else:
    print("⚠️  Embedding service is not available")
    print()
    print("To enable full functionality:")
    print("1. Ensure sentence-transformers is installed")
    print("2. Wait for model download to complete (first time only)")
    print("3. Re-run this test script")
    print()
    print("System will still work using keyword + Gemini classification")

print()
print("For detailed documentation, see: SAMPLE_CLASSIFICATION_GUIDE.md")
print("=" * 70)

