# ✅ GET Documents API - Order & Driver Filtering

## 🎯 Implementation Summary

**Endpoint:** `GET /api/documents/`

**New Feature:** Filter documents by order or driver, with automatic order lookup for mobile apps.

---

## 📊 How It Works

### **Desktop App Usage:**
```
GET /api/documents/?order_number=ORD-112-2025
```
Filters documents where `selected_order_number = "ORD-112-2025"`

### **Mobile App Usage:**
```
GET /api/documents/?driver_id=3
```
1. Finds driver's active order: `ORD-112-2027`
2. Filters documents where `selected_order_number = "ORD-112-2027"`

---

## 🔌 API Specification

### **Endpoint**
```
GET /api/documents/
```

### **Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `order_number` | string | No | Order number for filtering (Desktop app) |
| `driver_id` | integer | No | Driver's user ID (Mobile app) |
| `skip` | integer | No | Pagination offset (default: 0) |
| `limit` | integer | No | Page size (default: 100, max: 500) |
| `document_type` | string | No | Filter by document type |
| `validation_status` | string | No | Filter by validation status |

**Validation Rules:**
- ✅ Can provide `order_number` alone
- ✅ Can provide `driver_id` alone
- ✅ Can provide neither (returns all documents)
- ❌ Cannot provide both `order_number` AND `driver_id`

---

## 📋 Request Examples

### **Example 1: Desktop - Filter by Order Number**

```bash
GET http://localhost:8000/api/documents/?order_number=ORD-112-2025
Authorization: Bearer YOUR_JWT_TOKEN
```

**What Happens:**
1. API receives `order_number=ORD-112-2025`
2. Queries: `SELECT * FROM documents WHERE selected_order_number = 'ORD-112-2025'`
3. Returns all documents uploaded for this order

**Response:**
```json
{
  "total": 3,
  "documents": [
    {
      "id": 9,
      "filename": "uuid-xxx.pdf",
      "original_filename": "Commercial_Invoice.pdf",
      "selected_order_number": "ORD-112-2025",
      "order_number": "ORD-112-2025",
      "document_type": "Commercial Invoice",
      "validation_status": "Pass",
      "uploaded_by": 1,
      "created_at": "2026-02-22T10:00:00Z",
      ...
    },
    {
      "id": 12,
      "filename": "uuid-yyy.pdf",
      "original_filename": "BOL_Sample.pdf",
      "selected_order_number": "ORD-112-2025",
      ...
    },
    {
      "id": 13,
      "filename": "uuid-zzz.pdf",
      "original_filename": "Packing_List.pdf",
      "selected_order_number": "ORD-112-2025",
      ...
    }
  ]
}
```

---

### **Example 2: Mobile - Filter by Driver ID**

```bash
GET http://localhost:8000/api/documents/?driver_id=3
Authorization: Bearer YOUR_JWT_TOKEN
```

**What Happens:**
1. API receives `driver_id=3`
2. Looks up driver's order:
   ```sql
   SELECT * FROM order_info 
   WHERE driver_id = 3 AND is_active = true
   ```
   Result: `ORD-112-2027`
3. Queries documents:
   ```sql
   SELECT * FROM documents 
   WHERE selected_order_number = 'ORD-112-2027'
   ```
4. Returns documents for driver's active order

**Response:**
```json
{
  "total": 5,
  "documents": [
    {
      "id": 20,
      "filename": "uuid-aaa.pdf",
      "original_filename": "BOL.pdf",
      "selected_order_number": "ORD-112-2027",
      "document_type": "Bill of Lading",
      "uploaded_by": 3,
      ...
    },
    {
      "id": 21,
      "filename": "uuid-bbb.pdf",
      "original_filename": "Invoice.pdf",
      "selected_order_number": "ORD-112-2027",
      ...
    }
  ]
}
```

---

### **Example 3: Combined Filters**

```bash
GET http://localhost:8000/api/documents/?driver_id=3&document_type=Bill%20of%20Lading
Authorization: Bearer YOUR_JWT_TOKEN
```

**What Happens:**
1. Finds driver's order: `ORD-112-2027`
2. Filters by order AND document type
3. Returns only BOL documents for this driver's order

**Response:**
```json
{
  "total": 2,
  "documents": [
    {
      "id": 20,
      "document_type": "Bill of Lading",
      "selected_order_number": "ORD-112-2027",
      ...
    },
    {
      "id": 25,
      "document_type": "Bill of Lading",
      "selected_order_number": "ORD-112-2027",
      ...
    }
  ]
}
```

---

### **Example 4: Pagination**

```bash
GET http://localhost:8000/api/documents/?order_number=ORD-112-2025&skip=0&limit=10
Authorization: Bearer YOUR_JWT_TOKEN
```

Returns first 10 documents for order ORD-112-2025.

---

## ❌ Error Scenarios

### **Error 1: Both Parameters Provided**

```bash
GET /api/documents/?order_number=ORD-112-2025&driver_id=3
```

**Response (400 Bad Request):**
```json
{
  "detail": "Please provide only 'order_number' OR 'driver_id', not both"
}
```

---

### **Error 2: Driver Has No Active Order**

```bash
GET /api/documents/?driver_id=999
```

**Response (200 OK - Empty Result):**
```json
{
  "total": 0,
  "documents": []
}
```

**Note:** This is NOT an error - it just returns empty results if driver has no active order.

---

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  GET /api/documents/                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        │                                       │
   order_number?                          driver_id?
        │                                       │
        ↓                                       ↓
   Filter WHERE                          Lookup Order:
   selected_order_number                 SELECT * FROM order_info
   = order_number                        WHERE driver_id = ?
                                         AND is_active = true
                                              ↓
                                         Found order_number
                                              ↓
                                         Filter WHERE
                                         selected_order_number
                                         = found_order_number
        │                                       │
        └───────────────────┬───────────────────┘
                            ↓
                    Apply other filters:
                    - document_type
                    - validation_status
                    - user permissions
                            ↓
                    Apply pagination:
                    - skip
                    - limit
                            ↓
                    Return results
```

---

## 🔍 Implementation Details

### **Code Location:** `routers/documents.py` (Lines 228-303)

### **Key Logic:**

```python
# Validate exclusive parameters
if order_number and driver_id:
    raise HTTPException(400, "Provide only one parameter")

# Desktop: Direct filtering
if order_number:
    query = query.filter(Document.selected_order_number == order_number)

# Mobile: Lookup then filter
elif driver_id:
    driver_order = db.query(OrderInfo).filter(
        OrderInfo.driver_id == driver_id,
        OrderInfo.is_active == True
    ).first()
    
    if not driver_order:
        return {"total": 0, "documents": []}
    
    query = query.filter(Document.selected_order_number == driver_order.order_number)
```

---

## 📊 Database Queries

### **Desktop Query:**
```sql
SELECT * FROM documents
WHERE selected_order_number = 'ORD-112-2025'
ORDER BY created_at DESC
LIMIT 100 OFFSET 0;
```

### **Mobile Query (2 steps):**

**Step 1: Find Driver's Order**
```sql
SELECT * FROM order_info
WHERE driver_id = 3
  AND is_active = true
LIMIT 1;
-- Returns: order_number = 'ORD-112-2027'
```

**Step 2: Get Documents**
```sql
SELECT * FROM documents
WHERE selected_order_number = 'ORD-112-2027'
ORDER BY created_at DESC
LIMIT 100 OFFSET 0;
```

---

## 🧪 Testing Guide

### **Test 1: Desktop Filtering**

```python
import requests

# Login
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "test", "password": "password"}
)
token = login_response.json()["access_token"]

# Get documents for order
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/documents/",
    params={"order_number": "ORD-112-2025"},
    headers=headers
)

print(f"Found {response.json()['total']} documents")
```

---

### **Test 2: Mobile Filtering**

```python
# Get documents for driver
response = requests.get(
    "http://localhost:8000/api/documents/",
    params={"driver_id": 3},
    headers=headers
)

data = response.json()
print(f"Driver has {data['total']} documents")
for doc in data['documents']:
    print(f"  - {doc['original_filename']} (Order: {doc['selected_order_number']})")
```

---

### **Test 3: Error Validation**

```python
# Test both parameters (should fail)
response = requests.get(
    "http://localhost:8000/api/documents/",
    params={"order_number": "ORD-112-2025", "driver_id": 3},
    headers=headers
)

print(response.status_code)  # Should be 400
print(response.json()["detail"])  # Error message
```

---

## ✅ Features

**Desktop App:**
- ✅ Direct order number filtering
- ✅ Fast query (single table lookup)
- ✅ Works with copied/pasted order numbers

**Mobile App:**
- ✅ Automatic order detection via driver ID
- ✅ No need to know order number
- ✅ Always uses driver's current active order
- ✅ Graceful handling when driver has no order

**Both:**
- ✅ Filters by `selected_order_number` column
- ✅ Preserves `order_number` for OCR data
- ✅ Supports pagination
- ✅ Supports additional filters
- ✅ User permissions respected
- ✅ Validates parameter usage

---

## 🎯 Use Cases

### **Use Case 1: Desktop - View All Documents for Order**
```
Office staff enters order number → System shows all related documents
```

### **Use Case 2: Mobile - Driver Views Their Documents**
```
Driver opens app → System finds their order → Shows only their documents
```

### **Use Case 3: Desktop - Search Within Order**
```
Search order ORD-112-2025 + Type = "Invoice" → Shows only invoices for that order
```

### **Use Case 4: Mobile - Driver Views BOLs Only**
```
driver_id=3 + document_type="Bill of Lading" → Shows driver's BOLs only
```

---

## 📖 Summary

**What Was Implemented:**
- ✅ Added `order_number` parameter to GET documents API
- ✅ Added `driver_id` parameter to GET documents API
- ✅ Desktop: Filters by `selected_order_number = order_number`
- ✅ Mobile: Looks up driver's order, then filters by `selected_order_number`
- ✅ Validates exclusive parameter usage
- ✅ Returns empty result if driver has no active order
- ✅ Preserves existing filters and pagination
- ✅ Maintains user permission checks

**Files Modified:**
- ✅ `routers/documents.py` - Updated GET endpoint

**Files Created:**
- ✅ `test_get_documents_filtering.py` - Test script
- ✅ `GET_DOCUMENTS_ORDER_FILTERING.md` - This documentation

---

**Status:** ✅ **FULLY IMPLEMENTED AND TESTED**

The GET documents API now supports filtering by order number (desktop) and driver ID (mobile), using the `selected_order_number` column to maintain separation from OCR-extracted order numbers.

