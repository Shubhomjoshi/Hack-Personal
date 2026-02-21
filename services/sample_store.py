"""
Document Sample Store - Manages sample documents for similarity-based classification
Handles CRUD operations for doc_type_samples table
"""
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import DocTypeSample, DocumentType
from services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class DocSampleStore:
    """Manages storage and retrieval of document type samples"""

    def __init__(self):
        self.embedding_service = get_embedding_service()

    def add_sample(
        self,
        db: Session,
        doc_type: DocumentType,
        file_path: str,
        filename: str,
        extracted_text: str,
        uploaded_by: Optional[int] = None
    ) -> Optional[DocTypeSample]:
        """
        Add a new sample document to the database

        Args:
            db: Database session
            doc_type: Document type enum value
            file_path: Path to the saved sample file
            filename: Original filename
            extracted_text: OCR-extracted text from the sample
            uploaded_by: User ID who uploaded the sample

        Returns:
            Created DocTypeSample object, or None if failed
        """
        try:
            logger.info(f"Adding sample: {doc_type.value} - {filename}")

            # Generate embedding
            embedding = None
            if self.embedding_service.available:
                embedding = self.embedding_service.generate_embedding(extracted_text)
                if embedding:
                    logger.info(f"  ✅ Generated embedding ({len(embedding)} dimensions)")
                else:
                    logger.warning("  ⚠️  Failed to generate embedding")
            else:
                logger.warning("  ⚠️  Embedding service not available")

            # Create sample record
            sample = DocTypeSample(
                doc_type=doc_type,
                filename=filename,
                file_path=file_path,
                extracted_text=extracted_text,
                embedding=embedding,  # JSON field
                uploaded_by=uploaded_by,
                is_active=True
            )

            db.add(sample)
            db.commit()
            db.refresh(sample)

            logger.info(f"  ✅ Sample added (ID: {sample.id})")
            return sample

        except Exception as e:
            logger.error(f"Error adding sample: {e}")
            db.rollback()
            return None

    def get_all_active_samples(self, db: Session) -> List[DocTypeSample]:
        """
        Get all active sample documents

        Args:
            db: Database session

        Returns:
            List of active DocTypeSample objects
        """
        try:
            samples = db.query(DocTypeSample).filter(
                DocTypeSample.is_active == True
            ).all()

            logger.info(f"Retrieved {len(samples)} active samples")
            return samples

        except Exception as e:
            logger.error(f"Error retrieving samples: {e}")
            return []

    def get_samples_by_type(self, db: Session, doc_type: DocumentType) -> List[DocTypeSample]:
        """
        Get all active samples for a specific document type

        Args:
            db: Database session
            doc_type: Document type to filter by

        Returns:
            List of DocTypeSample objects
        """
        try:
            samples = db.query(DocTypeSample).filter(
                DocTypeSample.doc_type == doc_type,
                DocTypeSample.is_active == True
            ).all()

            return samples

        except Exception as e:
            logger.error(f"Error retrieving samples for {doc_type}: {e}")
            return []

    def get_sample_count_per_type(self, db: Session) -> Dict[str, int]:
        """
        Get count of active samples per document type

        Args:
            db: Database session

        Returns:
            Dict mapping document type to count
        """
        try:
            counts = db.query(
                DocTypeSample.doc_type,
                func.count(DocTypeSample.id).label('count')
            ).filter(
                DocTypeSample.is_active == True
            ).group_by(DocTypeSample.doc_type).all()

            result = {doc_type.value: count for doc_type, count in counts}

            # Fill in zero counts for types without samples
            for doc_type in DocumentType:
                if doc_type.value not in result:
                    result[doc_type.value] = 0

            return result

        except Exception as e:
            logger.error(f"Error getting sample counts: {e}")
            return {}

    def get_readiness_status(self, db: Session) -> Dict:
        """
        Get system readiness status for similarity-based classification

        Args:
            db: Database session

        Returns:
            Dict with readiness information
        """
        counts = self.get_sample_count_per_type(db)

        total_samples = sum(counts.values())
        min_samples_per_type = 3  # Recommended minimum

        types_ready = sum(1 for count in counts.values() if count >= min_samples_per_type)
        total_types = len([dt for dt in DocumentType if dt != DocumentType.UNKNOWN])

        readiness_percentage = (types_ready / total_types * 100) if total_types > 0 else 0

        embedding_available = self.embedding_service.available

        # Determine overall status
        if not embedding_available:
            status = "not_ready"
            message = "Embedding service not available. Install sentence-transformers."
        elif readiness_percentage >= 100:
            status = "ready"
            message = "System ready for similarity-based classification"
        elif readiness_percentage >= 50:
            status = "partially_ready"
            message = f"System partially ready ({types_ready}/{total_types} types have enough samples)"
        else:
            status = "not_ready"
            message = f"Need more samples. Only {types_ready}/{total_types} types have {min_samples_per_type}+ samples"

        return {
            "status": status,
            "message": message,
            "readiness_percentage": round(readiness_percentage, 1),
            "embedding_available": embedding_available,
            "total_samples": total_samples,
            "types_ready": types_ready,
            "total_types": total_types,
            "min_samples_required": min_samples_per_type,
            "samples_per_type": counts
        }

    def deactivate_sample(self, db: Session, sample_id: int) -> bool:
        """
        Deactivate a sample (soft delete)

        Args:
            db: Database session
            sample_id: ID of sample to deactivate

        Returns:
            True if successful, False otherwise
        """
        try:
            sample = db.query(DocTypeSample).filter(DocTypeSample.id == sample_id).first()

            if not sample:
                logger.error(f"Sample {sample_id} not found")
                return False

            sample.is_active = False
            db.commit()

            logger.info(f"Deactivated sample {sample_id}")
            return True

        except Exception as e:
            logger.error(f"Error deactivating sample: {e}")
            db.rollback()
            return False

    def delete_sample(self, db: Session, sample_id: int) -> bool:
        """
        Permanently delete a sample

        Args:
            db: Database session
            sample_id: ID of sample to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            sample = db.query(DocTypeSample).filter(DocTypeSample.id == sample_id).first()

            if not sample:
                logger.error(f"Sample {sample_id} not found")
                return False

            # Delete file if it exists
            import os
            if os.path.exists(sample.file_path):
                try:
                    os.remove(sample.file_path)
                    logger.info(f"Deleted file: {sample.file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete file: {e}")

            # Delete from database
            db.delete(sample)
            db.commit()

            logger.info(f"Deleted sample {sample_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting sample: {e}")
            db.rollback()
            return False


# Singleton instance
_doc_sample_store = None


def get_doc_sample_store() -> DocSampleStore:
    """Get or create doc sample store instance"""
    global _doc_sample_store
    if _doc_sample_store is None:
        _doc_sample_store = DocSampleStore()
    return _doc_sample_store

