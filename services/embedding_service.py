"""
Text Embedding Service - Generates embeddings for document similarity matching
Uses sentence-transformers for high-quality text embeddings
"""
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers"""

    def __init__(self):
        self.model = None
        self.model_name = "all-MiniLM-L6-v2"  # Fast, lightweight, accurate
        self.available = False
        self._initialize_model()

    def _initialize_model(self):
        """Initialize sentence-transformers model"""
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Initializing embedding model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            self.available = True
            logger.info("✅ Embedding model initialized successfully")

        except ImportError:
            logger.warning("⚠️  sentence-transformers not installed")
            logger.info("Install with: pip install sentence-transformers")
            self.available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding model: {e}")
            self.available = False

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding, or None if unavailable
        """
        if not self.available or not self.model:
            logger.warning("Embedding model not available")
            return None

        if not text or len(text.strip()) < 10:
            logger.warning("Text too short for embedding")
            return None

        try:
            # Clean and truncate text (model has token limit)
            text_clean = text.strip()[:5000]  # First 5000 chars

            # Generate embedding
            embedding = self.model.encode(text_clean, convert_to_numpy=True)

            # Convert to list for JSON storage
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)

            # Normalize to 0-1 range (cosine similarity is -1 to 1)
            similarity = (similarity + 1) / 2

            return float(similarity)

        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0

    def batch_generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts efficiently

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings (some may be None if generation failed)
        """
        if not self.available or not self.model:
            return [None] * len(texts)

        try:
            # Clean texts
            texts_clean = [text.strip()[:5000] if text else "" for text in texts]

            # Filter out empty texts
            valid_indices = [i for i, text in enumerate(texts_clean) if len(text) >= 10]
            valid_texts = [texts_clean[i] for i in valid_indices]

            if not valid_texts:
                return [None] * len(texts)

            # Generate embeddings in batch (faster)
            embeddings = self.model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=False)

            # Map back to original indices
            result = [None] * len(texts)
            for idx, embedding in zip(valid_indices, embeddings):
                result[idx] = embedding.tolist()

            return result

        except Exception as e:
            logger.error(f"Error in batch embedding generation: {e}")
            return [None] * len(texts)


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

