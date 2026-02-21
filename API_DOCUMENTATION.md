# 📚 Document Intelligence API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints (except authentication endpoints) require JWT authentication.

### Headers
```
Authorization: Bearer <your_access_token>
```

---

## 🔐 Authentication Endpoints

### 1. Register User
**POST** `/api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass@123"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*(),.?":{}|<>_-+=[]\\\/~`)

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-02-18T10:00:00"
}
```

**Error Responses:**

`400 Bad Request` - Email or username already exists:
```json
{
  "detail": "Email already registered"
}
```

`422 Unprocessable Entity` - Invalid password:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Password must contain at least one uppercase letter"
    }
  ]
}
```

---

### 2. Login
**POST** `/api/auth/login`

Login and receive access token.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "secretpass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "johndoe"
}
```

---

### 3. Get Current User
**GET** `/api/auth/me`

Get current authenticated user information.

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false
}
```

---

## 📄 Document Endpoints

### 1. Upload Document
**POST** `/api/documents/upload`

Upload a document for processing.

**Request:** `multipart/form-data`
- `file`: File (PDF, JPEG, PNG)
- `customer_id`: Integer (optional)

**Response:** `201 Created`
```json
{
  "document_id": 1,
  "filename": "abc123.pdf",
  "file_size": 524288,
  "message": "Document uploaded successfully. Processing started in background.",
  "processing_started": true
}
```

---

### 2. Upload Multiple Documents
**POST** `/api/documents/upload-multiple`

Upload multiple documents at once.

**Request:** `multipart/form-data`
- `files`: List of files
- `customer_id`: Integer (optional)

**Response:** `200 OK`
```json
[
  {
    "document_id": 1,
    "filename": "doc1.pdf",
    "file_size": 524288,
    "message": "Uploaded successfully",
    "processing_started": true
  },
  {
    "document_id": 2,
    "filename": "doc2.jpg",
    "file_size": 256000,
    "message": "Uploaded successfully",
    "processing_started": true
  }
]
```

---

### 3. Get Documents List
**GET** `/api/documents/`

Get list of documents with pagination and filtering.

**Query Parameters:**
- `skip`: Integer (default: 0)
- `limit`: Integer (default: 100, max: 500)
- `document_type`: String (optional) - e.g., "Bill of Lading"
- `validation_status`: String (optional) - "Pass", "Fail", "Needs Review", "Pending"

**Response:** `200 OK`
```json
{
  "total": 10,
  "documents": [
    {
      "id": 1,
      "filename": "abc123.pdf",
      "original_filename": "invoice.pdf",
      "file_type": "pdf",
      "file_size": 524288,
      "document_type": "Commercial Invoice",
      "classification_confidence": 0.95,
      "readability_status": "Clear",
      "quality_score": 85.5,
      "is_blurry": false,
      "is_skewed": false,
      "signature_count": 2,
      "has_signature": true,
      "order_number": "ORD-12345",
      "load_number": "LOAD-789",
      "invoice_number": "INV-456",
      "document_date": "2026-02-15",
      "validation_status": "Pass",
      "is_processed": true,
      "processing_error": null,
      "created_at": "2026-02-18T10:00:00"
    }
  ]
}
```

---

### 4. Get Document Details
**GET** `/api/documents/{document_id}`

Get details of a specific document.

**Response:** `200 OK`
```json
{
  "id": 1,
  "filename": "abc123.pdf",
  "original_filename": "invoice.pdf",
  "document_type": "Commercial Invoice",
  "classification_confidence": 0.95,
  "readability_status": "Clear",
  "quality_score": 85.5,
  "signature_count": 2,
  "has_signature": true,
  "order_number": "ORD-12345",
  "load_number": "LOAD-789",
  "validation_status": "Pass",
  "is_processed": true,
  "created_at": "2026-02-18T10:00:00"
}
```

---

### 5. Reprocess Document
**POST** `/api/documents/{document_id}/reprocess`

Reprocess a document (useful if processing failed).

**Response:** `200 OK`
```json
{
  "message": "Document 1 is being reprocessed",
  "success": true
}
```

---

### 6. Delete Document
**DELETE** `/api/documents/{document_id}`

Delete a document and its associated file.

**Response:** `200 OK`
```json
{
  "message": "Document 1 deleted successfully",
  "success": true
}
```

---

### 7. Get Document Text
**GET** `/api/documents/{document_id}/text`

Get extracted OCR text from a document.

**Response:** `200 OK`
```json
{
  "document_id": 1,
  "filename": "invoice.pdf",
  "text": "COMMERCIAL INVOICE\nInvoice Number: INV-456\nOrder Number: ORD-12345\n...",
  "is_processed": true
}
```

---

## ✅ Validation Rules Endpoints

### 1. Create Validation Rule
**POST** `/api/validation-rules/`

Create a new validation rule (Admin only).

**Request Body:**
```json
{
  "rule_name": "BOL Signature Requirement",
  "rule_description": "Bill of Lading must contain two signatures",
  "document_type": "Bill of Lading",
  "requires_signature": true,
  "minimum_signatures": 2,
  "requires_order_number": true,
  "requires_load_number": true,
  "customer_id": null
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "rule_name": "BOL Signature Requirement",
  "rule_description": "Bill of Lading must contain two signatures",
  "document_type": "Bill of Lading",
  "requires_signature": true,
  "minimum_signatures": 2,
  "requires_order_number": true,
  "requires_load_number": true,
  "customer_id": null,
  "is_active": true,
  "created_at": "2026-02-18T10:00:00"
}
```

---

### 2. Get Validation Rules
**GET** `/api/validation-rules/`

Get list of validation rules.

**Query Parameters:**
- `document_type`: String (optional)
- `customer_id`: Integer (optional)
- `is_active`: Boolean (optional)
- `skip`: Integer (default: 0)
- `limit`: Integer (default: 100)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "rule_name": "BOL Signature Requirement",
    "document_type": "Bill of Lading",
    "requires_signature": true,
    "minimum_signatures": 2,
    "is_active": true
  }
]
```

---

### 3. Initialize Default Rules
**POST** `/api/validation-rules/initialize-defaults`

Create default validation rules for all document types (Admin only).

**Response:** `200 OK`
```json
{
  "message": "Default validation rules created successfully",
  "success": true
}
```

---

## 📊 Analytics Endpoints

### 1. Get Statistics
**GET** `/api/analytics/statistics`

Get overall document processing statistics.

**Response:** `200 OK`
```json
{
  "total_documents": 100,
  "by_type": {
    "Bill of Lading": 30,
    "Proof of Delivery": 25,
    "Commercial Invoice": 20,
    "Freight Invoice": 15,
    "Lumper Receipt": 10
  },
  "by_status": {
    "Pass": 70,
    "Fail": 10,
    "Needs Review": 15,
    "Pending": 5
  },
  "average_quality_score": 78.5,
  "total_with_signatures": 65,
  "validation_pass_rate": 70.0
}
```

---

### 2. Get Quality Distribution
**GET** `/api/analytics/quality-distribution`

Get distribution of document quality scores.

**Response:** `200 OK`
```json
{
  "excellent_80_100": 45,
  "good_60_79": 30,
  "fair_40_59": 15,
  "poor_0_39": 10
}
```

---

### 3. Get Signature Statistics
**GET** `/api/analytics/signature-statistics`

Get signature detection statistics.

**Response:** `200 OK`
```json
{
  "total_processed": 100,
  "with_signatures": 65,
  "without_signatures": 35,
  "average_signature_count": 1.8,
  "percentage_with_signatures": 65.0
}
```

---

### 4. Get Processing Summary
**GET** `/api/analytics/processing-summary`

Get summary of document processing status.

**Response:** `200 OK`
```json
{
  "total_documents": 100,
  "processed": 95,
  "pending": 5,
  "with_errors": 2,
  "processing_completion_rate": 95.0
}
```

---

### 5. Get Validation Failures
**GET** `/api/analytics/validation-failures`

Get recent documents that failed validation.

**Query Parameters:**
- `limit`: Integer (default: 10, max: 100)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "filename": "bol_missing_signature.pdf",
    "document_type": "Bill of Lading",
    "validation_status": "Fail",
    "validation_result": {
      "status": "Fail",
      "failed_rules": [
        "BOL Signature Requirement: Document requires 2 signatures, found 1"
      ]
    },
    "created_at": "2026-02-18T10:00:00"
  }
]
```

---

### 6. Get Document Types Breakdown
**GET** `/api/analytics/document-types-breakdown`

Get detailed breakdown of document types with validation statistics.

**Response:** `200 OK`
```json
[
  {
    "document_type": "Bill of Lading",
    "total": 30,
    "passed": 25,
    "failed": 3,
    "needs_review": 2,
    "pass_rate": 83.33,
    "average_quality_score": 82.5
  }
]
```

---

## 📋 Document Types Supported

1. **Bill of Lading** - Contract of carriage, receipt of goods
2. **Proof of Delivery** - Signed confirmation of delivery
3. **Packing List** - Itemized contents, weights, dimensions
4. **Commercial Invoice** - Product details, value, payment terms
5. **Hazmat Document** - Required for dangerous goods
6. **Lumper Receipt** - Proof of payment for loading/unloading
7. **Trip Sheet** - Miles driven, fuel stops, state crossings
8. **Freight Invoice** - Carrier invoices for transportation

---

## 🔍 Processing Pipeline

When a document is uploaded, it goes through these steps:

1. **OCR** - Extract text using Tesseract OCR
2. **Classification** - Identify document type using keyword matching
3. **Quality Assessment** - Check blur, skew, brightness
4. **Signature Detection** - Detect and count signatures
5. **Metadata Extraction** - Extract order numbers, dates, etc.
6. **Validation** - Apply customer-specific rules

---

## 📝 Example Workflow

### Step 1: Register and Login
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"User@123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"User@123"}'
```

### Step 2: Upload Document
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@/path/to/document.pdf"
```

### Step 3: Check Processing Status
```bash
curl -X GET http://localhost:8000/api/documents/1 \
  -H "Authorization: Bearer <your_token>"
```

### Step 4: View Analytics
```bash
curl -X GET http://localhost:8000/api/analytics/statistics \
  -H "Authorization: Bearer <your_token>"
```

---

## ⚠️ Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP Status Codes:
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

---

## 🚀 Interactive Documentation

Visit these URLs when the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide interactive API testing interfaces!

