"""
Sample Management API Router
Handles document type sample uploads and management for similarity-based classification
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import logging
import os
import uuid
import shutil

from database import get_db
from models import User, DocumentType, ClassificationResult as ClassificationResultModel
from auth import get_current_user
from services.sample_store import get_doc_sample_store
from services.easyocr_service import easyocr_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["samples"])

# Upload directory for samples
SAMPLES_DIR = "samples"
os.makedirs(SAMPLES_DIR, exist_ok=True)


@router.post("/samples/upload")
async def upload_sample(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a sample document for a specific document type
    Admin uploads 3-5 samples per type for similarity matching

    Only admin users can upload samples
    """
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can upload samples"
            )

        # Validate document type
        try:
            doc_type_enum = DocumentType(doc_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type. Must be one of: {[dt.value for dt in DocumentType if dt != DocumentType.UNKNOWN]}"
            )

        if doc_type_enum == DocumentType.UNKNOWN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot upload samples for 'Unknown' type"
            )

        # Validate file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.pdf', '.jpg', '.jpeg', '.png']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, JPG, JPEG, and PNG files are allowed"
            )

        logger.info(f"Admin {current_user.username} uploading sample: {doc_type} - {file.filename}")

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(SAMPLES_DIR, unique_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Sample saved: {file_path}")

        # Extract text using OCR
        logger.info("Extracting text from sample...")
        extracted_text = easyocr_service.extract_text_from_file(file_path)

        if not extracted_text or len(extracted_text.strip()) < 10:
            # Clean up file
            if os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to extract text from sample. Please upload a clearer document."
            )

        logger.info(f"Extracted {len(extracted_text)} characters")

        # Add to sample store (generates embedding)
        sample_store = get_doc_sample_store()
        sample = sample_store.add_sample(
            db=db,
            doc_type=doc_type_enum,
            file_path=file_path,
            filename=file.filename,
            extracted_text=extracted_text,
            uploaded_by=current_user.id
        )

        if not sample:
            # Clean up file
            if os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save sample to database"
            )

        # Get updated sample counts
        sample_counts = sample_store.get_sample_count_per_type(db)

        return {
            "message": "Sample uploaded successfully",
            "sample": {
                "id": sample.id,
                "doc_type": sample.doc_type.value,
                "filename": sample.filename,
                "text_length": len(extracted_text),
                "has_embedding": sample.embedding is not None,
                "uploaded_at": sample.uploaded_at.isoformat()
            },
            "sample_counts": sample_counts
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading sample: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload sample: {str(e)}"
        )


@router.get("/samples/status")
async def get_sample_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system readiness status for similarity-based classification
    Shows sample counts per type and overall readiness
    """
    try:
        sample_store = get_doc_sample_store()
        status = sample_store.get_readiness_status(db)

        return status

    except Exception as e:
        logger.error(f"Error getting sample status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.get("/samples/list")
async def list_samples(
    doc_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all samples (optionally filtered by document type)
    Only admin users can view samples
    """
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can view samples"
            )

        sample_store = get_doc_sample_store()

        if doc_type:
            # Validate and filter by type
            try:
                doc_type_enum = DocumentType(doc_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid document type: {doc_type}"
                )

            samples = sample_store.get_samples_by_type(db, doc_type_enum)
        else:
            samples = sample_store.get_all_active_samples(db)

        return {
            "total": len(samples),
            "samples": [
                {
                    "id": s.id,
                    "doc_type": s.doc_type.value,
                    "filename": s.filename,
                    "text_length": len(s.extracted_text) if s.extracted_text else 0,
                    "has_embedding": s.embedding is not None,
                    "uploaded_at": s.uploaded_at.isoformat(),
                    "uploaded_by": s.uploaded_by
                }
                for s in samples
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing samples: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list samples: {str(e)}"
        )


@router.delete("/samples/{sample_id}")
async def delete_sample(
    sample_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a sample document
    Only admin users can delete samples
    """
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can delete samples"
            )

        sample_store = get_doc_sample_store()
        success = sample_store.delete_sample(db, sample_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sample {sample_id} not found"
            )

        return {"message": f"Sample {sample_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sample: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sample: {str(e)}"
        )


@router.post("/samples/feedback")
async def submit_classification_feedback(
    document_id: int = Form(...),
    correct_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback to correct a wrong classification
    Back office users can correct misclassifications for continuous learning
    """
    try:
        # Validate document type
        try:
            correct_type_enum = DocumentType(correct_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type: {correct_type}"
            )

        # Find classification result
        classification = db.query(ClassificationResultModel).filter(
            ClassificationResultModel.document_id == document_id
        ).order_by(ClassificationResultModel.created_at.desc()).first()

        if not classification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No classification found for document {document_id}"
            )

        # Check if already corrected
        if classification.is_correct is not None:
            return {
                "message": "Classification already reviewed",
                "classification": {
                    "document_id": document_id,
                    "predicted_type": classification.predicted_type.value if classification.predicted_type else None,
                    "is_correct": classification.is_correct,
                    "corrected_type": classification.corrected_type.value if classification.corrected_type else None
                }
            }

        # Update classification result
        is_correct = (classification.predicted_type == correct_type_enum)

        classification.is_correct = is_correct
        if not is_correct:
            classification.corrected_type = correct_type_enum
        classification.corrected_by = current_user.id
        classification.corrected_at = func.now()

        db.commit()

        logger.info(f"Feedback submitted for document {document_id}: " +
                   f"predicted={classification.predicted_type.value if classification.predicted_type else 'None'}, " +
                   f"correct={correct_type}, is_correct={is_correct}")

        return {
            "message": "Feedback submitted successfully",
            "classification": {
                "document_id": document_id,
                "predicted_type": classification.predicted_type.value if classification.predicted_type else None,
                "is_correct": is_correct,
                "corrected_type": correct_type,
                "corrected_by": current_user.username
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/samples/accuracy")
async def get_classification_accuracy(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get classification accuracy metrics based on feedback
    Shows overall accuracy and per-type accuracy
    """
    try:
        # Get all reviewed classifications
        reviewed = db.query(ClassificationResultModel).filter(
            ClassificationResultModel.is_correct.isnot(None)
        ).all()

        if not reviewed:
            return {
                "message": "No reviewed classifications yet",
                "total_reviewed": 0
            }

        total = len(reviewed)
        correct = sum(1 for c in reviewed if c.is_correct)
        accuracy = (correct / total * 100) if total > 0 else 0

        # Per-type accuracy
        type_stats = {}
        for classification in reviewed:
            pred_type = classification.predicted_type.value if classification.predicted_type else "Unknown"

            if pred_type not in type_stats:
                type_stats[pred_type] = {"total": 0, "correct": 0}

            type_stats[pred_type]["total"] += 1
            if classification.is_correct:
                type_stats[pred_type]["correct"] += 1

        # Calculate per-type accuracy
        for type_name in type_stats:
            stats = type_stats[type_name]
            stats["accuracy"] = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0

        return {
            "overall": {
                "total_reviewed": total,
                "correct": correct,
                "incorrect": total - correct,
                "accuracy": round(accuracy, 2)
            },
            "by_type": type_stats
        }

    except Exception as e:
        logger.error(f"Error getting accuracy metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get accuracy: {str(e)}"
        )

