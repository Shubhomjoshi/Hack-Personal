"""
FastAPI main application file
All connections and configurations are initialized here
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database import init_db
from routers import auth, documents, validation_rules, analytics, samples
import routers.orders as orders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler - runs on startup and shutdown
    """
    # Startup: Initialize database
    logger.info("🚀 Starting up Document Intelligence API...")
    init_db()
    logger.info("✅ Database initialized!")
    logger.info("📄 Document Intelligence System Ready")

    yield

    # Shutdown
    logger.info("👋 Shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="Document Intelligence API",
    description="AI-powered Document Intelligence System for Trucking Industry",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(validation_rules.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(samples.router, prefix="/api")
app.include_router(orders.router)


@app.get("/")
def root():
    """
    Root endpoint - API Information
    """
    return {
        "name": "Document Intelligence API",
        "version": "1.0.0",
        "description": "AI-powered document processing for trucking industry",
        "features": [
            "Document Upload & Processing",
            "Document Type Classification (8 types)",
            "Quality Assessment",
            "Signature Detection",
            "Metadata Extraction",
            "Rule-based Validation",
            "Analytics & Reporting"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "auth": "/api/auth",
            "documents": "/api/documents",
            "validation_rules": "/api/validation-rules",
            "analytics": "/api/analytics"
        }
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    # Check OCR service
    ocr_status = "unavailable"
    try:
        from services.ocr_service import ocr_service
        ocr_status = "available (PaddleOCR)" if ocr_service.ocr_available else "not_installed"
    except Exception as e:
        ocr_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "Document Intelligence API",
        "database": "connected",
        "ocr_engine": ocr_status,
        "message": "Install PaddleOCR: pip install paddlepaddle paddleocr" if ocr_status == "not_installed" else None
    }


@app.get("/api/info")
def api_info():
    """
    API information and capabilities
    """
    return {
        "api_version": "1.0.0",
        "supported_document_types": [
            "Bill of Lading",
            "Proof of Delivery",
            "Packing List",
            "Commercial Invoice",
            "Hazmat Document",
            "Lumper Receipt",
            "Trip Sheet",
            "Freight Invoice"
        ],
        "supported_file_formats": ["PDF", "JPEG", "PNG", "TIFF"],
        "capabilities": {
            "ocr": "Text extraction from documents",
            "classification": "Automatic document type identification",
            "quality_assessment": "Blur, skew, brightness detection",
            "signature_detection": "Detect and count signatures",
            "metadata_extraction": "Extract order numbers, dates, etc.",
            "validation": "Customer-specific rule validation"
        },
        "authentication": "JWT Bearer Token"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=[
            ".venv/*",
            ".venv/**/*",
            "*.pyc",
            "__pycache__/*",
            "uploads/*",
            "*.db",
            "*.log"
        ]
    )

