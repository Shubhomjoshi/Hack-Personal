"""
Display Configuration for Document Fields
Defines which fields to show for each document type and in what order
"""
from typing import List, Dict, Optional
from models import DocumentType


DISPLAY_CONFIGS = {
    DocumentType.BILL_OF_LADING: [
        {"key": "bol_number",      "label": "BOL Number",       "icon": "📋", "highlight": True},
        {"key": "order_number",    "label": "Order / Load No",  "icon": "🔢", "highlight": True},
        {"key": "shipper",         "label": "Shipper",          "icon": "📦"},
        {"key": "consignee",       "label": "Consignee",        "icon": "🏢"},
        {"key": "origin",          "label": "Origin",           "icon": "📍"},
        {"key": "destination",     "label": "Destination",      "icon": "🎯"},
        {"key": "ship_date",       "label": "Ship Date",        "icon": "📅"},
        {"key": "carrier",         "label": "Carrier",          "icon": "🚛"},
        {"key": "total_weight",    "label": "Total Weight",     "icon": "⚖️"},
        {"key": "total_pieces",    "label": "Total Pieces",     "icon": "📊"},
        {"key": "freight_terms",   "label": "Freight Terms",    "icon": "💼"},
    ],

    DocumentType.PROOF_OF_DELIVERY: [
        {"key": "order_number",    "label": "Order / Load No",  "icon": "🔢", "highlight": True},
        {"key": "delivery_date",   "label": "Delivery Date",    "icon": "📅", "highlight": True},
        {"key": "delivery_time",   "label": "Delivery Time",    "icon": "⏰"},
        {"key": "delivered_to",    "label": "Delivered To",     "icon": "👤"},
        {"key": "delivery_address","label": "Address",          "icon": "📍"},
        {"key": "condition",       "label": "Condition",        "icon": "✅"},
        {"key": "driver_name",     "label": "Driver",           "icon": "🚛"},
        {"key": "exceptions",      "label": "Exceptions",       "icon": "⚠️"},
    ],

    DocumentType.COMMERCIAL_INVOICE: [
        {"key": "invoice_number",  "label": "Invoice No",       "icon": "🧾", "highlight": True},
        {"key": "order_number",    "label": "Order No",         "icon": "🔢", "highlight": True},
        {"key": "invoice_date",    "label": "Invoice Date",     "icon": "📅"},
        {"key": "seller",          "label": "Seller",           "icon": "🏭"},
        {"key": "buyer",           "label": "Buyer",            "icon": "🏢"},
        {"key": "total_amount",    "label": "Total Amount",     "icon": "💰"},
        {"key": "currency",        "label": "Currency",         "icon": "💱"},
        {"key": "payment_terms",   "label": "Payment Terms",    "icon": "📋"},
        {"key": "incoterms",       "label": "Incoterms",        "icon": "🌐"},
    ],

    DocumentType.PACKING_LIST: [
        {"key": "order_number",    "label": "Order No",         "icon": "🔢", "highlight": True},
        {"key": "packing_date",    "label": "Packing Date",     "icon": "📅"},
        {"key": "total_cartons",   "label": "Total Cartons",    "icon": "📦"},
        {"key": "gross_weight",    "label": "Gross Weight",     "icon": "⚖️"},
        {"key": "net_weight",      "label": "Net Weight",       "icon": "⚖️"},
        {"key": "total_volume",    "label": "Total Volume",     "icon": "📐"},
        {"key": "destination",     "label": "Destination",      "icon": "🎯"},
    ],

    DocumentType.HAZMAT_DOCUMENT: [
        {"key": "un_number",       "label": "UN Number",        "icon": "⚠️", "highlight": True},
        {"key": "shipping_name",   "label": "Shipping Name",    "icon": "📋", "highlight": True},
        {"key": "hazard_class",    "label": "Hazard Class",     "icon": "🔥"},
        {"key": "packing_group",   "label": "Packing Group",    "icon": "📦"},
        {"key": "total_quantity",  "label": "Total Quantity",   "icon": "📊"},
        {"key": "emergency_contact","label": "Emergency Contact","icon": "🆘"},
        {"key": "shipper",         "label": "Shipper",          "icon": "🏭"},
    ],

    DocumentType.LUMPER_RECEIPT: [
        {"key": "order_number",    "label": "Order / Load No",  "icon": "🔢", "highlight": True},
        {"key": "date",            "label": "Date",             "icon": "📅"},
        {"key": "lumper_company",  "label": "Lumper Company",   "icon": "🏢"},
        {"key": "worker_name",     "label": "Worker Name",      "icon": "👤"},
        {"key": "service_type",    "label": "Service Type",     "icon": "🔧"},
        {"key": "hours_worked",    "label": "Hours Worked",     "icon": "⏱️"},
        {"key": "amount",          "label": "Amount Paid",      "icon": "💰"},
        {"key": "facility",        "label": "Facility",         "icon": "🏭"},
    ],

    DocumentType.TRIP_SHEET: [
        {"key": "trip_number",     "label": "Trip / Load No",   "icon": "🗺️", "highlight": True},
        {"key": "driver_name",     "label": "Driver Name",      "icon": "👤", "highlight": True},
        {"key": "truck_number",    "label": "Truck / Unit No",  "icon": "🚛"},
        {"key": "date",            "label": "Date",             "icon": "📅"},
        {"key": "total_miles",     "label": "Total Miles",      "icon": "📍"},
        {"key": "origin",          "label": "Origin",           "icon": "🟢"},
        {"key": "destination",     "label": "Destination",      "icon": "🔴"},
        {"key": "fuel_stops",      "label": "Fuel Stops",       "icon": "⛽"},
        {"key": "states_crossed",  "label": "States Crossed",   "icon": "🗾"},
    ],

    DocumentType.FREIGHT_INVOICE: [
        {"key": "pro_number",      "label": "PRO Number",       "icon": "📑", "highlight": True},
        {"key": "invoice_number",  "label": "Invoice No",       "icon": "🧾", "highlight": True},
        {"key": "order_number",    "label": "Order / Load No",  "icon": "🔢"},
        {"key": "invoice_date",    "label": "Invoice Date",     "icon": "📅"},
        {"key": "carrier_name",    "label": "Carrier",          "icon": "🚛"},
        {"key": "origin",          "label": "Origin",           "icon": "📍"},
        {"key": "destination",     "label": "Destination",      "icon": "🎯"},
        {"key": "linehaul",        "label": "Linehaul",         "icon": "💵"},
        {"key": "fuel_surcharge",  "label": "Fuel Surcharge",   "icon": "⛽"},
        {"key": "accessorial",     "label": "Accessorial",      "icon": "➕"},
        {"key": "total_charges",   "label": "Total Charges",    "icon": "💰"},
        {"key": "payment_due",     "label": "Payment Due",      "icon": "📅"},
    ],
}


def get_display_config(doc_type: DocumentType, metadata: Dict) -> List[Dict]:
    """
    Get display configuration for a document type with actual values attached
    Returns "N/A" for missing fields instead of null

    Args:
        doc_type: Document type enum
        metadata: Extracted metadata dictionary

    Returns:
        List of field configurations with values (N/A for missing fields)
    """
    config = DISPLAY_CONFIGS.get(doc_type, [])

    # Get doc_type_fields from metadata
    doc_type_fields = metadata.get('doc_type_fields', {}) if metadata else {}

    # Attach actual values to config, use "N/A" for missing fields
    return [
        {
            **field,
            "value": doc_type_fields.get(field["key"]) or "N/A",  # Return "N/A" instead of None
            "empty": doc_type_fields.get(field["key"]) is None
        }
        for field in config
    ]


def get_primary_identifier(doc_type: DocumentType, metadata: Dict) -> str:
    """
    Get the primary identifier for a document type (for list view)
    Returns "N/A" if not found

    Args:
        doc_type: Document type enum
        metadata: Extracted metadata dictionary

    Returns:
        Primary identifier string or "N/A"
    """
    if not metadata:
        return "N/A"

    doc_type_fields = metadata.get('doc_type_fields', {})

    # Map of document type to primary identifier field
    primary_id_map = {
        DocumentType.BILL_OF_LADING: doc_type_fields.get("bol_number") or doc_type_fields.get("order_number"),
        DocumentType.PROOF_OF_DELIVERY: doc_type_fields.get("order_number"),
        DocumentType.COMMERCIAL_INVOICE: doc_type_fields.get("invoice_number"),
        DocumentType.PACKING_LIST: doc_type_fields.get("order_number"),
        DocumentType.HAZMAT_DOCUMENT: doc_type_fields.get("un_number"),
        DocumentType.LUMPER_RECEIPT: doc_type_fields.get("order_number"),
        DocumentType.TRIP_SHEET: doc_type_fields.get("trip_number"),
        DocumentType.FREIGHT_INVOICE: doc_type_fields.get("pro_number") or doc_type_fields.get("invoice_number"),
    }

    return primary_id_map.get(doc_type) or "N/A"

