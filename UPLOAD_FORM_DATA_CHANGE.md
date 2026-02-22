# ✅ Upload API - Form Data Parameters

## 🎯 **Change Implemented**

Modified `/api/documents/upload` endpoint to accept `order_number` and `driver_user_id` from **Form data (request body)** instead of Query parameters.

---

## 📝 **Changes Made**

### **File:** `routers/documents.py`

#### **1. Added Form import**
```python
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Query, Form
```

#### **2. Changed Parameters from Query to Form**

**Before:**
```python
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    order_number: Optional[str] = Query(None, description="Order number (Desktop app)"),
    driver_user_id: Optional[int] = Query(None, description="Driver user ID (Mobile app)"),
    customer_id: Optional[int] = None,
    ...
)
```

**After:**
```python
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    order_number: Optional[str] = Form(None, description="Order number (Desktop app)"),
    driver_user_id: Optional[int] = Form(None, description="Driver user ID (Mobile app)"),
    customer_id: Optional[int] = Form(None),
    ...
)
```

---

## 🔌 **API Usage**

### **Before (Query Parameters):**
```bash
POST /api/documents/upload?order_number=ORD-112-2025
Content-Type: multipart/form-data

files: [file1.pdf, file2.pdf]
```

### **After (Form Data):**
```bash
POST /api/documents/upload
Content-Type: multipart/form-data

files: [file1.pdf, file2.pdf]
order_number: ORD-112-2025
```

---

## 📊 **Request Examples**

### **Desktop App Upload:**

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf" \
  -F "order_number=ORD-112-2025"
```

**Using JavaScript Fetch:**
```javascript
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);
formData.append('order_number', 'ORD-112-2025');

fetch('/api/documents/upload', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
});
```

**Using Python Requests:**
```python
import requests

files = [
    ('files', open('document1.pdf', 'rb')),
    ('files', open('document2.pdf', 'rb'))
]

data = {
    'order_number': 'ORD-112-2025'
}

response = requests.post(
    'http://localhost:8000/api/documents/upload',
    headers={'Authorization': f'Bearer {token}'},
    files=files,
    data=data
)
```

---

### **Mobile App Upload:**

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@photo.jpg" \
  -F "driver_user_id=3"
```

**Using JavaScript Fetch:**
```javascript
const formData = new FormData();
formData.append('files', photoFile);
formData.append('driver_user_id', '3');

fetch('/api/documents/upload', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
});
```

**Using Python Requests:**
```python
import requests

files = [('files', open('photo.jpg', 'rb'))]
data = {'driver_user_id': 3}

response = requests.post(
    'http://localhost:8000/api/documents/upload',
    headers={'Authorization': f'Bearer {token}'},
    files=files,
    data=data
)
```

---

## 🎯 **Why Form Data?**

### **Advantages:**

✅ **Better for File Uploads**
- All data in one place (files + metadata)
- Cleaner request structure

✅ **Mobile-Friendly**
- Easier to construct FormData in mobile apps
- Native support in most HTTP libraries

✅ **Consistent Structure**
- Files and parameters in same multipart body
- No mixing of query params and form data

✅ **Better Security**
- Sensitive data not in URL
- Not logged in access logs
- Not visible in browser history

---

## 📋 **Validation**

The endpoint validates:

1. **Required:** Either `order_number` OR `driver_user_id` (not both)
2. **Optional:** `customer_id`
3. **Required:** At least one file in `files`

**Validation Errors:**

```json
// No identifier provided
{
  "detail": "Either 'order_number' or 'driver_user_id' must be provided"
}

// Both identifiers provided
{
  "detail": "Please provide only 'order_number' OR 'driver_user_id', not both"
}

// Order not found
{
  "detail": "Active order with number 'ORD-XXX' not found"
}

// No active order for driver
{
  "detail": "No active order found for driver with user ID 3"
}
```

---

## 🔄 **Complete Flow**

```
Client prepares FormData
    ├─ files: [file1, file2, ...]
    ├─ order_number: "ORD-112-2025" (Desktop)
    └─ driver_user_id: 3 (Mobile)
        ↓
POST /api/documents/upload
    ↓
FastAPI receives FormData
    ↓
Validates parameters
    ↓
Finds order in database
    ↓
Saves files to disk
    ↓
Creates Document records
    ↓
Starts background processing
    ↓
Returns immediate response
```

---

## 📊 **Response Format**

Same as before - returns list of upload results:

```json
[
  {
    "document_id": 16,
    "filename": "uuid-xxx.pdf",
    "file_size": 123456,
    "message": "Uploaded Successfully",
    "selected_order_number": "ORD-112-2025",
    "customer_code": "LLTP1",
    "bill_to_code": "HILR1",
    "driver_id": 3,
    "web_status": "Sent to Imaging",
    "mob_status": "Uploaded Successfully - Verification Pending",
    "processing_started": true
  }
]
```

---

## ✅ **Testing**

### **Test 1: Desktop Upload with Order Number**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@test.pdf" \
  -F "order_number=ORD-112-2025"
```

Expected: ✅ Success

---

### **Test 2: Mobile Upload with Driver ID**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@photo.jpg" \
  -F "driver_user_id=3"
```

Expected: ✅ Success

---

### **Test 3: Multiple Files**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@doc3.jpg" \
  -F "order_number=ORD-112-2025"
```

Expected: ✅ Success (3 documents uploaded)

---

### **Test 4: Error - Both Parameters**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@test.pdf" \
  -F "order_number=ORD-112-2025" \
  -F "driver_user_id=3"
```

Expected: ❌ 400 Error - "Please provide only 'order_number' OR 'driver_user_id', not both"

---

### **Test 5: Error - No Parameters**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@test.pdf"
```

Expected: ❌ 400 Error - "Either 'order_number' or 'driver_user_id' must be provided"

---

## 🔍 **Debugging**

If upload fails, check:

1. **Content-Type header:** Should be `multipart/form-data` (usually set automatically)
2. **Form field names:** Must be exactly `files`, `order_number`, `driver_user_id`
3. **File field:** Use `files` (plural) even for single file
4. **Authorization:** Bearer token must be valid
5. **Order exists:** Order must be active in `order_info` table

---

## 📁 **Files Modified**

```
routers/
  └─ documents.py ........... Changed Query to Form parameters
```

---

## 🎯 **Summary**

**Change:** `order_number` and `driver_user_id` now come from **Form data** (request body) instead of Query parameters.

**Impact:**
- ✅ Better structure for file uploads
- ✅ More secure (not in URL)
- ✅ Mobile-friendly
- ✅ Consistent with multipart/form-data standard

**Compatibility:**
- ⚠️ **Breaking change** - clients must update from query params to form data
- ✅ All other functionality remains the same

---

**Status:** ✅ **IMPLEMENTED AND READY**

The upload endpoint now accepts all parameters from Form data in the request body!

