# 📘 Quick Reference Guide - Document Intelligence System

## 🚀 Quick Start

### **Start Server:**
```powershell
cd Backend
.venv\Scripts\activate
python main.py
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## 📊 Key Endpoints

### **Authentication:**
```bash
# Register
POST /api/auth/register
Body: {"username": "user", "email": "user@mail.com", "password": "pass"}

# Login
POST /api/auth/login
Body: {"username": "user", "password": "pass"}
```

### **Upload (Desktop):**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "files=@doc.pdf" \
  -F "order_number=ORD-112-2025"
```

### **Upload (Mobile):**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "files=@photo.jpg" \
  -F "driver_user_id=3"
```

### **List Documents:**
```bash
# Desktop
GET /api/documents/?order_number=ORD-112-2025

# Mobile
GET /api/documents/?driver_user_id=3
```

---

## 🗄️ Database Tables

```
users          → User accounts
order_info     → Order/load information
documents      → Document metadata + results
classification_results → Classification history
doc_type_samples → Sample documents
```

---

## 🔄 Processing Flow

```
Upload (< 1s)
  → Quality Check (< 1s)
  → OCR Extraction (2-4s)
  → Classification (< 1s)
  → Signature Detection (< 1s, if BOL)
  → Metadata Extraction (< 0.5s)
  → Field Extraction (< 0.5s)
  → Validation (< 0.5s)
  → Done! ✅
```

**Total:** 4-7 seconds

---

## 🤖 AI Components

**1 AI Agent:**
- DocumentProcessingAgent (makes decisions)

**3 AI Services:**
- GeminiDocumentAnalyzer (extraction)
- GeminiDocumentClassifier (classification)
- Sample-Based Classifier (multi-signal)

---

## 📝 Document Types

1. Bill of Lading (BOL)
2. Proof of Delivery (POD)
3. Commercial Invoice
4. Packing List
5. Hazmat Document
6. Lumper Receipt
7. Trip Sheet
8. Freight Invoice

---

## ✅ Validation Status

- **Pass** - All rules passed
- **Pass with Warnings** - Soft warnings only
- **Fail** - Hard rule failures
- **Needs Review** - Quality too low or uncertain
- **Pending** - Not yet processed

---

## 🔧 Common Commands

```powershell
# Initialize database
python init_database.py

# Add sample orders
python add_order_data.py

# Check system
python check_system.py

# Test upload
python test_order_document_integration.py

# Fix hardcoded values
python fix_hardcoded_order_numbers.py
```

---

## 🐛 Troubleshooting

**Server won't start:**
```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

**Gemini errors:**
- Check API key: `$env:GEMINI_API_KEY`
- Has automatic retry (3 attempts)
- Falls back to EasyOCR

**Order not found:**
```powershell
python add_order_data.py
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Upload response | ~200ms |
| Processing time | 4-7s |
| Classification accuracy | 92% |
| Throughput | 720 docs/hour |

---

## 🔐 Environment Variables

```bash
GEMINI_API_KEY=AIzaSy...
SECRET_KEY=random-secret-key
ENVIRONMENT=production
```

---

## 📖 Full Documentation

**COMPLETE_APPLICATION_DOCUMENTATION.md** - 1000+ lines covering:
- Introduction & Problem Statement
- High-Level Architecture
- Low-Level Design
- System Components
- Data Flow & Execution
- API Endpoints
- Database Schema
- AI Components
- Processing Pipeline
- Deployment
- Testing & Validation
- Troubleshooting

---

**Status:** ✅ Complete Application Documentation Available!

