import io
from typing import Optional

import pdfplumber


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from a PDF file."""
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts).strip()


def extract_text_from_pdf_fallback(file_bytes: bytes) -> str:
    """Fallback using PyPDF2 if pdfplumber fails."""
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts).strip()
    except Exception:
        return ""


def extract_pdf_text(file_bytes: bytes) -> str:
    text = extract_text_from_pdf(file_bytes)
    if not text:
        text = extract_text_from_pdf_fallback(file_bytes)
    return text