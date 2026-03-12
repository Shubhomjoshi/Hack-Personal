"""
FastAPI Server Startup Script
AI-Powered Document Intelligence Backend

Usage:
    python start_server.py              # Development mode with auto-reload
    python start_server.py --prod       # Production mode
    python start_server.py --port 8080  # Custom port
"""

import sys
import os
import uvicorn

def main():
    # Parse command line arguments
    args = sys.argv[1:]
    
    # Default configuration
    host = "0.0.0.0"
    port = 8000
    reload = True  # Auto-reload for development
    
    # Check for arguments
    if "--prod" in args:
        reload = False
        print("🚀 Starting in PRODUCTION mode...")
    else:
        print("🔧 Starting in DEVELOPMENT mode with auto-reload...")
    
    if "--port" in args:
        try:
            port_index = args.index("--port") + 1
            port = int(args[port_index])
        except (ValueError, IndexError):
            print("⚠️  Invalid port specified, using default: 8000")
            port = 8000
    
    # Display startup information
    print("=" * 70)
    print("  📄 AI-Powered Document Intelligence API")
    print("=" * 70)
    print(f"  🌐 Server URL:        http://localhost:{port}")
    print(f"  📚 API Docs:          http://localhost:{port}/docs")
    print(f"  📋 OpenAPI Spec:      http://localhost:{port}/openapi.json")
    print(f"  🔄 Auto-reload:       {'Enabled' if reload else 'Disabled'}")
    print("=" * 70)
    print()
    
    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

