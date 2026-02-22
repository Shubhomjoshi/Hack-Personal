# Debug Test Documents Folder

This folder is for testing the document processing pipeline with the debug script.

## How to Use

### Option 1: Test existing document from database
```bash
python debug_document_processing.py --id <document_id>
```
Example: `python debug_document_processing.py --id 123`

### Option 2: Upload and test a specific file
```bash
python debug_document_processing.py --file <path_to_file>
```
Example: `python debug_document_processing.py --file samples/my_bol.pdf`

### Option 3: Process all files from this folder
```bash
python debug_document_processing.py --folder
```
This will automatically process ALL PDF and image files in this `debug_test_docs/` folder.

## Supported File Types
- PDF (.pdf)
- JPEG/JPG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tif, .tiff)

## Instructions
1. Place your test documents in this `debug_test_docs/` folder
2. Run: `python debug_document_processing.py --folder`
3. The script will process each document and show detailed logs

## What the Debug Script Shows
- ✅ Which process/orchestrator is chosen
- ✅ What decisions are made at each step
- ✅ What data is being updated in the database
- ✅ Where the data is stored
- ✅ Complete execution summary

## Example Output
The debug script will show:
- Phase 1: Quality Assessment
- Phase 2: OCR Text Extraction
- Phase 3: Document Classification
- Phase 4: Signature Detection (if BOL)
- Phase 5: Metadata Extraction
- Phase 6: Document-Type-Specific Fields (NOT IMPLEMENTED - will show N/A)
- Phase 7: Rule Validation
- Execution Summary with all decisions and database updates

