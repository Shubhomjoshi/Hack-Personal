"""
AI Agent for Intelligent Document Processing
Uses Gemini 2.0 Flash to make smart decisions about OCR strategy, quality assessment, and processing optimization.
"""
import os
import json
import time
import logging
from typing import Dict, Any, List
from google import genai
from google.genai import types
import numpy as np
import cv2
from PIL import Image
import io

logger = logging.getLogger(__name__)


class DocumentProcessingAgent:
    """
    Intelligent AI Agent that orchestrates document processing.
    Makes decisions about:
    - Which OCR to use (EasyOCR, Gemini, or both)
    - Quality assessment strategy
    - Processing optimization
    - Error handling and recovery
    """

    def __init__(self, api_key: str = None):
        """Initialize the AI Agent"""
        logger.info("🤖 Initializing Document Processing Agent...")

        try:
            if api_key:
                os.environ['GEMINI_API_KEY'] = api_key
            elif not os.getenv('GEMINI_API_KEY'):
                raise ValueError("No API key provided")

            self.client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
            self.model = 'gemini-3-flash-preview'
            self.available = True

            # Agent memory (stores learning from past documents)
            self.processing_history = []

            logger.info(f"✅ Document Processing Agent ready!")
            logger.info(f"   Model: {self.model}")

        except Exception as e:
            logger.warning(f"⚠️  Agent initialization failed: {e}")
            self.available = False
            self.client = None

    def decide_processing_strategy(
        self,
        file_path: str,
        file_size: int,
        file_format: str,
        initial_quality_score: float = None
    ) -> Dict[str, Any]:
        """
        AI Agent decides the optimal processing strategy for a document.
        Uses LOCAL heuristics (no Gemini call) to avoid extra API costs.

        Args:
            file_path: Path to the document
            file_size: File size in bytes
            file_format: File format (pdf, jpg, png)
            initial_quality_score: Quick quality assessment (if available)

        Returns:
            Processing strategy with detailed instructions
        """
        logger.info("🧠 [AGENT] Analyzing document to decide processing strategy...")

        try:
            # Get file characteristics
            file_ext = file_format.lower()
            size_kb = file_size / 1024
            size_mb = size_kb / 1024

            # ============================================
            # DECISION LOGIC (LOCAL - NO API CALL)
            # ============================================

            strategy = "enhanced_ocr"  # Default
            reasoning = ""
            confidence = 0.8
            estimated_time = 5
            estimated_api_calls = 1
            skip_easyocr = False
            quality_check_first = True

            # Rule 1: Large high-quality PDFs → fast_track
            if file_ext == '.pdf' and size_mb > 2.0:
                strategy = "fast_track"
                reasoning = f"Large PDF ({size_mb:.1f} MB) likely has clear digital text. Skip EasyOCR to save time."
                estimated_time = 2
                estimated_api_calls = 1
                skip_easyocr = True
                confidence = 0.85

            # Rule 2: Small files → quality_first (might be low quality)
            elif size_kb < 500:
                strategy = "quality_first"
                reasoning = f"Small file ({size_kb:.1f} KB) may be low quality. Check quality before OCR."
                estimated_time = 3
                estimated_api_calls = 1
                quality_check_first = True
                confidence = 0.75

            # Rule 3: Very high quality score → fast_track
            elif initial_quality_score and initial_quality_score > 85:
                strategy = "fast_track"
                reasoning = f"High quality score ({initial_quality_score:.1f}%) detected. Use only Gemini for speed."
                estimated_time = 2
                estimated_api_calls = 1
                skip_easyocr = True
                confidence = 0.9

            # Rule 4: Low quality score → dual_ocr (need both for accuracy)
            elif initial_quality_score and initial_quality_score < 60:
                strategy = "dual_ocr"
                reasoning = f"Low quality ({initial_quality_score:.1f}%) detected. Use both OCRs for maximum accuracy."
                estimated_time = 5
                estimated_api_calls = 1
                confidence = 0.8

            # Rule 5: Mobile photos (JPG/PNG) → enhanced_ocr
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                strategy = "enhanced_ocr"
                reasoning = f"Mobile photo format ({file_ext}). Use EasyOCR first, then Gemini if needed."
                estimated_time = 4
                estimated_api_calls = 1
                confidence = 0.8

            # Rule 6: Default for everything else
            else:
                strategy = "enhanced_ocr"
                reasoning = f"Standard document ({file_ext}, {size_kb:.1f} KB). Balanced approach."
                estimated_time = 4
                estimated_api_calls = 1
                confidence = 0.75

            # Add learning insights
            historical_insights = self._get_historical_insights()
            if historical_insights and "Recent avg" in historical_insights:
                reasoning += f" {historical_insights}"

            result = {
                "strategy": strategy,
                "reasoning": reasoning,
                "confidence": confidence,
                "estimated_time_seconds": estimated_time,
                "estimated_api_calls": estimated_api_calls,
                "skip_easyocr": skip_easyocr,
                "quality_check_first": quality_check_first,
                "ocr_confidence_threshold": 0.70,
                "expected_challenges": [],
                "optimization_tips": []
            }

            logger.info(f"✅ [AGENT] Strategy decided: {result['strategy']}")
            logger.info(f"   Reasoning: {result['reasoning']}")
            logger.info(f"   Confidence: {result['confidence']:.0%}")
            logger.info(f"   Estimated time: {result['estimated_time_seconds']}s")
            logger.info(f"   API calls: {result['estimated_api_calls']}")
            logger.info(f"   🎯 NO EXTRA GEMINI CALL - Using local heuristics")

            return result

        except Exception as e:
            logger.error(f"❌ [AGENT] Strategy decision failed: {e}")
            return self._get_fallback_strategy()

    def provide_quality_feedback(
        self,
        image: np.ndarray,
        quality_score: float,
        blur_score: float,
        skew_angle: float,
        brightness: float
    ) -> Dict[str, Any]:
        """
        AI Agent provides actionable feedback on document quality.

        Args:
            image: Document image (numpy array)
            quality_score: Overall quality score (0-100)
            blur_score: Blur detection score
            skew_angle: Skew angle in degrees
            brightness: Brightness score

        Returns:
            Detailed feedback with actionable suggestions
        """
        if not self.available:
            return self._get_fallback_feedback(quality_score)

        logger.info("🔍 [AGENT] Analyzing document quality for feedback...")

        try:
            # Convert image to bytes
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else image)
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            image_bytes = img_byte_arr.getvalue()

            prompt = f"""
You are a quality coach agent helping truck drivers capture better document images.

**Current Document Quality Metrics:**
- Overall quality score: {quality_score:.1f}/100
- Blur score: {blur_score:.2f} (higher = more blurry)
- Skew angle: {skew_angle:.1f}°
- Brightness: {brightness:.2f}

**Your Task:**
Analyze the image and provide SPECIFIC, ACTIONABLE feedback to help the driver improve.

**Guidelines:**
- If blur_score > 100: "Image is too blurry"
- If skew_angle > 15°: "Document is tilted/skewed"
- If brightness < 0.3: "Image is too dark"
- If brightness > 0.7: "Image is too bright/washed out"
- Look for: edges cut off, shadows, glare, wrong document, multiple pages

**Tone:** Friendly, helpful, specific (not technical)

Return JSON:
{{
  "is_usable": true/false,
  "confidence": 0.0-1.0,
  "issues_detected": [
    {{
      "issue": "too blurry",
      "severity": "critical|high|medium|low",
      "explanation": "The text is not readable due to camera shake"
    }}
  ],
  "actionable_suggestions": [
    "Hold your phone steady for 2 seconds before taking the photo",
    "Rest your phone on a flat surface",
    "Move closer to the document"
  ],
  "estimated_reupload_success": "85%",
  "specific_problems": {{
    "blur": "yes|no",
    "skew": "yes|no",
    "lighting": "too_dark|too_bright|good",
    "edges_cut": "yes|no",
    "glare": "yes|no"
  }}
}}

Be honest but encouraging. Help the driver succeed on the next upload.
"""

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type='image/png')
                ],
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    response_mime_type="application/json"
                )
            )

            feedback = json.loads(response.text)

            logger.info(f"✅ [AGENT] Quality feedback generated")
            logger.info(f"   Usable: {feedback['is_usable']}")
            logger.info(f"   Issues: {len(feedback['issues_detected'])}")
            logger.info(f"   Suggestions: {len(feedback['actionable_suggestions'])}")

            return feedback

        except Exception as e:
            logger.error(f"❌ [AGENT] Quality feedback failed: {e}")
            return self._get_fallback_feedback(quality_score)

    def optimize_ocr_execution(
        self,
        strategy: Dict[str, Any],
        easyocr_result: Dict = None,
        gemini_result: Dict = None
    ) -> Dict[str, Any]:
        """
        AI Agent decides if additional OCR is needed or if current results are sufficient.
        Uses LOCAL heuristics (no Gemini call) to avoid extra API costs.

        Args:
            strategy: The original processing strategy
            easyocr_result: Result from EasyOCR (if executed)
            gemini_result: Result from Gemini (if executed)

        Returns:
            Decision on next steps
        """
        logger.info("🔄 [AGENT] Optimizing OCR execution based on current results...")

        try:
            # ============================================
            # LOCAL DECISION LOGIC (NO API CALL)
            # ============================================

            skip_gemini = False
            reasoning = ""
            estimated_accuracy = 0.85
            cost_savings = "$0"

            # If both already executed, stop
            if easyocr_result and gemini_result:
                return {
                    "continue_processing": False,
                    "skip_gemini": False,
                    "reasoning": "Both OCRs already executed",
                    "estimated_final_accuracy": 0.95,
                    "cost_savings": "$0"
                }

            # If we have EasyOCR results, analyze them
            if easyocr_result:
                confidence = easyocr_result.get('confidence', 0)
                text_length = len(easyocr_result.get('text', ''))

                # Rule 1: High confidence + sufficient text → skip Gemini
                if confidence > 0.85 and text_length > 500:
                    skip_gemini = True
                    reasoning = f"EasyOCR confidence high ({confidence:.0%}) with {text_length} chars extracted. Gemini not needed."
                    estimated_accuracy = 0.88
                    cost_savings = "$0.001"

                # Rule 2: Very high confidence + reasonable text → skip Gemini
                elif confidence > 0.90 and text_length > 200:
                    skip_gemini = True
                    reasoning = f"EasyOCR confidence very high ({confidence:.0%}). Sufficient quality."
                    estimated_accuracy = 0.90
                    cost_savings = "$0.001"

                # Rule 3: Low confidence → need Gemini
                elif confidence < 0.70:
                    skip_gemini = False
                    reasoning = f"EasyOCR confidence low ({confidence:.0%}). Running Gemini for better accuracy."
                    estimated_accuracy = 0.92
                    cost_savings = "$0"

                # Rule 4: Short text → need Gemini
                elif text_length < 100:
                    skip_gemini = False
                    reasoning = f"EasyOCR found only {text_length} chars. Running Gemini to ensure completeness."
                    estimated_accuracy = 0.90
                    cost_savings = "$0"

                # Rule 5: Medium confidence + medium text → use Gemini
                else:
                    skip_gemini = False
                    reasoning = f"EasyOCR results acceptable ({confidence:.0%}, {text_length} chars) but Gemini will improve accuracy."
                    estimated_accuracy = 0.93
                    cost_savings = "$0"

            # If no EasyOCR yet, don't skip Gemini
            else:
                skip_gemini = False
                reasoning = "No EasyOCR results yet. Gemini needed."
                estimated_accuracy = 0.92

            decision = {
                "continue_processing": True,
                "skip_gemini": skip_gemini,
                "reasoning": reasoning,
                "estimated_final_accuracy": estimated_accuracy,
                "cost_savings": cost_savings
            }

            logger.info(f"✅ [AGENT] OCR optimization decision made")
            logger.info(f"   Continue: {decision['continue_processing']}")
            logger.info(f"   Skip Gemini: {decision.get('skip_gemini', False)}")
            logger.info(f"   Reasoning: {decision['reasoning']}")
            logger.info(f"   🎯 NO EXTRA GEMINI CALL - Using local heuristics")

            if skip_gemini:
                logger.info(f"   💰 Cost savings: {cost_savings}")

            return decision

        except Exception as e:
            logger.error(f"❌ [AGENT] OCR optimization failed: {e}")
            return {"continue_processing": True, "skip_gemini": False}

    def learn_from_result(
        self,
        doc_id: str,
        strategy_used: str,
        actual_time: float,
        actual_quality: float,
        classification_confidence: float,
        user_feedback: Dict = None
    ):
        """
        Agent learns from processing results to improve future decisions.

        Args:
            doc_id: Document ID
            strategy_used: Which strategy was used
            actual_time: Actual processing time
            actual_quality: Actual quality score
            classification_confidence: Final classification confidence
            user_feedback: User corrections/feedback
        """
        logger.info(f"📚 [AGENT] Learning from document {doc_id} processing...")

        learning_record = {
            "doc_id": doc_id,
            "strategy": strategy_used,
            "time": actual_time,
            "quality": actual_quality,
            "confidence": classification_confidence,
            "feedback": user_feedback,
            "timestamp": time.time()
        }

        self.processing_history.append(learning_record)

        # Keep only last 100 records
        if len(self.processing_history) > 100:
            self.processing_history = self.processing_history[-100:]

        logger.info(f"   Learning record saved (total history: {len(self.processing_history)})")

    def _get_document_preview(self, file_path: str) -> str:
        """Get a quick preview of document characteristics"""
        try:
            import os
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                return "PDF document (may have text layer)"
            elif file_ext in ['.jpg', '.jpeg']:
                return "JPEG image (likely mobile camera photo)"
            elif file_ext == '.png':
                return "PNG image (could be scan or photo)"
            else:
                return f"{file_ext} file"
        except:
            return "Unknown format"

    def _get_historical_insights(self) -> str:
        """Get insights from processing history"""
        if not self.processing_history:
            return "No historical data yet (this is the first document)."

        recent = self.processing_history[-10:]
        avg_time = sum(r['time'] for r in recent) / len(recent)
        avg_quality = sum(r['quality'] for r in recent) / len(recent)

        return f"Recent avg processing time: {avg_time:.1f}s, avg quality: {avg_quality:.1f}/100"

    def _get_fallback_strategy(self) -> Dict[str, Any]:
        """Fallback strategy when agent is unavailable"""
        return {
            "strategy": "enhanced_ocr",
            "reasoning": "Using default balanced strategy (agent unavailable)",
            "confidence": 0.5,
            "estimated_time_seconds": 8,
            "estimated_api_calls": 2,
            "skip_easyocr": False,
            "quality_check_first": True,
            "ocr_confidence_threshold": 0.70,
            "expected_challenges": [],
            "optimization_tips": []
        }

    def _get_fallback_feedback(self, quality_score: float) -> Dict[str, Any]:
        """Fallback feedback when agent is unavailable"""
        is_usable = quality_score >= 55.0

        issues = []
        suggestions = []

        if quality_score < 55:
            issues.append({
                "issue": "low quality",
                "severity": "critical",
                "explanation": "Image quality is too low for reliable text extraction"
            })
            suggestions.append("Recapture the document with better lighting")
            suggestions.append("Hold the phone steady to avoid blur")
            suggestions.append("Make sure the entire document is visible")

        return {
            "is_usable": is_usable,
            "confidence": 0.6,
            "issues_detected": issues,
            "actionable_suggestions": suggestions,
            "estimated_reupload_success": "70%" if not is_usable else "N/A",
            "specific_problems": {
                "blur": "unknown",
                "skew": "unknown",
                "lighting": "unknown",
                "edges_cut": "unknown",
                "glare": "unknown"
            }
        }


# Singleton instance
_processing_agent = None

def get_processing_agent() -> DocumentProcessingAgent:
    """Get or create the Document Processing Agent instance"""
    global _processing_agent
    if _processing_agent is None:
        _processing_agent = DocumentProcessingAgent()
    return _processing_agent

