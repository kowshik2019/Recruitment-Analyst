"""
utils/file_reader.py
--------------------
Utility functions to read resume and JD files in multiple formats:
  - Plain text (.txt)
  - PDF         (.pdf)   — via PyPDF2
  - Word Doc    (.docx)  — via python-docx

Returns clean string content for downstream agents.
"""

from __future__ import annotations
from pathlib import Path


def read_file(file_path: str) -> str:
    """
    Detect file type by extension and extract plain text.

    Parameters
    ----------
    file_path : path to resume or JD file

    Returns
    -------
    str  — extracted text content
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    elif suffix == ".pdf":
        return _read_pdf(path)

    elif suffix in (".docx", ".doc"):
        return _read_docx(path)

    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use .txt, .pdf, or .docx")


def _read_pdf(path: Path) -> str:
    try:
        import PyPDF2
        text_parts = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)
    except ImportError:
        raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")


def _read_docx(path: Path) -> str:
    try:
        from docx import Document
        doc   = Document(str(path))
        lines = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(lines)
    except ImportError:
        raise ImportError("python-docx not installed. Run: pip install python-docx")
