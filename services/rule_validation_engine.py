"""
Rule Validation Engine - AI-Powered Document Validation
Validates documents against general and document-specific rules
"""
import logging
from typing import Dict, List, Any, Optional
from models import DocumentType, ValidationStatus

logger = logging.getLogger(__name__)


# ============================================
# GENERAL RULES (Apply to ALL Document Types)
# These run FIRST - hard failures stop processing
# ============================================

GENERAL_RULES = [
    {
        "rule_id": "GEN_001",
        "name": "Image Quality Check",
        "description": "Document must be readable",
        "check": lambda doc: (doc.get("quality_score") or 0) >= 55.0,
        "fail_reason": "Document image quality too low (< 55%). Please re-upload a clearer photo.",
        "severity": "hard",  # hard = stops processing, soft = warning only
        "category": "quality"
    },
    {
        "rule_id": "GEN_002",
        "name": "Minimum Text Extracted",
        "description": "OCR must extract meaningful text",
        "check": lambda doc: len(doc.get("ocr_text", "")) >= 50,
        "fail_reason": "Could not extract enough text (< 50 characters). Document may be blank or unreadable.",
        "severity": "hard",
        "category": "quality"
    },
    {
        "rule_id": "GEN_003",
        "name": "Document Type Identified",
        "description": "System must confidently identify doc type",
        "check": lambda doc: (doc.get("classification_confidence") or 0) >= 0.50,
        "fail_reason": "Document type could not be identified confidently. Manual review needed.",
        "severity": "hard",
        "category": "classification"
    },
    {
        "rule_id": "GEN_004",
        "name": "Not Severely Blurry",
        "description": "Document should not be severely blurred",
        "check": lambda doc: not (doc.get("is_blurry") == True and (doc.get("quality_score") or 0) < 60),
        "fail_reason": "Document is too blurry. Please re-upload a clearer image.",
        "severity": "hard",
        "category": "quality"
    },
    {
        "rule_id": "GEN_005",
        "name": "Date Present",
        "description": "Document must contain a date",
        "check": lambda doc: bool(
            doc.get("document_date") or
            doc.get("metadata", {}).get("doc_type_fields", {}).get("invoice_date") or
            doc.get("metadata", {}).get("doc_type_fields", {}).get("ship_date") or
            doc.get("metadata", {}).get("doc_type_fields", {}).get("delivery_date") or
            doc.get("metadata", {}).get("doc_type_fields", {}).get("date")
        ),
        "fail_reason": "No date found on document. Date is required for tracking.",
        "severity": "soft",
        "category": "data"
    },
    {
        "rule_id": "GEN_006",
        "name": "Extraction Completeness",
        "description": "At least 50% of expected fields must be extracted",
        "check": lambda doc: doc.get("metadata", {}).get("field_extraction_validation", {}).get("extraction_score", 0) >= 0.50,
        "fail_reason": "Less than 50% of required fields could be read from document.",
        "severity": "soft",
        "category": "data"
    },
]


# ============================================
# DOCUMENT-SPECIFIC RULES
# Run AFTER general rules pass
# ============================================

DOC_SPECIFIC_RULES = {
    # ── Bill of Lading ───────────────────────────────────────
    DocumentType.BILL_OF_LADING: [
        {
            "rule_id": "BOL_001",
            "name": "Requires 2 Signatures",
            "check": lambda doc: (doc.get("signature_count") or 0) >= 2,
            "fail_reason": "BOL must have minimum 2 signatures (shipper + carrier). Found {count}.",
            "severity": "hard"
        },
        {
            "rule_id": "BOL_002",
            "name": "BOL Number Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("bol_number")),
            "fail_reason": "BOL number is missing. This is required for tracking.",
            "severity": "hard"
        },
        {
            "rule_id": "BOL_003",
            "name": "Order/Load Number Present",
            "check": lambda doc: bool(doc.get("order_number") or doc.get("metadata", {}).get("doc_type_fields", {}).get("order_number")),
            "fail_reason": "Order or Load number is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "BOL_004",
            "name": "Shipper Name Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("shipper")),
            "fail_reason": "Shipper name is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "BOL_005",
            "name": "Consignee Name Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("consignee")),
            "fail_reason": "Consignee name is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "BOL_006",
            "name": "Origin and Destination Present",
            "check": lambda doc: bool(
                doc.get("metadata", {}).get("doc_type_fields", {}).get("origin") and
                doc.get("metadata", {}).get("doc_type_fields", {}).get("destination")
            ),
            "fail_reason": "Origin or Destination location is missing.",
            "severity": "soft"
        },
        {
            "rule_id": "BOL_007",
            "name": "Freight Terms Specified",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("freight_terms")),
            "fail_reason": "Freight terms (Prepaid/Collect) not specified.",
            "severity": "soft"
        },
        {
            "rule_id": "BOL_008",
            "name": "Weight Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("total_weight")),
            "fail_reason": "Total weight is missing.",
            "severity": "soft"
        },
    ],

    # ── Proof of Delivery ────────────────────────────────────
    DocumentType.PROOF_OF_DELIVERY: [
        {
            "rule_id": "POD_001",
            "name": "Consignee Signature Required",
            "check": lambda doc: (doc.get("signature_count") or 0) >= 1,
            "fail_reason": "POD must have consignee signature to confirm delivery.",
            "severity": "hard"
        },
        {
            "rule_id": "POD_002",
            "name": "Order Number Present",
            "check": lambda doc: bool(doc.get("order_number") or doc.get("metadata", {}).get("doc_type_fields", {}).get("order_number")),
            "fail_reason": "Order/Load number is missing on POD.",
            "severity": "hard"
        },
        {
            "rule_id": "POD_003",
            "name": "Delivery Date Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("delivery_date")),
            "fail_reason": "Delivery date is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "POD_004",
            "name": "Delivered To Name Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("delivered_to")),
            "fail_reason": "Recipient name is missing.",
            "severity": "soft"
        },
        {
            "rule_id": "POD_005",
            "name": "Delivery Condition Noted",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("condition")),
            "fail_reason": "Delivery condition (Good/Damaged) not noted.",
            "severity": "soft"
        },
        {
            "rule_id": "POD_006",
            "name": "No Damage Reported",
            "check": lambda doc: doc.get("metadata", {}).get("doc_type_fields", {}).get("condition", "").lower() not in ["damaged", "refused", "partial"],
            "fail_reason": "⚠️ Delivery condition shows damage or refusal - escalate for review.",
            "severity": "soft"
        },
    ],

    # ── Commercial Invoice ───────────────────────────────────
    DocumentType.COMMERCIAL_INVOICE: [
        {
            "rule_id": "INV_001",
            "name": "Invoice Number Present",
            "check": lambda doc: bool(doc.get("invoice_number") or doc.get("metadata", {}).get("doc_type_fields", {}).get("invoice_number")),
            "fail_reason": "Invoice number is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "INV_002",
            "name": "Order Number Present",
            "check": lambda doc: bool(doc.get("order_number") or doc.get("metadata", {}).get("doc_type_fields", {}).get("order_number")),
            "fail_reason": "Order/PO number is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "INV_003",
            "name": "Total Amount Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("total_amount")),
            "fail_reason": "Invoice total amount is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "INV_004",
            "name": "Seller and Buyer Present",
            "check": lambda doc: bool(
                doc.get("metadata", {}).get("doc_type_fields", {}).get("seller") and
                doc.get("metadata", {}).get("doc_type_fields", {}).get("buyer")
            ),
            "fail_reason": "Seller or Buyer name is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "INV_005",
            "name": "Payment Terms Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("payment_terms")),
            "fail_reason": "Payment terms are missing.",
            "severity": "soft"
        },
        {
            "rule_id": "INV_006",
            "name": "Invoice Date Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("invoice_date")),
            "fail_reason": "Invoice date is missing.",
            "severity": "soft"
        },
    ],

    # ── Packing List ─────────────────────────────────────────
    DocumentType.PACKING_LIST: [
        {
            "rule_id": "PKG_001",
            "name": "Order Number Present",
            "check": lambda doc: bool(doc.get("order_number") or doc.get("metadata", {}).get("doc_type_fields", {}).get("order_number")),
            "fail_reason": "Order number is missing on packing list.",
            "severity": "hard"
        },
        {
            "rule_id": "PKG_002",
            "name": "Total Cartons Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("total_cartons")),
            "fail_reason": "Total carton count is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "PKG_003",
            "name": "Weight Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("gross_weight")),
            "fail_reason": "Gross weight is missing.",
            "severity": "soft"
        },
        {
            "rule_id": "PKG_004",
            "name": "Destination Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("destination")),
            "fail_reason": "Destination is missing.",
            "severity": "soft"
        },
    ],

    # ── Hazmat Document ──────────────────────────────────────
    DocumentType.HAZMAT_DOCUMENT: [
        {
            "rule_id": "HAZ_001",
            "name": "UN Number Required",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("un_number")),
            "fail_reason": "⚠️ UN number is MANDATORY for hazmat documents.",
            "severity": "hard"
        },
        {
            "rule_id": "HAZ_002",
            "name": "Proper Shipping Name Required",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("shipping_name")),
            "fail_reason": "Proper shipping name is required.",
            "severity": "hard"
        },
        {
            "rule_id": "HAZ_003",
            "name": "Hazard Class Required",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("hazard_class")),
            "fail_reason": "Hazard class is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "HAZ_004",
            "name": "Emergency Contact Required",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("emergency_contact")),
            "fail_reason": "⚠️ Emergency contact number is MANDATORY for hazmat.",
            "severity": "hard"
        },
        {
            "rule_id": "HAZ_005",
            "name": "Packing Group Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("packing_group")),
            "fail_reason": "Packing group (I/II/III) is missing.",
            "severity": "soft"
        },
        {
            "rule_id": "HAZ_006",
            "name": "Shipper Signature Required",
            "check": lambda doc: (doc.get("signature_count") or 0) >= 1,
            "fail_reason": "Hazmat document requires shipper signature.",
            "severity": "hard"
        },
    ],

    # ── Lumper Receipt ───────────────────────────────────────
    DocumentType.LUMPER_RECEIPT: [
        {
            "rule_id": "LMP_001",
            "name": "Signature Required",
            "check": lambda doc: (doc.get("signature_count") or 0) >= 1,
            "fail_reason": "Lumper receipt must be signed.",
            "severity": "hard"
        },
        {
            "rule_id": "LMP_002",
            "name": "Order Number Present",
            "check": lambda doc: bool(doc.get("order_number") or doc.get("metadata", {}).get("doc_type_fields", {}).get("order_number")),
            "fail_reason": "Order/Load number is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "LMP_003",
            "name": "Amount Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("amount")),
            "fail_reason": "Payment amount is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "LMP_004",
            "name": "Date Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("date")),
            "fail_reason": "Date is missing on lumper receipt.",
            "severity": "soft"
        },
        {
            "rule_id": "LMP_005",
            "name": "Service Type Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("service_type")),
            "fail_reason": "Service type (Loading/Unloading) not specified.",
            "severity": "soft"
        },
    ],

    # ── Trip Sheet ───────────────────────────────────────────
    DocumentType.TRIP_SHEET: [
        {
            "rule_id": "TRP_001",
            "name": "Trip Number Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("trip_number")),
            "fail_reason": "Trip/Load number is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "TRP_002",
            "name": "Driver Name Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("driver_name")),
            "fail_reason": "Driver name is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "TRP_003",
            "name": "Driver Signature Required",
            "check": lambda doc: (doc.get("signature_count") or 0) >= 1,
            "fail_reason": "Driver signature is required on trip sheet.",
            "severity": "hard"
        },
        {
            "rule_id": "TRP_004",
            "name": "Mileage Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("total_miles")),
            "fail_reason": "Total mileage is missing.",
            "severity": "soft"
        },
        {
            "rule_id": "TRP_005",
            "name": "Truck Number Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("truck_number")),
            "fail_reason": "Truck/Unit number is missing.",
            "severity": "soft"
        },
    ],

    # ── Freight Invoice ──────────────────────────────────────
    DocumentType.FREIGHT_INVOICE: [
        {
            "rule_id": "FRT_001",
            "name": "PRO Number Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("pro_number")),
            "fail_reason": "PRO number is missing on freight invoice.",
            "severity": "hard"
        },
        {
            "rule_id": "FRT_002",
            "name": "Order Number Present",
            "check": lambda doc: bool(doc.get("order_number") or doc.get("metadata", {}).get("doc_type_fields", {}).get("order_number")),
            "fail_reason": "Order/Load number is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "FRT_003",
            "name": "Total Charges Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("total_charges")),
            "fail_reason": "Total charges amount is missing.",
            "severity": "hard"
        },
        {
            "rule_id": "FRT_004",
            "name": "Carrier Name Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("carrier_name")),
            "fail_reason": "Carrier name is missing.",
            "severity": "soft"
        },
        {
            "rule_id": "FRT_005",
            "name": "Invoice Date Present",
            "check": lambda doc: bool(doc.get("metadata", {}).get("doc_type_fields", {}).get("invoice_date")),
            "fail_reason": "Invoice date is missing.",
            "severity": "soft"
        },
    ],
}


class RuleValidationEngine:
    """
    Rule-based validation engine for documents
    Validates both general and document-specific rules
    """

    def __init__(self):
        self.general_rules = GENERAL_RULES
        self.doc_specific_rules = DOC_SPECIFIC_RULES

    def validate_document(self, document_dict: Dict) -> Dict[str, Any]:
        """
        Validate document against all applicable rules

        Args:
            document_dict: Document data as dictionary

        Returns:
            Validation result with status, failures, warnings
        """
        logger.info(f"🔍 [VALIDATION] Starting rule validation...")

        doc_type = document_dict.get("document_type")
        hard_failures = []
        soft_warnings = []
        passed_rules = []

        # ============================================
        # STEP 1: GENERAL RULES (Critical - stops processing if failed)
        # ============================================
        logger.info(f"📋 [VALIDATION] Checking {len(self.general_rules)} general rules...")

        for rule in self.general_rules:
            passed, reason = self._check_rule(rule, document_dict)

            if passed:
                passed_rules.append(rule["rule_id"])
                logger.info(f"   ✅ {rule['rule_id']}: {rule['name']}")
            else:
                entry = {
                    "rule_id": rule["rule_id"],
                    "name": rule["name"],
                    "reason": reason,
                    "category": rule.get("category", "general")
                }

                if rule["severity"] == "hard":
                    hard_failures.append(entry)
                    logger.error(f"   ❌ {rule['rule_id']}: {rule['name']} - {reason}")
                else:
                    soft_warnings.append(entry)
                    logger.warning(f"   ⚠️  {rule['rule_id']}: {rule['name']} - {reason}")

        # If hard failures in general rules, stop here
        if hard_failures:
            logger.error(f"❌ [VALIDATION] {len(hard_failures)} hard failures in general rules - PROCESSING STOPPED")
            return self._build_result(
                status="Fail",
                hard_failures=hard_failures,
                soft_warnings=soft_warnings,
                passed_rules=passed_rules,
                total_rules=len(self.general_rules),
                stop_processing=True
            )

        # ============================================
        # STEP 2: DOCUMENT-SPECIFIC RULES
        # ============================================
        doc_rules = self.doc_specific_rules.get(doc_type, [])

        if doc_rules:
            logger.info(f"📋 [VALIDATION] Checking {len(doc_rules)} {doc_type.value if doc_type else 'Unknown'}-specific rules...")

            for rule in doc_rules:
                passed, reason = self._check_rule(rule, document_dict)

                if passed:
                    passed_rules.append(rule["rule_id"])
                    logger.info(f"   ✅ {rule['rule_id']}: {rule['name']}")
                else:
                    entry = {
                        "rule_id": rule["rule_id"],
                        "name": rule["name"],
                        "reason": reason,
                        "category": "document_specific"
                    }

                    if rule["severity"] == "hard":
                        hard_failures.append(entry)
                        logger.error(f"   ❌ {rule['rule_id']}: {rule['name']} - {reason}")
                    else:
                        soft_warnings.append(entry)
                        logger.warning(f"   ⚠️  {rule['rule_id']}: {rule['name']} - {reason}")

        # ============================================
        # STEP 3: DETERMINE FINAL STATUS
        # ============================================
        total_rules = len(self.general_rules) + len(doc_rules)

        if hard_failures:
            status = "Fail"
            stop_processing = False  # Don't stop - just mark as failed
        elif soft_warnings:
            status = "Pass with Warnings"
            stop_processing = False
        else:
            status = "Pass"
            stop_processing = False

        result = self._build_result(
            status=status,
            hard_failures=hard_failures,
            soft_warnings=soft_warnings,
            passed_rules=passed_rules,
            total_rules=total_rules,
            stop_processing=stop_processing
        )

        logger.info(f"✅ [VALIDATION] Complete: {result['status']} ({result['score']:.0%} passed)")
        logger.info(f"   Total rules: {result['total_rules_checked']}")
        logger.info(f"   Passed: {result['total_passed']}")
        logger.info(f"   Hard failures: {len(hard_failures)}")
        logger.info(f"   Soft warnings: {len(soft_warnings)}")

        return result

    def _check_rule(self, rule: Dict, doc: Dict) -> tuple:
        """
        Check if document passes a rule

        Args:
            rule: Rule definition
            doc: Document dictionary

        Returns:
            Tuple of (passed: bool, reason: str)
        """
        try:
            passed = rule["check"](doc)

            if passed:
                return True, None
            else:
                # Format reason with dynamic values if needed
                reason = rule["fail_reason"]

                # Replace placeholders
                if "{count}" in reason:
                    reason = reason.format(count=doc.get("signature_count", 0))

                return False, reason

        except Exception as e:
            logger.error(f"Error checking rule {rule.get('rule_id')}: {e}")
            return False, f"Rule check failed: {str(e)}"

    def _build_result(
        self,
        status: str,
        hard_failures: List[Dict],
        soft_warnings: List[Dict],
        passed_rules: List[str],
        total_rules: int,
        stop_processing: bool = False
    ) -> Dict[str, Any]:
        """Build validation result dictionary"""

        return {
            "status": status,
            "validation_status_enum": self._map_status(status),
            "hard_failures": hard_failures,
            "soft_warnings": soft_warnings,
            "passed_rules": passed_rules,
            "total_rules_checked": total_rules,
            "total_passed": len(passed_rules),
            "total_hard_failures": len(hard_failures),
            "total_soft_warnings": len(soft_warnings),
            "score": round(len(passed_rules) / total_rules, 2) if total_rules > 0 else 0,
            "billing_ready": status == "Pass",
            "needs_manual_review": len(hard_failures) > 0 or len(soft_warnings) > 0,
            "stop_processing": stop_processing,  # True if quality checks failed
            "summary": self._build_summary(status, hard_failures, soft_warnings)
        }

    def _map_status(self, status: str) -> ValidationStatus:
        """Map string status to ValidationStatus enum"""
        if status == "Pass":
            return ValidationStatus.PASS
        elif status == "Pass with Warnings":
            return ValidationStatus.NEEDS_REVIEW
        else:
            return ValidationStatus.FAIL

    def _build_summary(self, status: str, hard_failures: List, soft_warnings: List) -> str:
        """Build human-readable summary"""
        if status == "Pass":
            return "✅ All validation rules passed. Document ready for processing."
        elif status == "Pass with Warnings":
            return f"⚠️ Document passed with {len(soft_warnings)} warning(s). Review recommended."
        else:
            return f"❌ Document failed {len(hard_failures)} critical rule(s). Action required."


# Singleton instance
_validation_engine = None


def get_validation_engine() -> RuleValidationEngine:
    """Get or create validation engine instance"""
    global _validation_engine
    if _validation_engine is None:
        _validation_engine = RuleValidationEngine()
    return _validation_engine

