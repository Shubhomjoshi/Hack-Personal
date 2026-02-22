"""
EasyOCR Service - Text extraction using EasyOCR for background processing
"""
import os
import logging
from typing import Tuple, Optional
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger(__name__)


class EasyOCRService:
    """Service for OCR text extraction using EasyOCR"""

    def __init__(self):
        self.reader = None
        self.ocr_available = False
        self.use_tesseract_fallback = False
        self._initialize_easyocr()

    def _initialize_easyocr(self):
        """Initialize EasyOCR with fallback to Tesseract"""
        try:
            import easyocr
            logger.info("Initializing EasyOCR...")
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            self.ocr_available = True
            logger.info("✅ EasyOCR initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️  EasyOCR not available: {e}")
            logger.info("Attempting to use Tesseract as fallback...")

            # Try Tesseract as fallback
            try:
                import pytesseract
                version = pytesseract.get_tesseract_version()
                self.use_tesseract_fallback = True
                self.ocr_available = True
                logger.info(f"✅ Using Tesseract OCR as fallback (v{version})")
            except Exception as e2:
                logger.error(f"❌ Neither EasyOCR nor Tesseract available: {e2}")
                logger.info("Install either:")
                logger.info("  - EasyOCR: pip install easyocr")
                logger.info("  - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
                self.ocr_available = False
                self.reader = None

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        """
        try:
            # Read image
            img = cv2.imread(image_path)

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # Denoise
            denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)

            # Apply adaptive threshold
            binary = cv2.adaptiveThreshold(
                denoised, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            return binary
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            # Return original image if preprocessing fails
            return cv2.imread(image_path)

    def convert_pdf_to_images(self, pdf_path: str) -> list:
        """
        Convert PDF pages to images for OCR processing
        """
        try:
            from pdf2image import convert_from_path
            logger.info(f"Converting PDF to images: {pdf_path}")

            # Convert with 300 DPI for better OCR
            images = convert_from_path(pdf_path, dpi=300)
            logger.info(f"✅ Converted {len(images)} page(s)")
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []

    def extract_text_from_image(self, image_path: str) -> Tuple[str, float]:
        """
        Extract text from image using EasyOCR or Tesseract fallback

        Returns:
            Tuple of (extracted_text, average_confidence)
        """
        if not self.ocr_available:
            logger.error("No OCR engine available")
            return "ERROR: No OCR engine initialized", 0.0

        try:
            logger.info(f"Extracting text from image: {image_path}")

            # Verify file exists
            import os
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return "ERROR: Image file not found", 0.0

            # Preprocess image
            try:
                preprocessed = self.preprocess_image(image_path)
            except Exception as prep_error:
                logger.error(f"Image preprocessing failed: {prep_error}")
                # Try with original image
                preprocessed = cv2.imread(image_path)

            # Use Tesseract fallback if EasyOCR not available
            if self.use_tesseract_fallback:
                return self._extract_with_tesseract(preprocessed, image_path)

            # Run EasyOCR (don't use paragraph mode, use default)
            try:
                results = self.reader.readtext(preprocessed)
            except Exception as ocr_error:
                logger.error(f"EasyOCR readtext failed: {ocr_error}")
                # Try Tesseract as emergency fallback
                if self.use_tesseract_fallback:
                    logger.info("Falling back to Tesseract...")
                    return self._extract_with_tesseract(preprocessed, image_path)
                return f"ERROR: OCR failed - {str(ocr_error)}", 0.0

            # Extract text and confidence
            texts = []
            confidences = []

            for detection in results:
                try:
                    # EasyOCR returns: (bbox, text, confidence) or (text, confidence)
                    if len(detection) == 3:
                        bbox, text, confidence = detection
                    elif len(detection) == 2:
                        text, confidence = detection
                    else:
                        logger.warning(f"Unexpected detection format: {detection}")
                        continue

                    if text and text.strip():
                        texts.append(text.strip())
                        confidences.append(confidence)
                except Exception as parse_error:
                    logger.warning(f"Failed to parse detection result: {parse_error}")
                    continue

            # Combine results
            combined_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            logger.info(f"✅ Extracted {len(combined_text)} characters (confidence: {avg_confidence:.2f})")
            return combined_text, avg_confidence

        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"ERROR: {str(e)}", 0.0

    def _extract_with_tesseract(self, preprocessed_img: np.ndarray, original_path: str) -> Tuple[str, float]:
        """Extract text using Tesseract OCR"""
        try:
            import pytesseract
            import cv2

            logger.info("Using Tesseract OCR...")

            # Save preprocessed image temporarily
            temp_path = original_path.replace('.', '_preprocessed.')
            cv2.imwrite(temp_path, preprocessed_img)

            # Run Tesseract
            ocr_data = pytesseract.image_to_data(
                temp_path,
                output_type=pytesseract.Output.DICT,
                config='--psm 3 --oem 3'
            )

            # Extract text and confidence
            texts = []
            confidences = []

            for i, conf in enumerate(ocr_data['conf']):
                if conf > 0:
                    text = ocr_data['text'][i].strip()
                    if text:
                        texts.append(text)
                        confidences.append(conf / 100.0)

            # Clean up
            try:
                os.remove(temp_path)
            except:
                pass

            combined_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            logger.info(f"✅ Tesseract extracted {len(combined_text)} characters (confidence: {avg_confidence:.2f})")
            return combined_text, avg_confidence

        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return f"ERROR: {str(e)}", 0.0

    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, float]:
        """
        Extract text from PDF file
        First tries direct text extraction, then falls back to OCR

        Returns:
            Tuple of (extracted_text, average_confidence)
        """
        # Try direct text extraction first
        try:
            import pdfplumber
            logger.info(f"Attempting direct text extraction from PDF: {pdf_path}")

            with pdfplumber.open(pdf_path) as pdf:
                all_text = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        all_text.append(text.strip())

                if all_text:
                    combined_text = "\n\n".join(all_text)
                    if len(combined_text.strip()) > 50:  # Meaningful content
                        logger.info(f"✅ Extracted {len(combined_text)} characters using direct extraction")
                        return combined_text.strip(), 0.95

            logger.warning("PDF has no extractable text - using OCR...")
        except Exception as e:
            logger.error(f"Direct PDF extraction failed: {e}")

        # Fall back to OCR
        if not self.ocr_available:
            return "ERROR: Cannot process scanned PDF - No OCR engine available", 0.0

        try:
            # Convert PDF to images
            images = self.convert_pdf_to_images(pdf_path)

            if not images:
                return "ERROR: Could not convert PDF to images", 0.0

            # Process each page
            all_texts = []
            all_confidences = []

            for i, img in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)}")

                # Save temporary image
                temp_path = pdf_path.replace('.pdf', f'_temp_page_{i}.png')
                img.save(temp_path, 'PNG')

                # Extract text (will use EasyOCR or Tesseract based on availability)
                text, confidence = self.extract_text_from_image(temp_path)

                # Clean up temp file
                try:
                    os.remove(temp_path)
                except:
                    pass

                if text and not text.startswith("ERROR"):
                    all_texts.append(text)
                    all_confidences.append(confidence)

            # Combine results
            combined_text = "\n\n".join(all_texts)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

            logger.info(f"✅ Extracted {len(combined_text)} characters from {len(images)} pages")
            return combined_text, avg_confidence

        except Exception as e:
            logger.error(f"Error processing PDF with OCR: {e}")
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
            Tuple of (extracted_text, average_confidence)
        """
        file_type = file_type.lower().replace('.', '')

        if file_type == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            return self.extract_text_from_image(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return "", 0.0

    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from any supported file (auto-detect file type from extension)

        Args:
            file_path: Path to the document file

        Returns:
            Extracted text as string (confidence is logged but not returned)
        """
        # Get file extension
        _, ext = os.path.splitext(file_path)
        file_type = ext.lower().replace('.', '')

        logger.info(f"Extracting text from file: {file_path} (type: {file_type})")

        # Call appropriate extraction method (returns tuple)
        text, confidence = self.extract_text(file_path, file_type)

        # Log confidence but only return text
        logger.info(f"Extraction confidence: {confidence:.2%}")

        return text  # Return only text string, not tuple


# Singleton instance
easyocr_service = EasyOCRService()

