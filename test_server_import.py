"""
Test if server can start with orders router
"""
print("Testing imports...")

try:
    from database import init_db
    print("✅ database imported")

    from routers import auth, documents, validation_rules, analytics, samples
    print("✅ All existing routers imported")

    import routers.orders as orders
    print("✅ Orders router imported")

    from fastapi import FastAPI
    print("✅ FastAPI imported")

    # Try to create app
    app = FastAPI()
    print("✅ FastAPI app created")

    # Try to register routers
    app.include_router(auth.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(validation_rules.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")
    app.include_router(samples.router, prefix="/api")
    app.include_router(orders.router)
    print("✅ All routers registered successfully")

    # Check orders routes
    print(f"\n📋 Orders Router Details:")
    print(f"   Prefix: {orders.router.prefix}")
    print(f"   Tags: {orders.router.tags}")
    print(f"   Routes: {len(orders.router.routes)}")
    for route in orders.router.routes:
        print(f"      - {route.methods} {route.path}")

    print("\n✅ ALL TESTS PASSED - Server should start successfully!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

