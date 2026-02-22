# Extracted Data Flow to Frontend - Complete Guide

## Overview

This document explains how document-type-specific extracted data flows from backend processing to frontend display in the AI-Powered Document Intelligence System.

---

## 📊 Data Flow Architecture

```
Document Upload
    ↓
Background Processing
    ↓
OCR Extraction (EasyOCR + Gemini)
    ↓
Document Classification
    ↓
Metadata Extraction (Type-Specific Fields)
    ↓
Database Storage (extracted_metadata JSON column)
    ↓
API Response with Display Configuration
    ↓
Frontend Dynamic Rendering
```

---

## 🗄️ Database Storage

### Documents Table Structure

**Relevant Columns:**
- `extracted_metadata` (JSON) - Stores all extracted document-type-specific fields
- `order_number` (String) - Common field extracted from all documents
- `invoice_number` (String) - Common field for invoice-type documents
- `document_date` (String) - Common field for date extraction
- `client_name` (String) - Common field for company/client name
- `document_type` (Enum) - Classification result

### Metadata JSON Structure

```json
{
  "doc_type_fields": {
    // Document-type-specific fields
    "bol_number": "BOL-78421",
    "shipper": "ABC Manufacturing",
    "consignee": "XYZ Distribution",
    "origin": "Chicago, IL",
    "destination": "Dallas, TX",
    "carrier": "FastFreight Inc.",
    "_extraction_score": 0.85,
    "_filled_fields": 8,
    "_total_fields": 10
  },
  "gemini_fields": {
    // Raw fields from Gemini analysis
    "order_numbers": ["ORD-2024-9981"],
    "detected_signatures": 2
  },
  "classification_method": "multi-signal-weighted",
  "client_name": "ABC Manufacturing"
}
```

---

## 🎯 API Endpoints for Frontend

### 1. Simple Document List - `GET /documents/all`

**Purpose:** Get all documents with basic information

**Response Fields:**
- `document_id`
- `document_type`
- `original_filename`
- `created_at`
- `quality_score`
- `validation_status`

**Use Case:** Document list/grid view in frontend

**Example Response:**
```json
{
  "total": 5,
  "documents": [
    {
      "document_id": 123,
      "document_type": "Bill of Lading",
      "original_filename": "BOL_2025.pdf",
      "created_at": "2026-02-22T10:30:00Z",
      "quality_score": 87.5,
      "validation_status": "Pass"
    }
  ]
}
```

---

### 2. Order Documents - `GET /api/orders/{order_number}/documents`

**Purpose:** Get all documents for a specific order

**Response Fields:** Same as `/documents/all` but filtered by order

**Use Case:** Order-specific document view

---

### 3. Basic Document Details - `GET /documents/{document_id}`

**Purpose:** Get standard document information

**Response Schema:** `DocumentResponse`

**Key Fields:**
- All basic document info
- `extracted_metadata` (JSON object with all fields)
- Classification, quality, signature details
- Validation status

**Limitation:** Frontend needs to manually parse `extracted_metadata` to display fields

**Example Response:**
```json
{
  "id": 123,
  "filename": "uuid-filename.pdf",
  "original_filename": "BOL_2025.pdf",
  "document_type": "Bill of Lading",
  "classification_confidence": 0.94,
  "quality_score": 87.5,
  "signature_count": 2,
  "has_signature": true,
  "order_number": "ORD-2024-9981",
  "invoice_number": null,
  "document_date": "14/02/2026",
  "client_name": "ABC Manufacturing",
  "extracted_metadata": {
    "doc_type_fields": {
      "bol_number": "BOL-78421",
      "shipper": "ABC Manufacturing",
      "consignee": "XYZ Distribution"
    }
  },
  "validation_status": "Pass",
  "is_processed": true
}
```

---

### 4. ⭐ Detailed Document with Display Config - `GET /documents/{document_id}/detail`

**Purpose:** Get document with frontend rendering instructions

**This is the MAIN endpoint for displaying extracted data!**

**Response Structure:**
```json
{
  // Common fields (always present for all doc types)
  "doc_id": 123,
  "doc_type": "Bill of Lading",
  "confidence": 0.94,
  "upload_date": "2026-02-22T10:30:00Z",
  "uploaded_by": 1,
  "page_count": 2,
  "quality_score": 87.5,
  "quality_status": "Clear",
  "signature_count": 2,
  "signature_present": true,
  "validation_status": "Pass",
  "needs_review": false,
  "file_path": "uploads/uuid.pdf",
  "filename": "uuid.pdf",
  
  // Metadata (doc-type specific fields + common metadata)
  "metadata": {
    // Common fields with N/A for missing values
    "order_number": "ORD-2024-9981",
    "invoice_number": "N/A",
    "document_date": "14/02/2026",
    "client_name": "ABC Manufacturing",
    
    // Classification info
    "classification_method": "multi-signal-weighted",
    "classification_confidence": 0.94,
    
    // Document-type specific fields (Bill of Lading example)
    "bol_number": "BOL-78421",
    "shipper": "ABC Manufacturing",
    "consignee": "XYZ Distribution",
    "origin": "Chicago, IL",
    "destination": "Dallas, TX",
    "carrier": "FastFreight Inc.",
    "total_weight": "4,500 lbs",
    "total_pieces": "12",
    "freight_terms": "Prepaid",
    
    // Extraction quality metrics
    "_extraction_score": 0.85,
    "_filled_fields": 8,
    "_total_fields": 10
  },
  
  // 🎨 Display configuration (TELLS FRONTEND HOW TO RENDER)
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
      "value": "ORD-2024-9981",
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
      "value": "N/A",
      "empty": true
    }
    // ... more fields
  ],
  
  // Extraction quality information
  "extraction_quality": {
    "is_complete": true,
    "extraction_score": 0.85,
    "status": "complete"
  }
}
```

---

## 🎨 Display Fields Configuration

### What is display_fields?

The `display_fields` array is a **frontend rendering instruction set**. Each document type has a predefined list of fields that should be displayed, in a specific order, with labels, icons, and highlighting.

### Benefits:

✅ **Generic Frontend** - One component renders ALL document types  
✅ **No Hardcoding** - Frontend doesn't need to know document schemas  
✅ **Easy Updates** - Change field order/labels in backend only  
✅ **Consistent UX** - All documents follow same display pattern  
✅ **Missing Data Handling** - "N/A" for missing fields automatically

### Display Field Object:

```json
{
  "key": "bol_number",           // Field key in metadata
  "label": "BOL Number",         // Human-readable label
  "icon": "📋",                  // Visual icon for UI
  "highlight": true,             // Should this field be emphasized?
  "value": "BOL-78421",          // Actual extracted value (or "N/A")
  "empty": false                 // Is this field missing/empty?
}
```

---

## 📋 Document Type Field Definitions

### Bill of Lading (BOL)

**Fields Extracted:**
- `bol_number` - BOL number
- `order_number` - Order/Load number
- `shipper` - Shipper company name
- `consignee` - Consignee company name
- `origin` - Origin location
- `destination` - Destination location
- `ship_date` - Shipping date
- `carrier` - Carrier company name
- `total_weight` - Total weight
- `total_pieces` - Number of pieces
- `freight_terms` - Freight payment terms (Prepaid/Collect)

**Highlighted Fields:** `bol_number`, `order_number`

---

### Proof of Delivery (POD)

**Fields Extracted:**
- `order_number` - Order/Load number
- `delivery_date` - Date of delivery
- `delivery_time` - Time of delivery
- `delivered_to` - Recipient name
- `delivery_address` - Delivery address
- `condition` - Delivery condition (Good/Damaged)
- `driver_name` - Driver name
- `exceptions` - Any exceptions or notes

**Highlighted Fields:** `order_number`, `delivery_date`

---

### Commercial Invoice

**Fields Extracted:**
- `invoice_number` - Invoice number
- `order_number` - Order/PO number
- `invoice_date` - Invoice date
- `seller` - Seller company
- `buyer` - Buyer company
- `total_amount` - Total invoice amount
- `currency` - Currency (USD, EUR, etc.)
- `payment_terms` - Payment terms (Net 30, etc.)
- `incoterms` - International trade terms

**Highlighted Fields:** `invoice_number`, `order_number`

---

### Packing List

**Fields Extracted:**
- `order_number` - Order number
- `packing_date` - Packing date
- `total_cartons` - Number of cartons
- `gross_weight` - Gross weight
- `net_weight` - Net weight
- `total_volume` - Total volume (CBM)
- `destination` - Destination

**Highlighted Fields:** `order_number`

---

### Hazmat Document

**Fields Extracted:**
- `un_number` - UN number (mandatory for hazmat)
- `shipping_name` - Proper shipping name
- `hazard_class` - Hazard classification
- `packing_group` - Packing group (I, II, III)
- `total_quantity` - Total quantity
- `emergency_contact` - Emergency contact number
- `shipper` - Shipper name

**Highlighted Fields:** `un_number`, `shipping_name`

---

### Lumper Receipt

**Fields Extracted:**
- `order_number` - Order/Load number
- `date` - Receipt date
- `lumper_company` - Lumper company name
- `worker_name` - Worker name
- `service_type` - Service type (Loading/Unloading)
- `hours_worked` - Hours worked
- `amount` - Payment amount
- `facility` - Facility name/location

**Highlighted Fields:** `order_number`

---

### Trip Sheet

**Fields Extracted:**
- `trip_number` - Trip/Load number
- `driver_name` - Driver name
- `truck_number` - Truck/Unit number
- `date` - Trip date
- `total_miles` - Total miles driven
- `origin` - Start location
- `destination` - End location
- `fuel_stops` - Number of fuel stops
- `states_crossed` - States crossed

**Highlighted Fields:** `trip_number`, `driver_name`

---

### Freight Invoice

**Fields Extracted:**
- `pro_number` - PRO number
- `invoice_number` - Invoice number
- `order_number` - Order/Load number
- `invoice_date` - Invoice date
- `carrier_name` - Carrier name
- `origin` - Origin location
- `destination` - Destination location
- `linehaul` - Linehaul charges
- `fuel_surcharge` - Fuel surcharge
- `accessorial` - Accessorial charges
- `total_charges` - Total charges
- `payment_due` - Payment due date

**Highlighted Fields:** `pro_number`, `invoice_number`

---

## 🖥️ Frontend Integration Examples

### React Component (Generic - Works for ALL Doc Types)

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function DocumentDetail({ documentId, token }) {
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/documents/${documentId}/detail`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        setDocument(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching document:', error);
        setLoading(false);
      }
    };

    fetchDocument();
  }, [documentId, token]);

  if (loading) return <div>Loading...</div>;
  if (!document) return <div>Document not found</div>;

  return (
    <div className="document-detail">
      {/* Header - Common for all documents */}
      <div className="document-header">
        <h2>{document.doc_type}</h2>
        <div className="badges">
          <span className={`badge ${document.validation_status.toLowerCase()}`}>
            {document.validation_status}
          </span>
          <span className="badge quality">
            Quality: {document.quality_score.toFixed(1)}%
          </span>
          {document.signature_present && (
            <span className="badge signatures">
              ✍️ {document.signature_count} Signature(s)
            </span>
          )}
        </div>
      </div>

      {/* Document Fields - GENERIC RENDERING */}
      <div className="document-fields">
        {document.display_fields.map((field, index) => (
          !field.empty && (
            <div 
              key={field.key} 
              className={`field ${field.highlight ? 'highlight' : ''}`}
            >
              <div className="field-label">
                <span className="icon">{field.icon}</span>
                <span className="label">{field.label}</span>
              </div>
              <div className="field-value">
                {field.value}
              </div>
            </div>
          )
        ))}
      </div>

      {/* Extraction Quality Indicator */}
      {document.extraction_quality && (
        <div className="extraction-quality">
          <div className="quality-bar">
            <div 
              className="quality-fill" 
              style={{ width: `${document.extraction_quality.extraction_score * 100}%` }}
            />
          </div>
          <p>
            Extracted {document.metadata._filled_fields} of {document.metadata._total_fields} fields
            ({(document.extraction_quality.extraction_score * 100).toFixed(0)}%)
          </p>
        </div>
      )}

      {/* Preview Section */}
      <div className="document-preview">
        <h3>Document Preview</h3>
        <iframe
          src={`http://localhost:8000/documents/${documentId}/preview`}
          width="100%"
          height="600px"
          title="Document Preview"
        />
      </div>
    </div>
  );
}

export default DocumentDetail;
```

### CSS for Styling

```css
.document-detail {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.document-header {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badges {
  display: flex;
  gap: 10px;
}

.badge {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.badge.pass {
  background: #d4edda;
  color: #155724;
}

.badge.fail {
  background: #f8d7da;
  color: #721c24;
}

.badge.pending {
  background: #fff3cd;
  color: #856404;
}

.document-fields {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.field {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 15px;
}

.field.highlight {
  border-color: #007bff;
  border-width: 2px;
  background: #f8f9ff;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.field-label .icon {
  font-size: 16px;
}

.field-value {
  font-size: 16px;
  font-weight: 500;
  color: #212529;
}

.extraction-quality {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.quality-bar {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.quality-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #20c997);
  transition: width 0.3s ease;
}

.document-preview iframe {
  border: 1px solid #dee2e6;
  border-radius: 6px;
}
```

---

## 🔄 Data Extraction Pipeline

### Step 1: OCR Text Extraction

Both EasyOCR and Gemini extract raw text from the document. Gemini also provides structured field extraction.

### Step 2: Document Classification

The system identifies the document type using multi-signal classification (keyword + embedding + AI vision).

### Step 3: Metadata Extraction

Based on the classified document type, the `metadata_extractor` service:
1. Checks Gemini's extracted fields first (most reliable)
2. Falls back to regex pattern matching on OCR text
3. Calculates extraction completeness

**Code Location:** `services/metadata_extractor.py`

### Step 4: Database Storage

Extracted fields are stored in the `extracted_metadata` JSON column:

```json
{
  "doc_type_fields": {
    "field_name": "value",
    "_extraction_score": 0.85,
    "_filled_fields": 8,
    "_total_fields": 10
  },
  "gemini_fields": { /* raw gemini data */ },
  "classification_method": "method_name"
}
```

### Step 5: API Response Generation

When frontend requests `/documents/{id}/detail`:
1. Load document from database
2. Parse `extracted_metadata` JSON
3. Get display configuration for document type
4. Attach actual values to display fields
5. Return structured response with `display_fields` array

**Code Location:** `routers/documents.py` - Line 556+

---

## 📊 Data Display Strategy

### ✅ Benefits of Current Approach

1. **Single Component Frontend** - One React component renders ALL document types
2. **No Type-Specific Code** - Frontend doesn't need switch/case for doc types
3. **Backend Controls Display** - Change field order/labels without frontend updates
4. **Automatic N/A Handling** - Missing fields show "N/A" automatically
5. **Extensible** - Add new document types by updating backend config only
6. **Visual Consistency** - All documents follow same display pattern with icons
7. **Field Highlighting** - Important fields are automatically emphasized

### 🎯 Frontend Developer Experience

Frontend developers don't need to:
- ❌ Know document type schemas
- ❌ Write type-specific rendering logic
- ❌ Handle missing field cases manually
- ❌ Worry about field ordering

They just need to:
- ✅ Loop through `display_fields` array
- ✅ Render label, icon, and value
- ✅ Apply highlight class if `highlight: true`
- ✅ Skip if `empty: true` (optional)

---

## 🛠️ Adding New Document Types

### Backend Configuration (3 steps):

1. **Add Document Type Enum** (`models.py`)
```python
class DocumentType(str, enum.Enum):
    NEW_TYPE = "New Document Type"
```

2. **Add Field Definitions** (`services/metadata_extractor.py`)
```python
NEW_TYPE_FIELDS = {
    "field_name": r"regex_pattern",
    # ... more fields
}
```

3. **Add Display Configuration** (`services/display_config.py`)
```python
DocumentType.NEW_TYPE: [
    {"key": "field_name", "label": "Field Label", "icon": "🎯", "highlight": True},
    # ... more fields
]
```

### Frontend Changes Required:

**ZERO** - Frontend automatically renders the new document type using the generic component!

---

## 📌 Summary

### Key Points:

✅ **All extracted data is stored in `extracted_metadata` JSON column**  
✅ **Frontend uses `/documents/{id}/detail` endpoint for displaying data**  
✅ **`display_fields` array provides rendering instructions**  
✅ **One generic frontend component handles ALL document types**  
✅ **Missing fields automatically show as "N/A"**  
✅ **Backend controls field ordering, labels, icons, and highlighting**  
✅ **Extraction quality metrics included in response**  

### Best Practices:

1. **Always use `/documents/{id}/detail` for displaying document data**
2. **Loop through `display_fields` for rendering - don't hardcode field names**
3. **Use the `empty` flag to optionally hide missing fields**
4. **Show extraction quality indicator to users**
5. **Use the preview endpoint to show original document alongside extracted data**

---

**Last Updated:** February 22, 2026  
**System Version:** 1.0

