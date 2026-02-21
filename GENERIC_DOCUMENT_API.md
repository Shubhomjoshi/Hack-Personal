# 🎯 Generic Document API - Implementation Complete!

## ✅ What Was Built

**ONE API endpoint that works for ALL 8 document types!**

No separate endpoints needed - frontend calls same API regardless of doc type.

---

## 📋 API Endpoints

### **1. Get Document Detail (Single Doc)**

```http
GET /api/documents/{document_id}/detail
Authorization: Bearer <token>
```

**Returns everything for rendering:**
- ✅ Common fields (quality, signatures, status)
- ✅ Document-type specific fields (66 fields across 8 types)
- ✅ Display configuration (tells frontend what to show)

**Response Example:**

```json
{
  "doc_id": 123,
  "doc_type": "Bill of Lading",
  "confidence": 0.94,
  "upload_date": "2026-02-15T14:32:00",
  "quality_score": 87,
  "quality_status": "Clear",
  "signature_count": 2,
  "signature_present": true,
  "validation_status": "Pass",
  "needs_review": false,
  "file_path": "uploads/abc-123.pdf",
  "filename": "bol_document.pdf",
  
  "metadata": {
    "order_number": "ORD-9981",
    "invoice_number": null,
    "document_date": "14/02/2026",
    "client_name": "ABC Manufacturing",
    
    // All doc-type specific fields
    "bol_number": "BOL-78421",
    "shipper": "ABC Manufacturing",
    "consignee": "XYZ Distribution",
    "origin": "Chicago, IL",
    "destination": "Dallas, TX",
    "carrier": "FastFreight Inc",
    "total_weight": "4500 lbs",
    "total_pieces": "12",
    "freight_terms": "Prepaid",
    
    // Extraction quality
    "_extraction_score": 0.91,
    "_filled_fields": 10,
    "_total_fields": 11
  },
  
  // Frontend uses this to render!
  "display_fields": [
    {
      "key": "bol_number",
      "label": "BOL Number",
      "icon": "📋",
      "highlight": true,
      "value": "BOL-78421",
      "empty": false
    },
    {
      "key": "order_number",
      "label": "Order / Load No",
      "icon": "🔢",
      "highlight": true,
      "value": "ORD-9981",
      "empty": false
    },
    {
      "key": "shipper",
      "label": "Shipper",
      "icon": "📦",
      "highlight": false,
      "value": "ABC Manufacturing",
      "empty": false
    },
    {
      "key": "carrier",
      "label": "Carrier",
      "icon": "🚛",
      "highlight": false,
      "value": "FastFreight Inc",
      "empty": false
    }
    // ... all other fields
  ],
  
  "extraction_quality": {
    "is_complete": true,
    "extraction_score": 0.91,
    "status": "complete"
  }
}
```

---

### **2. List Documents (Paginated)**

```http
GET /api/documents/list?page=1&limit=20&doc_type=Bill%20of%20Lading&status=Pass
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20, max: 100)
- `doc_type` (optional): "Bill of Lading", "Proof of Delivery", etc.
- `status` (optional): "Pass", "Fail", "Needs Review", "Pending"

**Response Example:**

```json
{
  "page": 1,
  "limit": 20,
  "total": 156,
  "total_pages": 8,
  "documents": [
    {
      "doc_id": 123,
      "doc_type": "Bill of Lading",
      "primary_id": "BOL-78421",  // Main identifier for this doc type
      "upload_date": "2026-02-15T14:32:00",
      "quality_score": 87,
      "signature_count": 2,
      "status": "Pass",
      "needs_review": false,
      "confidence": 0.94,
      "filename": "bol_document.pdf"
    },
    {
      "doc_id": 124,
      "doc_type": "Commercial Invoice",
      "primary_id": "INV-2024-00521",  // Different identifier for Invoice
      "upload_date": "2026-02-15T15:12:00",
      "quality_score": 92,
      "signature_count": 1,
      "status": "Pass",
      "needs_review": false,
      "confidence": 0.89,
      "filename": "invoice.pdf"
    }
    // ... more documents
  ]
}
```

---

### **3. Document Statistics**

```http
GET /api/documents/stats
Authorization: Bearer <token>
```

**Response Example:**

```json
{
  "total_documents": 156,
  "by_doc_type": {
    "Bill of Lading": 48,
    "Proof of Delivery": 35,
    "Commercial Invoice": 28,
    "Freight Invoice": 22,
    "Packing List": 12,
    "Trip Sheet": 8,
    "Lumper Receipt": 3
  },
  "by_status": {
    "Pass": 142,
    "Needs Review": 10,
    "Fail": 4
  },
  "recent_uploads": 23,
  "average_quality_score": 84.5
}
```

---

## 🎨 Frontend Implementation

### **React Component (Works for ALL Doc Types!)**

```jsx
import React, { useEffect, useState } from 'react';

function DocumentDetail({ docId }) {
  const [doc, setDoc] = useState(null);

  useEffect(() => {
    fetch(`/api/documents/${docId}/detail`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setDoc(data));
  }, [docId]);

  if (!doc) return <div>Loading...</div>;

  return (
    <div className="document-detail">
      {/* Common Header - same for ALL docs */}
      <div className="doc-header">
        <h2>{doc.doc_type}</h2>
        <span className={`status-${doc.validation_status}`}>
          {doc.validation_status}
        </span>
      </div>

      {/* Common Info - same for ALL docs */}
      <div className="doc-info">
        <div>Quality: {doc.quality_score}%</div>
        <div>Signatures: {doc.signature_count}</div>
        <div>Confidence: {(doc.confidence * 100).toFixed(0)}%</div>
        <div>Uploaded: {new Date(doc.upload_date).toLocaleDateString()}</div>
      </div>

      {/* Doc-type Specific Fields - dynamic! */}
      <div className="doc-fields">
        {doc.display_fields.map(field => (
          !field.empty && (
            <div 
              key={field.key}
              className={field.highlight ? "field-highlight" : "field-normal"}
            >
              <label>
                {field.icon} {field.label}
              </label>
              <span>{field.value}</span>
            </div>
          )
        ))}
      </div>

      {/* Extraction Quality */}
      {!doc.extraction_quality.is_complete && (
        <div className="warning">
          ⚠️ Document incomplete: 
          {(doc.extraction_quality.extraction_score * 100).toFixed(0)}% 
          of fields extracted
        </div>
      )}
    </div>
  );
}
```

**Key Point**: Same component renders Bill of Lading, Invoice, POD, everything! The `display_fields` array tells it what to show.

---

### **Document List Component**

```jsx
function DocumentList() {
  const [docs, setDocs] = useState([]);
  const [filters, setFilters] = useState({
    page: 1,
    doc_type: null,
    status: null
  });

  useEffect(() => {
    const params = new URLSearchParams({
      page: filters.page,
      limit: 20,
      ...(filters.doc_type && { doc_type: filters.doc_type }),
      ...(filters.status && { status: filters.status })
    });

    fetch(`/api/documents/list?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setDocs(data));
  }, [filters]);

  return (
    <div className="document-list">
      {/* Filters */}
      <div className="filters">
        <select onChange={(e) => setFilters({...filters, doc_type: e.target.value})}>
          <option value="">All Types</option>
          <option value="Bill of Lading">Bill of Lading</option>
          <option value="Proof of Delivery">Proof of Delivery</option>
          {/* ... other types */}
        </select>

        <select onChange={(e) => setFilters({...filters, status: e.target.value})}>
          <option value="">All Status</option>
          <option value="Pass">Pass</option>
          <option value="Needs Review">Needs Review</option>
          <option value="Fail">Fail</option>
        </select>
      </div>

      {/* Document rows */}
      <div className="doc-rows">
        {docs.documents?.map(doc => (
          <div key={doc.doc_id} className="doc-row">
            <div className="doc-type-icon">
              {getIconForType(doc.doc_type)}
            </div>
            <div className="doc-info">
              <strong>{doc.doc_type}</strong>
              <span>{doc.primary_id}</span>
            </div>
            <div className="doc-date">
              {new Date(doc.upload_date).toLocaleDateString()}
            </div>
            <div className="doc-quality">
              {doc.quality_score}%
            </div>
            <div className={`doc-status status-${doc.status}`}>
              {doc.status}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="pagination">
        <button 
          onClick={() => setFilters({...filters, page: filters.page - 1})}
          disabled={filters.page === 1}
        >
          Previous
        </button>
        <span>Page {docs.page} of {docs.total_pages}</span>
        <button 
          onClick={() => setFilters({...filters, page: filters.page + 1})}
          disabled={filters.page === docs.total_pages}
        >
          Next
        </button>
      </div>
    </div>
  );
}
```

---

## 🎯 Key Benefits

### **1. No Document-Type Specific Code**

❌ **DON'T need:**
```jsx
{docType === 'BOL' && <BOLComponent />}
{docType === 'Invoice' && <InvoiceComponent />}
{docType === 'POD' && <PODComponent />}
// ... 8 different components!
```

✅ **DO need:**
```jsx
{doc.display_fields.map(field => <Field {...field} />)}
// ONE component for ALL types!
```

### **2. Automatic Frontend Updates**

When you add a new document type or new field:
- ✅ Backend: Add to `display_config.py`
- ✅ Frontend: **NO CHANGES NEEDED!**

Frontend automatically renders new fields!

### **3. Dynamic Field Display**

- Only shows fields that have values (`!field.empty`)
- Highlights important fields (`field.highlight`)
- Shows icons (`field.icon`)
- Proper labels (`field.label`)

---

## 📊 Display Configuration

**Stored in**: `services/display_config.py`

**For each document type, defines:**
- Which fields to show
- In what order
- Field label (user-friendly)
- Icon
- Whether to highlight

**Example:**

```python
DocumentType.BILL_OF_LADING: [
    {"key": "bol_number",    "label": "BOL Number",    "icon": "📋", "highlight": True},
    {"key": "order_number",  "label": "Order / Load No", "icon": "🔢", "highlight": True},
    {"key": "shipper",       "label": "Shipper",       "icon": "📦"},
    {"key": "consignee",     "label": "Consignee",     "icon": "🏢"},
    // ... all 11 BOL fields
]
```

---

## 🔄 How It Works

```
1. Frontend requests document
   GET /api/documents/123/detail

2. Backend:
   ├─ Fetches document from DB
   ├─ Gets extracted_metadata (JSON with all fields)
   ├─ Gets display config for doc type
   └─ Merges: config + actual values

3. Returns:
   {
     doc_type: "Bill of Lading",
     metadata: {...all 11 BOL fields...},
     display_fields: [
       {key: "bol_number", label: "BOL Number", value: "BOL-78421", ...},
       {key: "shipper", label: "Shipper", value: "ABC Mfg", ...}
     ]
   }

4. Frontend:
   ├─ Loops through display_fields
   ├─ Renders each field with icon + label + value
   └─ ONE component works for ALL doc types!
```

---

## ✅ Summary

### **What Was Built:**

1. ✅ `services/display_config.py` - Field configurations for 8 doc types
2. ✅ `GET /api/documents/{id}/detail` - Generic detail endpoint
3. ✅ `GET /api/documents/list` - Paginated list with filters
4. ✅ `GET /api/documents/stats` - Dashboard statistics

### **Key Features:**

- ✅ **One API for all doc types** (no switch cases!)
- ✅ **Dynamic field rendering** (frontend loops display_fields)
- ✅ **Automatic updates** (add field → backend only)
- ✅ **66 fields** across 8 document types
- ✅ **Filtering & pagination**
- ✅ **Quality scoring** (extraction completeness)
- ✅ **Primary identifiers** (BOL#, Invoice#, etc. per type)

### **Frontend Simplicity:**

```jsx
// ONE component renders ALL 8 doc types:
{doc.display_fields.map(field => 
  <div>
    {field.icon} {field.label}: {field.value}
  </div>
)}
```

---

**Status**: ✅ **IMPLEMENTED & READY**  
**API Endpoints**: 3 generic endpoints  
**Document Types Supported**: 8  
**Total Fields**: 66  
**Frontend Components Needed**: 1 (not 8!)

---

**Your generic document API is production-ready!** 🎉

