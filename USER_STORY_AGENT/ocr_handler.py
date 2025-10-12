"""
OCR Handler Module
Extracts text from images using Tesseract OCR
"""

import os
from typing import Optional
from PIL import Image


class OCRHandler:
    """Handle OCR text extraction from images"""

    def __init__(self):
        self.tesseract_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        """Check if Tesseract is installed"""
        try:
            import pytesseract
            # Try to get version to verify it's working
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image file

        Args:
            image_path: Path to image file

        Returns:
            Extracted text content
        """
        if not self.tesseract_available:
            return self._get_fallback_message(image_path)

        try:
            import pytesseract

            # Open image
            image = Image.open(image_path)

            # Extract text
            text = pytesseract.image_to_string(image)

            return text.strip()

        except Exception as e:
            return f"Error extracting text from image: {str(e)}\n{self._get_fallback_message(image_path)}"

    def _get_fallback_message(self, image_path: str) -> str:
        """Get fallback message when OCR is not available"""
        filename = os.path.basename(image_path)
        return f"""
[Image File: {filename}]
Note: OCR text extraction is not available. To enable image text extraction:
1. Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract
2. Ensure pytesseract is installed: pip install pytesseract
3. Add Tesseract to your system PATH

For now, please describe the image content or provide text separately.
"""

    def is_image_file(self, file_path: str) -> bool:
        """Check if file is an image"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        _, ext = os.path.splitext(file_path)
        return ext.lower() in image_extensions


# Create singleton instance
ocr_handler = OCRHandler()


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image file

    Args:
        image_path: Path to image file

    Returns:
        Extracted text content
    """
    return ocr_handler.extract_text(image_path)


def is_image_file(file_path: str) -> bool:
    """
    Check if file is an image

    Args:
        file_path: Path to file

    Returns:
        True if file is an image
    """
    return ocr_handler.is_image_file(file_path)
