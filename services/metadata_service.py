"""
Metadata Extraction Service - Extracts key information from documents
"""
import re
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetadataExtractionService:
    """Service for extracting metadata from documents"""

    # Regex patterns for different fields
    PATTERNS = {
        'order_number': [
            r'order\s*(?:number|no|#)?[\s:]*([A-Z0-9\-]+)',
            r'order[\s:]+([A-Z0-9\-]{5,20})',
            r'po\s*(?:number|no|#)?[\s:]*([A-Z0-9\-]+)',
        ],
        'load_number': [
            r'load\s*(?:number|no|#)?[\s:]*([A-Z0-9\-]+)',
            r'load[\s:]+([A-Z0-9\-]{5,20})',
            r'shipment\s*(?:number|no|#)?[\s:]*([A-Z0-9\-]+)',
        ],
        'invoice_number': [
            r'invoice\s*(?:number|no|#)?[\s:]*([A-Z0-9\-]+)',
            r'invoice[\s:]+([A-Z0-9\-]{5,20})',
            r'inv\s*(?:no|#)?[\s:]*([A-Z0-9\-]+)',
        ],
        'date': [
            r'date[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'date[\s:]*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})',
        ],
        'bol_number': [
            r'bol\s*(?:number|no|#)?[\s:]*([A-Z0-9\-]+)',
            r'b/l\s*(?:number|no|#)?[\s:]*([A-Z0-9\-]+)',
            r'bill of lading[\s:]+([A-Z0-9\-]+)',
        ],
        'tracking_number': [
            r'tracking\s*(?:number|no|#)?[\s:]*([A-Z0-9\-]+)',
            r'track(?:ing)?[\s:]+([A-Z0-9\-]{10,30})',
        ],
        'reference_number': [
            r'reference\s*(?:number|no|#)?[\s:]*([A-Z0-9\-]+)',
            r'ref\s*(?:no|#)?[\s:]*([A-Z0-9\-]+)',
        ],
    }

    def extract_field(self, text: str, field_name: str) -> Optional[str]:
        """
        Extract a specific field from text using regex patterns

        Args:
            text: Document text
            field_name: Name of field to extract

        Returns:
            Extracted value or None
        """
        if field_name not in self.PATTERNS:
            return None

        patterns = self.PATTERNS[field_name]
        text_clean = ' '.join(text.split())  # Normalize whitespace

        for pattern in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value and len(value) >= 3:  # Minimum length check
                    logger.debug(f"Extracted {field_name}: {value}")
                    return value

        return None

    def extract_all_metadata(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract all available metadata from document text

        Args:
            text: Document text

        Returns:
            Dictionary of extracted metadata
        """
        metadata = {}

        for field_name in self.PATTERNS.keys():
            value = self.extract_field(text, field_name)
            metadata[field_name] = value

        # Additional processing for dates
        if metadata.get('date'):
            metadata['formatted_date'] = self._normalize_date(metadata['date'])

        # Log extraction results
        extracted_fields = [k for k, v in metadata.items() if v is not None]
        logger.info(f"Extracted metadata fields: {extracted_fields}")

        return metadata

    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        Normalize date string to consistent format (YYYY-MM-DD)

        Args:
            date_str: Date string in various formats

        Returns:
            Normalized date string or None
        """
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y',
            '%m/%d/%y', '%m-%d-%y', '%d/%m/%y', '%d-%m-%y',
            '%B %d, %Y', '%b %d, %Y', '%B %d %Y', '%b %d %Y',
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue

        return date_str  # Return original if cannot parse

    def extract_amounts(self, text: str) -> Dict[str, float]:
        """
        Extract monetary amounts from text

        Args:
            text: Document text

        Returns:
            Dictionary of found amounts
        """
        amounts = {}

        # Pattern for currency amounts
        pattern = r'\$\s*([0-9,]+\.?\d{0,2})'
        matches = re.findall(pattern, text)

        if matches:
            parsed_amounts = []
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    parsed_amounts.append(amount)
                except ValueError:
                    pass

            if parsed_amounts:
                amounts['total'] = max(parsed_amounts)  # Assume largest is total
                amounts['all_amounts'] = parsed_amounts

        return amounts

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information from text

        Args:
            text: Document text

        Returns:
            Dictionary of contact information
        """
        contact = {}

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()

        # Phone pattern (US format)
        phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = f"{phone_match.group(1)}-{phone_match.group(2)}-{phone_match.group(3)}"

        return contact


# Singleton instance
metadata_service = MetadataExtractionService()

