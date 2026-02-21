"""
Analytics routes - Document processing statistics and insights
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from database import get_db
from models import User, Document, DocumentType, ValidationStatus, ReadabilityStatus
from schemas import DocumentStatistics
from auth import get_current_user

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/statistics", response_model=DocumentStatistics)
def get_document_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get overall document processing statistics

    Returns aggregated statistics including:
    - Total documents
    - Documents by type
    - Documents by validation status
    - Average quality score
    - Total documents with signatures
    - Validation pass rate
    """
    # Base query
    query = db.query(Document)

    # Filter by user (non-admin can only see their own documents)
    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    # Total documents
    total_documents = query.count()

    # Documents by type
    by_type = {}
    for doc_type in DocumentType:
        count = query.filter(Document.document_type == doc_type).count()
        if count > 0:
            by_type[doc_type.value] = count

    # Documents by status
    by_status = {}
    for status in ValidationStatus:
        count = query.filter(Document.validation_status == status).count()
        if count > 0:
            by_status[status.value] = count

    # Average quality score
    avg_quality = db.query(func.avg(Document.quality_score)).filter(
        Document.uploaded_by == current_user.id if not current_user.is_admin else True
    ).scalar() or 0.0

    # Total with signatures
    total_with_signatures = query.filter(Document.has_signature == True).count()

    # Validation pass rate
    total_validated = query.filter(Document.is_processed == True).count()
    total_passed = query.filter(Document.validation_status == ValidationStatus.PASS).count()
    validation_pass_rate = (total_passed / total_validated * 100) if total_validated > 0 else 0.0

    return DocumentStatistics(
        total_documents=total_documents,
        by_type=by_type,
        by_status=by_status,
        average_quality_score=round(avg_quality, 2),
        total_with_signatures=total_with_signatures,
        validation_pass_rate=round(validation_pass_rate, 2)
    )


@router.get("/quality-distribution")
def get_quality_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get distribution of document quality scores

    Returns count of documents in each quality range
    """
    query = db.query(Document)

    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    distribution = {
        "excellent_80_100": query.filter(Document.quality_score >= 80).count(),
        "good_60_79": query.filter(
            Document.quality_score >= 60,
            Document.quality_score < 80
        ).count(),
        "fair_40_59": query.filter(
            Document.quality_score >= 40,
            Document.quality_score < 60
        ).count(),
        "poor_0_39": query.filter(Document.quality_score < 40).count()
    }

    return distribution


@router.get("/readability-distribution")
def get_readability_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get distribution of document readability status
    """
    query = db.query(Document)

    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    distribution = {}
    for status in ReadabilityStatus:
        count = query.filter(Document.readability_status == status).count()
        distribution[status.value] = count

    return distribution


@router.get("/signature-statistics")
def get_signature_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get signature detection statistics
    """
    query = db.query(Document)

    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    total_processed = query.filter(Document.is_processed == True).count()
    with_signatures = query.filter(Document.has_signature == True).count()
    without_signatures = query.filter(Document.has_signature == False).count()

    # Average signature count (for documents that have signatures)
    avg_signatures = db.query(func.avg(Document.signature_count)).filter(
        Document.has_signature == True,
        Document.uploaded_by == current_user.id if not current_user.is_admin else True
    ).scalar() or 0.0

    return {
        "total_processed": total_processed,
        "with_signatures": with_signatures,
        "without_signatures": without_signatures,
        "average_signature_count": round(avg_signatures, 2),
        "percentage_with_signatures": round((with_signatures / total_processed * 100) if total_processed > 0 else 0, 2)
    }


@router.get("/processing-summary")
def get_processing_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of document processing status
    """
    query = db.query(Document)

    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    total = query.count()
    processed = query.filter(Document.is_processed == True).count()
    pending = query.filter(Document.is_processed == False).count()
    with_errors = query.filter(Document.processing_error != None).count()

    return {
        "total_documents": total,
        "processed": processed,
        "pending": pending,
        "with_errors": with_errors,
        "processing_completion_rate": round((processed / total * 100) if total > 0 else 0, 2)
    }


@router.get("/validation-failures")
def get_validation_failures(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent documents that failed validation

    Returns list of documents that need review or failed validation
    """
    query = db.query(Document).filter(
        Document.validation_status.in_([ValidationStatus.FAIL, ValidationStatus.NEEDS_REVIEW])
    )

    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    failed_docs = query.order_by(Document.created_at.desc()).limit(limit).all()

    results = []
    for doc in failed_docs:
        results.append({
            "id": doc.id,
            "filename": doc.original_filename,
            "document_type": doc.document_type.value,
            "validation_status": doc.validation_status.value,
            "validation_result": doc.validation_result,
            "created_at": doc.created_at.isoformat()
        })

    return results


@router.get("/document-types-breakdown")
def get_document_types_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed breakdown of document types with validation statistics
    """
    query = db.query(Document)

    if not current_user.is_admin:
        query = query.filter(Document.uploaded_by == current_user.id)

    breakdown = []

    for doc_type in DocumentType:
        type_query = query.filter(Document.document_type == doc_type)
        total = type_query.count()

        if total == 0:
            continue

        passed = type_query.filter(Document.validation_status == ValidationStatus.PASS).count()
        failed = type_query.filter(Document.validation_status == ValidationStatus.FAIL).count()
        needs_review = type_query.filter(Document.validation_status == ValidationStatus.NEEDS_REVIEW).count()

        avg_quality = db.query(func.avg(Document.quality_score)).filter(
            Document.document_type == doc_type,
            Document.uploaded_by == current_user.id if not current_user.is_admin else True
        ).scalar() or 0.0

        breakdown.append({
            "document_type": doc_type.value,
            "total": total,
            "passed": passed,
            "failed": failed,
            "needs_review": needs_review,
            "pass_rate": round((passed / total * 100) if total > 0 else 0, 2),
            "average_quality_score": round(avg_quality, 2)
        })

    return breakdown

