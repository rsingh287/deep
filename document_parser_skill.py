import os

from docx import Document
from pypdf import PdfReader


def run_document_parser(file_path: str) -> str:
    """Reads a PDF or DOCX file and extracts the text."""
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    ext = file_path.lower().split(".")[-1]
    text = ""

    try:
        if ext == "pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif ext == "docx":
            doc = Document(file_path)
            for p in doc.paragraphs:
                text += p.text + "\n"
        else:
            # Try reading as plain text
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

        return f"Successfully extracted {len(text)} characters from {file_path}. Text preview:\n\n{text[:500]}..."

    except Exception as e:
        return f"Error parsing document: {e}"
