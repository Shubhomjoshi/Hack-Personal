"""
DEBUG DOCUMENT PROCESSING - Complete Flow Test
===============================================

This script tests the entire document processing pipeline and logs:
1. Which process/orchestrator is chosen
2. What decisions are made at each step
3. What data is being updated in the database
4. Where the data is stored

TWO MODES OF OPERATION:

MODE 1 - Test existing document by ID:
    python debug_document_processing.py --id <document_id>
    Example: python debug_document_processing.py --id 123

MODE 2 - Upload and test a file:
    python debug_document_processing.py --file <path_to_file>
    Example: python debug_document_processing.py --file test_docs/my_document.pdf

MODE 3 - Process all files from debug folder:
    python debug_document_processing.py --folder
    This will process all PDF/image files from ./debug_test_docs/ folder
"""

import sys
import os
import json
import shutil
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Document, DocumentType, ValidationStatus, User
from services.background_processor import BackgroundProcessor

# Debug test folder for file uploads
DEBUG_TEST_FOLDER = "debug_test_docs"
UPLOAD_DIR = "uploads"


class DebugLogger:
    """Enhanced logger that tracks all operations"""

    def __init__(self):
        self.logs = []
        self.db_updates = []
        self.decisions = []

    def log(self, category: str, message: str, data: dict = None):
        """Log a message with category"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = {
            "timestamp": timestamp,
            "category": category,
            "message": message,
            "data": data
        }
        self.logs.append(log_entry)

        # Color coding
        colors = {
            "ORCHESTRATOR": "\033[95m",  # Magenta
            "PROCESS": "\033[94m",       # Blue
            "DECISION": "\033[93m",      # Yellow
            "DB_UPDATE": "\033[92m",     # Green
            "ERROR": "\033[91m",         # Red
            "INFO": "\033[96m",          # Cyan
        }
        reset = "\033[0m"

        color = colors.get(category, "")
        print(f"{color}[{timestamp}] [{category}] {message}{reset}")
        if data:
            print(f"  Data: {json.dumps(data, indent=2, default=str)}")

    def log_decision(self, decision_point: str, decision: str, reason: str):
        """Log an orchestrator decision"""
        self.decisions.append({
            "point": decision_point,
            "decision": decision,
            "reason": reason
        })
        self.log("DECISION", f"🎯 {decision_point}: {decision}", {"reason": reason})

    def log_db_update(self, table: str, record_id: int, field: str, old_value, new_value):
        """Log a database update"""
        update_info = {
            "table": table,
            "record_id": record_id,
            "field": field,
            "old_value": old_value,
            "new_value": new_value
        }
        self.db_updates.append(update_info)
        self.log("DB_UPDATE",
                f"💾 Updated {table}.{field} (ID: {record_id})",
                {"old": old_value, "new": new_value})

    def log_process(self, process_name: str, status: str):
        """Log process execution"""
        self.log("PROCESS", f"⚙️  {process_name}: {status}")

    def print_summary(self):
        """Print execution summary"""
        print("\n" + "="*80)
        print("EXECUTION SUMMARY")
        print("="*80)

        print(f"\n📊 Total Logs: {len(self.logs)}")
        print(f"🎯 Decisions Made: {len(self.decisions)}")
        print(f"💾 Database Updates: {len(self.db_updates)}")

        if self.decisions:
            print("\n🎯 DECISION FLOW:")
            for i, dec in enumerate(self.decisions, 1):
                print(f"\n  {i}. {dec['point']}")
                print(f"     → Decision: {dec['decision']}")
                print(f"     → Reason: {dec['reason']}")

        if self.db_updates:
            print("\n💾 DATABASE UPDATES:")
            for i, update in enumerate(self.db_updates, 1):
                print(f"\n  {i}. Table: {update['table']} (ID: {update['record_id']})")
                print(f"     Field: {update['field']}")
                print(f"     Old: {update['old_value']}")
                print(f"     New: {update['new_value']}")


class DebugBackgroundProcessor(BackgroundProcessor):
    """Enhanced processor with debug logging"""

    def __init__(self, logger: DebugLogger):
        super().__init__()
        self.debug_logger = logger

    def process_document_debug(self, document_id: int, db: Session):
        """Process document with detailed logging"""

        self.debug_logger.log("ORCHESTRATOR", "🚀 Starting Document Processing Pipeline")

        # Load document
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            self.debug_logger.log("ERROR", f"❌ Document {document_id} not found")
            return

        self.debug_logger.log("INFO", f"📄 Loaded Document: {document.original_filename}", {
            "id": document.id,
            "filename": document.original_filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "uploaded_at": document.created_at
        })

        print("\n" + "="*80)
        print("PHASE 1: QUALITY ASSESSMENT")
        print("="*80)

        # Step 1: Quality Assessment
        self.debug_logger.log_decision(
            "Quality Assessment Strategy",
            "Run OpenCV Quality Check",
            "All documents must pass quality threshold"
        )

        try:
            quality_result = self._assess_quality_debug(document, db)

            if quality_result:
                self.debug_logger.log_db_update(
                    "documents", document.id,
                    "quality_score", "None", quality_result.get('quality_score')
                )
                self.debug_logger.log_db_update(
                    "documents", document.id,
                    "is_blurry", "None", quality_result.get('is_blurry')
                )
                self.debug_logger.log_db_update(
                    "documents", document.id,
                    "is_skewed", "None", quality_result.get('is_skewed')
                )
                self.debug_logger.log_db_update(
                    "documents", document.id,
                    "readability_status", "None", quality_result.get('readability_status')
                )
        except Exception as e:
            self.debug_logger.log("ERROR", f"Quality assessment failed: {e}")

        # Decision: Should we continue?
        if document.quality_score and document.quality_score < 55.0:
            self.debug_logger.log_decision(
                "Continue Processing?",
                "STOP - Quality too low",
                f"Quality score {document.quality_score} < 55.0 threshold"
            )
            self.debug_logger.log_db_update(
                "documents", document.id,
                "validation_status", document.validation_status, "Fail"
            )
            document.validation_status = ValidationStatus.FAIL
            db.commit()
            return
        else:
            self.debug_logger.log_decision(
                "Continue Processing?",
                "CONTINUE",
                f"Quality score {document.quality_score} ≥ 55.0 threshold"
            )

        print("\n" + "="*80)
        print("PHASE 2: OCR TEXT EXTRACTION")
        print("="*80)

        # Step 2: OCR Text Extraction
        self.debug_logger.log_decision(
            "OCR Strategy Selection",
            "EasyOCR + Gemini Combined",
            "Use both OCR engines and combine results"
        )

        try:
            ocr_result = self._extract_text_debug(document, db)

            if ocr_result:
                self.debug_logger.log_db_update(
                    "documents", document.id,
                    "ocr_text", "None", f"{len(ocr_result.get('text', ''))} characters"
                )
        except Exception as e:
            self.debug_logger.log("ERROR", f"OCR extraction failed: {e}")

        print("\n" + "="*80)
        print("PHASE 3: DOCUMENT CLASSIFICATION")
        print("="*80)

        # Step 3: Document Classification
        self.debug_logger.log_decision(
            "Classification Strategy",
            "Multi-Signal Weighted Classification",
            "Use keyword + embedding similarity + Gemini vision"
        )

        try:
            classification_result = self._classify_document_debug(document, db)

            if classification_result:
                self.debug_logger.log_db_update(
                    "documents", document.id,
                    "document_type", "Unknown", classification_result.get('doc_type')
                )
                self.debug_logger.log_db_update(
                    "documents", document.id,
                    "classification_confidence", "None", classification_result.get('confidence')
                )

                # Store in extracted_metadata
                if not document.extracted_metadata:
                    document.extracted_metadata = {}
                document.extracted_metadata["classification_method"] = classification_result.get("method_used")
                self.debug_logger.log_db_update(
                    "documents", document.id,
                    "extracted_metadata.classification_method", "None", classification_result.get("method_used")
                )
        except Exception as e:
            self.debug_logger.log("ERROR", f"Classification failed: {e}")

        # Decision: Run signature detection?
        if document.document_type == DocumentType.BILL_OF_LADING:
            self.debug_logger.log_decision(
                "Run Signature Detection?",
                "YES",
                "Document type is Bill of Lading - requires signatures"
            )

            print("\n" + "="*80)
            print("PHASE 4: SIGNATURE DETECTION (BOL only)")
            print("="*80)

            try:
                signature_result = self._detect_signatures_debug(document, db)

                if signature_result:
                    self.debug_logger.log_db_update(
                        "documents", document.id,
                        "signature_count", "None", signature_result.get('signature_count')
                    )
                    self.debug_logger.log_db_update(
                        "documents", document.id,
                        "has_signature", "None", signature_result.get('has_signature')
                    )
            except Exception as e:
                self.debug_logger.log("ERROR", f"Signature detection failed: {e}")
        else:
            self.debug_logger.log_decision(
                "Run Signature Detection?",
                "NO",
                f"Document type is {document.document_type} - signatures not required"
            )

        print("\n" + "="*80)
        print("PHASE 5: METADATA EXTRACTION")
        print("="*80)

        # Step 4: Metadata Extraction (from Gemini)
        self.debug_logger.log_decision(
            "Metadata Extraction Strategy",
            "Use Gemini extracted_fields",
            "Gemini provides structured field extraction"
        )

        try:
            self._extract_metadata_debug(document, db)
        except Exception as e:
            self.debug_logger.log("ERROR", f"Metadata extraction failed: {e}")

        print("\n" + "="*80)
        print("PHASE 6: DOCUMENT-TYPE-SPECIFIC FIELD EXTRACTION")
        print("="*80)

        # Step 5: Document-Type-Specific Fields
        self.debug_logger.log("INFO", "⚠️  CRITICAL: This step is NOT IMPLEMENTED!")
        self.debug_logger.log("INFO", "The system expects 'doc_type_fields' in extracted_metadata")
        self.debug_logger.log("INFO", "Currently, this object is NEVER created")
        self.debug_logger.log("INFO", "Result: Frontend will show 'N/A' for all doc-type-specific fields")

        self.debug_logger.log_decision(
            "Extract Document-Type-Specific Fields?",
            "SKIPPED - NOT IMPLEMENTED",
            "No service exists to extract fields like shipper, consignee, carrier, etc."
        )

        print("\n" + "="*80)
        print("PHASE 7: RULE VALIDATION")
        print("="*80)

        # Step 6: Rule Validation
        self.debug_logger.log_decision(
            "Run Rule Validation?",
            "YES",
            "Validate document against general and doc-type-specific rules"
        )

        try:
            validation_result = self._validate_rules_debug(document, db)

            if validation_result:
                self.debug_logger.log_db_update(
                    "documents", document.id,
                    "validation_status", document.validation_status, validation_result.get('status')
                )
        except Exception as e:
            self.debug_logger.log("ERROR", f"Rule validation failed: {e}")

        # Final update
        self.debug_logger.log_db_update(
            "documents", document.id,
            "is_processed", False, True
        )
        document.is_processed = True
        db.commit()

        self.debug_logger.log("ORCHESTRATOR", "✅ Document Processing Complete")

    def _assess_quality_debug(self, document: Document, db: Session):
        """Quality assessment with logging"""
        self.debug_logger.log_process("Quality Assessment", "STARTED")

        from services.quality_service import QualityService
        quality_service = QualityService()

        try:
            result = quality_service.assess_quality(document.file_path)

            self.debug_logger.log("INFO", "Quality Assessment Results", {
                "quality_score": result.get('quality_score'),
                "is_blurry": result.get('is_blurry'),
                "is_skewed": result.get('is_skewed'),
                "readability_status": result.get('readability_status'),
                "recommendation": result.get('recommendation')
            })

            # Update document with error handling
            try:
                document.quality_score = result.get('quality_score')
                document.is_blurry = result.get('is_blurry')
                document.is_skewed = result.get('is_skewed')
                document.readability_status = result.get('readability_status')
                db.commit()
            except Exception as db_error:
                self.debug_logger.log("ERROR", f"Database commit error: {db_error}")
                db.rollback()

            self.debug_logger.log_process("Quality Assessment", "COMPLETED")
            return result

        except Exception as e:
            self.debug_logger.log("ERROR", f"Quality assessment error: {e}")
            db.rollback()
            return None

    def _extract_text_debug(self, document: Document, db: Session):
        """OCR text extraction with logging"""
        self.debug_logger.log_process("EasyOCR Text Extraction", "STARTED")

        from services.easyocr_service import EasyOCRService
        easyocr_service = EasyOCRService()

        try:
            easyocr_text = easyocr_service.extract_text_from_file(document.file_path)

            self.debug_logger.log("INFO", "EasyOCR Extraction", {
                "text_length": len(easyocr_text) if easyocr_text else 0,
                "preview": easyocr_text[:200] if easyocr_text else "No text"
            })

            self.debug_logger.log_process("EasyOCR Text Extraction", "COMPLETED")

            # Gemini will also extract text (in signature detection or metadata extraction)
            self.debug_logger.log("INFO", "Gemini also extracts text during its analysis")

            # Update document - with error handling
            try:
                document.ocr_text = easyocr_text
                db.commit()
            except Exception as db_error:
                self.debug_logger.log("ERROR", f"Database commit error: {db_error}")
                db.rollback()
                # Try again with fresh session state
                document.ocr_text = easyocr_text
                db.commit()

            return {"text": easyocr_text}

        except Exception as e:
            self.debug_logger.log("ERROR", f"OCR extraction error: {e}")
            db.rollback()  # Rollback on any error
            return None

    def _classify_document_debug(self, document: Document, db: Session):
        """Document classification with logging"""
        self.debug_logger.log_process("Document Classification", "STARTED")

        from services.document_classifier import DocumentClassifierService
        classifier = DocumentClassifierService()

        try:
            # Read image
            with open(document.file_path, 'rb') as f:
                image_bytes = f.read()

            result = classifier.classify(document.ocr_text or "", image_bytes)

            self.debug_logger.log("INFO", "Classification Results", {
                "doc_type": result.get('doc_type'),
                "confidence": result.get('confidence'),
                "method": result.get('method_used'),
                "signals_used": result.get('signals_used', [])
            })

            # Update document
            doc_type_str = result.get('doc_type')
            try:
                document.document_type = DocumentType(doc_type_str)
            except:
                document.document_type = DocumentType.UNKNOWN

            document.classification_confidence = result.get('confidence')
            db.commit()

            self.debug_logger.log_process("Document Classification", "COMPLETED")
            return result

        except Exception as e:
            self.debug_logger.log("ERROR", f"Classification error: {e}")
            return None

    def _detect_signatures_debug(self, document: Document, db: Session):
        """Signature detection with logging"""
        self.debug_logger.log_process("Signature Detection (Gemini)", "STARTED")

        from services.gemini_service import GeminiService
        gemini_service = GeminiService()

        try:
            # Read image
            with open(document.file_path, 'rb') as f:
                image_bytes = f.read()

            result = gemini_service.analyze_document(image_bytes, document.ocr_text)

            signature_count = result.get('signatures', {}).get('count', 0)
            has_signature = signature_count > 0

            self.debug_logger.log("INFO", "Signature Detection Results", {
                "signature_count": signature_count,
                "has_signature": has_signature,
                "details": result.get('signatures', {}).get('details', [])
            })

            # Update document with error handling
            try:
                document.signature_count = signature_count
                document.has_signature = has_signature

                if not document.extracted_metadata:
                    document.extracted_metadata = {}
                document.extracted_metadata['signature_details'] = result.get('signatures', {}).get('details', [])

                db.commit()
            except Exception as db_error:
                self.debug_logger.log("ERROR", f"Database commit error: {db_error}")
                db.rollback()

            self.debug_logger.log_process("Signature Detection", "COMPLETED")
            return {"signature_count": signature_count, "has_signature": has_signature}

        except Exception as e:
            self.debug_logger.log("ERROR", f"Signature detection error: {e}")
            db.rollback()
            return None

    def _extract_metadata_debug(self, document: Document, db: Session):
        """Metadata extraction with logging"""
        self.debug_logger.log_process("Metadata Extraction (from Gemini)", "STARTED")

        # This uses Gemini extracted_fields
        self.debug_logger.log("INFO", "Extracting basic metadata: order_number, invoice_number, document_date")

        # In actual implementation, this comes from Gemini result
        # For now, show what would be extracted

        if document.order_number:
            self.debug_logger.log("INFO", f"Found order_number: {document.order_number}")
        else:
            self.debug_logger.log("INFO", "No order_number extracted")

        if document.invoice_number:
            self.debug_logger.log("INFO", f"Found invoice_number: {document.invoice_number}")
        else:
            self.debug_logger.log("INFO", "No invoice_number extracted")

        if document.document_date:
            self.debug_logger.log("INFO", f"Found document_date: {document.document_date}")
        else:
            self.debug_logger.log("INFO", "No document_date extracted")

        self.debug_logger.log_process("Metadata Extraction", "COMPLETED")

    def _validate_rules_debug(self, document: Document, db: Session):
        """Rule validation with logging"""
        self.debug_logger.log_process("Rule Validation", "STARTED")

        from services.rule_validation_engine import RuleValidationEngine
        rule_engine = RuleValidationEngine()

        try:
            # Build document dict for validation
            doc_dict = {
                "id": document.id,
                "document_type": document.document_type,
                "signature_count": document.signature_count,
                "has_signature": document.has_signature,
                "order_number": document.order_number,
                "invoice_number": document.invoice_number,
                "quality_score": document.quality_score,
                "metadata": document.extracted_metadata or {}
            }

            result = rule_engine.validate(doc_dict)

            self.debug_logger.log("INFO", "Validation Results", {
                "status": result.get('status'),
                "score": result.get('score'),
                "hard_failures": len(result.get('hard_failures', [])),
                "soft_warnings": len(result.get('soft_warnings', [])),
                "rules_checked": result.get('total_rules_checked')
            })

            if result.get('hard_failures'):
                self.debug_logger.log("ERROR", "Hard Failures Found", {
                    "failures": result.get('hard_failures')
                })

            if result.get('soft_warnings'):
                self.debug_logger.log("INFO", "Soft Warnings Found", {
                    "warnings": result.get('soft_warnings')
                })

            # Update document with error handling
            try:
                if result.get('status') == 'Fail':
                    document.validation_status = ValidationStatus.FAIL
                elif result.get('status') == 'Pass with Warnings':
                    document.validation_status = ValidationStatus.NEEDS_REVIEW
                else:
                    document.validation_status = ValidationStatus.PASS

                db.commit()
            except Exception as db_error:
                self.debug_logger.log("ERROR", f"Database commit error: {db_error}")
                db.rollback()

            self.debug_logger.log_process("Rule Validation", "COMPLETED")
            return result

        except Exception as e:
            self.debug_logger.log("ERROR", f"Rule validation error: {e}")
            db.rollback()
            return None


def create_test_document(file_path: str, db: Session) -> Document:
    """Create a document record from a file for testing"""

    print(f"\n📤 Creating test document from file: {file_path}")

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Get file info
    original_filename = os.path.basename(file_path)
    file_extension = os.path.splitext(original_filename)[1].lower().replace('.', '')
    file_size = os.path.getsize(file_path)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Copy file to uploads
    shutil.copy2(file_path, dest_path)
    print(f"✅ File copied to: {dest_path}")

    # Get or create test user
    test_user = db.query(User).filter(User.username == "debug_test_user").first()
    if not test_user:
        test_user = User(
            username="debug_test_user",
            email="debug@test.com",
            hashed_password="debug_hash",
            is_active=True,
            is_admin=False
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Created test user: {test_user.username}")

    # Create document record
    document = Document(
        filename=unique_filename,
        original_filename=original_filename,
        file_path=dest_path,
        file_size=file_size,
        file_type=file_extension.upper(),
        document_type=DocumentType.UNKNOWN,
        validation_status=ValidationStatus.PENDING,
        is_processed=False,
        uploaded_by=test_user.id
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    print(f"✅ Document record created with ID: {document.id}")

    return document


def get_files_from_folder(folder_path: str) -> list:
    """Get all processable files from a folder"""

    if not os.path.exists(folder_path):
        print(f"\n📁 Creating debug test folder: {folder_path}")
        os.makedirs(folder_path, exist_ok=True)
        print(f"   Place your test documents (PDF/images) in this folder")
        return []

    supported_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif']
    files = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_extensions:
                files.append(file_path)

    return files


def print_usage():
    """Print usage instructions"""
    print("\n" + "="*80)
    print(" "*20 + "DOCUMENT PROCESSING DEBUG TOOL")
    print("="*80)
    print("\n📖 USAGE OPTIONS:\n")
    print("  1. Test existing document by ID:")
    print("     python debug_document_processing.py --id <document_id>")
    print("     Example: python debug_document_processing.py --id 123\n")
    print("  2. Upload and test a specific file:")
    print("     python debug_document_processing.py --file <path_to_file>")
    print("     Example: python debug_document_processing.py --file test_docs/my_bol.pdf\n")
    print("  3. Process all files from debug folder:")
    print("     python debug_document_processing.py --folder")
    print("     This processes all PDF/images from ./debug_test_docs/ folder\n")
    print("="*80 + "\n")


def main():
    """Main debug function"""

    if len(sys.argv) < 2:
        print_usage()
        print("❌ Error: No arguments provided\n")
        sys.exit(1)

    mode = sys.argv[1]

    # Parse arguments
    if mode == "--id":
        if len(sys.argv) < 3:
            print("❌ Error: Document ID required after --id")
            print("Example: python debug_document_processing.py --id 123")
            sys.exit(1)

        try:
            document_id = int(sys.argv[2])
            mode_type = "existing_document"
            test_file = None
        except ValueError:
            print(f"❌ Error: Invalid document ID '{sys.argv[2]}' - must be a number")
            sys.exit(1)

    elif mode == "--file":
        if len(sys.argv) < 3:
            print("❌ Error: File path required after --file")
            print("Example: python debug_document_processing.py --file test_docs/my_document.pdf")
            sys.exit(1)

        test_file = sys.argv[2]
        if not os.path.exists(test_file):
            print(f"❌ Error: File not found: {test_file}")
            sys.exit(1)

        mode_type = "upload_file"
        document_id = None

    elif mode == "--folder":
        mode_type = "process_folder"
        document_id = None
        test_file = None

    else:
        print(f"❌ Error: Invalid mode '{mode}'")
        print_usage()
        sys.exit(1)

    print("\n" + "="*80)
    print(" "*20 + "DOCUMENT PROCESSING DEBUG TOOL")
    print("="*80)

    if mode_type == "existing_document":
        print(f"\n🎯 MODE: Testing existing document")
        print(f"📄 Document ID: {document_id}")
    elif mode_type == "upload_file":
        print(f"\n🎯 MODE: Upload and test file")
        print(f"📄 File: {test_file}")
    else:
        print(f"\n🎯 MODE: Process all files from folder")
        print(f"📁 Folder: {DEBUG_TEST_FOLDER}/")

    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize database session
    db = SessionLocal()

    try:
        # Process based on mode
        if mode_type == "upload_file":
            # Create document from file
            document = create_test_document(test_file, db)
            document_ids = [document.id]

        elif mode_type == "process_folder":
            # Get all files from folder
            files = get_files_from_folder(DEBUG_TEST_FOLDER)

            if not files:
                print(f"\n⚠️  No files found in {DEBUG_TEST_FOLDER}/")
                print(f"   Place your test documents (PDF/images) in this folder and run again")
                sys.exit(0)

            print(f"\n📦 Found {len(files)} file(s) to process:")
            for f in files:
                print(f"   • {os.path.basename(f)}")

            # Create documents for all files
            document_ids = []
            for file_path in files:
                try:
                    document = create_test_document(file_path, db)
                    document_ids.append(document.id)
                except Exception as e:
                    print(f"❌ Failed to create document for {file_path}: {e}")

        else:  # existing_document
            document_ids = [document_id]

        # Process each document
        for idx, doc_id in enumerate(document_ids, 1):
            if len(document_ids) > 1:
                print("\n" + "="*80)
                print(f" PROCESSING DOCUMENT {idx} of {len(document_ids)} ".center(80, "="))
                print("="*80)

            # Initialize logger
            logger = DebugLogger()

            # Create debug processor
            processor = DebugBackgroundProcessor(logger)

            # Process document with debug logging
            processor.process_document_debug(doc_id, db)

            # Print summary
            logger.print_summary()

        print("\n" + "="*80)
        print(" "*25 + "DEBUG COMPLETE")
        print("="*80)
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"✅ Documents processed: {len(document_ids)}\n")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

