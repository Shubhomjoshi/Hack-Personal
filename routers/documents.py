"""
Document routes - Upload, process, and manage documents
"""
import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User, Document, DocumentType, ValidationStatus
from schemas import (
    DocumentUploadResponse, DocumentResponse, DocumentListResponse,
    DocumentProcessingResult, MessageResponse
)
from auth import get_current_user
from services.processing_service import processing_service
from services.display_config import get_display_config, get_primary_identifier

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

# Upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    customer_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing

    - **file**: PDF or image file (JPEG, PNG)
    - **customer_id**: Customer ID for customer-specific validation rules (optional)

    The document will be saved immediately and processed in the background.
    OCR engine will extract text, check quality, and update status.
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )

    # Get file size
    file_size = os.path.getsize(file_path)

    # Create document record in database
    document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_ext.replace('.', ''),
        uploaded_by=current_user.id,
        customer_id=customer_id,
        is_processed=False,
        validation_status=ValidationStatus.PENDING
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Start background processing (OCR + Quality Check)
    def process_in_background(doc_id: int):
        from database import SessionLocal
        from services.background_processor import background_processor

        db_session = SessionLocal()
        try:
            background_processor.process_document_async(doc_id, db_session)
        except Exception as e:
            import logging
            logging.error(f"Background processing failed: {e}")
        finally:
            db_session.close()

    background_tasks.add_task(process_in_background, document.id)

    return DocumentUploadResponse(
        document_id=document.id,
        filename=unique_filename,
        file_size=file_size,
        message="Uploaded Successfully",
        web_status="Sent to Imaging",
        mob_status="Uploaded Successfully - Verification Pending",
        processing_started=True
    )


@router.post("/upload-multiple", response_model=List[DocumentUploadResponse])
async def upload_multiple_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    customer_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload multiple documents at once

    - **files**: List of PDF or image files
    - **customer_id**: Customer ID for customer-specific validation rules (optional)
    """
    results = []

    for file in files:
        try:
            # Validate file type
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff']
            file_ext = os.path.splitext(file.filename)[1].lower()

            if file_ext not in allowed_extensions:
                results.append(DocumentUploadResponse(
                    document_id=0,
                    filename=file.filename,
                    file_size=0,
                    message=f"File type not supported: {file_ext}",
                    processing_started=False
                ))
                continue

            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            file_size = os.path.getsize(file_path)

            # Create document record
            document = Document(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_ext.replace('.', ''),
                uploaded_by=current_user.id,
                customer_id=customer_id,
                is_processed=False
            )

            db.add(document)
            db.commit()
            db.refresh(document)

            # Process in background
            background_tasks.add_task(processing_service.process_document, document, db)

            results.append(DocumentUploadResponse(
                document_id=document.id,
                filename=unique_filename,
                file_size=file_size,
                message="Uploaded successfully",
                processing_started=True
            ))

        except Exception as e:
            results.append(DocumentUploadResponse(
                document_id=0,
                filename=file.filename,
                file_size=0,
                message=f"Upload failed: {str(e)}",
                processing_started=False
            ))

    return results


@router.get("/", response_model=DocumentListResponse)
def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    document_type: Optional[str] = None,
    validation_status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of documents with pagination and filtering

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **document_type**: Filter by document type (optional)
    - **validation_status**: Filter by validation status (optional)
    """
    query = db.query(Document)

    # Filter by user (non-admin can only see their own documents)
    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    # Apply filters
    if document_type:
        try:
            doc_type_enum = DocumentType(document_type)
            query = query.filter(Document.document_type == doc_type_enum)
        except ValueError:
            pass

    if validation_status:
        query = query.filter(Document.validation_status == validation_status)

    # Get total count
    total = query.count()

    # Get paginated results
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    return DocumentListResponse(
        total=total,
        documents=documents
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID

    Returns complete document information including processing results
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check permissions
    if not current_user.is_admin and document.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this document"
        )

    return document


@router.post("/{document_id}/reprocess", response_model=MessageResponse)
async def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reprocess a document

    Useful if processing failed or if you want to re-run validation
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check permissions
    if not current_user.is_admin and document.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reprocess this document"
        )

    # Reset processing flags
    document.is_processed = False
    document.processing_error = None
    db.commit()

    # Reprocess in background
    background_tasks.add_task(processing_service.process_document, document, db)

    return MessageResponse(
        message=f"Document {document_id} is being reprocessed",
        success=True
    )


@router.delete("/{document_id}", response_model=MessageResponse)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document

    Removes document record and associated file
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check permissions
    if not current_user.is_admin and document.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this document"
        )

    # Delete file
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            print(f"Warning: Could not delete file: {str(e)}")

    # Delete database record
    db.delete(document)
    db.commit()

    return MessageResponse(
        message=f"Document {document_id} deleted successfully",
        success=True
    )


@router.get("/{document_id}/text", response_model=dict)
def get_document_text(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get extracted OCR text from document
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check permissions
    if not current_user.is_admin and document.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this document"
        )

    return {
        "document_id": document.id,
        "filename": document.original_filename,
        "text": document.ocr_text or "No text extracted yet",
        "is_processed": document.is_processed
    }


@router.post("/{document_id}/test-process", response_model=dict)
def test_process_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test document processing - run synchronously and return detailed results

    This endpoint is for debugging - it processes the document immediately
    and returns detailed results including any errors.
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check permissions
    if not current_user.is_admin and document.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to process this document"
        )

    # Process the document synchronously
    try:
        results = processing_service.process_document(document, db)
        return {
            "success": True,
            "message": "Processing completed",
            "results": results,
            "document": {
                "id": document.id,
                "document_type": document.document_type.value if document.document_type else "Unknown",
                "readability_status": document.readability_status.value if document.readability_status else None,
                "quality_score": document.quality_score,
                "signature_count": document.signature_count,
                "has_signature": document.has_signature,
                "order_number": document.order_number,
                "extracted_metadata": document.extracted_metadata,  # Contains client_name, consignee, etc.
                "validation_status": document.validation_status.value if document.validation_status else "Pending",
                "is_processed": document.is_processed
            }
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "Processing failed - see error details"
        }


# ============================================
# GENERIC DOCUMENT API - Works for ALL Doc Types
# ============================================

@router.get("/{document_id}/detail")
async def get_document_detail(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete document details with doc-type specific fields

    Returns everything needed to render the document:
    - Common fields (quality, signatures, status)
    - Document-type specific fields (BOL#, Invoice#, etc.)
    - Display configuration (what fields to show and how)

    Frontend uses this single endpoint for ALL document types!
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check permissions
    if not current_user.is_admin and document.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this document"
        )

    # Get metadata
    metadata = document.extracted_metadata or {}
    doc_type_fields = metadata.get('doc_type_fields', {})

    # Calculate page count (estimate from file size if not stored)
    page_count = 1  # Default
    if document.file_type and document.file_type.lower() == 'pdf':
        # Could implement actual page count here
        page_count = metadata.get('page_count', 1)

    return {
        # ── Common fields (always present) ──────────────
        "doc_id": document.id,
        "doc_type": document.document_type.value if document.document_type else "Unknown",
        "confidence": document.classification_confidence or 0.0,
        "upload_date": document.created_at.isoformat() if document.created_at else None,
        "uploaded_by": document.uploaded_by,
        "page_count": page_count,
        "quality_score": document.quality_score or 0.0,
        "quality_status": document.readability_status.value if document.readability_status else "Unknown",
        "signature_count": document.signature_count or 0,
        "signature_present": (document.signature_count or 0) > 0,
        "validation_status": document.validation_status.value if document.validation_status else "Pending",
        "needs_review": metadata.get('field_extraction_validation', {}).get('is_complete', True) == False,
        "file_path": document.file_path,
        "filename": document.filename,

        # ── Document-type specific fields ──────────────
        "metadata": {
            # Core metadata (N/A for missing values)
            "order_number": document.order_number or "N/A",
            "invoice_number": document.invoice_number or "N/A",
            "document_date": document.document_date or "N/A",
            "client_name": metadata.get('client_name') or "N/A",

            # Classification info
            "classification_method": metadata.get('classification_method') or "N/A",
            "classification_confidence": document.classification_confidence or 0.0,

            # All doc-type specific fields (already handled by display_config)
            **doc_type_fields,

            # Extraction quality
            "_extraction_score": doc_type_fields.get('_extraction_score', 0.0),
            "_filled_fields": doc_type_fields.get('_filled_fields', 0),
            "_total_fields": doc_type_fields.get('_total_fields', 0),
        },

        # ── Display config for frontend ─────────────────
        # Tells frontend WHAT to show and in WHAT ORDER
        "display_fields": get_display_config(document.document_type, metadata),

        # ── Extraction quality info ─────────────────────
        "extraction_quality": metadata.get('field_extraction_validation', {
            "is_complete": True,
            "extraction_score": 1.0,
            "status": "complete"
        })
    }


@router.get("/list")
async def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    doc_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of documents with summary info

    Supports filtering by:
    - doc_type: Filter by document type (e.g., "Bill of Lading")
    - status: Filter by validation status (e.g., "Pass", "Needs Review")

    Returns summary row for each document showing:
    - Document type
    - Primary identifier (BOL#, Invoice#, etc.)
    - Quality and status
    """
    query = db.query(Document)

    # Filter by user (non-admins see only their docs)
    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    # Filter by document type
    if doc_type:
        try:
            doc_type_enum = DocumentType(doc_type)
            query = query.filter(Document.document_type == doc_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type: {doc_type}"
            )

    # Filter by validation status
    if status:
        try:
            status_enum = ValidationStatus(status)
            query = query.filter(Document.validation_status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )

    # Get total count
    total = query.count()

    # Paginate
    documents = query.order_by(Document.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    # Build response
    document_list = []
    for doc in documents:
        metadata = doc.extracted_metadata or {}

        document_list.append({
            "doc_id": doc.id,
            "doc_type": doc.document_type.value if doc.document_type else "Unknown",
            "primary_id": get_primary_identifier(doc.document_type, metadata),
            "upload_date": doc.created_at.isoformat() if doc.created_at else None,
            "quality_score": doc.quality_score or 0.0,
            "signature_count": doc.signature_count or 0,
            "status": doc.validation_status.value if doc.validation_status else "Pending",
            "needs_review": metadata.get('field_extraction_validation', {}).get('is_complete', True) == False,
            "confidence": doc.classification_confidence or 0.0,
            "filename": doc.filename,
        })

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "documents": document_list
    }


@router.get("/stats")
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get document statistics for dashboard

    Returns counts by document type, status, etc.
    """
    query = db.query(Document)

    # Filter by user (non-admins see only their docs)
    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    total_docs = query.count()

    # Count by document type
    doc_type_counts = {}
    for doc_type in DocumentType:
        count = query.filter(Document.document_type == doc_type).count()
        if count > 0:
            doc_type_counts[doc_type.value] = count

    # Count by validation status
    status_counts = {}
    for val_status in ValidationStatus:
        count = query.filter(Document.validation_status == val_status).count()
        if count > 0:
            status_counts[val_status.value] = count

    # Recent uploads (last 7 days)
    from datetime import datetime, timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_count = query.filter(Document.created_at >= seven_days_ago).count()

    return {
        "total_documents": total_docs,
        "by_doc_type": doc_type_counts,
        "by_status": status_counts,
        "recent_uploads": recent_count,
        "average_quality_score": db.query(func.avg(Document.quality_score)).filter(
            Document.uploaded_by == current_user.id if not current_user.is_admin else True
        ).scalar() or 0.0
    }

