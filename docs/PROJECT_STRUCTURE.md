# 📁 Project Structure Guide

## Overview
This document describes the clean, production-ready structure of the AI-Powered Document Intelligence Backend API.

---

## 🗂️ Root Directory Files

### Core Application Files
- **`main.py`** - FastAPI application entry point, API routes configuration
- **`database.py`** - Database configuration and session management
- **`models.py`** - SQLAlchemy ORM models (User, Document, OrderInfo, etc.)
- **`schemas.py`** - Pydantic schemas for request/response validation
- **`auth.py`** - Authentication and authorization utilities
- **`init_database.py`** - Database initialization script

### Utility Scripts
- **`debug_document_processing.py`** - Debug tool for testing document processing pipeline
- **`reset_database.py`** - Database reset utility

### Configuration Files
- **`.env`** - Environment variables (API keys, database URLs)
- **`.env.example`** - Template for environment variables
- **`requirements.txt`** - Python dependencies for standard deployment
- **`requirements_azure.txt`** - Python dependencies for Azure deployment
- **`runtime.txt`** - Python version specification

### Deployment Files
- **`Procfile`** - Process configuration for cloud platforms
- **`render.yaml`** - Render.com deployment configuration
- **`deploy_azure.ps1`** - Azure deployment script
- **`azure_config.py`** - Azure-specific configuration
- **`.dockerignore`** - Docker build exclusions
- **`.gitignore`** - Git version control exclusions

### Database Files
- **`app.db`** - SQLite database (production data)
- **`app.db.backup`** - Database backup

---

## 📂 Folders

### `/routers`
API route handlers organized by feature:
- `auth.py` - Authentication endpoints (login, register)
- `documents.py` - Document upload, retrieval, preview endpoints
- `orders.py` - Order management endpoints
- `samples.py` - Sample document management for classification training

### `/services`
Core business logic and AI processing:
- **AI Agents:**
  - `document_classification_agent.py` - AI agent for document type classification
  - `signature_detection_agent.py` - AI agent for signature detection
  - `document_processing_agent.py` - Main orchestrator agent

- **OCR & Text Extraction:**
  - `easyocr_service.py` - EasyOCR integration for text extraction
  - `gemini_service.py` - Google Gemini AI for advanced OCR and analysis

- **Document Processing:**
  - `background_processor.py` - Background document processing orchestrator
  - `quality_assessment_service.py` - Document quality analysis (blur, skew detection)
  - `enhanced_metadata_extractor.py` - Field extraction from OCR text

- **Classification:**
  - `keyword_classifier.py` - Keyword-based document classification
  - `similarity_matcher.py` - Embedding-based similarity matching

- **Validation:**
  - `rule_validation_engine.py` - Business rule validation system

### `/docs`
**📚 Documentation Hub** - All essential project documentation:
- **`README.md`** - Project overview and quick start guide
- **`API_DOCUMENTATION.md`** - Complete API endpoint reference
- **`ARCHITECTURE.md`** - System architecture and design decisions
- **`BACKEND_HANDOVER_DOCUMENTATION.md`** - Handover guide for clients
- **`PROJECT_STRUCTURE.md`** (this file) - Project organization guide

### `/uploads`
Uploaded document storage (PDF, images)

### `/samples`
Sample documents for training the classification system

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Initialize Database
```bash
python init_database.py
```

### 3. Run Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access API
- **API Docs:** http://localhost:8000/docs
- **OpenAPI Spec:** http://localhost:8000/openapi.json

---

## 🧹 Cleanup Summary

This project has been cleaned up from development to production state:

### Files Removed:
- ✅ **47 test files** (test_*.py)
- ✅ **54 redundant documentation files** (various .md files)
- ✅ **11 output/text files** (logs, test outputs)
- ✅ **30 utility scripts** (migration scripts, verification tools)
- ✅ **8 batch/PowerShell scripts** (setup scripts)
- ✅ **6 image/temp files** (test images)
- ✅ **2 sample PDFs** (reference documents)

### Total Files Removed: **162 files**

### Files Preserved:
- ✅ All core application code
- ✅ Essential documentation (moved to `/docs`)
- ✅ Configuration files
- ✅ Deployment scripts

---

## 📖 Documentation Index

For detailed information, refer to these documents in the `/docs` folder:

1. **[README.md](./README.md)** - Start here for project overview
2. **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - API endpoint reference
3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design and architecture
4. **[BACKEND_HANDOVER_DOCUMENTATION.md](./BACKEND_HANDOVER_DOCUMENTATION.md)** - Client handover guide

---

## 🔧 Development Guidelines

### Adding New Features
1. Create appropriate service in `/services`
2. Add API routes in `/routers`
3. Update schemas in `schemas.py`
4. Update models if database changes needed
5. Document API changes in `API_DOCUMENTATION.md`

### Code Organization
- **Models:** Database tables and relationships
- **Schemas:** Request/response data structures
- **Services:** Business logic and AI processing
- **Routers:** API endpoints and route handlers
- **Agents:** Autonomous AI processing units

---

## 📦 Database Schema

Key tables:
- **users** - User authentication and profile
- **documents** - Uploaded documents and metadata
- **order_info** - Order/load information
- **classification_results** - Document classification results
- **doc_type_samples** - Sample documents for classification training

---

## 🎯 Production Ready

This codebase is now:
- ✅ Clean and organized
- ✅ Well-documented
- ✅ Production-ready
- ✅ Ready for client handover
- ✅ Deployment-ready (Azure, Render, Docker)

---

*Last Updated: March 12, 2026*
*Project: AI-Powered Document Intelligence for Trucking Industry*

