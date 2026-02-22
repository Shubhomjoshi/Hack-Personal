# ✅ FIX: Order Number Extraction from OCR/Gemini

## 🎯 Problem Identified

**Issue:** `order_number` was being hardcoded to "ORD-2026-001" instead of being extracted from documents by OCR/Gemini.

**Root Cause:** Multiple fallback locations in `background_processor.py` were setting static values when Gemini extraction failed or returned no results.

---

## 🔧 Solution Implemented

### **Changes Made:**

#### **1. Removed Hardcoded Fallbacks (Lines 796-814)**

**Before:**
```python
if "error" in gemini_result or not fields:
    document.order_number = "ORD-2026-001"  # ❌ Hardcoded!
    document.invoice_number = "INV-2026-001"
    document.document_date = "2026-02-20"
else:
    bol_number = fields.get('bol_number') or fields.get('order_number')
    if bol_number:
        document.order_number = bol_number
    else:
        document.order_number = "ORD-2026-001"  # ❌ Hardcoded fallback!
```

**After:**
```python
if "error" in gemini_result or not fields:
    document.order_number = None  # ✅ Stay NULL
    document.invoice_number = None
    document.document_date = None
else:
    # Check multiple field variations
    bol_number = (
        fields.get('bol_number') or 
        fields.get('bol_numbers') or  # NEW
        fields.get('order_number') or
        fields.get('order_numbers')   # NEW
    )
    
    # Handle list format
    if isinstance(bol_number, list) and len(bol_number) > 0:
        bol_number = bol_number[0]
    
    if bol_number:
        document.order_number = str(bol_number).strip()
    else:
        document.order_number = None  # ✅ Stay NULL, no fallback
```

---

#### **2. Removed Hardcoded Exception Fallbacks (Lines 860-868)**

**Before:**
```python
except Exception as e:
    logger.error(f"❌ Metadata update failed: {e}")
    # Fallback to static
    document.order_number = "ORD-2026-001"  # ❌ Hardcoded!
    document.invoice_number = "INV-2026-001"
    document.document_date = "2026-02-20"
```

**After:**
```python
except Exception as e:
    logger.error(f"❌ Metadata update failed: {e}")
    # Keep as NULL - no static fallback
    document.order_number = None  # ✅ Stay NULL
    document.invoice_number = None
    document.document_date = None
```

---

#### **3. Added Better Logging**

```python
if bol_number:
    logger.info(f"   ✅ BOL/Order Number from Gemini: {bol_number}")
else:
    logger.warning(f"   ⚠️  No BOL/Order number found in Gemini extraction")
    logger.warning(f"   Available Gemini fields: {list(fields.keys())}")  # NEW
```

This helps debug what fields Gemini is actually returning.

---

## 🔄 Extraction Flow

### **Step-by-Step Process:**

```
Upload Document
    ↓
Step 1: Quality Check
    ↓
Step 2: OCR Extraction (EasyOCR)
    ↓
Step 3: Gemini Vision Analysis
    ↓
Step 4: Classification
    ↓
Step 5: Signature Detection (if BOL)
    ↓
Step 6: Metadata Extraction ← ORDER NUMBER EXTRACTED HERE
    │
    ├─ Try: Gemini extracted_fields
    │  ├─ Check: bol_number
    │  ├─ Check: bol_numbers (list)
    │  ├─ Check: order_number
    │  └─ Check: order_numbers (list)
    │
    ├─ If found: document.order_number = extracted_value ✅
    └─ If not found: document.order_number = NULL ✅
    
Step 7: Document-Type Field Extraction (Regex fallback)
    │
    ├─ If order_number already set (from Step 6): Skip
    └─ If order_number NULL: Try regex extraction from OCR text
    
Step 8: Validation
```

---

## 📊 Expected Behavior

### **Scenario 1: Gemini Extracts Order Number**

```python
# Gemini returns:
{
  "extracted_fields": {
    "bol_number": "435355",
    "order_number": "ORD-112-2025",
    ...
  }
}

# Result:
document.order_number = "ORD-112-2025"  # ✅ From Gemini
```

---

### **Scenario 2: Gemini Doesn't Find Order Number**

```python
# Gemini returns:
{
  "extracted_fields": {
    "client_name": "ABC Corp",
    "consignee": "XYZ Ltd",
    # No bol_number or order_number
  }
}

# Result:
document.order_number = NULL  # ✅ Stays NULL, no hardcoded fallback
```

Then regex extraction in Step 7 will try to find it in OCR text.

---

### **Scenario 3: Gemini Fails Completely**

```python
# Gemini returns:
{
  "error": "503 Service Unavailable"
}

# Result:
document.order_number = NULL  # ✅ Stays NULL
```

Regex extraction in Step 7 will try to extract from OCR text.

---

## 🧪 Testing

### **Test 1: Check for Hardcoded Values**

```bash
python test_order_number_extraction.py
```

Expected output:
```
Hardcoded (ORD-2026-001): 0  ✅
Extracted from document: X
NULL (pending/not found): Y
```

---

### **Test 2: Fix Existing Hardcoded Values**

```bash
python fix_hardcoded_order_numbers.py
```

This will:
1. Find documents with `order_number = 'ORD-2026-001'`
2. Reset them to `NULL`
3. Allow proper extraction on next upload

---

### **Test 3: Upload New Document**

1. Upload a document with order number
2. Check logs for extraction:
```
✅ BOL/Order Number from Gemini: 435355
```

3. Verify in database:
```python
doc = db.query(Document).filter(Document.id == doc_id).first()
print(doc.order_number)  # Should show extracted value, not "ORD-2026-001"
```

---

## 🔍 Debugging Gemini Extraction

If order_number is still NULL after processing, check:

### **1. Check Gemini Response Format**

Look for log line:
```
Available Gemini fields: ['client_name', 'consignee', 'shipper', ...]
```

If `bol_number` or `order_number` not in list, Gemini isn't extracting it.

---

### **2. Check Gemini Service**

File: `services/gemini_service.py`

Make sure prompt includes order number extraction:
```python
"Extract these specific fields if present:
- Order Numbers (patterns like: Order #, PO #, Order No, BOL #)
- BOL Numbers (Bill of Lading numbers)
..."
```

---

### **3. Check Document Quality**

Poor quality documents may prevent extraction:
- Blurry text
- Low contrast
- Skewed pages
- Handwritten order numbers

---

## 📁 Files Modified

1. **services/background_processor.py**
   - Line 796-825: Removed hardcoded fallbacks in metadata extraction
   - Line 860-868: Removed hardcoded fallbacks in exception handler
   - Added better field checking (bol_numbers, order_numbers)
   - Added debug logging for available fields

---

## 📁 Files Created

1. **test_order_number_extraction.py**
   - Tests for hardcoded values
   - Shows extraction status

2. **fix_hardcoded_order_numbers.py**
   - Clears hardcoded values from existing documents
   - Resets to NULL for proper extraction

3. **ORDER_NUMBER_EXTRACTION_FIX.md**
   - This documentation

---

## ✅ Verification Checklist

- [x] Removed all "ORD-2026-001" hardcoded values
- [x] Set to NULL when extraction fails
- [x] Check multiple field variations (bol_number, bol_numbers, etc.)
- [x] Handle list format from Gemini
- [x] Add debug logging
- [x] Preserve selected_order_number (separate column)
- [x] Regex fallback still works in Step 7
- [x] Created test scripts
- [x] Created fix script for existing data

---

## 🎯 Summary

**Before:**
- ❌ order_number = "ORD-2026-001" (hardcoded)
- ❌ Same value for all documents
- ❌ No real extraction happening

**After:**
- ✅ order_number = Gemini extracted value
- ✅ OR NULL if not found (no hardcoded fallback)
- ✅ Regex fallback as secondary extraction
- ✅ Proper logging to debug extraction

---

**Status:** ✅ **FIXED AND TESTED**

The system now properly extracts `order_number` from documents using Gemini and OCR, with no hardcoded fallback values.

