
import io
import shutil

import cv2
import numpy as np
import pytesseract
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings


MAX_IMAGE_SIZE = 8 * 1024 * 1024  # 8 MB
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def extract_text(image_bytes: bytes) -> dict:
    """Extract text from a supported food-label image."""

    if not image_bytes:
        raise ValueError("The uploaded image is empty.")

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError("Image size must not exceed 8 MB.")

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            if image.format not in ALLOWED_FORMATS:
                raise ValueError("Upload a JPEG, PNG, or WebP image.")

            image.verify()

        with Image.open(io.BytesIO(image_bytes)) as image:
            image = image.convert("RGB")
            image.thumbnail((2000, 2000))

            image_array = np.array(image)
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            processed = cv2.resize(
                gray,
                None,
                fx=1.5,
                fy=1.5,
                interpolation=cv2.INTER_CUBIC,
            )
            processed = cv2.GaussianBlur(processed, (3, 3), 0)

            settings = get_settings()
            if settings.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = (
                    settings.tesseract_cmd
                )
            elif not shutil.which("tesseract"):
                raise RuntimeError(
                    "Tesseract was not found. Configure TESSERACT_CMD "
                    "in your .env file."
                )

            text = pytesseract.image_to_string(
                processed,
                config="--psm 6",
            ).strip()

            return {
                "extracted_text": text,
                "character_count": len(text),
                "has_text": bool(text),
            }

    except UnidentifiedImageError as exc:
        raise ValueError(
            "The uploaded file is not a valid image."
        ) from exc
