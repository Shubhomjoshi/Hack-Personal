"""
Document Classification Service - Classifies documents by type
"""
import re
from typing import Tuple
import logging
from models import DocumentType

logger = logging.getLogger(__name__)


class DocumentClassificationService:
    """Service for classifying document types"""

    # Keywords for each document type
    DOCUMENT_KEYWORDS = {
        DocumentType.BILL_OF_LADING: [
            'bill of lading', 'bol', 'b/l', 'shipper', 'consignee', 'carrier',
            'freight charges', 'shipping terms', 'vessel', 'port of loading'
        ],
        DocumentType.PROOF_OF_DELIVERY: [
            'proof of delivery', 'pod', 'delivery confirmation', 'received by',
            'signature of receiver', 'delivery date', 'delivery time'
        ],
        DocumentType.PACKING_LIST: [
            'packing list', 'pack list', 'package list', 'carton', 'quantity',
            'weight', 'dimensions', 'package contents', 'pcs', 'units'
        ],
        DocumentType.COMMERCIAL_INVOICE: [
            'commercial invoice', 'invoice', 'amount due', 'payment terms',
            'total amount', 'unit price', 'product description', 'invoice number'
        ],
        DocumentType.HAZMAT_DOCUMENT: [
            'hazmat', 'hazardous materials', 'dangerous goods', 'un number',
            'material safety', 'msds', 'hazard class', 'proper shipping name'
        ],
        DocumentType.LUMPER_RECEIPT: [
            'lumper receipt', 'lumper fee', 'unloading fee', 'loading fee',
            'labor charge', 'warehouse receipt'
        ],
        DocumentType.TRIP_SHEET: [
            'trip sheet', 'trip report', 'driver log', 'mileage', 'fuel stop',
            'state crossing', 'route', 'odometer'
        ],
        DocumentType.FREIGHT_INVOICE: [
            'freight invoice', 'freight bill', 'transportation charge',
            'carrier invoice', 'shipping invoice', 'freight charges'
        ]
    }

    def classify_document(self, text: str) -> Tuple[DocumentType, float]:
        """
        Classify document based on extracted text

        Args:
            text: Extracted text from document

        Returns:
            Tuple of (DocumentType, confidence_score)
        """
        # Handle error messages or scanned PDFs
        if not text or len(text.strip()) < 10 or "ERROR:" in text or "[SCANNED PDF" in text:
            logger.warning("Insufficient text for classification")
            return DocumentType.UNKNOWN, 0.0

        text_lower = text.lower()

        # Count keyword matches for each document type
        scores = {}
        for doc_type, keywords in self.DOCUMENT_KEYWORDS.items():
            score = 0
            matched_keywords = []

            for keyword in keywords:
                # Use regex for better matching
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += len(matches)
                    matched_keywords.append(keyword)

            scores[doc_type] = score

            if score > 0:
                logger.debug(f"{doc_type.value}: {score} points - Keywords: {matched_keywords}")

        # Find the document type with the highest score
        if not scores or max(scores.values()) == 0:
            return DocumentType.UNKNOWN, 0.0

        best_doc_type = max(scores, key=scores.get)
        best_score = scores[best_doc_type]

        # Calculate confidence based on score
        # Normalize to 0-1 range (assuming max 10 keyword matches is high confidence)
        confidence = min(best_score / 10.0, 1.0)

        # Require at least 2 keyword matches for non-UNKNOWN classification
        if best_score < 2:
            return DocumentType.UNKNOWN, confidence

        logger.info(f"Classified as {best_doc_type.value} with confidence {confidence:.2f}")

        return best_doc_type, confidence

    def classify_document_advanced(self, text: str, filename: str = "") -> Tuple[DocumentType, float]:
        """
        Advanced classification using both text and filename

        Args:
            text: Extracted text from document
            filename: Original filename

        Returns:
            Tuple of (DocumentType, confidence_score)
        """
        # First, try basic classification
        doc_type, text_confidence = self.classify_document(text)

        # Boost confidence if filename matches
        if filename:
            filename_lower = filename.lower()
            for dt, keywords in self.DOCUMENT_KEYWORDS.items():
                for keyword in keywords[:3]:  # Check top 3 keywords
                    if keyword in filename_lower:
                        if dt == doc_type:
                            # Boost confidence if matches
                            text_confidence = min(text_confidence + 0.1, 1.0)
                        elif doc_type == DocumentType.UNKNOWN:
                            # Use filename classification if text was unknown
                            doc_type = dt
                            text_confidence = 0.5
                        break

        return doc_type, text_confidence


# Singleton instance
classification_service = DocumentClassificationService()

