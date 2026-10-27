"""Optical Character Recognition (OCR) service for packaged food labels.

Applies computer-vision preprocessing (scaling, grayscale, adaptive contrast
enhancement via CLAHE, and noise suppression) to optimize food packaging photos
for Tesseract text extraction.
"""

import io
import shutil
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings


MAX_IMAGE_SIZE = 8 * 1024 * 1024  # 8 MB
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def preprocess_label_image(image_array: np.ndarray) -> np.ndarray:
    """Preprocess image array for optimal text recognition on curved/glossy food labels."""
    # Convert to grayscale if RGB
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_array

    # Upscale slightly if the image is modest to sharpen fine print
    height, width = gray.shape[:2]
    if width < 1200 or height < 1200:
        gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # Neutralizes shadows, glossy glare, and uneven illumination on food packaging
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Gentle Gaussian blur to remove digital sensor noise while preserving character edges
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

    return blurred


def extract_text(image_bytes: bytes) -> dict:
    """Extract text from a food-label image with robust validation and preprocessing."""

    if not image_bytes:
        raise ValueError("The uploaded image is empty.")

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError("Image size must not exceed 8 MB.")

    try:
        # Validate that the bytes form a valid, uncorrupted image in supported format
        with Image.open(io.BytesIO(image_bytes)) as probe:
            image_format = probe.format
            if image_format not in ALLOWED_FORMATS:
                raise ValueError("Upload a JPEG, PNG, or WebP image.")
            probe.verify()

        # Reopen to convert and process
        with Image.open(io.BytesIO(image_bytes)) as image:
            image = image.convert("RGB")
            # Downscale overly huge photos to 2200px max dimension for memory efficiency
            image.thumbnail((2200, 2200), Image.Resampling.LANCZOS)
            image_array = np.array(image)

        processed = preprocess_label_image(image_array)

        # Configure Tesseract binary path from settings or system PATH
        settings = get_settings()
        tesseract_binary = None

        if settings.tesseract_cmd and Path(settings.tesseract_cmd).is_file():
            tesseract_binary = settings.tesseract_cmd
        elif shutil.which("tesseract"):
            tesseract_binary = shutil.which("tesseract")

        if tesseract_binary:
            pytesseract.pytesseract.tesseract_cmd = tesseract_binary
        else:
            raise RuntimeError(
                "Tesseract was not found. Configure TESSERACT_CMD in your .env file."
            )

        # PSM 6: Assume a single uniform block of text (ideal for ingredient paragraphs)
        text = pytesseract.image_to_string(
            processed,
            config="--psm 6 -l eng",
        ).strip()

        # If PSM 6 yielded empty text, fallback to PSM 3 (fully automatic page segmentation)
        if not text:
            text = pytesseract.image_to_string(
                processed,
                config="--psm 3 -l eng",
            ).strip()

        return {
            "extracted_text": text,
            "character_count": len(text),
            "has_text": bool(text),
            "image_format": image_format,
        }

    except UnidentifiedImageError as exc:
        raise ValueError(
            "The uploaded file is not a valid or supported image."
        ) from exc
