"""
OCR Service - Text extraction from documents using PaddleOCR
"""
import io
import os
import shutil
from typing import Optional, Tuple, List
from PIL import Image
import numpy as np
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

logger = logging.getLogger(__name__)


class OCRService:
    """Service for OCR text extraction using PaddleOCR"""

    def __init__(self):
        self.paddle_ocr = None
        self._initialize_paddle_ocr()

    def _initialize_paddle_ocr(self):
        """Initialize OCR - Using Tesseract with preprocessing"""
        try:
            # Test if Tesseract is available
            import pytesseract
            from services.image_preprocessor import image_preprocessor

            # Try to get Tesseract version to verify installation
            try:
                version = pytesseract.get_tesseract_version()
                logger.info(f"✅ Tesseract OCR initialized successfully (v{version})")
                self.ocr_available = True
                self.paddle_ocr = None  # Not using PaddleOCR
                self.preprocessor = image_preprocessor
            except Exception as e:
                logger.warning(f"Tesseract not found: {e}")
                logger.info("Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
                self.ocr_available = False
                self.paddle_ocr = None
                self.preprocessor = None

        except ImportError:
            logger.warning("pytesseract not installed. Install: pip install pytesseract")
            self.ocr_available = False
            self.paddle_ocr = None
            self.preprocessor = None

    def extract_text_from_image(self, image_path: str) -> Tuple[str, float]:
        """
        Extract text from image file using Tesseract OCR with preprocessing

        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not self.ocr_available or not hasattr(self, 'preprocessor') or not self.preprocessor:
            logger.error("OCR is not available. Cannot extract text.")
            return "ERROR: Tesseract OCR not installed. Install from: https://github.com/UB-Mannheim/tesseract/wiki", 0.0

        try:
            import pytesseract
            import cv2

            logger.info(f"Extracting text from image: {image_path}")

            # Step 1: Preprocess image (critical for quality)
            logger.debug("Preprocessing image...")
            preprocessed_img = self.preprocessor.preprocess(image_path)

            # Save preprocessed image temporarily for OCR
            temp_path = image_path.replace('.', '_preprocessed.')
            cv2.imwrite(temp_path, preprocessed_img)

            # Step 2: Run Tesseract OCR with detailed output
            logger.debug("Running Tesseract OCR...")

            # Get detailed data including confidence scores
            ocr_data = pytesseract.image_to_data(
                temp_path,
                output_type=pytesseract.Output.DICT,
                config='--psm 3 --oem 3'  # PSM 3 = Fully automatic page segmentation
            )

            # Extract text and calculate average confidence
            texts = []
            confidences = []

            for i, conf in enumerate(ocr_data['conf']):
                if conf > 0:  # Valid confidence score
                    text = ocr_data['text'][i].strip()
                    if text:
                        texts.append(text)
                        confidences.append(conf / 100.0)  # Convert to 0-1 scale

            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass

            combined_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            logger.info(f"✅ Extracted {len(combined_text)} characters from image (confidence: {avg_confidence:.2f})")
            return combined_text.strip(), avg_confidence

        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"ERROR: {str(e)}", 0.0

        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"ERROR: {str(e)}", 0.0

    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, float]:
        """
        Extract text from PDF file
        First tries direct text extraction (pdfplumber)
        Falls back to OCR (PaddleOCR) for scanned PDFs

        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        # Try direct text extraction first (faster and doesn't need OCR)
        try:
            import pdfplumber
            logger.info(f"Attempting to extract text from PDF: {pdf_path}")

            with pdfplumber.open(pdf_path) as pdf:
                all_text = []
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        all_text.append(text.strip())
                        logger.debug(f"Page {i+1}: Extracted {len(text.strip())} characters")

                if all_text:
                    combined_text = "\n\n".join(all_text)
                    if len(combined_text.strip()) > 10:
                        logger.info(f"✅ Successfully extracted {len(combined_text)} characters from PDF using pdfplumber ({len(all_text)} pages)")
                        return combined_text.strip(), 0.95
                    else:
                        logger.warning("PDF text extraction returned minimal content")
                else:
                    logger.warning("PDF has no extractable text - trying OCR...")
        except Exception as e:
            logger.error(f"Direct PDF text extraction failed: {str(e)}")
            logger.info("Falling back to OCR...")

        # PDF has no extractable text - return helpful message
        if not self.ocr_available or not self.paddle_ocr:
            return (
                "[SCANNED PDF - TEXT EXTRACTION NOT AVAILABLE]\n\n"
                "This PDF appears to be a scanned document (image-based) with no extractable text.\n\n"
                "For best results, please use a PDF with selectable text layer.\n"
                "Most modern PDFs created from Word, Excel, or similar tools have text layers.\n\n"
                "The document will be processed based on filename and metadata only."
            ), 0.1


            logger.error(f"Error processing PDF with OCR: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"ERROR: {str(e)}", 0.0

    def extract_text(self, file_path: str, file_type: str) -> Tuple[str, float]:
        """
        Extract text from document (auto-detect type)

        Args:
            file_path: Path to the document
            file_type: File extension (pdf, jpg, jpeg, png)

        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        file_type = file_type.lower().replace('.', '')

        if file_type == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            return self.extract_text_from_image(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return "", 0.0


# Singleton instance
ocr_service = OCRService()

