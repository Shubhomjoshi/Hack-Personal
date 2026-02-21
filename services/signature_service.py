"""
Signature Detection Service - Detects and counts signatures in documents
"""
import cv2
import numpy as np
from typing import Tuple, List
from PIL import Image
from pdf2image import convert_from_path
import logging

logger = logging.getLogger(__name__)


class SignatureDetectionService:
    """Service for detecting signatures in documents"""

    def detect_signatures_simple(self, image_path: str) -> Tuple[int, List[dict]]:
        """
        Simple signature detection using contour analysis

        Returns:
            Tuple of (signature_count, signature_regions)
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return 0, []

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )

            # Find contours
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            signatures = []
            image_height, image_width = gray.shape

            for contour in contours:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)

                # Filter by size (signatures are usually medium-sized)
                if w < 50 or h < 20 or w > image_width * 0.5 or h > image_height * 0.3:
                    continue

                # Calculate aspect ratio
                aspect_ratio = w / float(h)

                # Signatures typically have aspect ratio between 1.5 and 6
                if aspect_ratio < 1.5 or aspect_ratio > 6:
                    continue

                # Calculate density (filled pixels / area)
                roi = binary[y:y+h, x:x+w]
                density = cv2.countNonZero(roi) / float(w * h)

                # Signatures have moderate density (0.1 to 0.4)
                if density < 0.05 or density > 0.5:
                    continue

                # Check if in bottom half of document (signatures usually at bottom)
                if y > image_height * 0.3:
                    signatures.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'confidence': float(density)
                    })

            # Remove overlapping signatures (keep the one with higher confidence)
            filtered_signatures = self._remove_overlapping_regions(signatures)

            logger.info(f"Detected {len(filtered_signatures)} potential signatures")

            return len(filtered_signatures), filtered_signatures

        except Exception as e:
            logger.error(f"Error detecting signatures: {str(e)}")
            return 0, []

    def _remove_overlapping_regions(self, regions: List[dict]) -> List[dict]:
        """Remove overlapping signature regions"""
        if not regions:
            return []

        # Sort by confidence
        sorted_regions = sorted(regions, key=lambda x: x['confidence'], reverse=True)

        filtered = []
        for region in sorted_regions:
            # Check if overlaps with any existing region
            overlaps = False
            for existing in filtered:
                if self._regions_overlap(region, existing):
                    overlaps = True
                    break

            if not overlaps:
                filtered.append(region)

        return filtered

    def _regions_overlap(self, region1: dict, region2: dict, threshold: float = 0.3) -> bool:
        """Check if two regions overlap significantly"""
        x1, y1, w1, h1 = region1['x'], region1['y'], region1['width'], region1['height']
        x2, y2, w2, h2 = region2['x'], region2['y'], region2['width'], region2['height']

        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)

        if x_right < x_left or y_bottom < y_top:
            return False

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2

        # Calculate overlap ratio
        overlap_ratio = intersection_area / min(area1, area2)

        return overlap_ratio > threshold

    def detect_signatures_from_pdf(self, pdf_path: str) -> Tuple[int, bool]:
        """
        Detect signatures in PDF document

        Returns:
            Tuple of (total_signature_count, has_signature)
        """
        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path, dpi=200)

            total_count = 0
            all_signatures = []

            for i, image in enumerate(images):
                # Save temp image
                temp_path = pdf_path.replace('.pdf', f'_page{i}.jpg')
                image.save(temp_path, 'JPEG')

                # Detect signatures
                count, signatures = self.detect_signatures_simple(temp_path)
                total_count += count
                all_signatures.extend(signatures)

                # Clean up
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            has_signature = bool(total_count > 0)

            logger.info(f"PDF signature detection: {total_count} signatures across {len(images)} pages")

            return int(total_count), has_signature

        except Exception as e:
            logger.error(f"Error detecting signatures in PDF: {str(e)}")
            return 0, False

    def detect_signatures(self, file_path: str, file_type: str) -> Tuple[int, bool, float]:
        """
        Detect signatures in document (auto-detect type)

        Args:
            file_path: Path to document
            file_type: File extension

        Returns:
            Tuple of (signature_count, has_signature, confidence)
        """
        file_type = file_type.lower().replace('.', '')

        try:
            if file_type == 'pdf':
                count, has_sig = self.detect_signatures_from_pdf(file_path)
                confidence = 0.7 if count > 0 else 0.0
                return int(count), bool(has_sig), float(confidence)
            elif file_type in ['jpg', 'jpeg', 'png', 'tiff']:
                count, regions = self.detect_signatures_simple(file_path)
                has_sig = bool(count > 0)
                # Average confidence from all detected signatures
                confidence = np.mean([r['confidence'] for r in regions]) if regions else 0.0
                return int(count), has_sig, float(confidence)
            else:
                return 0, False, 0.0

        except Exception as e:
            logger.error(f"Error in signature detection: {str(e)}")
            return 0, False, 0.0


# Singleton instance
signature_service = SignatureDetectionService()

