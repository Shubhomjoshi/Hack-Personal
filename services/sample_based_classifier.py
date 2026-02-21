"""
Sample-Based Document Classifier
Orchestrates 3 signals: Embedding Similarity, Keyword Matching, Gemini Vision
Uses weighted voting for final classification result
"""
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from services.similarity_matcher import get_similarity_matcher
from services.document_classifier import KeywordDocumentClassifier, GeminiDocumentClassifier, ClassificationResult
from services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


@dataclass
class WeightedVote:
    """Weighted vote from each classification signal"""
    embedding_vote: Optional[str] = None
    embedding_confidence: float = 0.0

    keyword_vote: Optional[str] = None
    keyword_confidence: float = 0.0

    gemini_vote: Optional[str] = None
    gemini_confidence: float = 0.0


class SampleBasedClassifier:
    """
    Advanced classifier using 3 signals with weighted voting

    Signal priority (by confidence threshold):
    1. Embedding similarity >= 72% → Use it (45% weight in voting)
    2. Keyword match >= 55% → Use it (20% weight in voting)
    3. Gemini Vision (fallback) → (35% weight in voting)

    Weighted voting formula:
    - Embedding: 45%
    - Gemini: 35%
    - Keyword: 20%
    """

    def __init__(self):
        self.similarity_matcher = get_similarity_matcher()
        self.keyword_clf = KeywordDocumentClassifier()
        self.gemini_clf = GeminiDocumentClassifier()
        self.embedding_service = get_embedding_service()

        # Confidence thresholds for early exit
        self.EMBEDDING_THRESHOLD = 0.72
        self.KEYWORD_THRESHOLD = 0.55

        # Voting weights (must sum to 1.0)
        self.WEIGHTS = {
            'embedding': 0.45,
            'gemini': 0.35,
            'keyword': 0.20
        }

    def classify(
        self,
        extracted_text: str,
        image_path: str,
        db: Session
    ) -> Dict:
        """
        Classify document using multi-signal approach with weighted voting

        Args:
            extracted_text: Combined OCR text from EasyOCR + Gemini
            image_path: Path to document image
            db: Database session

        Returns:
            Dict with classification results
        """
        logger.info("🔍 Starting multi-signal document classification...")

        votes = WeightedVote()
        signals_used = []

        # SIGNAL 1: Embedding Similarity (Primary - 45% weight)
        embedding_result = self._run_embedding_signal(extracted_text, db)
        if embedding_result:
            votes.embedding_vote = embedding_result.doc_type
            votes.embedding_confidence = embedding_result.confidence
            signals_used.append("embedding")
            logger.info(f"  📊 Embedding: {embedding_result.doc_type} ({embedding_result.confidence:.1%})")

            # Early exit if very high confidence
            if embedding_result.confidence >= self.EMBEDDING_THRESHOLD:
                logger.info(f"  ✅ High embedding confidence ({embedding_result.confidence:.1%}) - Using result")
                return self._format_result(
                    doc_type=embedding_result.doc_type,
                    confidence=embedding_result.confidence,
                    method="embedding_high_confidence",
                    matched_sample_id=getattr(embedding_result, 'matched_sample_id', None),
                    signals_used=signals_used,
                    votes=votes
                )

        # SIGNAL 2: Keyword Match (Fast - 20% weight)
        keyword_result = self._run_keyword_signal(extracted_text)
        if keyword_result:
            votes.keyword_vote = keyword_result.doc_type
            votes.keyword_confidence = keyword_result.confidence
            signals_used.append("keyword")
            logger.info(f"  🔤 Keyword: {keyword_result.doc_type} ({keyword_result.confidence:.1%})")

            # Early exit if embedding + keyword both agree with high confidence
            if (votes.embedding_vote == votes.keyword_vote and
                votes.embedding_confidence >= 0.60 and
                votes.keyword_confidence >= self.KEYWORD_THRESHOLD):

                combined_conf = (votes.embedding_confidence * 0.7 + votes.keyword_confidence * 0.3)
                logger.info(f"  ✅ Embedding + Keyword agree ({combined_conf:.1%}) - Using result")
                return self._format_result(
                    doc_type=votes.embedding_vote,
                    confidence=combined_conf,
                    method="embedding+keyword_agreed",
                    matched_sample_id=getattr(embedding_result, 'matched_sample_id', None) if embedding_result else None,
                    signals_used=signals_used,
                    votes=votes
                )

        # SIGNAL 3: Gemini Vision (Fallback - 35% weight)
        # Only call if we don't have strong signals yet
        if votes.embedding_confidence < self.EMBEDDING_THRESHOLD or votes.keyword_confidence < self.KEYWORD_THRESHOLD:
            gemini_result = self._run_gemini_signal(image_path, extracted_text)
            if gemini_result:
                votes.gemini_vote = gemini_result.doc_type
                votes.gemini_confidence = gemini_result.confidence
                signals_used.append("gemini")
                logger.info(f"  🤖 Gemini: {gemini_result.doc_type} ({gemini_result.confidence:.1%})")

        # WEIGHTED VOTING: Combine all signals
        final_result = self._weighted_voting(votes, embedding_result)

        logger.info(f"  ✅ Final: {final_result['doc_type']} ({final_result['confidence']:.1%}) via {final_result['method']}")

        return final_result

    def _run_embedding_signal(self, text: str, db: Session):
        """Run embedding similarity matching"""
        try:
            if not self.embedding_service.available:
                logger.info("  ⚠️  Embedding service not available - skipping")
                return None

            match = self.similarity_matcher.match_with_text(text, db)
            if match:
                # Convert to ClassificationResult for consistency
                return type('EmbeddingResult', (), {
                    'doc_type': match.doc_type,
                    'confidence': match.confidence,
                    'matched_sample_id': match.matched_sample_id,
                    'similarity_score': match.similarity_score
                })()
            return None

        except Exception as e:
            logger.error(f"Error in embedding signal: {e}")
            return None

    def _run_keyword_signal(self, text: str) -> Optional[ClassificationResult]:
        """Run keyword matching"""
        try:
            return self.keyword_clf.classify(text)
        except Exception as e:
            logger.error(f"Error in keyword signal: {e}")
            return None

    def _run_gemini_signal(self, image_path: str, text: str) -> Optional[ClassificationResult]:
        """Run Gemini Vision classification"""
        try:
            if not self.gemini_clf.gemini or not self.gemini_clf.gemini.available:
                logger.info("  ⚠️  Gemini not available - skipping")
                return None

            return self.gemini_clf.classify(image_path, text)
        except Exception as e:
            logger.error(f"Error in Gemini signal: {e}")
            return None

    def _weighted_voting(self, votes: WeightedVote, embedding_result) -> Dict:
        """
        Perform weighted voting across all signals

        Weights: Embedding 45%, Gemini 35%, Keyword 20%
        """
        # Collect all votes with their weighted confidences
        vote_scores = {}

        # Embedding vote (45% weight)
        if votes.embedding_vote and votes.embedding_confidence > 0:
            doc_type = votes.embedding_vote
            weighted_conf = votes.embedding_confidence * self.WEIGHTS['embedding']
            vote_scores[doc_type] = vote_scores.get(doc_type, 0) + weighted_conf

        # Gemini vote (35% weight)
        if votes.gemini_vote and votes.gemini_confidence > 0:
            doc_type = votes.gemini_vote
            weighted_conf = votes.gemini_confidence * self.WEIGHTS['gemini']
            vote_scores[doc_type] = vote_scores.get(doc_type, 0) + weighted_conf

        # Keyword vote (20% weight)
        if votes.keyword_vote and votes.keyword_confidence > 0:
            doc_type = votes.keyword_vote
            weighted_conf = votes.keyword_confidence * self.WEIGHTS['keyword']
            vote_scores[doc_type] = vote_scores.get(doc_type, 0) + weighted_conf

        if not vote_scores:
            return self._format_result(
                doc_type="Unknown",
                confidence=0.0,
                method="no_signals",
                signals_used=[],
                votes=votes
            )

        # Find winner
        winner = max(vote_scores, key=vote_scores.get)
        confidence = vote_scores[winner]

        # Determine method used
        signals = []
        if votes.embedding_vote: signals.append("embedding")
        if votes.keyword_vote: signals.append("keyword")
        if votes.gemini_vote: signals.append("gemini")

        method = "multi_signal_vote" if len(signals) > 1 else signals[0] if signals else "unknown"

        return self._format_result(
            doc_type=winner,
            confidence=confidence,
            method=method,
            matched_sample_id=getattr(embedding_result, 'matched_sample_id', None) if embedding_result else None,
            signals_used=signals,
            votes=votes
        )

    def _format_result(
        self,
        doc_type: str,
        confidence: float,
        method: str,
        matched_sample_id: Optional[int] = None,
        signals_used: list = None,
        votes: WeightedVote = None
    ) -> Dict:
        """Format final classification result"""

        status = (
            "high_confidence" if confidence >= 0.75
            else "medium_confidence" if confidence >= 0.50
            else "needs_review"
        )

        result = {
            "doc_type": doc_type,
            "confidence": round(confidence, 4),
            "confidence_status": status,
            "method_used": method,
            "signals_used": signals_used or [],
            "needs_manual_review": confidence < 0.50,
            "matched_sample_id": matched_sample_id
        }

        # Add detailed voting breakdown if available
        if votes:
            result["vote_breakdown"] = {
                "embedding": {
                    "vote": votes.embedding_vote,
                    "confidence": round(votes.embedding_confidence, 3) if votes.embedding_confidence else 0,
                    "weight": self.WEIGHTS['embedding']
                },
                "gemini": {
                    "vote": votes.gemini_vote,
                    "confidence": round(votes.gemini_confidence, 3) if votes.gemini_confidence else 0,
                    "weight": self.WEIGHTS['gemini']
                },
                "keyword": {
                    "vote": votes.keyword_vote,
                    "confidence": round(votes.keyword_confidence, 3) if votes.keyword_confidence else 0,
                    "weight": self.WEIGHTS['keyword']
                }
            }

        return result


# Singleton instance
_sample_based_classifier = None


def get_sample_based_classifier() -> SampleBasedClassifier:
    """Get or create sample-based classifier instance"""
    global _sample_based_classifier
    if _sample_based_classifier is None:
        _sample_based_classifier = SampleBasedClassifier()
    return _sample_based_classifier

