"""
Image Preprocessing Module
Handles mobile camera photos and scanned documents
"""
import cv2
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    Preprocesses images for optimal OCR results.
    Critical for mobile camera photos and scanned documents.
    """

    def preprocess(self, image_path: str) -> np.ndarray:
        """
        Full preprocessing pipeline for OCR

        Args:
            image_path: Path to image file

        Returns:
            Preprocessed image as numpy array
        """
        try:
            img = cv2.imread(image_path)

            if img is None:
                raise ValueError(f"Could not read image: {image_path}")

            # Pipeline: Deskew → Denoise → Enhance → Binarize
            img = self.deskew(img)
            img = self.denoise(img)
            img = self.enhance_contrast(img)
            img = self.binarize(img)

            return img

        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            # Return original if preprocessing fails
            return cv2.imread(image_path)

    def deskew(self, img: np.ndarray) -> np.ndarray:
        """Fix rotation from mobile cameras"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find all non-zero points
            coords = np.column_stack(np.where(gray > 0))

            # Calculate rotation angle
            angle = cv2.minAreaRect(coords)[-1]

            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            # Only rotate if angle is significant
            if abs(angle) < 0.5:
                return img

            # Rotate image
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                img, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )

            logger.debug(f"Deskewed image by {angle:.2f} degrees")
            return rotated

        except Exception as e:
            logger.warning(f"Deskew failed: {e}, returning original")
            return img

    def denoise(self, img: np.ndarray) -> np.ndarray:
        """Remove noise from image"""
        try:
            # Fast denoising for colored images
            denoised = cv2.fastNlMeansDenoisingColored(
                img, None,
                h=10,           # Filter strength for luminance
                hColor=10,      # Filter strength for color
                templateWindowSize=7,
                searchWindowSize=21
            )
            return denoised
        except Exception as e:
            logger.warning(f"Denoise failed: {e}")
            return img

    def enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        """
        CLAHE (Contrast Limited Adaptive Histogram Equalization)
        Critical for handling uneven lighting from mobile cameras
        """
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(
                clipLimit=3.0,
                tileGridSize=(8, 8)
            )
            l = clahe.apply(l)

            # Merge channels
            enhanced = cv2.merge((l, a, b))
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

            return enhanced

        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {e}")
            return img

    def binarize(self, img: np.ndarray) -> np.ndarray:
        """
        Adaptive thresholding - handles varying lighting conditions
        Much better than global thresholding for real-world photos
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                blockSize=31,  # Size of pixel neighborhood
                C=10           # Constant subtracted from mean
            )

            return binary

        except Exception as e:
            logger.warning(f"Binarization failed: {e}")
            # Return grayscale as fallback
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def preprocess_for_display(self, image_path: str) -> Tuple[np.ndarray, dict]:
        """
        Preprocess and return stats for debugging/display

        Returns:
            Tuple of (preprocessed_image, stats_dict)
        """
        img = cv2.imread(image_path)
        stats = {
            'original_size': img.shape,
            'steps': []
        }

        # Track each step
        deskewed = self.deskew(img)
        stats['steps'].append('deskew')

        denoised = self.denoise(deskewed)
        stats['steps'].append('denoise')

        enhanced = self.enhance_contrast(denoised)
        stats['steps'].append('enhance')

        final = self.binarize(enhanced)
        stats['steps'].append('binarize')
        stats['final_size'] = final.shape

        return final, stats


# Singleton instance
image_preprocessor = ImagePreprocessor()

