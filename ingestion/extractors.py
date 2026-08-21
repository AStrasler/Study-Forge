"""
Text extraction from supported study-material formats.

Currently supports: PDF, DOCX, PPTX.
Additional formats (TXT, MD, images/OCR, audio/video) can be added cleanly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from utils.logging import get_logger

logger = get_logger(__name__)

PathLike = Union[str, Path]


def extract_text(path: PathLike) -> str:
    """Dispatch to the correct extractor based on file extension."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(p)
    if suffix in {".docx"}:
        return _extract_docx(p)
    if suffix in {".pptx"}:
        return _extract_pptx(p)
    if suffix in {".txt", ".md", ".markdown"}:
        return p.read_text(encoding="utf-8", errors="replace")

    raise ValueError(f"Unsupported file type: {suffix} ({p.name})")


def _extract_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    parts: list[str] = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
            if text.strip():
                parts.append(text)
        except Exception as exc:
            logger.warning("PDF page %d extraction failed in %s: %s", i, path.name, exc)
    return "\n\n".join(parts).strip()


def _extract_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n\n".join(paragraphs).strip()


def _extract_pptx(path: Path) -> str:
    from pptx import Presentation

    prs = Presentation(str(path))
    parts: list[str] = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text and shape.text.strip():
                parts.append(shape.text.strip())
    return "\n\n".join(parts).strip()
