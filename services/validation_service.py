"""
Validation Service - Validates documents against defined rules
"""
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
import logging

from models import Document, ValidationRule, DocumentValidation, DocumentType, ValidationStatus
from schemas import ValidationStatusEnum

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating documents against rules"""

    def validate_document(
        self,
        document: Document,
        rules: List[ValidationRule],
        db: Session
    ) -> Tuple[ValidationStatusEnum, List[str], List[str]]:
        """
        Validate document against multiple rules

        Args:
            document: Document to validate
            rules: List of validation rules to apply
            db: Database session

        Returns:
            Tuple of (validation_status, passed_rules, failed_rules_with_reasons)
        """
        passed_rules = []
        failed_rules = []

        for rule in rules:
            # Check if rule applies to this document type
            if rule.document_type != document.document_type:
                continue

            # Validate against this rule
            passed, reason = self._validate_single_rule(document, rule)

            if passed:
                passed_rules.append(rule.rule_name)
            else:
                failed_rules.append(f"{rule.rule_name}: {reason}")

            # Store validation result
            validation = DocumentValidation(
                document_id=document.id,
                validation_rule_id=rule.id,
                passed=passed,
                failure_reason=reason if not passed else None,
                validation_details={
                    'rule_name': rule.rule_name,
                    'document_type': document.document_type.value,
                    'signature_count': document.signature_count,
                    'has_order_number': bool(document.order_number)
                }
            )
            db.add(validation)

        # Determine overall status
        if not rules:
            status = ValidationStatusEnum.PASS  # No rules = pass
        elif failed_rules:
            # Check if failures are critical
            if len(failed_rules) >= len(rules) / 2:
                status = ValidationStatusEnum.FAIL
            else:
                status = ValidationStatusEnum.NEEDS_REVIEW
        else:
            status = ValidationStatusEnum.PASS

        db.commit()

        logger.info(f"Document {document.id} validation: {status.value}")
        logger.info(f"Passed: {passed_rules}")
        logger.info(f"Failed: {failed_rules}")

        return status, passed_rules, failed_rules

    def _validate_single_rule(self, document: Document, rule: ValidationRule) -> Tuple[bool, str]:
        """
        Validate document against a single rule

        Returns:
            Tuple of (passed, failure_reason)
        """
        # Check signature requirements
        if rule.requires_signature:
            if not document.has_signature:
                return False, "Document must contain signature"

            if rule.minimum_signatures > 0 and document.signature_count < rule.minimum_signatures:
                return False, f"Document requires {rule.minimum_signatures} signatures, found {document.signature_count}"

        # Check order number requirement
        if rule.requires_order_number:
            if not document.order_number or len(document.order_number.strip()) == 0:
                return False, "Document must contain Order Number"


        # All checks passed
        return True, ""

    def get_applicable_rules(
        self,
        document_type: DocumentType,
        customer_id: int = None,
        db: Session = None
    ) -> List[ValidationRule]:
        """
        Get all applicable validation rules for a document

        Args:
            document_type: Type of document
            customer_id: Customer ID (optional)
            db: Database session

        Returns:
            List of applicable validation rules
        """
        query = db.query(ValidationRule).filter(
            ValidationRule.is_active == True,
            ValidationRule.document_type == document_type
        )

        # Get customer-specific rules and global rules
        if customer_id:
            query = query.filter(
                (ValidationRule.customer_id == customer_id) |
                (ValidationRule.customer_id == None)
            )
        else:
            query = query.filter(ValidationRule.customer_id == None)

        rules = query.all()

        logger.info(f"Found {len(rules)} applicable rules for {document_type.value}")

        return rules

    def create_default_rules(self, db: Session):
        """
        Create default validation rules for all document types
        """
        default_rules = [
            # Bill of Lading
            {
                'rule_name': 'BOL Signature Requirement',
                'rule_description': 'Bill of Lading must contain two signatures',
                'document_type': DocumentType.BILL_OF_LADING,
                'requires_signature': True,
                'minimum_signatures': 2,
                'requires_order_number': True
            },
            # Proof of Delivery
            {
                'rule_name': 'POD Signature Requirement',
                'rule_description': 'Proof of Delivery must contain consignee signature',
                'document_type': DocumentType.PROOF_OF_DELIVERY,
                'requires_signature': True,
                'minimum_signatures': 1,
                'requires_order_number': True
            },
            # Commercial Invoice
            {
                'rule_name': 'Invoice Number Requirement',
                'rule_description': 'Commercial Invoice must contain order number',
                'document_type': DocumentType.COMMERCIAL_INVOICE,
                'requires_signature': False,
                'requires_order_number': True
            },
            # Lumper Receipt
            {
                'rule_name': 'Lumper Receipt Requirements',
                'rule_description': 'Lumper Receipt must contain order number',
                'document_type': DocumentType.LUMPER_RECEIPT,
                'requires_signature': False,
                'requires_order_number': True
            },
            # Freight Invoice
            {
                'rule_name': 'Freight Invoice Requirements',
                'rule_description': 'Freight Invoice must contain order number',
                'document_type': DocumentType.FREIGHT_INVOICE,
                'requires_signature': False,
                'requires_order_number': True
            }
        ]

        for rule_data in default_rules:
            # Check if rule already exists
            existing = db.query(ValidationRule).filter(
                ValidationRule.rule_name == rule_data['rule_name']
            ).first()

            if not existing:
                rule = ValidationRule(**rule_data)
                db.add(rule)

        db.commit()
        logger.info(f"Created {len(default_rules)} default validation rules")


# Singleton instance
validation_service = ValidationService()

