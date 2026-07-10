# modules/ocr_engine.py
import pytesseract
from PIL import Image, ImageOps

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path: str) -> str:
    """
    Stand-alone processing file for vendor-uploaded certificates or single-page images.
    """
    image = Image.open(image_path)
    image = ImageOps.grayscale(image)

    # Upscale constraints to prevent line dropouts
    if image.width < 1500:
        image = image.resize(
            (image.width * 2, image.height * 2),
            Image.Resampling.LANCZOS
        )

    # Performance bounding guardrail
    MAX_SIDE = 3500
    if max(image.size) > MAX_SIDE:
        image.thumbnail((MAX_SIDE, MAX_SIDE))

    # Match system-wide automatic page segmentation layout rules
    text = pytesseract.image_to_string(
        image,
        lang="eng",
        config="--oem 3 --psm 3"
    )
    return text.strip()