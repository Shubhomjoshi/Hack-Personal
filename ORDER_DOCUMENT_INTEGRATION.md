# ✅ Order Integration with Document Upload API

## 🎯 Implementation Summary

**Date:** February 22, 2026  
**Status:** ✅ Completed

---

## 📋 What Was Implemented

### **Problem:**
- Desktop app uploads with `order_number`
- Mobile app uploads with `driver_user_id` (driver's user ID)
- Need to link documents to orders automatically

### **Solution:**
- Added `order_info_id` foreign key to `documents` table
- Modified `/api/documents/upload` to accept **either** `order_number` OR `driver_user_id`
- System automatically finds the order and links the document

---

## 🔧 Database Changes

### **documents Table - New Column**

```sql
ALTER TABLE documents 
ADD COLUMN order_info_id INTEGER REFERENCES order_info(id);
```

**Column Details:**
- **Name:** `order_info_id`
- **Type:** Integer
- **Foreign Key:** References `order_info.id`
- **Nullable:** Yes
- **Indexed:** Yes

**Relationship:**
```python
# In Document model
order_info = relationship("OrderInfo", backref="documents")

# Usage:
document.order_info  # → OrderInfo object
order.documents      # → List of Document objects
```

---

## 🔌 API Changes

### **Endpoint:** `POST /api/documents/upload`

### **New Parameters:**

| Parameter | Type | Required | Source | Description |
|-----------|------|----------|--------|-------------|
| `order_number` | string | Either this OR driver_user_id | Desktop app | Order number from order_info table |
| `driver_user_id` | integer | Either this OR order_number | Mobile app | User ID of the driver |
| `files` | file(s) | Yes | Both | Document files to upload |
| `customer_id` | integer | No | Both | Customer ID (optional) |

**Validation Rules:**
1. ✅ **One is mandatory:** Must provide either `order_number` OR `driver_user_id`
2. ❌ **Not both:** Cannot provide both parameters at once
3. ✅ **Order must exist:** Order must be found in `order_info` table
4. ✅ **Order must be active:** Only `is_active = true` orders accepted
5. ✅ **Driver must have order:** If using `driver_user_id`, driver must have an active order

---

## 📊 API Usage Examples

### **Example 1: Desktop App Upload (with order_number)**

```bash
POST http://localhost:8000/api/documents/upload
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data

Parameters:
- files: [document.pdf]
- order_number: "ORD-112-2025"
```

**Response:**
```json
[
  {
    "document_id": 15,
    "filename": "uuid-xxx.pdf",
    "file_size": 245632,
    "message": "Uploaded Successfully",
    "order_number": "ORD-112-2025",
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

### **Example 2: Mobile App Upload (with driver_user_id)**

```bash
POST http://localhost:8000/api/documents/upload
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data

Parameters:
- files: [document.pdf]
- driver_user_id: 3
```

**System Logic:**
1. Receives `driver_user_id = 3`
2. Queries: `SELECT * FROM order_info WHERE driver_id = 3 AND is_active = true`
3. Finds order: `ORD-112-2025`
4. Links document to this order

**Response:**
```json
[
  {
    "document_id": 16,
    "filename": "uuid-yyy.pdf",
    "file_size": 189456,
    "message": "Uploaded Successfully",
    "order_number": "ORD-112-2025",
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

### **Example 3: Multiple Files Upload**

```bash
POST http://localhost:8000/api/documents/upload
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data

Parameters:
- files: [document1.pdf, document2.jpg, document3.png]
- order_number: "ORD-112-2026"
```

**Response:** Returns array with results for all 3 files

---

## ❌ Error Scenarios

### **Error 1: Neither parameter provided**

```bash
POST /api/documents/upload
- files: [document.pdf]
# Missing both order_number and driver_user_id
```

**Response (400 Bad Request):**
```json
{
  "detail": "Either 'order_number' or 'driver_user_id' must be provided"
}
```

---

### **Error 2: Both parameters provided**

```bash
POST /api/documents/upload
- files: [document.pdf]
- order_number: "ORD-112-2025"
- driver_user_id: 3
```

**Response (400 Bad Request):**
```json
{
  "detail": "Please provide only 'order_number' OR 'driver_user_id', not both"
}
```

---

### **Error 3: Order not found**

```bash
POST /api/documents/upload
- files: [document.pdf]
- order_number: "ORD-999-9999"  # Does not exist
```

**Response (404 Not Found):**
```json
{
  "detail": "Active order with number 'ORD-999-9999' not found"
}
```

---

### **Error 4: Driver has no active order**

```bash
POST /api/documents/upload
- files: [document.pdf]
- driver_user_id: 99  # Driver exists but has no active orders
```

**Response (404 Not Found):**
```json
{
  "detail": "No active order found for driver with user ID 99"
}
```

---

## 🔄 Processing Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  DOCUMENT UPLOAD FLOW                        │
└─────────────────────────────────────────────────────────────┘

Step 1: Receive Upload Request
   ├─ Desktop: order_number = "ORD-112-2025"
   └─ Mobile:  driver_user_id = 3

Step 2: Validate Input
   ├─ Check: One parameter provided? ✅
   ├─ Check: Not both parameters? ✅
   └─ Continue...

Step 3: Find Order
   ├─ IF order_number:
   │    └─ SELECT * FROM order_info 
   │       WHERE order_number = 'ORD-112-2025' 
   │       AND is_active = true
   │
   └─ IF driver_user_id:
        └─ SELECT * FROM order_info 
           WHERE driver_id = 3 
           AND is_active = true

Step 4: Validate Order Found
   ├─ IF not found → Return 404 Error
   └─ IF found → Continue...

Step 5: Save File to Disk
   └─ uploads/uuid-xxx.pdf

Step 6: Create Document Record
   INSERT INTO documents (
      filename,
      original_filename,
      file_path,
      uploaded_by,
      order_info_id,  ← ✅ Link to order
      order_number    ← ✅ Store for quick access
   )

Step 7: Return Response with Order Info
   {
      "document_id": 15,
      "order_number": "ORD-112-2025",
      "customer_code": "LLTP1",
      "bill_to_code": "HILR1",
      "driver_id": 3,
      ...
   }

Step 8: Background Processing Starts
   └─ OCR → Classification → Validation
```

---

## 🔗 Database Relationships

```
users
  └─ id (PK)
      └─ order_info.driver_id (FK) ───┐
                                      │
order_info                            │
  └─ id (PK)                          │
      ├─ driver_id (FK) ──────────────┘
      ├─ order_number (Unique)
      ├─ customer_code
      └─ bill_to_code
          │
          │ (One-to-Many)
          ↓
      documents.order_info_id (FK)
      
documents
  └─ id (PK)
      ├─ order_info_id (FK) → order_info.id
      ├─ order_number (String, for quick access)
      ├─ uploaded_by (FK) → users.id
      └─ ...other columns
```

---

## 🚀 How to Apply Changes

### **Option 1: Run Migration (If documents table exists)**

```bash
python migrate_add_order_link.py
```

This will:
1. Add `order_info_id` column to `documents` table
2. Link existing documents to orders (where order_number matches)
3. Verify the change

---

### **Option 2: Fresh Installation**

```bash
# Delete existing database
del app.db

# Create all tables with new schema
python create_order_table_now.py

# Start server
python main.py
```

---

### **Option 3: Manual SQL**

```sql
-- Add column
ALTER TABLE documents 
ADD COLUMN order_info_id INTEGER REFERENCES order_info(id);

-- Create index
CREATE INDEX ix_documents_order_info_id ON documents(order_info_id);

-- Link existing documents (optional)
UPDATE documents 
SET order_info_id = (
    SELECT id FROM order_info 
    WHERE order_info.order_number = documents.order_number
)
WHERE order_number IS NOT NULL;
```

---

## 🧪 Testing Guide

### **Test 1: Desktop Upload**

```python
import requests

url = "http://localhost:8000/api/documents/upload"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"files": open("test.pdf", "rb")}
params = {"order_number": "ORD-112-2025"}

response = requests.post(url, headers=headers, files=files, params=params)
print(response.json())

# Expected: Success with order info in response
```

---

### **Test 2: Mobile Upload**

```python
import requests

url = "http://localhost:8000/api/documents/upload"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"files": open("test.pdf", "rb")}
params = {"driver_user_id": 3}

response = requests.post(url, headers=headers, files=files, params=params)
print(response.json())

# Expected: Success with driver's order info in response
```

---

### **Test 3: Error Handling**

```python
# Test missing parameters
response = requests.post(url, headers=headers, files=files)
# Expected: 400 - "Either order_number or driver_user_id must be provided"

# Test both parameters
params = {"order_number": "ORD-112-2025", "driver_user_id": 3}
response = requests.post(url, headers=headers, files=files, params=params)
# Expected: 400 - "Please provide only order_number OR driver_user_id, not both"

# Test invalid order
params = {"order_number": "INVALID-ORDER"}
response = requests.post(url, headers=headers, files=files, params=params)
# Expected: 404 - "Active order with number 'INVALID-ORDER' not found"
```

---

## 📊 Query Examples

### **Get all documents for an order:**

```python
from models import OrderInfo

order = db.query(OrderInfo).filter(
    OrderInfo.order_number == "ORD-112-2025"
).first()

print(f"Order: {order.order_number}")
print(f"Documents: {len(order.documents)}")
for doc in order.documents:
    print(f"  - {doc.original_filename} (ID: {doc.id})")
```

---

### **Get order info from a document:**

```python
from models import Document

document = db.query(Document).filter(Document.id == 15).first()

if document.order_info:
    print(f"Document linked to order: {document.order_info.order_number}")
    print(f"Customer: {document.order_info.customer_code}")
    print(f"Driver: {document.order_info.driver_id}")
else:
    print("Document not linked to any order")
```

---

### **Get all documents for a driver:**

```python
from models import User

driver = db.query(User).filter(User.id == 3).first()

# Get driver's orders
orders = driver.assigned_orders

print(f"Driver: {driver.username}")
print(f"Active Orders: {len([o for o in orders if o.is_active])}")

# Get all documents across all orders
all_docs = []
for order in orders:
    all_docs.extend(order.documents)

print(f"Total Documents: {len(all_docs)}")
```

---

## ✅ Summary

**What was implemented:**
✅ `order_info_id` foreign key in `documents` table  
✅ Modified upload API to accept `order_number` OR `driver_user_id`  
✅ Automatic order lookup and linking  
✅ Response includes full order information  
✅ Validation ensures only active orders accepted  
✅ Error handling for all edge cases  

**Benefits:**
✅ Desktop app: Direct order assignment  
✅ Mobile app: Automatic order detection via driver  
✅ Documents automatically linked to orders  
✅ Customer/billing info automatically associated  
✅ Complete audit trail (who uploaded, which order, when)  

---

**Status:** ✅ **IMPLEMENTED AND READY**  
**Next Step:** Run migration script and test both upload methods

