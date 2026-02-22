# ✅ Mobile Upload: Order Number Auto-Save Feature

## 🎯 How It Works

When a **mobile app** uploads a document with `driver_user_id`, the system automatically:

1. **Finds the driver's active order** from `order_info` table
2. **Saves BOTH** values in the `documents` table:
   - `order_info_id` → Foreign key link to order
   - `order_number` → String value of the order number

This ensures the order number is always available even without joining tables.

---

## 📊 Flow Diagram

```
Mobile App Upload Request
    ↓
POST /api/documents/upload?driver_user_id=3
    ↓
System queries order_info table:
SELECT * FROM order_info 
WHERE driver_id = 3 
AND is_active = true
    ↓
Found: Order #ORD-112-2027
    ↓
Document saved with:
- order_info_id = 3 (FK link)
- order_number = "ORD-112-2027" (string)
    ↓
Response includes full order info
```

---

## 💾 Database Storage

### **documents Table Record:**

```sql
INSERT INTO documents (
    filename,
    original_filename,
    file_path,
    uploaded_by,
    order_info_id,     ← FK: Links to order_info.id = 3
    order_number       ← String: "ORD-112-2027"
) VALUES (
    'uuid-xxx.pdf',
    'invoice.pdf',
    'uploads/uuid-xxx.pdf',
    3,                 ← user_id of driver
    3,                 ← order_info.id
    'ORD-112-2027'     ← order_info.order_number
);
```

**Key Point:** The `order_number` column stores the actual order number string directly in the documents table, so you can:
- Query documents by order number without joins
- Display order number without loading relationships
- Search/filter by order number efficiently

---

## 🔌 API Example: Mobile Upload

### **Request:**

```bash
POST http://localhost:8000/api/documents/upload
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data

Query Parameters:
- driver_user_id: 3

Body:
- files: [invoice.pdf]
```

### **What Happens Internally:**

```python
# Step 1: System receives driver_user_id = 3
driver_user_id = 3

# Step 2: Find driver's active order
order = db.query(OrderInfo).filter(
    OrderInfo.driver_id == 3,
    OrderInfo.is_active == True
).first()
# Returns: order_number = "ORD-112-2027"

# Step 3: Save document with order info
document = Document(
    filename=unique_filename,
    original_filename=file.filename,
    file_path=file_path,
    uploaded_by=current_user.id,
    order_info_id=order.id,          # ← FK: 3
    order_number=order.order_number   # ← String: "ORD-112-2027"
)
db.add(document)
db.commit()
```

### **Response:**

```json
[
  {
    "document_id": 16,
    "filename": "uuid-xxx.pdf",
    "file_size": 189456,
    "message": "Uploaded Successfully",
    "order_number": "ORD-112-2027",        ← ✅ Order number saved
    "customer_code": "LLTP3",
    "bill_to_code": "HILR3",
    "driver_id": 3,
    "web_status": "Sent to Imaging",
    "mob_status": "Uploaded Successfully - Verification Pending",
    "processing_started": true
  }
]
```

---

## 📋 Complete Code Flow

### **Location:** `routers/documents.py` Line ~88-178

```python
# Mobile app scenario
elif driver_user_id:
    # Find driver's active order
    order = db.query(OrderInfo).filter(
        OrderInfo.driver_id == driver_user_id,
        OrderInfo.is_active == True
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"No active order found for driver {driver_user_id}"
        )

# ... file save logic ...

# Create document record with order linkage
document = Document(
    filename=unique_filename,
    original_filename=file.filename,
    file_path=file_path,
    file_size=file_size,
    file_type=file_ext.replace('.', ''),
    uploaded_by=current_user.id,
    order_info_id=order.id,                    # ← FK link
    order_number=order.order_number            # ← String value ✅
)

db.add(document)
db.commit()
```

**Line 177:** `order_number=order.order_number` ← This saves the order number!

---

## 🔍 Querying Documents by Order Number

### **Method 1: Direct Query (No Join Needed)**

```python
from models import Document

# Find all documents for a specific order
documents = db.query(Document).filter(
    Document.order_number == "ORD-112-2027"
).all()

print(f"Found {len(documents)} documents for order ORD-112-2027")
for doc in documents:
    print(f"  - {doc.original_filename}")
```

### **Method 2: Using Relationship**

```python
from models import OrderInfo

# Get order and its documents
order = db.query(OrderInfo).filter(
    OrderInfo.order_number == "ORD-112-2027"
).first()

print(f"Order: {order.order_number}")
print(f"Documents: {len(order.documents)}")
for doc in order.documents:
    print(f"  - {doc.original_filename}")
    print(f"    Saved order_number: {doc.order_number}")  # ← Available directly!
```

### **Method 3: API Query**

```bash
GET /api/documents?order_number=ORD-112-2027
Authorization: Bearer TOKEN
```

Returns all documents linked to that order.

---

## ✅ Verification Test

### **Test 1: Mobile Upload**

```python
import requests

# Login first to get token
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "sagar", "password": "your_password"}
)
token = login_response.json()["access_token"]

# Upload document with driver_user_id
headers = {"Authorization": f"Bearer {token}"}
files = {"files": open("test_document.pdf", "rb")}
params = {"driver_user_id": 3}

response = requests.post(
    "http://localhost:8000/api/documents/upload",
    headers=headers,
    files=files,
    params=params
)

result = response.json()[0]
print(f"✅ Document uploaded")
print(f"   Document ID: {result['document_id']}")
print(f"   Order Number: {result['order_number']}")  # ← Should show "ORD-112-2027"
print(f"   Driver ID: {result['driver_id']}")        # ← Should show 3
```

### **Test 2: Verify in Database**

```python
from database import SessionLocal
from models import Document

db = SessionLocal()

# Get the uploaded document
doc = db.query(Document).filter(Document.id == result['document_id']).first()

print(f"\n✅ Verification:")
print(f"   order_info_id (FK): {doc.order_info_id}")      # ← Should be 3
print(f"   order_number (String): {doc.order_number}")    # ← Should be "ORD-112-2027"
print(f"   uploaded_by: {doc.uploaded_by}")               # ← Should be 3 (driver's user_id)

# Access order via relationship
print(f"\n   Order Info (via FK):")
print(f"   - Order Number: {doc.order_info.order_number}")
print(f"   - Customer Code: {doc.order_info.customer_code}")
print(f"   - Driver ID: {doc.order_info.driver_id}")

db.close()
```

---

## 📊 Current System Status

Based on the integration test:

✅ **5 Active Orders with Drivers Assigned:**
- ORD-112-2025 → Driver ID: 1
- ORD-112-2026 → Driver ID: 2
- ORD-112-2027 → Driver ID: 3
- ORD-112-2028 → Driver ID: 4
- ORD-112-2029 → Driver ID: 5

✅ **Upload API Ready:**
- Desktop: Use `order_number` parameter
- Mobile: Use `driver_user_id` parameter

✅ **Order Number Auto-Save:**
- When mobile uploads with `driver_user_id`, system finds active order
- Saves `order_number` directly in documents table
- No need for joins to get order number

---

## 🎯 Summary

**Question:** When mobile uploads with `driver_user_id`, does the system save the order_number?

**Answer:** ✅ **YES!** 

**How:**
1. Mobile sends: `driver_user_id=3`
2. System queries: `order_info` table for driver's active order
3. Finds: `ORD-112-2027`
4. Saves in `documents` table:
   - `order_info_id = 3` (FK)
   - `order_number = "ORD-112-2027"` (string)

**Result:**
- Order number is stored directly in documents table
- Available without joins
- Returned in API response
- Can be queried efficiently

---

**Status:** ✅ **WORKING AS EXPECTED**

The code on line 177 of `routers/documents.py` already implements this:
```python
order_number=order.order_number  # Store for quick access
```

This line ensures that whether the upload comes from desktop (with order_number) or mobile (with driver_user_id), the order number is ALWAYS saved in the documents table! 🎉

