# src/processing/extractors.py
"""Extract raw text from PDF, image, and DOCX files."""
from pathlib import Path
import os


def extract_from_pdf(filepath):
    """Extract text from PDF. Tries pdfplumber, falls back to PyPDF2."""
    # Try pdfplumber first
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
        text = "\n\n".join(parts).strip()
        if text:
            return text
    except ImportError:
        pass  # pdfplumber not installed — use PyPDF2
    except Exception as e:
        print(f"⚠️ pdfplumber failed: {e}")

    # Fallback: PyPDF2
    try:
        import PyPDF2
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            parts = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
        return "\n\n".join(parts).strip()
    except Exception as e:
        print(f"⚠️ PyPDF2 failed: {e}")
        return ""


def extract_from_image(filepath):
    """Extract text from image using Tesseract."""
    try:
        import pytesseract
        from PIL import Image
        from src.core.config import TESSERACT_CMD

        if os.path.exists(TESSERACT_CMD):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

        img = Image.open(filepath)
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        print(f"⚠️ Tesseract failed: {e}")
        return ""


def extract_from_docx(filepath):
    """Extract text from DOCX."""
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs
                          if p.text.strip())
    except Exception as e:
        print(f"⚠️ DOCX failed: {e}")
        return ""


def extract_from_txt(filepath):
    """Read plain text file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception as e:
        print(f"⚠️ TXT read failed: {e}")
        return ""


def extract_text(filepath):
    """Auto-detect file type and extract text."""
    ext = Path(filepath).suffix.lower()

    if ext == ".pdf":
        return extract_from_pdf(filepath), "pdf"

    if ext in (".docx", ".doc"):
        return extract_from_docx(filepath), "docx"

    if ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return extract_from_image(filepath), "ocr"

    if ext in (".txt", ".text", ".md"):
        return extract_from_txt(filepath), "txt"

    return "", "unsupported"