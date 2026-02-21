"""
Similarity Matcher - Compares query documents against stored samples using embeddings
"""
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from models import DocTypeSample, DocumentType
from services.embedding_service import get_embedding_service
from services.sample_store import get_doc_sample_store

logger = logging.getLogger(__name__)


@dataclass
class SimilarityMatch:
    """Result of similarity matching"""
    doc_type: str
    confidence: float
    matched_sample_id: int
    similarity_score: float
    sample_filename: str


class SimilarityMatcher:
    """Matches query documents against stored samples using embedding similarity"""

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.sample_store = get_doc_sample_store()

    def match(self, query_embedding: List[float], db: Session) -> Optional[SimilarityMatch]:
        """
        Find best matching document type based on embedding similarity

        Args:
            query_embedding: Embedding vector of the query document
            db: Database session

        Returns:
            SimilarityMatch object with best match, or None if no match
        """
        if not query_embedding:
            logger.warning("No query embedding provided")
            return None

        if not self.embedding_service.available:
            logger.warning("Embedding service not available")
            return None

        try:
            # Get all active samples
            samples = self.sample_store.get_all_active_samples(db)

            if not samples:
                logger.warning("No samples available for matching")
                return None

            # Filter samples that have embeddings
            samples_with_embeddings = [s for s in samples if s.embedding]

            if not samples_with_embeddings:
                logger.warning("No samples have embeddings")
                return None

            logger.info(f"Comparing against {len(samples_with_embeddings)} sample embeddings...")

            # Calculate similarity scores
            similarities = []
            for sample in samples_with_embeddings:
                try:
                    score = self.embedding_service.compute_similarity(
                        query_embedding,
                        sample.embedding
                    )
                    similarities.append({
                        'sample': sample,
                        'score': score
                    })
                except Exception as e:
                    logger.warning(f"Error computing similarity for sample {sample.id}: {e}")
                    continue

            if not similarities:
                logger.warning("Failed to compute any similarities")
                return None

            # Group by document type and aggregate scores
            type_scores = self._aggregate_scores_by_type(similarities)

            if not type_scores:
                return None

            # Find best match
            best_type = max(type_scores, key=lambda k: type_scores[k]['confidence'])
            best_match = type_scores[best_type]

            logger.info(f"  Best match: {best_type} (confidence: {best_match['confidence']:.1%}, " +
                       f"top similarity: {best_match['top_score']:.1%})")

            return SimilarityMatch(
                doc_type=best_type,
                confidence=best_match['confidence'],
                matched_sample_id=best_match['top_sample_id'],
                similarity_score=best_match['top_score'],
                sample_filename=best_match['top_sample_filename']
            )

        except Exception as e:
            logger.error(f"Error in similarity matching: {e}")
            return None

    def _aggregate_scores_by_type(self, similarities: List[Dict]) -> Dict:
        """
        Aggregate similarity scores by document type
        Uses weighted average: top match gets 60%, rest get 40%

        Args:
            similarities: List of dicts with 'sample' and 'score' keys

        Returns:
            Dict mapping document type name to aggregated confidence
        """
        type_groups = {}

        # Group by document type
        for item in similarities:
            sample = item['sample']
            score = item['score']
            doc_type = sample.doc_type.value

            if doc_type not in type_groups:
                type_groups[doc_type] = []

            type_groups[doc_type].append({
                'sample_id': sample.id,
                'filename': sample.filename,
                'score': score
            })

        # Aggregate scores for each type
        result = {}
        for doc_type, scores in type_groups.items():
            # Sort by score descending
            scores.sort(key=lambda x: x['score'], reverse=True)

            if not scores:
                continue

            # Top match gets 60% weight, rest get 40% distributed
            top_score = scores[0]['score']

            if len(scores) == 1:
                # Only one sample - use it directly
                confidence = top_score
            else:
                # Multiple samples - weighted average
                rest_scores = [s['score'] for s in scores[1:]]
                avg_rest = sum(rest_scores) / len(rest_scores) if rest_scores else 0

                confidence = (top_score * 0.6) + (avg_rest * 0.4)

            result[doc_type] = {
                'confidence': confidence,
                'top_score': top_score,
                'top_sample_id': scores[0]['sample_id'],
                'top_sample_filename': scores[0]['filename'],
                'num_samples': len(scores)
            }

        return result

    def match_with_text(self, extracted_text: str, db: Session) -> Optional[SimilarityMatch]:
        """
        Match document by generating embedding from text first

        Args:
            extracted_text: OCR-extracted text from document
            db: Database session

        Returns:
            SimilarityMatch object with best match, or None if no match
        """
        if not extracted_text or len(extracted_text.strip()) < 10:
            logger.warning("Text too short for similarity matching")
            return None

        # Generate embedding
        embedding = self.embedding_service.generate_embedding(extracted_text)

        if not embedding:
            logger.warning("Failed to generate embedding for query text")
            return None

        # Match using embedding
        return self.match(embedding, db)


# Singleton instance
_similarity_matcher = None


def get_similarity_matcher() -> SimilarityMatcher:
    """Get or create similarity matcher instance"""
    global _similarity_matcher
    if _similarity_matcher is None:
        _similarity_matcher = SimilarityMatcher()
    return _similarity_matcher

