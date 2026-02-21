"""
Document Processing Service - Orchestrates all document processing steps
"""
import os
import time
from typing import Dict, Any
from sqlalchemy.orm import Session
import logging

from models import Document, ProcessingLog, DocumentType, ReadabilityStatus, ValidationStatus
from services.ocr_service import ocr_service
from services.classification_service import classification_service
from services.quality_service import quality_service
from services.signature_service import signature_service
from services.metadata_service import metadata_service
from services.validation_service import validation_service

logger = logging.getLogger(__name__)


class DocumentProcessingService:
    """Service for processing documents end-to-end"""

    def process_document(self, document: Document, db: Session) -> Dict[str, Any]:
        """
        Process a document through all stages

        Args:
            document: Document to process
            db: Database session

        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        results = {
            'document_id': document.id,
            'filename': document.filename,
            'steps': []
        }

        try:
            # Step 1: OCR - Extract text
            logger.info(f"Processing document {document.id}: Step 1 - OCR")
            ocr_result = self._run_ocr(document, db)
            results['steps'].append(ocr_result)

            # Continue processing even if OCR had warnings (scanned PDFs)
            # Only stop if it completely failed
            if not ocr_result['success'] and 'error' in ocr_result:
                logger.warning("OCR failed completely, but continuing with limited processing")

            # Step 2: Classification
            logger.info(f"Processing document {document.id}: Step 2 - Classification")
            classification_result = self._run_classification(document, db)
            results['steps'].append(classification_result)

            # Step 3: Quality Assessment
            logger.info(f"Processing document {document.id}: Step 3 - Quality Assessment")
            quality_result = self._run_quality_assessment(document, db)
            results['steps'].append(quality_result)

            # Step 4: Signature Detection
            logger.info(f"Processing document {document.id}: Step 4 - Signature Detection")
            signature_result = self._run_signature_detection(document, db)
            results['steps'].append(signature_result)

            # Step 5: Metadata Extraction
            logger.info(f"Processing document {document.id}: Step 5 - Metadata Extraction")
            metadata_result = self._run_metadata_extraction(document, db)
            results['steps'].append(metadata_result)

            # Step 6: Validation
            logger.info(f"Processing document {document.id}: Step 6 - Validation")
            validation_result = self._run_validation(document, db)
            results['steps'].append(validation_result)

            # Mark as processed
            document.is_processed = True
            db.commit()

            results['success'] = True
            results['processing_time'] = time.time() - start_time

            logger.info(f"Document {document.id} processed successfully in {results['processing_time']:.2f}s")

        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            document.processing_error = str(e)
            db.commit()

            results['success'] = False
            results['error'] = str(e)
            results['processing_time'] = time.time() - start_time

        return results

    def _run_ocr(self, document: Document, db: Session) -> Dict[str, Any]:
        """Run OCR on document"""
        step_start = time.time()

        try:
            text, confidence = ocr_service.extract_text(
                document.file_path,
                document.file_type
            )

            document.ocr_text = text
            db.commit()

            # Check if this is an error message or scanned PDF warning
            is_error = "ERROR:" in text or "[SCANNED PDF" in text
            status = "WARNING" if is_error else "SUCCESS"

            # Log step
            log = ProcessingLog(
                document_id=document.id,
                step_name="OCR",
                status=status,
                execution_time=time.time() - step_start,
                details={'text_length': len(text), 'confidence': confidence, 'is_error': is_error}
            )
            db.add(log)
            db.commit()

            return {
                'step': 'OCR',
                'success': not is_error,  # Success if no error
                'data': {'text_length': len(text), 'confidence': confidence, 'warning': text if is_error else None}
            }

        except Exception as e:
            log = ProcessingLog(
                document_id=document.id,
                step_name="OCR",
                status="FAILED",
                execution_time=time.time() - step_start,
                error_message=str(e)
            )
            db.add(log)
            db.commit()

            return {'step': 'OCR', 'success': False, 'error': str(e)}

    def _run_classification(self, document: Document, db: Session) -> Dict[str, Any]:
        """Run document classification"""
        step_start = time.time()

        try:
            doc_type, confidence = classification_service.classify_document_advanced(
                document.ocr_text,
                document.original_filename
            )

            document.document_type = doc_type
            document.classification_confidence = confidence
            db.commit()

            log = ProcessingLog(
                document_id=document.id,
                step_name="Classification",
                status="SUCCESS",
                execution_time=time.time() - step_start,
                details={'document_type': doc_type.value, 'confidence': confidence}
            )
            db.add(log)
            db.commit()

            return {
                'step': 'Classification',
                'success': True,
                'data': {'document_type': doc_type.value, 'confidence': confidence}
            }

        except Exception as e:
            log = ProcessingLog(
                document_id=document.id,
                step_name="Classification",
                status="FAILED",
                execution_time=time.time() - step_start,
                error_message=str(e)
            )
            db.add(log)
            db.commit()

            return {'step': 'Classification', 'success': False, 'error': str(e)}

    def _run_quality_assessment(self, document: Document, db: Session) -> Dict[str, Any]:
        """Run quality assessment"""
        step_start = time.time()

        try:
            if document.file_type.lower() == 'pdf':
                quality_data = quality_service.assess_pdf_quality(document.file_path)
            else:
                quality_data = quality_service.calculate_quality_score(document.file_path)

            document.quality_score = quality_data['quality_score']
            document.readability_status = ReadabilityStatus(quality_data['readability_status'])
            document.is_blurry = quality_data['is_blurry']
            document.is_skewed = quality_data['is_skewed']
            db.commit()

            log = ProcessingLog(
                document_id=document.id,
                step_name="Quality Assessment",
                status="SUCCESS",
                execution_time=time.time() - step_start,
                details=quality_data
            )
            db.add(log)
            db.commit()

            return {
                'step': 'Quality Assessment',
                'success': True,
                'data': quality_data
            }

        except Exception as e:
            log = ProcessingLog(
                document_id=document.id,
                step_name="Quality Assessment",
                status="FAILED",
                execution_time=time.time() - step_start,
                error_message=str(e)
            )
            db.add(log)
            db.commit()

            return {'step': 'Quality Assessment', 'success': False, 'error': str(e)}

    def _run_signature_detection(self, document: Document, db: Session) -> Dict[str, Any]:
        """Run signature detection"""
        step_start = time.time()

        try:
            count, has_sig, confidence = signature_service.detect_signatures(
                document.file_path,
                document.file_type
            )

            document.signature_count = count
            document.has_signature = has_sig
            db.commit()

            log = ProcessingLog(
                document_id=document.id,
                step_name="Signature Detection",
                status="SUCCESS",
                execution_time=time.time() - step_start,
                details={'count': count, 'has_signature': has_sig, 'confidence': confidence}
            )
            db.add(log)
            db.commit()

            return {
                'step': 'Signature Detection',
                'success': True,
                'data': {'count': count, 'has_signature': has_sig, 'confidence': confidence}
            }

        except Exception as e:
            log = ProcessingLog(
                document_id=document.id,
                step_name="Signature Detection",
                status="FAILED",
                execution_time=time.time() - step_start,
                error_message=str(e)
            )
            db.add(log)
            db.commit()

            return {'step': 'Signature Detection', 'success': False, 'error': str(e)}

    def _run_metadata_extraction(self, document: Document, db: Session) -> Dict[str, Any]:
        """Run metadata extraction"""
        step_start = time.time()

        try:
            metadata = metadata_service.extract_all_metadata(document.ocr_text)

            document.order_number = metadata.get('order_number')
            document.load_number = metadata.get('load_number')
            document.invoice_number = metadata.get('invoice_number')
            document.document_date = metadata.get('formatted_date') or metadata.get('date')
            document.extracted_metadata = metadata
            db.commit()

            log = ProcessingLog(
                document_id=document.id,
                step_name="Metadata Extraction",
                status="SUCCESS",
                execution_time=time.time() - step_start,
                details=metadata
            )
            db.add(log)
            db.commit()

            return {
                'step': 'Metadata Extraction',
                'success': True,
                'data': metadata
            }

        except Exception as e:
            log = ProcessingLog(
                document_id=document.id,
                step_name="Metadata Extraction",
                status="FAILED",
                execution_time=time.time() - step_start,
                error_message=str(e)
            )
            db.add(log)
            db.commit()

            return {'step': 'Metadata Extraction', 'success': False, 'error': str(e)}

    def _run_validation(self, document: Document, db: Session) -> Dict[str, Any]:
        """Run document validation"""
        step_start = time.time()

        try:
            # Get applicable rules
            rules = validation_service.get_applicable_rules(
                document.document_type,
                document.customer_id,
                db
            )

            if rules:
                status, passed, failed = validation_service.validate_document(
                    document, rules, db
                )

                document.validation_status = ValidationStatus(status.value)
                document.validation_result = {
                    'status': status.value,
                    'passed_rules': passed,
                    'failed_rules': failed
                }
            else:
                # No rules = pass
                document.validation_status = ValidationStatus.PASS
                document.validation_result = {
                    'status': 'Pass',
                    'passed_rules': [],
                    'failed_rules': [],
                    'message': 'No validation rules defined for this document type'
                }

            db.commit()

            log = ProcessingLog(
                document_id=document.id,
                step_name="Validation",
                status="SUCCESS",
                execution_time=time.time() - step_start,
                details=document.validation_result
            )
            db.add(log)
            db.commit()

            return {
                'step': 'Validation',
                'success': True,
                'data': document.validation_result
            }

        except Exception as e:
            log = ProcessingLog(
                document_id=document.id,
                step_name="Validation",
                status="FAILED",
                execution_time=time.time() - step_start,
                error_message=str(e)
            )
            db.add(log)
            db.commit()

            return {'step': 'Validation', 'success': False, 'error': str(e)}


# Singleton instance
processing_service = DocumentProcessingService()

