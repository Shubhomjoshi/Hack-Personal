"""
Quality Assessment Service - Evaluates document image quality
"""
import cv2
import numpy as np
from typing import Tuple, Dict
from PIL import Image
from pdf2image import convert_from_path
import logging

logger = logging.getLogger(__name__)


class QualityAssessmentService:
    """Service for assessing document quality"""

    def detect_blur(self, image_path: str) -> Tuple[bool, float]:
        """
        Detect if image is blurry using Laplacian variance

        Returns:
            Tuple of (is_blurry, blur_score)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return True, 0.0

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Threshold: below 100 is considered blurry
            is_blurry = bool(laplacian_var < 100)

            # Normalize score (higher is better)
            blur_score = min(laplacian_var / 200.0, 1.0)

            logger.debug(f"Blur detection: var={laplacian_var:.2f}, is_blurry={is_blurry}")

            return is_blurry, float(blur_score)

        except Exception as e:
            logger.error(f"Error detecting blur: {str(e)}")
            return True, 0.0

    def detect_skew(self, image_path: str) -> Tuple[bool, float]:
        """
        Detect if image is skewed/rotated

        Returns:
            Tuple of (is_skewed, skew_angle)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return True, 0.0

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)

            # Detect lines using Hough Transform
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

            if lines is None:
                return False, 0.0

            # Calculate angles
            angles = []
            for line in lines[:50]:  # Check first 50 lines
                rho, theta = line[0]
                angle = np.degrees(theta) - 90
                angles.append(angle)

            # Find the median angle
            median_angle = np.median(angles) if angles else 0.0

            # Consider skewed if angle > 2 degrees
            is_skewed = bool(abs(median_angle) > 2.0)

            logger.debug(f"Skew detection: angle={median_angle:.2f}, is_skewed={is_skewed}")

            return is_skewed, float(median_angle)

        except Exception as e:
            logger.error(f"Error detecting skew: {str(e)}")
            return False, 0.0

    def check_brightness(self, image_path: str) -> Tuple[bool, float]:
        """
        Check if image is overexposed or underexposed

        Returns:
            Tuple of (has_brightness_issue, brightness_score)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return True, 0.0

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            mean_brightness = np.mean(gray)

            # Ideal range: 80-180
            has_issue = bool(mean_brightness < 60 or mean_brightness > 200)

            # Normalize score (closer to 130 is better)
            brightness_score = 1.0 - (abs(mean_brightness - 130) / 130.0)
            brightness_score = max(0.0, min(1.0, brightness_score))

            logger.debug(f"Brightness: mean={mean_brightness:.2f}, has_issue={has_issue}")

            return has_issue, float(brightness_score)

        except Exception as e:
            logger.error(f"Error checking brightness: {str(e)}")
            return True, 0.0

    def calculate_quality_score(self, image_path: str) -> Dict[str, any]:
        """
        Calculate overall quality score and assessment

        Returns:
            Dictionary with quality metrics
        """
        try:
            # Run all quality checks
            is_blurry, blur_score = self.detect_blur(image_path)
            is_skewed, skew_angle = self.detect_skew(image_path)
            has_brightness_issue, brightness_score = self.check_brightness(image_path)

            # Calculate overall quality score (0-100)
            overall_score = (blur_score * 40 + brightness_score * 30 + (0.8 if not is_skewed else 0.3) * 30)

            # Determine readability status
            if overall_score >= 75:
                readability = "Clear"
                recommendation = "Accept"
            elif overall_score >= 50:
                readability = "Partially Clear"
                recommendation = "Accept"
            else:
                readability = "Unreadable"
                recommendation = "Re-upload"

            result = {
                'quality_score': float(round(overall_score, 2)),
                'readability_status': readability,
                'recommendation': recommendation,
                'is_blurry': bool(is_blurry),
                'blur_score': float(round(blur_score, 2)),
                'is_skewed': bool(is_skewed),
                'skew_angle': float(round(skew_angle, 2) if skew_angle else 0.0),
                'has_brightness_issue': bool(has_brightness_issue),
                'brightness_score': float(round(brightness_score, 2))
            }

            logger.info(f"Quality assessment: {readability}, score={overall_score:.2f}")

            return result

        except Exception as e:
            logger.error(f"Error calculating quality score: {str(e)}")
            return {
                'quality_score': 0.0,
                'readability_status': 'Unreadable',
                'recommendation': 'Re-upload',
                'is_blurry': True,
                'blur_score': 0.0,
                'is_skewed': False,
                'skew_angle': 0.0,
                'has_brightness_issue': True,
                'brightness_score': 0.0
            }

    def assess_pdf_quality(self, pdf_path: str) -> Dict[str, any]:
        """
        Assess quality of PDF by converting first page to image

        Returns:
            Dictionary with quality metrics
        """
        try:
            # Convert first page to image
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)

            if not images:
                return self.calculate_quality_score("")

            # Save temp image
            temp_image_path = pdf_path.replace('.pdf', '_temp.jpg')
            images[0].save(temp_image_path, 'JPEG')

            # Assess quality
            result = self.calculate_quality_score(temp_image_path)

            # Clean up
            import os
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

            return result

        except Exception as e:
            logger.error(f"Error assessing PDF quality: {str(e)}")
            return self.calculate_quality_score("")

    def assess_quality(self, file_path: str, file_type: str) -> Dict[str, any]:
        """
        Main method to assess document quality based on file type

        Args:
            file_path: Path to the file
            file_type: File type (pdf, jpg, jpeg, png, etc.)

        Returns:
            Dictionary with quality metrics
        """
        try:
            if file_type.lower() == 'pdf':
                return self.assess_pdf_quality(file_path)
            else:
                return self.calculate_quality_score(file_path)
        except Exception as e:
            logger.error(f"Error assessing quality: {str(e)}")
            return {
                'quality_score': 0.0,
                'readability_status': 'Unreadable',
                'recommendation': 'Re-upload',
                'is_blurry': True,
                'blur_score': 0.0,
                'is_skewed': False,
                'skew_angle': 0.0,
                'has_brightness_issue': True,
                'brightness_score': 0.0
            }


# Singleton instance
quality_service = QualityAssessmentService()

