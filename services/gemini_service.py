"""
Enhanced Gemini Document Analyzer
Uses Gemini Vision + OCR for comprehensive document understanding
"""
import os
import io
import json
from typing import Dict, Any
from PIL import Image
import numpy as np
import cv2
from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)


class GeminiDocumentAnalyzer:
    """
    Advanced document analyzer using Gemini Vision AI.
    Combines OCR text with Gemini's own vision analysis for comprehensive extraction.
    """

    def __init__(self, api_key: str = None):
        """Initialize Gemini document analyzer."""
        logger.info("Initializing Gemini Document Analyzer...")

        try:
            # Hardcoded API key (as per user requirement)
            final_api_key = "AIzaSyBB4zqR0mf6xToxUdYzZ6rkrFJumwWGVE0"
            logger.info("   Using hardcoded API key")

            # Initialize Gemini client with the API key
            self.client = genai.Client(api_key=final_api_key)
            self.model = 'gemini-3-flash-preview'  # Using gemini-3-flash-preview as required
            self.available = True

            logger.info(f"✅ Gemini Document Analyzer ready!")
            logger.info(f"   Model: {self.model}")
            logger.info(f"   API Key (first 10 chars): {final_api_key[:10]}...")

        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
            self.available = False
            self.client = None

    def analyze_document(self, image: np.ndarray, ocr_text: str = None, max_retries: int = 3) -> Dict[str, Any]:
        """
        Comprehensive document analysis using Gemini Vision with retry logic.

        Args:
            image: Document image (numpy array)
            ocr_text: Pre-extracted OCR text (optional, Gemini will do its own OCR too)
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Complete analysis including signatures, fields, and extracted information
        """
        if not self.available:
            return {"error": "Gemini not available", "available": False}

        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                # Convert image to bytes
                if len(image.shape) == 2:
                    pil_image = Image.fromarray(image)
                else:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(rgb_image)

                # Resize if needed
                max_size = 2048  # Higher resolution for better text reading
                if max(pil_image.size) > max_size:
                    ratio = max_size / max(pil_image.size)
                    new_size = (int(pil_image.size[0] * ratio), int(pil_image.size[1] * ratio))
                    pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

                # Convert to bytes
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='PNG')
                image_bytes = img_byte_arr.getvalue()

                # Build comprehensive prompt
                prompt = self._build_analysis_prompt(ocr_text)

                # Call Gemini
                if attempt > 0:
                    logger.info(f"🔄 Retrying Gemini API call (attempt {attempt + 1}/{max_retries})...")
                else:
                    logger.info("📤 Sending document to Gemini for comprehensive analysis...")

                response = self.client.models.generate_content(
                    model=self.model,
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

                logger.info(f"✅ Gemini analysis complete!")
                logger.info(f"   • Signatures: {result.get('signatures', {}).get('count', 0)}")
                logger.info(f"   • Text extracted: {len(result.get('extracted_text', ''))} characters")
                logger.info(f"   • Fields found: {len(result.get('extracted_fields', {}))}")

                return result

            except json.JSONDecodeError as e:
                logger.warning(f"⚠️  JSON parse error: {e}")
                # Try to parse response_text if available
                if 'response_text' in locals():
                    return self._parse_fallback(response_text)
                else:
                    return self._parse_fallback("")

            except Exception as e:
                error_str = str(e)

                # Check for API key errors (non-retryable)
                if any(keyword in error_str for keyword in ['API_KEY_INVALID', 'API Key not found', 'INVALID_ARGUMENT', '400']):
                    logger.error("❌ Gemini API Key Error!")
                    logger.error(f"   Error: {error_str}")
                    logger.error("   💡 Solution:")
                    logger.error("      1. Visit: https://aistudio.google.com/app/apikey")
                    logger.error("      2. Generate a new API key")
                    logger.error("      3. Update your .env file: GEMINI_API_KEY=your_new_key")
                    logger.error("      4. Restart the server")
                    logger.error("      5. Run: python test_gemini_api_key.py to verify")
                    return {
                        "error": "Invalid or missing Gemini API key",
                        "error_type": "API_KEY_ERROR",
                        "available": False,
                        "solution": "Update GEMINI_API_KEY in .env file and restart server"
                    }

                # Check if it's a retryable error (503, rate limit, high demand)
                is_retryable = any(keyword in error_str.lower() for keyword in [
                    '503', 'unavailable', 'high demand', 'rate limit',
                    'quota', 'try again', 'temporarily', 'spike'
                ])

                if is_retryable and attempt < max_retries - 1:
                    # Calculate exponential backoff delay
                    import time
                    delay = (2 ** attempt) * 2  # 2s, 4s, 8s, 16s...
                    logger.warning(f"⚠️  Gemini API error (attempt {attempt + 1}/{max_retries}): {error_str}")
                    logger.info(f"⏳ Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    continue  # Retry
                else:
                    # Non-retryable error or max retries reached
                    if attempt >= max_retries - 1:
                        logger.error(f"❌ Gemini analysis failed after {max_retries} attempts")
                    else:
                        logger.error(f"❌ Gemini analysis failed with non-retryable error")

                    logger.error(f"Error: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    return {"error": str(e), "available": False}

        # Should not reach here, but just in case
        return {"error": "Max retries exceeded", "available": False}

    def _build_analysis_prompt(self, ocr_text: str = None) -> str:
        """Build comprehensive analysis prompt."""

        prompt = """You are analyzing a business document (likely a Bill of Lading, invoice, or shipping document).

TASK: Perform COMPREHENSIVE document analysis and extraction.

STEP 1: READ ALL TEXT (Use your own OCR)
- Extract ALL visible text from the document
- Include printed text, handwritten text, numbers, dates
- Maintain text structure and organization
"""

        if ocr_text:
            prompt += f"""
- I'm also providing pre-extracted OCR text for reference (but use your own OCR too):
{ocr_text[:2000]}
"""

        prompt += """

STEP 2: SIGNATURE DETECTION
Detect handwritten signatures:
- Count: How many actual handwritten signatures
- Location: Where each signature is (e.g., "bottom left", "shipper signature field")
- Signer: Who signed (name/role if readable)
- Type: handwritten/stamp/digital

DO NOT count as signatures:
- Printed names
- Empty signature lines
- Checkboxes or tick marks
- Form labels

STEP 3: CRITICAL FIELD EXTRACTION (IMPORTANT!)

**BOL NUMBER / ORDER NUMBER** (HIGHEST PRIORITY):
- Look for the PRIMARY BOL number (Bill of Lading number)
- It's usually a pure numeric value (e.g., "44853" or "40352")
- Common labels: "BOL #", "B/L #", "Bill of Lading #", "Order #", "Order No"
- Location: Usually in the top section of the document
- **IMPORTANT**: Extract ONLY the main BOL/Order number, NOT reference numbers or tracking numbers
- If multiple numbers appear, choose the one labeled as "BOL" or "Order"
- Return as a single number (e.g., "44853"), not a list

**CLIENT NAME** (REQUIRED):
- Find the main client/customer company name
- Common labels: "Shipper", "Client", "Customer", "From", "Consignor"
- Location: Usually in the shipper/from section
- Extract the company name only (not address)

**DOCUMENT DATE** (REQUIRED):
- Find the document creation/issue date
- Common labels: "Date", "Issued Date", "BOL Date", "Shipment Date"
- Location: Usually in the top section near BOL number
- Return in format: YYYY-MM-DD (e.g., "2024-01-15")

**OTHER FIELDS** (Extract if present):
- Consignee/Receiver name
- Invoice Numbers
- Email addresses
- Phone numbers
- Addresses

STEP 4: DOCUMENT METADATA
- Document type (BOL, Invoice, Receipt, etc.)
- Key parties involved (shipper, carrier, consignee)

Return response as JSON (NO markdown, NO code blocks):
{
  "extracted_text": "Complete text extracted from document using your OCR",
  "text_quality": "excellent/good/fair/poor",
  
  "signatures": {
    "count": <number>,
    "present": true/false,
    "details": [
      {
        "location": "description of location",
        "signer": "name or role if readable",
        "type": "handwritten/stamp/digital",
        "confidence": 0.0-1.0
      }
    ]
  },
  
  "extracted_fields": {
    "document_type": "BOL/Invoice/etc",
    "bol_number": "single BOL/Order number (e.g., 44853)",
    "order_number": "same as BOL number",
    "client_name": "main client/shipper company name",
    "document_date": "YYYY-MM-DD format",
    "consignee": "receiver/consignee name",
    "invoice_numbers": ["list if different from BOL"],
    "emails": ["list of emails"],
    "phone_numbers": ["list"],
    "shipper_address": "shipper full address",
    "consignee_address": "consignee full address"
  },
  
  "key_information": "2-3 sentence summary of the document",
  "confidence": 0.0-1.0
}

CRITICAL REMINDERS:
- bol_number should be a SINGLE number (e.g., "44853"), not a list
- order_number is the SAME as bol_number
- client_name is the shipper/from company name
- document_date must be in YYYY-MM-DD format
- Extract the PRIMARY BOL number, not secondary reference numbers

BE THOROUGH: Extract ALL information you can read from the document.
"""

        return prompt

    def _parse_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback parser if JSON fails."""
        import re

        result = {
            "extracted_text": "",
            "signatures": {"count": 0, "present": False, "details": []},
            "extracted_fields": {},
            "error": "JSON parse failed",
            "raw_response": text[:500]
        }

        # Try to extract signature count
        sig_match = re.search(r'"count"\s*:\s*(\d+)', text)
        if sig_match:
            count = int(sig_match.group(1))
            result["signatures"]["count"] = count
            result["signatures"]["present"] = count > 0

        return result

    def combine_ocr_results(self, easyocr_text: str, gemini_text: str, gemini_confidence: float = 0.0) -> str:
        """
        Combine EasyOCR and Gemini OCR results to get the best text.

        Args:
            easyocr_text: Text from EasyOCR
            gemini_text: Text from Gemini Vision
            gemini_confidence: Confidence from Gemini

        Returns:
            Combined/improved text
        """
        logger.info("🔄 Combining OCR results from EasyOCR and Gemini...")

        # If one is significantly longer, prefer that one
        easy_len = len(easyocr_text.strip()) if easyocr_text else 0
        gemini_len = len(gemini_text.strip()) if gemini_text else 0

        logger.info(f"   EasyOCR length: {easy_len} characters")
        logger.info(f"   Gemini length: {gemini_len} characters")

        # If Gemini has high confidence and more text, use it
        if gemini_confidence > 0.8 and gemini_len > easy_len:
            logger.info("   ✅ Using Gemini text (higher confidence and more content)")
            return gemini_text

        # If EasyOCR has significantly more text, use it
        if easy_len > gemini_len * 1.5:
            logger.info("   ✅ Using EasyOCR text (significantly more content)")
            return easyocr_text

        # If Gemini has more text, use it
        if gemini_len > easy_len:
            logger.info("   ✅ Using Gemini text (more content)")
            return gemini_text

        # Default to EasyOCR
        logger.info("   ✅ Using EasyOCR text (default)")
        return easyocr_text if easyocr_text else gemini_text


# Singleton instance
_gemini_analyzer = None

def get_gemini_analyzer() -> GeminiDocumentAnalyzer:
    """Get or create Gemini analyzer instance."""
    global _gemini_analyzer
    if _gemini_analyzer is None:
        _gemini_analyzer = GeminiDocumentAnalyzer()
    return _gemini_analyzer

