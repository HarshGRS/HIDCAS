import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageEnhance

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"D:\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"


def preprocess_image(image):
    """Image quality improve karo OCR ke liye"""
    # Grayscale 
    image = image.convert("L")
    # Sharpness 
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    # Contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    return image


def ocr_pdf(file_path: str) -> str:
    try:
        pages = convert_from_path(file_path, dpi=400, poppler_path=POPPLER_PATH)
        full_text = ""

        for page in pages:
            # Image preprocess 
            processed = preprocess_image(page)

            # For table structure psm 6
            table_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(
                processed,
                lang="eng",
                config=table_config
            )
            full_text += text + "\n"

        return full_text.strip()

    except Exception as e:
        print(f"OCR error: {e}")
        return ""