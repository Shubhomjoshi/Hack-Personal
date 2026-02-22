"""
Background Processing Service - AI Agent-Powered Document Processing
Uses intelligent AI agents to optimize OCR, quality assessment, and processing flow
Supports concurrent processing for classification, signatures, and metadata extraction
"""
import time
import logging
import os
import cv2
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Document, ReadabilityStatus, ValidationStatus, DocumentType, ClassificationResult as ClassificationResultModel
from services.easyocr_service import easyocr_service
from services.quality_service import quality_service
from services.signature_service import signature_service
from services.metadata_service import metadata_service
from services.gemini_service import get_gemini_analyzer
from services.document_classifier import get_document_classifier
from services.sample_based_classifier import get_sample_based_classifier
from services.document_processing_agent import get_processing_agent
from services.enhanced_metadata_extractor import get_enhanced_metadata_extractor
from services.rule_validation_engine import get_validation_engine

logger = logging.getLogger(__name__)


class BackgroundProcessor:
    """AI Agent-Powered Background Document Processing Service"""

    def __init__(self):
        """Initialize the processor with AI agent"""
        self.agent = get_processing_agent()

    def process_document_async(self, document_id: int, db: Session):
        """
        AI Agent-powered intelligent document processing.
        Agent makes smart decisions about OCR strategy, quality assessment, and optimization.

        Args:
            document_id: Document ID to process
            db: Database session
        """
        try:
            # Fetch document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document {document_id} not found")
                return

            logger.info(f"🤖 [AI AGENT] Starting intelligent processing for document {document_id}: {document.filename}")
            start_time = time.time()

            # Get file information
            if not os.path.exists(document.file_path):
                logger.error(f"❌ File not found: {document.file_path}")
                document.processing_error = "File not found"
                document.validation_status = ValidationStatus.FAIL
                db.commit()
                return

            file_size = os.path.getsize(document.file_path)
            file_format = os.path.splitext(document.file_path)[1]

            # ============================================
            # STEP 1: AI AGENT DECIDES PROCESSING STRATEGY
            # ============================================
            logger.info(f"🧠 [AI AGENT] Analyzing document to determine optimal strategy...")
            strategy = self.agent.decide_processing_strategy(
                file_path=document.file_path,
                file_size=file_size,
                file_format=file_format,
                initial_quality_score=None
            )

            logger.info(f"✅ [AI AGENT] Strategy: {strategy['strategy']}")
            logger.info(f"   └─ Reasoning: {strategy['reasoning']}")

            # ============================================
            # STEP 2: QUALITY CHECK (IF AGENT RECOMMENDS)
            # ============================================
            quality_score = None
            quality_details = None

            if strategy.get('quality_check_first', True):
                logger.info(f"🔍 [AI AGENT] Running quality assessment first...")
                quality_score = self._run_quality_check(document, db)
                quality_details = {
                    'score': quality_score,
                    'blur_score': document.blur_score if hasattr(document, 'blur_score') else 0,
                    'skew_angle': document.skew_angle if hasattr(document, 'skew_angle') else 0,
                    'brightness': document.brightness_score if hasattr(document, 'brightness_score') else 0.5
                }

                # If quality is too low, get AI feedback
                if quality_score < 55.0:
                    logger.warning(f"⚠️  [AI AGENT] Low quality detected: {quality_score}%")

                    # Load image for agent analysis
                    image = cv2.imread(document.file_path)
                    if image is not None:
                        feedback = self.agent.provide_quality_feedback(
                            image=image,
                            quality_score=quality_score,
                            blur_score=quality_details['blur_score'],
                            skew_angle=quality_details['skew_angle'],
                            brightness=quality_details['brightness']
                        )

                        # Update document with detailed feedback
                        feedback_msg = f"Quality score: {quality_score}%\n\n"
                        feedback_msg += "Issues:\n"
                        for issue in feedback['issues_detected']:
                            feedback_msg += f"- {issue['issue'].title()}: {issue['explanation']}\n"
                        feedback_msg += "\nHow to fix:\n"
                        for i, suggestion in enumerate(feedback['actionable_suggestions'], 1):
                            feedback_msg += f"{i}. {suggestion}\n"

                        document.processing_error = feedback_msg
                    else:
                        document.processing_error = f"Low quality document ({quality_score}%). Please re-upload a clearer image."

                    document.validation_status = ValidationStatus.NEEDS_REVIEW
                    document.is_processed = False
                    document.updated_at = func.now()
                    db.commit()

                    self._notify_driver_reupload(document, quality_score, db)

                    logger.info(f"❌ [AI AGENT] Document rejected - Quality: {quality_score}%")
                    return

            # ============================================
            # STEP 3: INTELLIGENT OCR EXECUTION
            # ============================================
            ocr_text = ""
            ocr_confidence = 0.0
            gemini_result = None
            easyocr_result = None

            # Execute based on agent's strategy
            if strategy['strategy'] == 'fast_track':
                # Skip EasyOCR, use only Gemini
                logger.info(f"⚡ [AI AGENT] Fast-track: Using only Gemini OCR")
                gemini_result = self._run_gemini_analysis(document, None, db)
                ocr_text = gemini_result.get('extracted_text', '') if gemini_result else ""
                ocr_confidence = gemini_result.get('confidence', 0.0) if gemini_result else 0.0

            elif strategy['strategy'] == 'dual_ocr':
                # Use both OCRs
                logger.info(f"🔄 [AI AGENT] Dual OCR: Running both EasyOCR and Gemini")
                ocr_text, ocr_confidence = self._run_ocr(document, db)
                easyocr_result = {'text': ocr_text, 'confidence': ocr_confidence}

                gemini_result = self._run_gemini_analysis(document, ocr_text, db)

                # Combine results (Gemini service handles this)
                if gemini_result and gemini_result.get('extracted_text'):
                    gemini_analyzer = get_gemini_analyzer()
                    ocr_text = gemini_analyzer.combine_ocr_results(
                        ocr_text,
                        gemini_result['extracted_text'],
                        gemini_result.get('confidence', 0.0)
                    )

            elif strategy['strategy'] == 'enhanced_ocr':
                # Run EasyOCR first, then decide
                logger.info(f"📊 [AI AGENT] Enhanced OCR: Running EasyOCR first...")
                ocr_text, ocr_confidence = self._run_ocr(document, db)
                easyocr_result = {'text': ocr_text, 'confidence': ocr_confidence}

                # Ask agent if we need Gemini
                optimization = self.agent.optimize_ocr_execution(
                    strategy=strategy,
                    easyocr_result=easyocr_result
                )

                if not optimization.get('skip_gemini', False):
                    logger.info(f"🔄 [AI AGENT] Running Gemini for enhanced accuracy")
                    gemini_result = self._run_gemini_analysis(document, ocr_text, db)

                    if gemini_result and gemini_result.get('extracted_text'):
                        gemini_analyzer = get_gemini_analyzer()
                        ocr_text = gemini_analyzer.combine_ocr_results(
                            ocr_text,
                            gemini_result['extracted_text'],
                            gemini_result.get('confidence', 0.0)
                        )
                else:
                    logger.info(f"⚡ [AI AGENT] Skipping Gemini - EasyOCR results sufficient")
                    logger.info(f"   └─ Reason: {optimization.get('reasoning', 'Good confidence')}")

            elif strategy['strategy'] == 'quality_first':
                # Quality was already checked above
                # Proceed with standard OCR
                logger.info(f"📊 [AI AGENT] Quality-first: Running standard OCR")
                ocr_text, ocr_confidence = self._run_ocr(document, db)
                gemini_result = self._run_gemini_analysis(document, ocr_text, db)

            # Update document with OCR text
            document.ocr_text = ocr_text

            # ============================================
            # STEP 4: CLASSIFICATION (Must run first to determine document type)
            # ============================================
            logger.info(f"🎯 [AI AGENT] Step 1: Running document classification...")
            classification_start = time.time()

            classification_result = self._classify_document_safe(document.id, gemini_result)

            if classification_result.get('error'):
                logger.error(f"   ❌ Classification failed: {classification_result['error']}")
            else:
                logger.info(f"   ✅ Classification completed: {classification_result.get('doc_type', 'Unknown')} "
                           f"(Confidence: {classification_result.get('confidence', 0):.1%})")

            classification_time = time.time() - classification_start

            # Refresh document to get updated document_type
            db.refresh(document)

            # ============================================
            # STEP 5: CONDITIONAL SIGNATURE DETECTION (Only for Bill of Lading)
            # ============================================
            signature_result = {"skipped": True}
            signature_time = 0

            if document.document_type == DocumentType.BILL_OF_LADING:
                logger.info(f"✍️  [SIGNATURE DETECTION] Document type is Bill of Lading - Running signature detection...")
                logger.info(f"   📌 Analyzing document for handwritten signatures...")
                signature_start = time.time()

                signature_result = self._update_signature_from_gemini_safe(document.id, gemini_result)

                signature_time = time.time() - signature_start

                if signature_result.get('error'):
                    logger.error(f"   ❌ Signature detection failed: {signature_result['error']}")
                else:
                    sig_count = signature_result.get('signature_count', 0)
                    logger.info(f"   ✅ Signature detection completed: Found {sig_count} signature(s)")
                    if sig_count > 0:
                        logger.info(f"   📝 Signature details updated in database")
            else:
                doc_type_name = document.document_type.value if document.document_type else "Unknown"
                logger.info(f"⏭️  [SIGNATURE DETECTION] Document type is '{doc_type_name}' - Skipping signature detection")
                logger.info(f"   ℹ️  Signature detection only runs for Bill of Lading documents")

            # ============================================
            # STEP 6: CONCURRENT METADATA EXTRACTION (Can run in parallel)
            # ============================================
            logger.info(f"📋 [AI AGENT] Step 2: Running metadata extraction...")
            metadata_start = time.time()

            metadata_result = self._update_metadata_from_gemini_safe(document.id, gemini_result)

            metadata_time = time.time() - metadata_start

            if metadata_result.get('error'):
                logger.error(f"   ❌ Metadata extraction failed: {metadata_result['error']}")
            else:
                logger.info(f"   ✅ Metadata extraction completed")

            # Calculate total processing time for these steps
            total_step_time = classification_time + signature_time + metadata_time
            logger.info(f"✅ [AI AGENT] Processing steps complete in {total_step_time:.2f}s")
            logger.info(f"   ├─ Classification: {classification_time:.2f}s")
            logger.info(f"   ├─ Signature Detection: {signature_time:.2f}s {'(Skipped)' if signature_result.get('skipped') else ''}")
            logger.info(f"   └─ Metadata Extraction: {metadata_time:.2f}s")


            # Refresh document from database to get updated fields
            db.refresh(document)

            # ============================================
            # STEP 7: DOCUMENT-TYPE SPECIFIC FIELD EXTRACTION
            # Extract fields based on document type (BOL, POD, Invoice, etc.)
            # ============================================
            logger.info(f"📋 [FIELD EXTRACTION] Extracting document-type specific fields...")
            self._extract_document_fields(document, gemini_result, db)

            # Refresh again to get extracted fields
            db.refresh(document)

            # ============================================
            # STEP 8: RULE VALIDATION
            # Validate document against general and doc-specific rules
            # ============================================
            logger.info(f"✅ [VALIDATION] Running rule validation...")
            validation_result = self._validate_document_rules(document, db)

            # If validation requires stopping (quality issues), stop here
            if validation_result.get('stop_processing', False):
                logger.error(f"❌ [VALIDATION] Processing stopped due to critical failures")
                document.validation_status = ValidationStatus.FAIL
                document.validation_result = validation_result
                document.is_processed = False
                db.commit()

                # Notify driver to re-upload
                self._notify_driver_reupload(document, document.quality_score or 0, db)
                return

            # ============================================
            # STEP 9: FINALIZE & LEARN
            # ============================================
            document.is_processed = True
            # Validation status already set by _validate_document_rules
            document.updated_at = func.now()
            db.commit()

            processing_time = time.time() - start_time
            doc_type_name = document.document_type.value if document.document_type else "Unknown"

            # Agent learns from this processing
            self.agent.learn_from_result(
                doc_id=str(document.id),
                strategy_used=strategy['strategy'],
                actual_time=processing_time,
                actual_quality=quality_score if quality_score else 0,
                classification_confidence=document.classification_confidence if hasattr(document, 'classification_confidence') else 0.0
            )

            logger.info(f"✅ [AI AGENT] Processing complete in {processing_time:.2f}s")
            logger.info(f"   Strategy: {strategy['strategy']}")
            logger.info(f"   Quality: {quality_score}%")
            logger.info(f"   Type: {doc_type_name}")
            logger.info(f"   Confidence: {document.classification_confidence:.1%}" if hasattr(document, 'classification_confidence') else "")
            logger.info(f"   Estimated time: {strategy['estimated_time_seconds']}s (actual: {processing_time:.1f}s)")

        except Exception as e:
            logger.error(f"❌ [AI AGENT] Error processing document {document_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # Update document with error
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.processing_error = str(e)
                    document.validation_status = ValidationStatus.FAIL
                    db.commit()
            except:
                pass

    def _run_ocr(self, document: Document, db: Session) -> tuple:
        """
        Run OCR extraction with timeout protection

        Returns:
            Tuple of (extracted_text, confidence)
        """
        try:
            logger.info(f"📄 Running OCR on document {document.id}: {document.file_path}")

            # Verify file exists
            import os
            if not os.path.exists(document.file_path):
                logger.error(f"❌ File not found: {document.file_path}")
                document.ocr_text = "ERROR: File not found"
                db.commit()
                return "", 0.0

            # Extract text using EasyOCR with timeout protection
            import signal
            from contextlib import contextmanager

            @contextmanager
            def timeout_context(seconds):
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"OCR extraction timed out after {seconds} seconds")

                # Set up timeout (Windows doesn't support signal.SIGALRM, so we skip it)
                try:
                    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(seconds)
                except AttributeError:
                    # Windows - no signal.SIGALRM, just proceed without timeout
                    pass

                try:
                    yield
                finally:
                    try:
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, old_handler)
                    except AttributeError:
                        pass

            # Try OCR extraction (with 60 second timeout on Unix systems)
            try:
                text, confidence = easyocr_service.extract_text(
                    document.file_path,
                    document.file_type
                )
            except TimeoutError as te:
                logger.error(f"⏱️ OCR timeout: {te}")
                document.ocr_text = "ERROR: OCR processing timed out"
                db.commit()
                return "", 0.0
            except Exception as ocr_error:
                logger.error(f"❌ OCR extraction failed: {ocr_error}")
                import traceback
                logger.error(traceback.format_exc())
                document.ocr_text = f"ERROR: {str(ocr_error)}"
                db.commit()
                return "", 0.0

            # Log the extraction result
            logger.info(f"📝 OCR Result: {len(text) if text else 0} characters, confidence: {confidence:.2f}")

            # Save OCR text to document (even if empty)
            if text and len(text.strip()) > 0:
                document.ocr_text = text
                logger.info(f"✅ OCR text saved: First 100 chars: {text[:100]}...")
            else:
                document.ocr_text = "[No text extracted - may be blank or unreadable]"
                logger.warning(f"⚠️ No text extracted from document")

            # Force update of updated_at timestamp
            document.updated_at = func.now()

            db.commit()

            logger.info(f"✅ OCR completed: {len(text) if text else 0} characters extracted (confidence: {confidence:.2f})")
            return text, confidence

        except Exception as e:
            logger.error(f"❌ OCR failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            document.ocr_text = f"ERROR: {str(e)}"
            db.commit()
            return "", 0.0

    def _run_gemini_analysis(self, document: Document, easyocr_text: str, db: Session) -> dict:
        """
        Run Gemini Vision analysis for enhanced OCR and signature detection

        Args:
            document: Document to analyze
            easyocr_text: Text from EasyOCR
            db: Database session

        Returns:
            Gemini analysis result dictionary
        """
        try:
            logger.info(f"🤖 Running Gemini Vision analysis on document {document.id}")

            # Get Gemini analyzer
            gemini_analyzer = get_gemini_analyzer()

            if not gemini_analyzer.available:
                logger.warning(f"⚠️  Gemini not available, skipping enhanced analysis")
                return {"error": "Gemini not available"}

            # Load image from file
            import cv2
            from pdf2image import convert_from_path

            # Convert PDF to image or load image
            if document.file_type.lower() == 'pdf':
                images = convert_from_path(document.file_path, dpi=300, first_page=1, last_page=1)
                if images:
                    import numpy as np
                    image_np = np.array(images[0])
                else:
                    logger.error(f"❌ Failed to convert PDF to image")
                    return {"error": "PDF conversion failed"}
            else:
                image_np = cv2.imread(document.file_path)
                if image_np is None:
                    logger.error(f"❌ Failed to load image")
                    return {"error": "Image load failed"}

            # Run Gemini analysis
            gemini_result = gemini_analyzer.analyze_document(image_np, easyocr_text)

            if "error" in gemini_result:
                logger.warning(f"⚠️  Gemini analysis error: {gemini_result['error']}")
                return gemini_result

            # Combine OCR texts
            gemini_text = gemini_result.get("extracted_text", "")
            combined_text = gemini_analyzer.combine_ocr_results(
                easyocr_text,
                gemini_text,
                gemini_result.get('confidence', 0.0)
            )

            # Always update document with combined/improved OCR text
            if combined_text and len(combined_text.strip()) > 0:
                document.ocr_text = combined_text
                logger.info(f"✅ Updated OCR text with combined result ({len(combined_text)} chars)")
                logger.info(f"   EasyOCR: {len(easyocr_text)} chars, Gemini: {len(gemini_text)} chars, Combined: {len(combined_text)} chars")
            elif easyocr_text:
                # If combination failed, at least keep EasyOCR text
                document.ocr_text = easyocr_text
                logger.info(f"✅ Using EasyOCR text ({len(easyocr_text)} chars)")

            # Force update timestamp
            document.updated_at = func.now()
            db.commit()

            logger.info(f"✅ Gemini analysis complete: {gemini_result.get('signatures', {}).get('count', 0)} signatures detected")
            return gemini_result

        except Exception as e:
            logger.error(f"❌ Gemini analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    def _run_quality_check(self, document: Document, db: Session) -> float:
        """
        Run quality assessment

        Returns:
            Quality score (0-100)
        """
        try:
            logger.info(f"🔍 Running quality check on document {document.id}")

            # Verify file exists
            import os
            if not os.path.exists(document.file_path):
                logger.error(f"❌ File not found for quality check: {document.file_path}")
                document.quality_score = 0.0
                document.readability_status = ReadabilityStatus.UNREADABLE
                document.is_blurry = True
                document.is_skewed = False
                db.commit()
                return 0.0

            # Assess quality
            quality_result = quality_service.assess_quality(
                document.file_path,
                document.file_type
            )

            # Log the quality result details
            logger.info(f"📊 Quality Result: {quality_result}")

            # Update document with all quality metrics
            document.quality_score = float(quality_result['quality_score'])
            document.readability_status = ReadabilityStatus(quality_result['readability_status'])
            document.is_blurry = bool(quality_result['is_blurry'])
            document.is_skewed = bool(quality_result['is_skewed'])

            # Force update of updated_at timestamp
            document.updated_at = func.now()

            db.commit()

            logger.info(f"✅ Quality check completed: Score={quality_result['quality_score']}%, Blurry={quality_result['is_blurry']}, Skewed={quality_result['is_skewed']}, Status={quality_result['readability_status']}")
            return float(quality_result['quality_score'])

        except Exception as e:
            logger.error(f"❌ Quality check failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            document.quality_score = 0.0
            document.readability_status = ReadabilityStatus.UNREADABLE
            document.is_blurry = True
            document.is_skewed = False
            db.commit()
            return 0.0

    def _classify_document(self, document: Document, gemini_result: dict, db: Session):
        """
        Classify document type using multi-signal approach (embedding + keyword + Gemini)

        Args:
            document: Document to classify
            gemini_result: Result from Gemini analysis (includes extracted text)
            db: Database session
        """
        try:
            logger.info(f"🏷️ Classifying document {document.id}")

            # Get combined OCR text (from document.ocr_text which is already set)
            combined_text = document.ocr_text or ""

            if not combined_text or len(combined_text.strip()) < 20:
                logger.warning(f"⚠️ Insufficient text for classification, using Unknown")
                document.document_type = DocumentType.UNKNOWN
                document.classification_confidence = 0.0
                db.commit()
                return

            # Get sample-based classifier (uses embedding + keyword + Gemini with weighted voting)
            classifier = get_sample_based_classifier()
            classification_result = classifier.classify(
                extracted_text=combined_text,
                image_path=document.file_path,
                db=db
            )

            # Map result to DocumentType enum
            doc_type_str = classification_result["doc_type"]
            try:
                document.document_type = DocumentType(doc_type_str)
            except ValueError:
                logger.warning(f"⚠️ Unknown document type: {doc_type_str}, using UNKNOWN")
                document.document_type = DocumentType.UNKNOWN

            document.classification_confidence = classification_result["confidence"]

            # Store classification metadata
            if not document.extracted_metadata:
                document.extracted_metadata = {}

            document.extracted_metadata["classification_method"] = classification_result["method_used"]
            document.extracted_metadata["classification_signals"] = classification_result.get("signals_used", [])
            document.extracted_metadata["classification_status"] = classification_result["confidence_status"]

            # Save vote breakdown if available
            if "vote_breakdown" in classification_result:
                document.extracted_metadata["classification_votes"] = classification_result["vote_breakdown"]

            # Save classification result to tracking table
            try:
                classification_record = ClassificationResultModel(
                    document_id=document.id,
                    predicted_type=document.document_type,
                    confidence=classification_result["confidence"],
                    method=classification_result["method_used"],
                    matched_sample_id=classification_result.get("matched_sample_id"),
                    similarity_score=classification_result.get("vote_breakdown", {}).get("embedding", {}).get("confidence") if "vote_breakdown" in classification_result else None
                )
                db.add(classification_record)
            except Exception as e:
                logger.warning(f"Failed to save classification result to tracking table: {e}")

            db.commit()

            signals_info = f" using {', '.join(classification_result.get('signals_used', []))}" if classification_result.get('signals_used') else ""
            logger.info(f"✅ Classification: {doc_type_str} (confidence: {classification_result['confidence']:.1%}, method: {classification_result['method_used']}{signals_info})")

        except Exception as e:
            logger.error(f"❌ Classification failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback to Unknown
            document.document_type = DocumentType.UNKNOWN
            document.classification_confidence = 0.0
            db.commit()

    def _set_static_signature(self, document: Document, db: Session):
        """Set static signature detection - 1 signature, True (DEPRECATED - using Gemini)"""
        try:
            logger.info(f"✍️ Setting static signature for document {document.id}")

            # Static values
            document.has_signature = True
            document.signature_count = 1
            db.commit()

            logger.info(f"✅ Signature: 1 signature found (static)")

        except Exception as e:
            logger.error(f"❌ Signature setting failed: {e}")

    def _update_signature_from_gemini(self, document: Document, gemini_result: dict, db: Session):
        """
        Update signature information from Gemini Vision analysis
        Includes validation and smart fallback logic
        """
        try:
            logger.info(f"✍️ Updating signature info from Gemini for document {document.id}")

            # Extract signature info from Gemini result
            signatures = gemini_result.get('signatures', {})

            if "error" in gemini_result:
                # Fallback to reasonable defaults if Gemini failed
                logger.warning(f"⚠️  Gemini not available, using default signature values")
                document.has_signature = bool(False)  # Conservative: assume no signature
                document.signature_count = int(0)

                # Store error info
                if not document.extracted_metadata:
                    document.extracted_metadata = {}
                document.extracted_metadata['signature_detection_error'] = str(gemini_result.get('error'))

            else:
                # Use Gemini detected signatures
                signature_count = signatures.get('count', 0)
                has_signature = signatures.get('present', False)

                # ============================================
                # VALIDATION: Ensure results make sense
                # ============================================

                # Validate count (most documents have 0-5 signatures)
                if signature_count > 10:
                    logger.warning(f"⚠️  Suspicious signature count: {signature_count}. Capping at 10.")
                    signature_count = 10

                if signature_count < 0:
                    logger.warning(f"⚠️  Negative signature count: {signature_count}. Setting to 0.")
                    signature_count = 0

                # Validate consistency (if count > 0, has_signature should be true)
                if signature_count > 0 and not has_signature:
                    logger.warning(f"⚠️  Inconsistent: count={signature_count} but present=False. Fixing.")
                    has_signature = True

                if signature_count == 0 and has_signature:
                    logger.warning(f"⚠️  Inconsistent: count=0 but present=True. Fixing.")
                    has_signature = False

                # Update document with validated values
                document.has_signature = bool(has_signature)
                document.signature_count = int(signature_count)

                # Store signature details with validation
                signature_details = signatures.get('details', [])
                if signature_details:
                    # Validate details count matches signature count
                    if len(signature_details) != signature_count:
                        logger.warning(f"⚠️  Detail count mismatch: {len(signature_details)} details for {signature_count} signatures")

                    if not document.extracted_metadata:
                        document.extracted_metadata = {}
                    document.extracted_metadata['signature_details'] = signature_details

                    # Log each signature found
                    for idx, sig_detail in enumerate(signature_details, 1):
                        location = sig_detail.get('location', 'unknown')
                        signer = sig_detail.get('signer', 'unknown')
                        sig_type = sig_detail.get('type', 'unknown')
                        logger.info(f"   Signature {idx}: {sig_type} by {signer} at {location}")

                # Store confidence if available
                confidence = signatures.get('confidence')
                if confidence:
                    if not document.extracted_metadata:
                        document.extracted_metadata = {}
                    document.extracted_metadata['signature_confidence'] = confidence

                logger.info(f"✅ Signature from Gemini: {signature_count} signature(s), present={has_signature}")

            db.commit()

        except Exception as e:
            logger.error(f"❌ Signature update failed: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # Safe fallback with explicit type conversion
            document.has_signature = bool(False)
            document.signature_count = int(0)

            # Store error for debugging
            if not document.extracted_metadata:
                document.extracted_metadata = {}
            document.extracted_metadata['signature_update_error'] = str(e)

            db.commit()

    def _set_static_metadata(self, document: Document, db: Session):
        """Set static metadata values (DEPRECATED - using Gemini extracted values)"""
        try:
            logger.info(f"📊 Setting static metadata for document {document.id}")

            # Static values
            document.order_number = "ORD-2026-001"
            document.invoice_number = "INV-2026-001"
            document.document_date = "2026-02-20"
            document.load_number = None  # Not needed
            document.extracted_metadata = {
                "order_number": "ORD-2026-001",
                "invoice_number": "INV-2026-001",
                "document_date": "2026-02-20",
                "static_data": True
            }
            db.commit()

            logger.info(f"✅ Metadata: Order# ORD-2026-001, Invoice# INV-2026-001, Date: 2026-02-20")

        except Exception as e:
            logger.error(f"❌ Metadata setting failed: {e}")

    def _update_metadata_from_gemini(self, document: Document, gemini_result: dict, db: Session):
        """Update metadata from Gemini Vision analysis (BOL#, Client Name, Date)"""
        try:
            logger.info(f"📊 Updating metadata from Gemini for document {document.id}")

            # Extract fields from Gemini result
            fields = gemini_result.get('extracted_fields', {})

            if "error" in gemini_result or not fields:
                # Gemini failed - leave fields as NULL
                logger.warning(f"⚠️  Gemini fields not available, leaving order_number as NULL")
                document.order_number = None
                document.invoice_number = None
                document.document_date = None
            else:
                # Use Gemini extracted fields

                # BOL Number / Order Number (check multiple variations)
                bol_number = (
                    fields.get('bol_number') or
                    fields.get('bol_numbers') or
                    fields.get('order_number') or
                    fields.get('order_numbers')
                )

                # Handle if it's a list
                if isinstance(bol_number, list) and len(bol_number) > 0:
                    bol_number = bol_number[0]

                if bol_number:
                    # Ensure it's a string and clean it
                    bol_number = str(bol_number).strip()
                    document.order_number = bol_number
                    logger.info(f"   ✅ BOL/Order Number from Gemini: {bol_number}")
                else:
                    document.order_number = None
                    logger.warning(f"   ⚠️  No BOL/Order number found in Gemini extraction")
                    logger.warning(f"   Available Gemini fields: {list(fields.keys())}")

                # Client Name (from extracted_metadata as it's not in main model)
                client_name = fields.get('client_name')
                if client_name:
                    if not document.extracted_metadata:
                        document.extracted_metadata = {}
                    document.extracted_metadata['client_name'] = client_name
                    logger.info(f"   ✅ Client Name from Gemini: {client_name}")

                # Document Date
                doc_date = fields.get('document_date')
                if doc_date:
                    document.document_date = doc_date
                    logger.info(f"   ✅ Document Date from Gemini: {doc_date}")
                else:
                    document.document_date = None
                    logger.warning(f"   ⚠️  No document date found, keeping as NULL")

                # Invoice Number
                invoice_num = fields.get('invoice_numbers')
                if invoice_num and isinstance(invoice_num, list) and len(invoice_num) > 0:
                    document.invoice_number = invoice_num[0]
                    logger.info(f"   ✅ Invoice Number from Gemini: {invoice_num[0]}")
                else:
                    document.invoice_number = None
                    logger.warning(f"   ⚠️  No invoice number found, keeping as NULL")

                # Consignee (store in metadata)
                consignee = fields.get('consignee')
                if consignee:
                    if not document.extracted_metadata:
                        document.extracted_metadata = {}
                    document.extracted_metadata['consignee'] = consignee
                    logger.info(f"   ✅ Consignee from Gemini: {consignee}")

                # Store all extracted fields
                if not document.extracted_metadata:
                    document.extracted_metadata = {}
                document.extracted_metadata['gemini_fields'] = fields
                document.extracted_metadata['extraction_source'] = 'gemini'

                logger.info(f"✅ Metadata from Gemini: BOL# {document.order_number}, Date: {document.document_date}")

            db.commit()

        except Exception as e:
            logger.error(f"❌ Metadata update failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Keep as NULL - don't use static fallback
            document.order_number = None
            document.invoice_number = None
            document.document_date = None
            db.commit()

    def _run_classification(self, document: Document, db: Session):
        """Run document classification (DEPRECATED - now using _classify_document)"""
        try:
            logger.info(f"🏷️ Classifying document {document.id} (using new multi-signal classifier)")

            # Use new classification method instead
            self._classify_document(document, {}, db)

            logger.info(f"✅ Classification complete")

        except Exception as e:
            logger.error(f"❌ Classification failed: {e}")

    def _run_signature_detection(self, document: Document, db: Session):
        """Run signature detection (DEPRECATED - using static values)"""
        try:
            logger.info(f"✍️ Detecting signatures in document {document.id}")

            # Detect signatures
            signature_result = signature_service.detect_signature(
                document.file_path,
                document.file_type
            )

            # Update document
            document.has_signature = signature_result['has_signature']
            document.signature_count = signature_result['signature_count']
            db.commit()

            logger.info(f"✅ Signature detection: {signature_result['signature_count']} signature(s) found")

        except Exception as e:
            logger.error(f"❌ Signature detection failed: {e}")

    def _run_metadata_extraction(self, document: Document, db: Session):
        """Run metadata extraction (DEPRECATED - using static values)"""
        try:
            logger.info(f"📊 Extracting metadata from document {document.id}")

            # Extract metadata
            metadata_result = metadata_service.extract_metadata(
                document.ocr_text,
                document.document_type
            )

            # Update document
            document.order_number = metadata_result.get('order_number')
            document.load_number = metadata_result.get('load_number')
            document.invoice_number = metadata_result.get('invoice_number')
            document.document_date = metadata_result.get('document_date')
            document.extracted_metadata = metadata_result
            db.commit()

            logger.info(f"✅ Metadata extraction completed")

        except Exception as e:
            logger.error(f"❌ Metadata extraction failed: {e}")

    def _notify_driver_reupload(self, document: Document, quality_score: float, db: Session):
        """
        Send notification to driver to re-upload document

        This is a placeholder for actual notification implementation
        (e.g., push notification, SMS, email, etc.)
        """
        try:
            logger.info(f"📢 Sending re-upload notification for document {document.id}")

            # TODO: Implement actual notification logic here
            # For now, just log it
            notification_message = {
                "document_id": document.id,
                "filename": document.original_filename,
                "quality_score": quality_score,
                "message": f"Please re-upload: Document quality is too low ({quality_score}%). Please take a clearer photo.",
                "status": "REUPLOAD_REQUIRED"
            }

            logger.warning(f"📱 NOTIFICATION: {notification_message}")

            # You can implement:
            # - Push notification via Firebase/OneSignal
            # - SMS via Twilio
            # - Email notification
            # - WebSocket message
            # - Database notification table

        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")

    def _extract_document_fields(self, document: Document, gemini_result: dict, db: Session):
        """
        Extract document-type specific fields based on document classification
        Called after classification completes

        Args:
            document: Document to extract fields from
            gemini_result: Gemini analysis result (contains extracted_fields)
            db: Database session
        """
        try:
            logger.info(f"📋 [FIELD EXTRACTION] Starting for {document.document_type.value}...")

            # Skip if document type is Unknown
            if document.document_type == DocumentType.UNKNOWN:
                logger.warning("⚠️  Skipping field extraction for Unknown document type")
                return

            # Get enhanced metadata extractor
            extractor = get_enhanced_metadata_extractor()

            # Get fields already extracted by Gemini
            gemini_fields = gemini_result.get('extracted_fields', {}) if gemini_result else {}

            # Extract document-type specific fields
            extracted_fields = extractor.extract_fields(
                text=document.ocr_text or "",
                doc_type=document.document_type,
                gemini_extracted_fields=gemini_fields
            )

            # Store extracted fields in document metadata
            if not document.extracted_metadata:
                document.extracted_metadata = {}

            # Add document-type specific fields to metadata
            document.extracted_metadata['doc_type_fields'] = extracted_fields

            # Validate completeness
            validation = extractor.validate_completeness(extracted_fields, threshold=0.5)
            document.extracted_metadata['field_extraction_validation'] = validation

            # Update common fields in main document columns
            self._update_main_fields_from_extracted(document, extracted_fields)

            db.commit()

            # Log results
            extraction_score = extracted_fields.get('_extraction_score', 0.0)
            filled_count = extracted_fields.get('_filled_fields', 0)
            total_count = extracted_fields.get('_total_fields', 0)

            logger.info(f"✅ [FIELD EXTRACTION] Complete: {filled_count}/{total_count} fields ({extraction_score:.0%})")

            if validation['is_complete']:
                logger.info(f"   ✅ Document is complete ({extraction_score:.0%} >= 50% threshold)")
            else:
                logger.warning(f"   ⚠️  Document is incomplete ({extraction_score:.0%} < 50% threshold)")
                logger.warning(f"   📢 May need manual review or re-upload")

        except Exception as e:
            logger.error(f"❌ [FIELD EXTRACTION] Failed: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _update_main_fields_from_extracted(self, document: Document, extracted_fields: Dict):
        """
        Update main document columns from extracted fields
        Maps common fields across document types

        Args:
            document: Document to update
            extracted_fields: Extracted fields dictionary
        """
        try:
            # Order Number (common across most docs)
            if extracted_fields.get('order_number') and not document.order_number:
                document.order_number = extracted_fields['order_number']
                logger.info(f"   📝 Updated order_number: {document.order_number}")

            # Invoice Number (for invoices)
            if extracted_fields.get('invoice_number') and not document.invoice_number:
                document.invoice_number = extracted_fields['invoice_number']
                logger.info(f"   📝 Updated invoice_number: {document.invoice_number}")

            # Date fields (multiple variations)
            date_value = (
                extracted_fields.get('ship_date') or
                extracted_fields.get('delivery_date') or
                extracted_fields.get('invoice_date') or
                extracted_fields.get('packing_date') or
                extracted_fields.get('date')
            )
            if date_value and not document.document_date:
                document.document_date = date_value
                logger.info(f"   📝 Updated document_date: {document.document_date}")

            # BOL Number (specific to BOL)
            if extracted_fields.get('bol_number'):
                if not document.extracted_metadata:
                    document.extracted_metadata = {}
                document.extracted_metadata['bol_number'] = extracted_fields['bol_number']
                logger.info(f"   📝 Stored bol_number: {extracted_fields['bol_number']}")

        except Exception as e:
            logger.warning(f"⚠️  Error updating main fields: {e}")

    def _validate_document_rules(self, document: Document, db: Session) -> Dict:
        """
        Validate document against general and document-specific rules

        Args:
            document: Document to validate
            db: Database session

        Returns:
            Validation result dictionary
        """
        try:
            logger.info(f"✅ [VALIDATION] Validating document {document.id} against rules...")

            # Convert document to dict for validation engine
            document_dict = {
                "document_type": document.document_type,
                "quality_score": document.quality_score,
                "is_blurry": document.is_blurry,
                "is_skewed": document.is_skewed,
                "ocr_text": document.ocr_text,
                "classification_confidence": document.classification_confidence,
                "signature_count": document.signature_count,
                "order_number": document.order_number,
                "invoice_number": document.invoice_number,
                "document_date": document.document_date,
                "metadata": document.extracted_metadata or {}
            }

            # Get validation engine and run validation
            validation_engine = get_validation_engine()
            validation_result = validation_engine.validate_document(document_dict)

            # Update document with validation results
            document.validation_status = validation_result['validation_status_enum']
            document.validation_result = validation_result

            db.commit()

            # Log summary
            status = validation_result['status']
            hard_failures = len(validation_result['hard_failures'])
            soft_warnings = len(validation_result['soft_warnings'])

            if status == "Pass":
                logger.info(f"✅ [VALIDATION] Document passed all rules ({validation_result['score']:.0%})")
            elif status == "Pass with Warnings":
                logger.warning(f"⚠️  [VALIDATION] Document passed with {soft_warnings} warning(s)")
            else:
                logger.error(f"❌ [VALIDATION] Document failed with {hard_failures} hard failure(s)")

            return validation_result

        except Exception as e:
            logger.error(f"❌ [VALIDATION] Validation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # Set as needs review on error
            document.validation_status = ValidationStatus.NEEDS_REVIEW
            document.validation_result = {
                "status": "Needs Review",
                "error": str(e)
            }
            db.commit()

            return {
                "status": "Needs Review",
                "stop_processing": False,
                "error": str(e)
            }

    # ============================================
    # THREAD-SAFE METHODS FOR CONCURRENT PROCESSING
    # Each method creates its own database session to avoid conflicts
    # ============================================

    def _classify_document_safe(self, document_id: int, gemini_result: dict) -> dict:
        """
        Thread-safe wrapper for document classification.
        Creates its own database session to avoid conflicts during concurrent execution.

        Args:
            document_id: Document ID to classify
            gemini_result: Result from Gemini analysis

        Returns:
            Classification result dictionary
        """
        from database import SessionLocal
        db = SessionLocal()

        try:
            logger.info(f"🏷️  [CONCURRENT] Classifying document {document_id}...")

            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return {"error": "Document not found"}

            # Run classification
            self._classify_document(document, gemini_result, db)

            return {
                "success": True,
                "doc_type": document.document_type.value if document.document_type else "Unknown",
                "confidence": document.classification_confidence
            }

        except Exception as e:
            logger.error(f"❌ [CONCURRENT] Classification failed: {e}")
            return {"error": str(e)}

        finally:
            db.close()

    def _update_signature_from_gemini_safe(self, document_id: int, gemini_result: dict) -> dict:
        """
        Thread-safe wrapper for signature detection.
        Creates its own database session to avoid conflicts during concurrent execution.

        Args:
            document_id: Document ID
            gemini_result: Result from Gemini analysis

        Returns:
            Signature detection result dictionary
        """
        from database import SessionLocal
        db = SessionLocal()

        try:
            logger.info(f"✍️  [CONCURRENT] Detecting signatures for document {document_id}...")

            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return {"error": "Document not found"}

            # Run signature detection
            self._update_signature_from_gemini(document, gemini_result, db)

            return {
                "success": True,
                "signature_count": document.signature_count,
                "has_signature": document.has_signature
            }

        except Exception as e:
            logger.error(f"❌ [CONCURRENT] Signature detection failed: {e}")
            return {"error": str(e)}

        finally:
            db.close()

    def _update_metadata_from_gemini_safe(self, document_id: int, gemini_result: dict) -> dict:
        """
        Thread-safe wrapper for metadata extraction.
        Creates its own database session to avoid conflicts during concurrent execution.

        Args:
            document_id: Document ID
            gemini_result: Result from Gemini analysis

        Returns:
            Metadata extraction result dictionary
        """
        from database import SessionLocal
        db = SessionLocal()

        try:
            logger.info(f"📋 [CONCURRENT] Extracting metadata for document {document_id}...")

            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return {"error": "Document not found"}

            # Run metadata extraction
            self._update_metadata_from_gemini(document, gemini_result, db)

            return {
                "success": True,
                "order_number": document.order_number,
                "client_name": document.extracted_metadata.get('client_name') if document.extracted_metadata else None,
                "document_date": document.document_date
            }

        except Exception as e:
            logger.error(f"❌ [CONCURRENT] Metadata extraction failed: {e}")
            return {"error": str(e)}

        finally:
            db.close()


# Singleton instance
background_processor = BackgroundProcessor()

