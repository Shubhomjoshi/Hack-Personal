"""
Document Type Classification Service
Uses keyword-based classification + Gemini Vision fallback for high accuracy
"""
import json
import logging
from typing import Dict, List
from dataclasses import dataclass
from services.gemini_service import get_gemini_analyzer

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Classification result container"""
    doc_type: str
    confidence: float
    method: str
    matched_keywords: List[str]


class KeywordDocumentClassifier:
    """Fast keyword-based document classifier"""

    # Strong keywords that almost guarantee a doc type
    STRONG_SIGNALS = {
        "Bill of Lading": [
            "bill of lading", "b/l", "bol", "shipper", "consignee",
            "notify party", "vessel", "port of loading", "port of discharge",
            "freight collect", "freight prepaid", "on board", "carrier",
            "scac", "pro number", "shipment", "freight charges"
        ],
        "Proof of Delivery": [
            "proof of delivery", "pod", "delivered to", "received in good condition",
            "delivery receipt", "consignee signature", "delivery confirmation",
            "goods received", "recipient signature", "delivery date",
            "received by", "date received"
        ],
        "Packing List": [
            "packing list", "pack list", "carton", "gross weight", "net weight",
            "dimensions", "pieces", "packages", "hs code", "item description",
            "quantity", "total packages", "package contents", "packing details"
        ],
        "Commercial Invoice": [
            "commercial invoice", "invoice no", "invoice number", "invoice date",
            "payment terms", "unit price", "total amount", "tax invoice",
            "seller", "buyer", "incoterms", "vat", "subtotal", "net total",
            "invoice total", "invoice amount"
        ],
        "Hazmat Document": [
            "hazardous", "hazmat", "dangerous goods", "un number", "un no",
            "class", "packing group", "emergency contact", "proper shipping name",
            "flashpoint", "placard", "imdg", "dot", "msds", "safety data",
            "un id", "hazard class", "emergency response"
        ],
        "Lumper Receipt": [
            "lumper", "lumper receipt", "unloading", "loading labor",
            "labor receipt", "lumper service", "unload receipt",
            "warehouse labor", "lumper fee", "lumper payment", "lumper charges"
        ],
        "Trip Sheet": [
            "trip sheet", "trip report", "odometer", "miles driven",
            "fuel stop", "state crossing", "driver log", "trip log",
            "departure time", "arrival time", "mileage", "fuel receipt",
            "trip number", "route", "stops"
        ],
        "Freight Invoice": [
            "freight invoice", "freight bill", "carrier invoice",
            "transportation charges", "freight charges", "linehaul",
            "fuel surcharge", "accessorial", "pro number", "pro#",
            "carrier charges", "transportation invoice"
        ]
    }

    def classify(self, text: str) -> ClassificationResult:
        """
        Classify document based on keyword matching

        Args:
            text: Extracted text from OCR

        Returns:
            ClassificationResult with doc type and confidence
        """
        if not text or len(text.strip()) < 10:
            return ClassificationResult("Unknown", 0.0, "keyword", [])

        text_lower = text.lower()
        scores = {}
        matched = {}

        for doc_type, keywords in self.STRONG_SIGNALS.items():
            hits = [kw for kw in keywords if kw in text_lower]
            # Weight calculation:
            # - Exact document name (e.g., "bill of lading"): 5.0 points
            # - Multi-word phrases (2+ words): 2.0 points
            # - Single words: 1.0 point
            score = 0
            for kw in hits:
                # Check if this is the exact document type name (first keyword in list)
                if kw == keywords[0]:  # First keyword is always the exact name
                    score += 5.0
                elif len(kw.split()) > 1:
                    score += 2.0
                else:
                    score += 1.0
            scores[doc_type] = score
            matched[doc_type] = hits

        if not any(scores.values()):
            return ClassificationResult("Unknown", 0.0, "keyword", [])

        best = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = scores[best] / total if total > 0 else 0

        logger.info(f"  Keyword classification: {best} ({confidence:.1%}) - matched: {matched[best][:3]}")

        return ClassificationResult(
            doc_type=best,
            confidence=round(confidence, 3),
            method="keyword",
            matched_keywords=matched[best]
        )


class GeminiDocumentClassifier:
    """Gemini Vision-based document classifier (fallback for low confidence)"""

    def __init__(self):
        self.gemini = get_gemini_analyzer()

    def classify(self, image_path: str, extracted_text: str) -> ClassificationResult:
        """
        Classify document using Gemini Vision

        Args:
            image_path: Path to document image
            extracted_text: Pre-extracted OCR text

        Returns:
            ClassificationResult with doc type and confidence
        """
        if not self.gemini or not self.gemini.available:
            logger.warning("  Gemini not available for classification")
            return ClassificationResult("Unknown", 0.0, "gemini_unavailable", [])

        try:
            # Build classification prompt
            prompt = self._build_classification_prompt(extracted_text)

            # Read image
            import cv2
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"  Failed to read image: {image_path}")
                return ClassificationResult("Unknown", 0.0, "gemini_error", [])

            # Call Gemini (reusing existing analyze_document infrastructure)
            logger.info("  Calling Gemini Vision for document classification...")

            # Use Gemini's built-in classification via custom prompt
            from PIL import Image
            import io
            import numpy as np

            # Convert to PIL Image
            if len(image.shape) == 2:
                pil_image = Image.fromarray(image)
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_image)

            # Resize if needed
            max_size = 2048
            if max(pil_image.size) > max_size:
                ratio = max_size / max(pil_image.size)
                new_size = (int(pil_image.size[0] * ratio), int(pil_image.size[1] * ratio))
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            image_bytes = img_byte_arr.getvalue()

            # Call Gemini
            from google import genai
            from google.genai import types

            response = self.gemini.client.models.generate_content(
                model=self.gemini.model,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/png',
                    ),
                    prompt
                ]
            )

            # Parse response
            response_text = response.text.strip()

            # Clean markdown
            if "```" in response_text:
                parts = response_text.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    if part.startswith("{") and part.endswith("}"):
                        response_text = part
                        break

            result = json.loads(response_text)

            logger.info(f"  Gemini classification: {result.get('doc_type')} ({result.get('confidence', 0):.1%})")

            return ClassificationResult(
                doc_type=result.get("doc_type", "Unknown"),
                confidence=float(result.get("confidence", 0.0)),
                method="gemini_vision",
                matched_keywords=result.get("key_evidence", [])
            )

        except json.JSONDecodeError as e:
            logger.error(f"  JSON parse error in Gemini classification: {e}")
            return ClassificationResult("Unknown", 0.0, "gemini_json_error", [])
        except Exception as e:
            logger.error(f"  Error in Gemini classification: {e}")
            return ClassificationResult("Unknown", 0.0, "gemini_error", [])

    def _build_classification_prompt(self, extracted_text: str) -> str:
        """Build classification prompt for Gemini"""

        prompt = f"""You are classifying a trucking/shipping industry document.

The OCR text extracted from this document is:
---
{extracted_text[:2000]}
---

Classify this document into EXACTLY ONE of these types:
1. Bill of Lading
2. Proof of Delivery
3. Packing List
4. Commercial Invoice
5. Hazmat Document
6. Lumper Receipt
7. Trip Sheet
8. Freight Invoice
9. Unknown

Use both the visual layout AND the extracted text to make your decision.

Return ONLY valid JSON (NO markdown, NO code blocks):
{{
  "doc_type": "exact name from list above",
  "confidence": 0.0-1.0,
  "reasoning": "one sentence explanation",
  "key_evidence": ["evidence1", "evidence2"]
}}
"""
        return prompt


class DocumentTypeClassifier:
    """
    Main document classifier - combines keyword + Gemini Vision
    """

    def __init__(self):
        self.keyword_clf = KeywordDocumentClassifier()
        self.gemini_clf = GeminiDocumentClassifier()

        # Confidence threshold — below this, escalate to Gemini
        self.CONFIDENCE_THRESHOLD = 0.55

    def classify(self, extracted_text: str, image_path: str = None) -> Dict:
        """
        Classify document using multi-stage approach

        Args:
            extracted_text: Combined OCR text from EasyOCR + Gemini
            image_path: Path to document image (optional, for Gemini fallback)

        Returns:
            Dict with classification results
        """
        logger.info("🔍 Starting document classification...")

        # Stage 1: Fast keyword classification
        keyword_result = self.keyword_clf.classify(extracted_text)

        logger.info(f"  Keyword result: {keyword_result.doc_type} ({keyword_result.confidence:.0%})")

        # Stage 2: High confidence → done
        if keyword_result.confidence >= self.CONFIDENCE_THRESHOLD:
            return self._format(keyword_result)

        # Stage 3: Low confidence → use Gemini Vision (if available)
        if image_path and self.gemini_clf.gemini and self.gemini_clf.gemini.available:
            logger.info(f"  Low confidence ({keyword_result.confidence:.0%}) — escalating to Gemini Vision...")
            gemini_result = self.gemini_clf.classify(image_path, extracted_text)

            # Stage 4: Merge both signals
            final = self._merge(keyword_result, gemini_result)
            return self._format(final)
        else:
            # No Gemini available, return keyword result
            logger.warning("  Gemini not available, using keyword result only")
            return self._format(keyword_result)

    def _merge(self, kw: ClassificationResult, gem: ClassificationResult) -> ClassificationResult:
        """Merge keyword and Gemini results"""

        # If they agree → high confidence
        if kw.doc_type == gem.doc_type:
            return ClassificationResult(
                doc_type=gem.doc_type,
                confidence=min(0.99, (kw.confidence + gem.confidence) / 2 + 0.2),
                method="keyword+gemini_agreed",
                matched_keywords=kw.matched_keywords + gem.matched_keywords
            )

        # If they disagree → trust Gemini (vision > keywords for edge cases)
        logger.info(f"  Disagreement: Keyword={kw.doc_type}, Gemini={gem.doc_type} → Using Gemini")
        return ClassificationResult(
            doc_type=gem.doc_type,
            confidence=gem.confidence * 0.85,  # slight penalty for disagreement
            method="gemini_override",
            matched_keywords=gem.matched_keywords
        )

    def _format(self, result: ClassificationResult) -> Dict:
        """Format classification result for database storage"""

        status = (
            "high_confidence" if result.confidence >= 0.75
            else "medium_confidence" if result.confidence >= 0.5
            else "needs_review"
        )

        # Map to DocumentType enum values
        doc_type_map = {
            "Bill of Lading": "Bill of Lading",
            "Proof of Delivery": "Proof of Delivery",
            "Packing List": "Packing List",
            "Commercial Invoice": "Commercial Invoice",
            "Hazmat Document": "Hazmat Document",
            "Lumper Receipt": "Lumper Receipt",
            "Trip Sheet": "Trip Sheet",
            "Freight Invoice": "Freight Invoice",
            "Unknown": "Unknown"
        }

        doc_type = doc_type_map.get(result.doc_type, "Unknown")

        logger.info(f"  ✅ Classification complete: {doc_type} ({result.confidence:.0%}) via {result.method}")

        return {
            "doc_type": doc_type,
            "confidence": result.confidence,
            "confidence_status": status,
            "method_used": result.method,
            "matched_evidence": result.matched_keywords[:5],  # Top 5 evidence
            "needs_manual_review": result.confidence < 0.5
        }


# Singleton instance
_document_classifier = None


def get_document_classifier() -> DocumentTypeClassifier:
    """Get or create document classifier instance"""
    global _document_classifier
    if _document_classifier is None:
        _document_classifier = DocumentTypeClassifier()
    return _document_classifier


