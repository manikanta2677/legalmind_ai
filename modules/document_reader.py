import pdfplumber
from docx import Document
from pdf2image import convert_from_bytes
import pytesseract


# Change this path if your Tesseract installed somewhere else
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def read_pdf(file):
    text = ""

    # First try normal text extraction
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        text = ""

    # If normal extraction fails, use OCR
    if len(text.strip()) < 50:
        text = read_scanned_pdf(file)

    return text


def read_scanned_pdf(file):
    text = ""

    file.seek(0)
    images = convert_from_bytes(file.read())

    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image)
        text += f"\n--- Page {i + 1} ---\n"
        text += page_text + "\n"

    return text


def read_docx(file):
    doc = Document(file)
    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def read_txt(file):
    return file.read().decode("utf-8")