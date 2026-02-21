"""
Validation Rules routes - Manage document validation rules
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User, ValidationRule, DocumentType
from schemas import (
    ValidationRuleCreate, ValidationRuleUpdate, ValidationRuleResponse, MessageResponse
)
from auth import get_current_user, get_current_admin_user

router = APIRouter(
    prefix="/validation-rules",
    tags=["Validation Rules"]
)


@router.post("/", response_model=ValidationRuleResponse, status_code=status.HTTP_201_CREATED)
def create_validation_rule(
    rule: ValidationRuleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new validation rule

    Requires admin privileges.

    - **rule_name**: Name of the rule
    - **document_type**: Type of document this rule applies to
    - **requires_signature**: Whether signature is required
    - **minimum_signatures**: Minimum number of signatures required
    - **requires_order_number**: Whether order number is required
    - **customer_id**: Customer ID (null for global rules)
    """
    # Check if rule already exists
    existing = db.query(ValidationRule).filter(
        ValidationRule.rule_name == rule.rule_name,
        ValidationRule.document_type == rule.document_type
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A rule with this name already exists for this document type"
        )

    db_rule = ValidationRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)

    return db_rule


@router.get("/", response_model=List[ValidationRuleResponse])
def get_validation_rules(
    document_type: Optional[str] = None,
    customer_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of validation rules with filtering

    - **document_type**: Filter by document type (optional)
    - **customer_id**: Filter by customer ID (optional)
    - **is_active**: Filter by active status (optional)
    """
    query = db.query(ValidationRule)

    # Apply filters
    if document_type:
        try:
            doc_type_enum = DocumentType(document_type)
            query = query.filter(ValidationRule.document_type == doc_type_enum)
        except ValueError:
            pass

    if customer_id is not None:
        query = query.filter(ValidationRule.customer_id == customer_id)

    if is_active is not None:
        query = query.filter(ValidationRule.is_active == is_active)

    rules = query.order_by(ValidationRule.created_at.desc()).offset(skip).limit(limit).all()

    return rules


@router.get("/{rule_id}", response_model=ValidationRuleResponse)
def get_validation_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific validation rule by ID
    """
    rule = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation rule not found"
        )

    return rule


@router.put("/{rule_id}", response_model=ValidationRuleResponse)
def update_validation_rule(
    rule_id: int,
    rule_update: ValidationRuleUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a validation rule

    Requires admin privileges.
    """
    rule = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation rule not found"
        )

    # Update fields
    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)

    return rule


@router.delete("/{rule_id}", response_model=MessageResponse)
def delete_validation_rule(
    rule_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a validation rule

    Requires admin privileges.
    """
    rule = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation rule not found"
        )

    db.delete(rule)
    db.commit()

    return MessageResponse(
        message=f"Validation rule {rule_id} deleted successfully",
        success=True
    )


@router.post("/initialize-defaults", response_model=MessageResponse)
def initialize_default_rules(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Initialize default validation rules for all document types

    Requires admin privileges.

    This creates standard validation rules for:
    - Bill of Lading
    - Proof of Delivery
    - Commercial Invoice
    - Lumper Receipt
    - Freight Invoice
    """
    from services.validation_service import validation_service

    try:
        validation_service.create_default_rules(db)
        return MessageResponse(
            message="Default validation rules created successfully",
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating default rules: {str(e)}"
        )

