# modules/pdf_reader.py
import fitz
import io
import pytesseract
from PIL import Image, ImageOps

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_and_ocr(pil_image) -> str:
    """
    Standardized structural OCR processor optimized for multi-column layout tracking.
    """
    # Convert to grayscale
    image = ImageOps.grayscale(pil_image)
    
    # Scale up small or faint text layers to drastically improve accuracy
    if image.width < 1500:
        image = image.resize(
            (image.width * 2, image.height * 2), 
            Image.Resampling.LANCZOS
        )
        
    # --psm 3 handles automatic layout and column structural flows perfectly
    text = pytesseract.image_to_string(
        image,
        lang="eng",
        config="--oem 3 --psm 3"
    )
    return text.strip()

def extract_pdf_pages(pdf_path: str) -> list:
    """
    Extract text from each PDF page. Uses embedded structural streams first, 
    falling back instantly to high-resolution full-page rendering if OCR is required.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Pull direct digital text streams if present
        text = page.get_text("text").strip()

        # OCR fallback gate (executed if page is scanned or contains broken font maps)
        if len(text) < 50:
            print(f"OCR Full Page Render Fallback -> Page {page_num + 1}")
            
            # Avoid extracting raw object streams. Render the entire page layout at 300 DPI
            pix = page.get_pixmap(dpi=150, alpha=False)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            
            text = preprocess_and_ocr(image)

        pages.append({
            "page": page_num + 1,
            "text": text
        })

    doc.close()
    return pages