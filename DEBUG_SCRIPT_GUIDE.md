# Debug Script Quick Start Guide

## ✅ Bug Fixed!

The database error `Error binding parameter 0 - probably unsupported type` has been fixed.

**Root Cause:** EasyOCR was returning a tuple `(text, confidence)` instead of just the text string, which SQLite couldn't save.

**Solution:** Modified `extract_text_from_file()` to return only the text string.

---

## 🚀 How to Use the Debug Script

### Three Usage Modes:

### 1️⃣ Test with Existing Document ID
```bash
python debug_document_processing.py --id 123
```
Tests a document already in the database.

### 2️⃣ Upload and Test Specific File
```bash
python debug_document_processing.py --file "C:\path\to\document.pdf"
```
Uploads a file, creates database record, and processes it.

### 3️⃣ Process All Files from Debug Folder
```bash
python debug_document_processing.py --folder
```
Processes ALL PDF/image files in the `debug_test_docs/` folder.

---

## 📁 Debug Folder Setup

1. Navigate to: `C:\Amazatic\Hackathon Personal\Backend\debug_test_docs\`
2. Place your test documents (PDF, JPG, PNG) in this folder
3. Run: `python debug_document_processing.py --folder`

---

## 📊 What the Debug Script Shows

### Phase 1: Quality Assessment
- OpenCV quality check
- Blurriness detection
- Skew detection
- Quality score calculation
- **Decision:** Continue or stop based on quality threshold (55%)

### Phase 2: OCR Text Extraction
- EasyOCR extraction
- Text length and preview
- **Database Update:** `ocr_text` column

### Phase 3: Document Classification
- Multi-signal classification (keyword + embedding + Gemini)
- Classification confidence
- **Database Update:** `document_type`, `classification_confidence`
- **Decision:** Which document type identified

### Phase 4: Signature Detection (BOL Only)
- **Decision:** Only runs if document type is Bill of Lading
- Gemini Vision analysis for signatures
- Signature count and location
- **Database Update:** `signature_count`, `has_signature`

### Phase 5: Metadata Extraction
- Extracts: order_number, invoice_number, document_date
- Uses Gemini extracted_fields
- **Database Update:** `order_number`, `invoice_number`, `document_date`

### Phase 6: Document-Type-Specific Fields
- ⚠️ **NOT IMPLEMENTED** - Shows warning
- This is where shipper, consignee, carrier, etc. should be extracted
- Currently shows "N/A" for all doc-type-specific fields

### Phase 7: Rule Validation
- Validates against general and doc-type-specific rules
- Hard failures vs soft warnings
- **Database Update:** `validation_status`
- **Decision:** Pass, Fail, or Needs Review

---

## 📋 Example Output

```
[10:30:15.123] [ORCHESTRATOR] 🚀 Starting Document Processing Pipeline
[10:30:15.234] [INFO] 📄 Loaded Document: test_bol.pdf
[10:30:15.345] [DECISION] 🎯 Quality Assessment Strategy: Run OpenCV Quality Check
[10:30:16.456] [DB_UPDATE] 💾 Updated documents.quality_score (ID: 123)
[10:30:16.567] [DECISION] 🎯 Continue Processing?: CONTINUE
[10:30:17.678] [PROCESS] ⚙️ EasyOCR Text Extraction: STARTED
...
```

---

## 🎯 Decision Points Logged

The debug script logs every orchestrator decision:

1. **Quality Assessment Strategy** - Which quality check to run
2. **Continue Processing?** - Based on quality threshold
3. **OCR Strategy Selection** - Which OCR engine to use
4. **Classification Strategy** - How to classify document
5. **Run Signature Detection?** - Based on document type
6. **Extract Document-Type-Specific Fields?** - NOT IMPLEMENTED warning
7. **Run Rule Validation?** - Always YES

---

## 💾 Database Updates Tracked

Every database update is logged:

```
💾 Updated documents.quality_score (ID: 123)
   Old: None
   New: 87.5

💾 Updated documents.document_type (ID: 123)
   Old: Unknown
   New: Bill of Lading
```

---

## 📈 Execution Summary

At the end, you get a complete summary:

```
EXECUTION SUMMARY
=================

📊 Total Logs: 47
🎯 Decisions Made: 7
💾 Database Updates: 12

🎯 DECISION FLOW:
  1. Quality Assessment Strategy: Run OpenCV Quality Check
     → Decision: Run OpenCV Quality Check
     → Reason: All documents must pass quality threshold

  2. Continue Processing?: CONTINUE
     → Decision: CONTINUE
     → Reason: Quality score 87.5 ≥ 55.0 threshold
  
  ... (all decisions listed)

💾 DATABASE UPDATES:
  1. Table: documents (ID: 123)
     Field: quality_score
     Old: None
     New: 87.5
  
  ... (all updates listed)
```

---

## ⚠️ Known Issues Highlighted

The debug script will highlight that **Phase 6** (Document-Type-Specific Field Extraction) is **NOT IMPLEMENTED**:

```
PHASE 6: DOCUMENT-TYPE-SPECIFIC FIELD EXTRACTION
==================================================

⚠️  CRITICAL: This step is NOT IMPLEMENTED!
The system expects 'doc_type_fields' in extracted_metadata
Currently, this object is NEVER created
Result: Frontend will show 'N/A' for all doc-type-specific fields
```

This means fields like:
- shipper, consignee, carrier (BOL)
- delivered_to, delivery_address (POD)
- seller, buyer, total_amount (Invoice)

Are **NOT being extracted or saved** to the database.

---

## 🔧 Error Handling

The debug script now has comprehensive error handling:

✅ All database operations wrapped in try-except  
✅ Automatic rollback on database errors  
✅ Continues processing even if one phase fails  
✅ Clear error messages with full context  

---

## 🎨 Color-Coded Output

- **Magenta** - Orchestrator decisions
- **Blue** - Process execution
- **Yellow** - Decision points
- **Green** - Database updates
- **Red** - Errors
- **Cyan** - Information

---

## 📞 Support

If you encounter any issues:

1. Check the error messages in red
2. Review the database updates to see what was saved
3. Check the decision flow to understand why something happened
4. Look for "NOT IMPLEMENTED" warnings

---

**Created:** February 22, 2026  
**Last Updated:** February 22, 2026  
**Status:** ✅ Ready to Use

