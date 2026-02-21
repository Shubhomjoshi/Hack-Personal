"""
Enhanced Metadata Extractor - Document Type Specific Field Extraction
Hybrid approach: Regex (fast) + Gemini fallback (accurate)
"""
import re
import logging
from typing import Dict, Optional, List
from models import DocumentType

logger = logging.getLogger(__name__)


# ============================================
# FIELD DEFINITIONS PER DOCUMENT TYPE
# ============================================

BOL_FIELDS = {
    "bol_number": r"b/?l[\s#:no\.]*([A-Z0-9\-]+)",
    "order_number": r"(?:order|load)[\s#:no\.]*([A-Z0-9\-]+)",
    "shipper": r"shipper[\s:]*([A-Za-z\s,\.&]+)",
    "consignee": r"consignee[\s:]*([A-Za-z\s,\.&]+)",
    "origin": r"(?:origin|from|port of loading)[\s:]*([A-Za-z\s,]+)",
    "destination": r"(?:destination|to|port of discharge)[\s:]*([A-Za-z\s,]+)",
    "ship_date": r"(?:ship date|date)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    "carrier": r"carrier[\s:]*([A-Za-z\s,\.&]+)",
    "total_weight": r"(?:total weight|gross weight)[\s:]*([0-9,\.]+\s*(?:lbs|kg)?)",
    "total_pieces": r"(?:total pieces|pieces|units)[\s:]*([0-9,]+)",
    "freight_terms": r"(?:freight terms|terms)[\s:]*(prepaid|collect|third party)",
}

POD_FIELDS = {
    "order_number": r"(?:order|load)[\s#:no\.]*([A-Z0-9\-]+)",
    "delivery_date": r"(?:delivery date|delivered on)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    "delivery_time": r"(?:time|delivery time)[\s:]*(\d{1,2}:\d{2}\s*(?:AM|PM)?)",
    "delivered_to": r"(?:delivered to|received by|recipient)[\s:]*([A-Za-z\s]+)",
    "delivery_address": r"(?:address|delivery address)[\s:]*([A-Za-z0-9\s,\.#]+)",
    "condition": r"(?:condition|goods condition)[\s:]*(good|damaged|partial|refused)",
    "driver_name": r"(?:driver|driver name)[\s:]*([A-Za-z\s]+)",
    "exceptions": r"(?:exceptions|notes|remarks)[\s:]*([A-Za-z0-9\s,\.]+)",
}

INVOICE_FIELDS = {
    "invoice_number": r"invoice[\s#:no\.]*([A-Z0-9\-]+)",
    "invoice_date": r"(?:invoice date|date)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    "order_number": r"(?:order|po number|po#)[\s#:no\.]*([A-Z0-9\-]+)",
    "seller": r"(?:seller|from|vendor)[\s:]*([A-Za-z\s,\.&]+)",
    "buyer": r"(?:buyer|bill to|sold to)[\s:]*([A-Za-z\s,\.&]+)",
    "total_amount": r"(?:total|total amount|grand total)[\s:]*\$?\s*([0-9,\.]+)",
    "currency": r"\b(USD|EUR|GBP|CAD|INR)\b",
    "payment_terms": r"(?:payment terms|terms)[\s:]*(net\s*\d+|due on receipt|prepaid)",
    "incoterms": r"\b(FOB|CIF|EXW|DDP|DAP|CFR)\b",
}

PACKING_FIELDS = {
    "order_number": r"(?:order|load|ref)[\s#:no\.]*([A-Z0-9\-]+)",
    "packing_date": r"(?:date|packing date)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    "total_cartons": r"(?:total cartons|cartons|packages|total packages)[\s:]*([0-9,]+)",
    "gross_weight": r"(?:gross weight|total gross)[\s:]*([0-9,\.]+\s*(?:lbs|kg)?)",
    "net_weight": r"(?:net weight|total net)[\s:]*([0-9,\.]+\s*(?:lbs|kg)?)",
    "total_volume": r"(?:volume|cbm|total volume)[\s:]*([0-9,\.]+\s*(?:cbm|m3|ft3)?)",
    "destination": r"(?:destination|ship to)[\s:]*([A-Za-z\s,]+)",
}

HAZMAT_FIELDS = {
    "un_number": r"(?:un|un no|un number)[\s#:\.]*(\d{4})",
    "shipping_name": r"(?:proper shipping name|shipping name)[\s:]*([A-Za-z\s,]+)",
    "hazard_class": r"(?:class|hazard class)[\s:]*([0-9\.]+[A-Z]?)",
    "packing_group": r"(?:packing group|pg)[\s:]*(I{1,3}|1|2|3)",
    "total_quantity": r"(?:total quantity|quantity)[\s:]*([0-9,\.]+\s*(?:L|kg|lbs|gal)?)",
    "emergency_contact": r"(?:emergency|emergency contact|chemtrec)[\s:]*([0-9\-\+\(\)\s]+)",
    "shipper": r"shipper[\s:]*([A-Za-z\s,\.&]+)",
}

LUMPER_FIELDS = {
    "order_number": r"(?:order|load|ref)[\s#:no\.]*([A-Z0-9\-]+)",
    "date": r"date[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    "lumper_company": r"(?:company|lumper company|service)[\s:]*([A-Za-z\s,\.&]+)",
    "worker_name": r"(?:worker|employee|name)[\s:]*([A-Za-z\s]+)",
    "service_type": r"(?:service|type)[\s:]*(unloading|loading|both)",
    "hours_worked": r"(?:hours|hrs worked)[\s:]*([0-9\.]+\s*(?:hrs|hours)?)",
    "amount": r"(?:amount|total|fee|charge)[\s:]*\$?\s*([0-9,\.]+)",
    "facility": r"(?:facility|location|warehouse)[\s:]*([A-Za-z0-9\s,#\.]+)",
}

TRIP_FIELDS = {
    "trip_number": r"(?:trip|load|trip no)[\s#:no\.]*([A-Z0-9\-]+)",
    "driver_name": r"(?:driver|driver name)[\s:]*([A-Za-z\s]+)",
    "truck_number": r"(?:truck|unit|vehicle)[\s#:no\.]*([A-Z0-9\-]+)",
    "date": r"date[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    "start_odometer": r"(?:start|beginning|odometer start)[\s:]*([0-9,]+)",
    "end_odometer": r"(?:end|ending|odometer end)[\s:]*([0-9,]+)",
    "total_miles": r"(?:total miles|miles driven|mileage)[\s:]*([0-9,]+)",
    "origin": r"(?:origin|from|start location)[\s:]*([A-Za-z\s,]+)",
    "destination": r"(?:destination|to|end location)[\s:]*([A-Za-z\s,]+)",
    "fuel_stops": r"(?:fuel stops|stops)[\s:]*([0-9]+)",
    "states_crossed": r"(?:states|states crossed)[\s:]*([A-Z,\s]+)",
}

FREIGHT_INV_FIELDS = {
    "pro_number": r"(?:pro|pro no|pro#)[\s#:\.]*([A-Z0-9\-]+)",
    "invoice_number": r"invoice[\s#:no\.]*([A-Z0-9\-]+)",
    "order_number": r"(?:order|load|ref)[\s#:no\.]*([A-Z0-9\-]+)",
    "invoice_date": r"(?:invoice date|date)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    "carrier_name": r"(?:carrier|carrier name)[\s:]*([A-Za-z\s,\.&]+)",
    "origin": r"(?:origin|from)[\s:]*([A-Za-z\s,]+)",
    "destination": r"(?:destination|to)[\s:]*([A-Za-z\s,]+)",
    "linehaul": r"(?:linehaul|line haul)[\s:]*\$?\s*([0-9,\.]+)",
    "fuel_surcharge": r"(?:fuel surcharge|fsc)[\s:]*\$?\s*([0-9,\.]+)",
    "accessorial": r"(?:accessorial|accessorial charges)[\s:]*\$?\s*([0-9,\.]+)",
    "total_charges": r"(?:total|total charges|amount due)[\s:]*\$?\s*([0-9,\.]+)",
    "payment_due": r"(?:due date|payment due|pay by)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
}

# Map document types to field definitions
DOC_FIELDS_MAP = {
    DocumentType.BILL_OF_LADING: BOL_FIELDS,
    DocumentType.PROOF_OF_DELIVERY: POD_FIELDS,
    DocumentType.COMMERCIAL_INVOICE: INVOICE_FIELDS,
    DocumentType.PACKING_LIST: PACKING_FIELDS,
    DocumentType.HAZMAT_DOCUMENT: HAZMAT_FIELDS,
    DocumentType.LUMPER_RECEIPT: LUMPER_FIELDS,
    DocumentType.TRIP_SHEET: TRIP_FIELDS,
    DocumentType.FREIGHT_INVOICE: FREIGHT_INV_FIELDS,
}


class EnhancedMetadataExtractor:
    """
    Enhanced metadata extractor with document-type specific field extraction
    Uses hybrid approach: Regex (fast) + Gemini fallback (accurate)
    """

    def __init__(self):
        self.field_definitions = DOC_FIELDS_MAP

    def extract_fields(
        self,
        text: str,
        doc_type: DocumentType,
        gemini_extracted_fields: Dict = None
    ) -> Dict:
        """
        Extract document-type specific fields using hybrid approach

        Args:
            text: OCR extracted text
            doc_type: Document type classification result
            gemini_extracted_fields: Fields already extracted by Gemini (optional)

        Returns:
            Dictionary with extracted fields and extraction score
        """
        logger.info(f"🔍 Extracting fields for document type: {doc_type.value}")

        # Get field definitions for this document type
        field_defs = self.field_definitions.get(doc_type, {})
        if not field_defs:
            logger.warning(f"No field definitions for {doc_type.value}")
            return {"_extraction_score": 0.0, "_extraction_method": "none"}

        extracted_fields = {}

        # ============================================
        # STEP 1: REGEX EXTRACTION (Fast, reliable for structured data)
        # ============================================
        for field_name, pattern in field_defs.items():
            value = self._extract_with_regex(text, pattern)
            extracted_fields[field_name] = value

        # ============================================
        # STEP 2: GEMINI FALLBACK (Fill missing fields)
        # ============================================
        if gemini_extracted_fields:
            logger.info("📋 Using Gemini-extracted fields as fallback")
            for field_name in field_defs.keys():
                if not extracted_fields.get(field_name):
                    # Try to find field in Gemini results (case-insensitive)
                    gemini_value = gemini_extracted_fields.get(field_name)
                    if gemini_value:
                        extracted_fields[field_name] = gemini_value
                        logger.info(f"   ✅ {field_name} from Gemini: {gemini_value}")

        # ============================================
        # STEP 3: CALCULATE EXTRACTION SCORE
        # ============================================
        total_fields = len(field_defs)
        filled_fields = sum(1 for v in extracted_fields.values() if v)
        extraction_score = round(filled_fields / total_fields, 2) if total_fields > 0 else 0.0

        extracted_fields["_extraction_score"] = extraction_score
        extracted_fields["_total_fields"] = total_fields
        extracted_fields["_filled_fields"] = filled_fields
        extracted_fields["_extraction_method"] = "regex+gemini_hybrid"

        logger.info(f"✅ Extraction complete: {filled_fields}/{total_fields} fields ({extraction_score:.0%})")

        return extracted_fields

    def _extract_with_regex(self, text: str, pattern: str) -> Optional[str]:
        """
        Extract field value using regex pattern

        Args:
            text: Text to search
            pattern: Regex pattern

        Returns:
            Extracted value or None
        """
        try:
            # Normalize whitespace
            text_clean = ' '.join(text.split())

            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Validation: minimum 2 characters
                if value and len(value) >= 2:
                    return value
        except Exception as e:
            logger.debug(f"Regex extraction error: {e}")

        return None

    def get_field_list_for_type(self, doc_type: DocumentType) -> List[str]:
        """
        Get list of fields for a specific document type

        Args:
            doc_type: Document type

        Returns:
            List of field names
        """
        field_defs = self.field_definitions.get(doc_type, {})
        return list(field_defs.keys())

    def validate_completeness(self, extracted_fields: Dict, threshold: float = 0.5) -> Dict:
        """
        Validate if document extraction is complete enough

        Args:
            extracted_fields: Extracted fields dictionary
            threshold: Minimum extraction score to consider complete (default 50%)

        Returns:
            Validation result
        """
        extraction_score = extracted_fields.get("_extraction_score", 0.0)
        is_complete = extraction_score >= threshold

        return {
            "is_complete": is_complete,
            "extraction_score": extraction_score,
            "threshold": threshold,
            "status": "complete" if is_complete else "incomplete",
            "message": (
                f"Document is {'complete' if is_complete else 'incomplete'}: "
                f"{extraction_score:.0%} of fields extracted (threshold: {threshold:.0%})"
            )
        }


# Singleton instance
_metadata_extractor = None

def get_enhanced_metadata_extractor() -> EnhancedMetadataExtractor:
    """Get or create the enhanced metadata extractor instance"""
    global _metadata_extractor
    if _metadata_extractor is None:
        _metadata_extractor = EnhancedMetadataExtractor()
    return _metadata_extractor

