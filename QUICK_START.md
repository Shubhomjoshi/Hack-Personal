# 🚀 Quick Start Guide - Document Intelligence API

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.10+ installed
- ✅ Virtual environment activated (`.venv`)
- ✅ All dependencies installed (`pip install -r requirements.txt`)

---

## 🔧 Setup Instructions

### Step 1: Configure Gemini API Key

The application uses Google Gemini AI for signature detection and enhanced OCR.

**Get your API key:**
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy...`)

**Update `.env` file:**
```bash
# Edit: C:\Amazatic\Hackathon Personal\Backend\.env
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

### Step 2: Verify Configuration

Run the API key test:
```powershell
python test_gemini_api_key.py
```

Expected output:
```
✅ API Key is VALID!
✅ TEST PASSED - Gemini API is ready to use!
```

---

## 🚀 Starting the Server

### Option 1: Simple Start (Recommended)
```powershell
python main.py
```

### Option 2: Start with Environment Loader
```powershell
.\start_server_with_env.ps1
```

### Option 3: Manual Environment Setup
```powershell
# Set API key manually
$env:GEMINI_API_KEY = "AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw"

# Start server
python main.py
```

**Server will start on:** http://localhost:8000

---

## ✅ Verify Everything is Working

### 1. Check Health Endpoint
```bash
# In browser or using curl:
http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Document Intelligence API",
  "database": "connected",
  "ocr_engine": "available (PaddleOCR)",
  "gemini_api": "configured"
}
```

### 2. Access API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 3. Test Document Upload

**From Desktop App:**
```bash
POST /api/documents/upload
Headers:
  Authorization: Bearer YOUR_JWT_TOKEN
Body (form-data):
  files: [your_document.pdf]
  order_number: "ORD-112-2025"
```

**From Mobile App:**
```bash
POST /api/documents/upload
Headers:
  Authorization: Bearer YOUR_JWT_TOKEN
Body (form-data):
  files: [your_document.jpg]
  driver_user_id: 8
```

---

## 📊 Key API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/register` - Register new user

### Documents
- `POST /api/documents/upload` - Upload document(s)
- `GET /api/documents/` - List all documents
- `GET /api/documents/{doc_id}` - Get document details
- `GET /api/documents/{doc_id}/preview` - Get document preview
- `GET /api/documents/order/{order_number}` - Get documents by order

### Orders
- `GET /api/orders/` - List all orders
- `GET /api/orders/{order_number}` - Get order details

### Validation
- `POST /api/validation-results/get-reasons` - Get validation failure reasons

### Health & Info
- `GET /health` - Health check
- `GET /api/info` - API capabilities

---

## 🔍 Troubleshooting

### Problem: Gemini API Error
**Symptoms:**
```
400 INVALID_ARGUMENT - API Key not found
```

**Solution:**
1. Check `.env` file has correct API key
2. Run: `python test_gemini_api_key.py`
3. Restart server after updating `.env`
4. See: `GEMINI_API_FIX_GUIDE.md` for details

### Problem: Server Won't Start
**Symptoms:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Database Error
**Symptoms:**
```
Database locked or not found
```

**Solution:**
```powershell
# Reinitialize database
python init_database.py
```

### Problem: OCR Not Working
**Symptoms:**
```
OCR service unavailable
```

**Solution:**
```powershell
# Install PaddleOCR
pip install paddlepaddle paddleocr
```

---

## 📖 Document Processing Flow

```
1. Upload Document
   ↓
2. Quality Assessment (blur, skew, brightness)
   ↓
3. OCR Text Extraction (EasyOCR + Gemini)
   ↓
4. Document Classification (8 types)
   ↓
5. Signature Detection (if BOL type)
   ↓
6. Metadata Extraction (order numbers, dates, etc.)
   ↓
7. Rule Validation (general + doc-specific)
   ↓
8. Save Results → Database
   ↓
9. Return Status to Frontend
```

---

## 🎯 Document Types Supported

1. **Bill of Lading (BOL)** - Requires 2+ signatures
2. **Proof of Delivery (POD)** - Requires 1+ signature
3. **Commercial Invoice** - Financial document
4. **Packing List** - Shipment contents
5. **Hazmat Document** - Dangerous goods
6. **Lumper Receipt** - Labor payment
7. **Trip Sheet** - Driver activity
8. **Freight Invoice** - Carrier billing

---

## 🔐 Security

### API Authentication
All endpoints (except `/health` and `/`) require JWT authentication:

```bash
Authorization: Bearer <your_jwt_token>
```

### Get JWT Token
```bash
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "email": "admin@example.com",
  "username": "admin",
  "id": 1,
  "is_active": true,
  "is_admin": true
}
```

---

## 📁 Project Structure

```
Backend/
├── main.py                    # FastAPI application
├── database.py                # Database configuration
├── models.py                  # SQLAlchemy models
├── auth.py                    # JWT authentication
├── .env                       # Environment variables (API keys)
├── requirements.txt           # Python dependencies
│
├── routers/                   # API endpoints
│   ├── auth.py
│   ├── documents.py
│   ├── orders.py
│   └── validation_results.py
│
├── services/                  # Business logic
│   ├── gemini_service.py      # Gemini AI integration
│   ├── easyocr_service.py     # EasyOCR integration
│   ├── document_classifier.py # Document type classification
│   ├── orchestrator.py        # Processing orchestration
│   └── rule_engine.py         # Validation rules
│
├── uploads/                   # Uploaded documents
├── app.db                     # SQLite database
│
└── test_*.py                  # Test scripts
```

---

## 📞 Support

### Common Issues
- **Gemini API Key:** See `GEMINI_API_FIX_GUIDE.md`
- **General Setup:** See `GEMINI_FIX_SUMMARY.md`
- **Architecture:** See `SYSTEM_DOCUMENTATION.md`

### Testing Tools
- `test_gemini_api_key.py` - Test Gemini API
- `debug_document_processing.py` - Debug document processing
- `verify_system_complete.py` - Full system check

### Logs
Server logs show detailed processing steps:
- Quality assessment results
- OCR extraction progress
- Classification decisions
- Validation outcomes

---

## 🎉 Quick Test

```powershell
# 1. Start server
python main.py

# 2. In another terminal - test health
curl http://localhost:8000/health

# 3. Access docs
# Open browser: http://localhost:8000/docs

# 4. Login
# Use Swagger UI to login with admin/admin123

# 5. Upload a test document
# Use the /api/documents/upload endpoint in Swagger
```

---

**Status:** ✅ Ready to Use  
**Last Updated:** February 22, 2026  
**Version:** 1.0.0

