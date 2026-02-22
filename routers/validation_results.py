"""
Validation Results API - Get validation failure reasons for a document
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

from database import get_db
from models import Document, DocumentValidation
from auth import get_current_user

router = APIRouter(
    prefix="/validation-results",
    tags=["Validation Results"]
)


class ValidationReasonRequest(BaseModel):
    """Request model for getting validation reasons"""
    document_id: int


class ValidationReason(BaseModel):
    """Individual validation failure reason"""
    rule_id: str
    rule_name: str
    reason: str
    severity: str  # "hard" or "soft"


class ValidationResultResponse(BaseModel):
    """Response model with all validation reasons"""
    document_id: int
    validation_status: str
    overall_score: Optional[float]
    total_rules_checked: int
    passed_count: int
    failed_count: int
    hard_failures: List[ValidationReason]
    soft_warnings: List[ValidationReason]
    all_failure_reasons: List[str]  # Simple list of all failure reasons


@router.post("/get-reasons", response_model=ValidationResultResponse)
async def get_validation_reasons(
    request: ValidationReasonRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all validation failure reasons for a specific document.

    Extracts validation results from the document's validation_result JSON field
    and returns all failure reasons in a structured format.

    **Parameters:**
    - **document_id**: The ID of the document to get validation results for

    **Returns:**
    - Document validation status
    - List of hard failures (blocking issues)
    - List of soft warnings (non-blocking issues)
    - Combined list of all failure reasons
    """
    # Fetch the document
    document = db.query(Document).filter(Document.id == request.document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {request.document_id} not found"
        )

    # Check if validation_result exists
    if not document.validation_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No validation results found for document {request.document_id}. Document may not have been validated yet."
        )

    # Parse validation results
    try:
        # validation_result is already a dict (JSON column type)
        validation_data = document.validation_result

        # Extract data
        status_value = validation_data.get('status', 'Unknown')
        overall_score = validation_data.get('score', 0.0)
        total_rules = validation_data.get('total_rules_checked', 0)
        passed_count = validation_data.get('total_passed', 0)

        # Extract hard failures
        hard_failures_data = validation_data.get('hard_failures', [])
        hard_failures = []
        for failure in hard_failures_data:
            hard_failures.append(ValidationReason(
                rule_id=failure.get('rule_id', 'UNKNOWN'),
                rule_name=failure.get('name', 'Unknown Rule'),
                reason=failure.get('reason', 'No reason provided'),
                severity='hard'
            ))

        # Extract soft warnings
        soft_warnings_data = validation_data.get('soft_warnings', [])
        soft_warnings = []
        for warning in soft_warnings_data:
            soft_warnings.append(ValidationReason(
                rule_id=warning.get('rule_id', 'UNKNOWN'),
                rule_name=warning.get('name', 'Unknown Rule'),
                reason=warning.get('reason', 'No reason provided'),
                severity='soft'
            ))

        # Create combined list of all failure reasons (just the reason text)
        all_failure_reasons = []

        # Add hard failure reasons
        for failure in hard_failures_data:
            reason_text = failure.get('reason', 'No reason provided')
            all_failure_reasons.append(f"[CRITICAL] {reason_text}")

        # Add soft warning reasons
        for warning in soft_warnings_data:
            reason_text = warning.get('reason', 'No reason provided')
            all_failure_reasons.append(f"[WARNING] {reason_text}")

        # Calculate failed count
        failed_count = len(hard_failures) + len(soft_warnings)

        return ValidationResultResponse(
            document_id=document.id,
            validation_status=status_value,
            overall_score=overall_score,
            total_rules_checked=total_rules,
            passed_count=passed_count,
            failed_count=failed_count,
            hard_failures=hard_failures,
            soft_warnings=soft_warnings,
            all_failure_reasons=all_failure_reasons
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing validation results: {str(e)}"
        )


@router.get("/{document_id}", response_model=ValidationResultResponse)
async def get_validation_reasons_by_id(
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get validation reasons using document ID in URL path (alternative endpoint).

    **Parameters:**
    - **document_id**: Document ID in URL path

    **Returns:**
    - Same as POST /get-reasons endpoint
    """
    # Reuse the POST endpoint logic
    request = ValidationReasonRequest(document_id=document_id)
    return await get_validation_reasons(request, current_user, db)


@router.get("/document/{document_id}/summary")
async def get_validation_summary(
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a simple validation summary for a document.

    **Returns:**
    - Quick summary with just the failure reasons as a list
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    if not document.validation_result:
        return {
            "document_id": document_id,
            "has_validation": False,
            "status": "Not validated yet",
            "failure_reasons": []
        }

    validation_data = document.validation_result

    # Extract all failure reasons
    failure_reasons = []

    # Hard failures
    for failure in validation_data.get('hard_failures', []):
        failure_reasons.append({
            "type": "CRITICAL",
            "rule": failure.get('name', 'Unknown'),
            "reason": failure.get('reason', 'No reason provided')
        })

    # Soft warnings
    for warning in validation_data.get('soft_warnings', []):
        failure_reasons.append({
            "type": "WARNING",
            "rule": warning.get('name', 'Unknown'),
            "reason": warning.get('reason', 'No reason provided')
        })

    return {
        "document_id": document_id,
        "has_validation": True,
        "status": validation_data.get('status', 'Unknown'),
        "overall_score": validation_data.get('score', 0.0),
        "failure_count": len(failure_reasons),
        "failure_reasons": failure_reasons
    }

