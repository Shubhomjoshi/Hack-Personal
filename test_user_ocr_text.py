"""
Test the document classifier with the user's actual OCR text
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.document_classifier import get_document_classifier

print("=" * 70)
print("TESTING DOCUMENT CLASSIFICATION WITH ACTUAL OCR TEXT")
print("=" * 70)

# User's actual OCR text
user_ocr_text = """2/19/26, 1:47 AM Bill of Lading Form | Printable Template
Bill of Lading
Date: 19-February-2026
Ship From:
Mumbai
Bill of Lading No: 435355
BARCODE SPACE
SID#: 34234234234 [ ] FOB
Carrier Name: Carrier Name
Trailer No: T7868
Ship To:
Location No:
Seal Number(s): 4565464645
Pune
SCAC: 456546456
Pro No: 456546546
BARCODE SPACE
CID#: 757732424 [ ] FOB
Third Party Freight Charges - Bill To:
Pune Ravet
Freight Charge Terms (prepaid unless marked otherwise)
[ ] Prepaid [ ] Collect [ ] 3rd Party
[ ] Master BOL: w/attached underlying BOLs
Special Instructions:
Customer Order Information
Customer Order No. # Pkgs. Weight Pallet/Slip (Y/N) Additional Shipper Info
Totals
Carrier Information
Handling Unit Package Commodity Description LTL Only
QTY TYPE QTY TYPE Weight H.M. (X) Commodities requiring special or additional care or attention in handling or stowing must be marked and packaged as to ensure safe transportation with ordinary care. See Section 2(e) of NMFC Item 360 NMFC No. Class
Totals
Where the rate is dependent on value, shippers are required to state specifically in writing the agreed or declared value of the property as follows:
"The agreed or declared value of the property is specifically stated by the shipper to be not exceeding ______ FOB ______"
COD Amt. $__________
Fee Terms: [ ] Collect [ ] Prepaid
[ ] Customer Check Acceptable
NOTE: Liability Limitation for loss or damage in this shipment may be applicable. See 49 U.S.C. - 14706(c)(1)(A) and (B).
RECEIVED, subject to individually determined rates or contracts that have been agreed upon in between the carrier and shipper; if applicable; otherwise to the rates, classifications and rules that have been established by the carrier and are available to the shipper, on request, and to all applicable state and federal regulations.
The carrier shall not make delivery of this shipment without payment of freight and all other lawful charges.
Shipper Signature____________________
This is to certify that the above named materials are properly classified, packaged, marked and labeled, and are in proper condition for transportation according to the applicable regulations of the DOT.
Trailer Loaded:
[ ] By Shipper
[ ] By Driver
Freight Counted:
[ ] By Shipper
[ ] By Driver/pallets said to contain
[ ] By Driver/Pieces
Carrier acknowledges receipt of packages and required placards. Carrier certifies emergency response information was made available and/or carrier has the DOT emergency response guidebook or equivalent documentation in the vehicle. Property described above is received in good order, except as noted.
Shipper Signature____________________ Date__________
Carrier Signature____________________ Pickup Date__________
https://billoflading.org 1/1"""

print("\n1️⃣  Testing with user's actual OCR text...")
print(f"   Text length: {len(user_ocr_text)} characters")
print(f"   First 100 chars: {user_ocr_text[:100]}...")

# Initialize classifier
classifier = get_document_classifier()

# Test classification
result = classifier.classify(
    extracted_text=user_ocr_text,
    image_path=None
)

print("\n2️⃣  Classification Results:")
print(f"   Document Type: {result['doc_type']}")
print(f"   Confidence: {result['confidence']:.1%}")
print(f"   Method Used: {result['method_used']}")
print(f"   Confidence Status: {result['confidence_status']}")
print(f"   Matched Evidence: {result['matched_evidence']}")

# Check if it found "Bill of Lading"
if result['doc_type'] == "Bill of Lading":
    print("\n✅ SUCCESS! Document correctly identified as Bill of Lading")
else:
    print(f"\n❌ FAILED! Document identified as: {result['doc_type']}")
    print("   Expected: Bill of Lading")

# Show which keywords were found
print("\n3️⃣  Keyword Analysis:")
text_lower = user_ocr_text.lower()
bol_keywords = [
    "bill of lading", "b/l", "bol", "shipper", "consignee",
    "carrier", "scac", "pro number", "freight charges", "freight collect"
]

found_keywords = []
for kw in bol_keywords:
    if kw in text_lower:
        count = text_lower.count(kw)
        found_keywords.append(f"{kw} ({count}x)")

print(f"   Found BOL keywords: {', '.join(found_keywords)}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

