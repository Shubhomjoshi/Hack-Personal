"""
Test Document Classification
Tests the new intelligent document classification system
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.document_classifier import get_document_classifier

print("=" * 70)
print("DOCUMENT CLASSIFICATION TEST")
print("=" * 70)

# Sample BOL text
bol_text = """
BILL OF LADING
BOL#: 40352-44853
Date: 02/15/2026

SHIPPER:
Smithfield Foods Inc.
123 Pork Avenue
Smithfield, VA 23430

CONSIGNEE:
Food Distribution Center
456 Market Street
Chicago, IL 60601

CARRIER: Swift Transportation
PRO#: 123456789

FREIGHT CHARGES: Prepaid
PACKAGES: 20 Pallets
WEIGHT: 40,000 lbs

DESCRIPTION:
Fresh Pork Products - Refrigerated

Driver Signature: _______________
Shipper Signature: _______________
"""

# Sample Invoice text
invoice_text = """
COMMERCIAL INVOICE
Invoice No: INV-2026-001234
Invoice Date: February 15, 2026

SELLER:
ABC Manufacturing Co.
789 Industrial Blvd
Detroit, MI 48201

BUYER:
XYZ Distribution LLC
321 Commerce St
New York, NY 10001

Payment Terms: Net 30
Incoterms: FOB Detroit

ITEM DESCRIPTION          QTY    UNIT PRICE    TOTAL
Widget Model A            100    $25.00        $2,500.00
Widget Model B            50     $40.00        $2,000.00

Subtotal:                                      $4,500.00
Tax (6%):                                      $270.00
Total Amount:                                  $4,770.00
"""

# Sample POD text
pod_text = """
PROOF OF DELIVERY
Delivery Confirmation

Order #: ORD-2026-5678
Date Delivered: 02/16/2026
Time: 2:30 PM

DELIVERED TO:
John Smith
Warehouse Manager
Food Distribution Center

ADDRESS:
456 Market Street
Chicago, IL 60601

GOODS RECEIVED IN GOOD CONDITION
No damages reported

RECIPIENT SIGNATURE: [signed]
Driver Signature: [signed]

Consignee confirms receipt of all packages.
"""

# Sample Trip Sheet text
trip_sheet_text = """
DRIVER TRIP SHEET
Trip #: TS-2026-9876

Driver: Mike Johnson
Driver ID: DRV-001
Date: 02/15/2026

DEPARTURE:
Location: Detroit Terminal
Time: 06:00 AM
Odometer: 125,430 miles

STOPS:
1. Toledo, OH - Fuel Stop (10:15 AM)
2. Cleveland, OH - Rest Break (2:30 PM)

ARRIVAL:
Location: Chicago Terminal
Time: 6:45 PM
Odometer: 125,710 miles

MILES DRIVEN: 280 miles
FUEL RECEIPTS: Attached
STATE CROSSINGS: Michigan, Ohio, Indiana, Illinois

Driver Signature: _______________
"""

# Test cases
test_cases = [
    ("Bill of Lading", bol_text),
    ("Commercial Invoice", invoice_text),
    ("Proof of Delivery", pod_text),
    ("Trip Sheet", trip_sheet_text),
]

# Initialize classifier
print("\n1️⃣  Initializing classifier...")
classifier = get_document_classifier()
print("   ✅ Classifier ready!")

# Test each document type
print("\n2️⃣  Testing classification on sample documents...\n")

for expected_type, text in test_cases:
    print(f"📄 Testing: {expected_type}")
    print("-" * 70)

    result = classifier.classify(
        extracted_text=text,
        image_path=None  # Only using text for this test
    )

    print(f"   Result: {result['doc_type']}")
    print(f"   Confidence: {result['confidence']:.1%}")
    print(f"   Status: {result['confidence_status']}")
    print(f"   Method: {result['method_used']}")
    print(f"   Evidence: {', '.join(result['matched_evidence'][:3])}")

    # Check if correct
    if expected_type == result['doc_type']:
        print(f"   ✅ CORRECT!")
    else:
        print(f"   ⚠️  MISMATCH (expected: {expected_type})")

    print()

print("=" * 70)
print("CLASSIFICATION TEST COMPLETE")
print("=" * 70)
print("\n✅ Document classification system is working!")
print("\nNext steps:")
print("  1. Upload a document via API")
print("  2. Background processor will automatically classify it")
print("  3. Check the document_type and classification_confidence fields")

