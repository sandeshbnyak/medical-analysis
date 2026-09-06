import os
from pathlib import Path

import fitz


SECTION_HINTS = [
    "abstract",
    "introduction",
    "methods",
    "materials and methods",
    "results",
    "discussion",
    "conclusion",
    "limitations",
    "references",
]


def extract_pdf_text(pdf_path):
    """Extract page-based text content from a PDF."""
    doc = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page": page_number + 1,
            "text": text.strip(),
        })

    doc.close()
    return pages


def extract_document_metadata(pdf_path):
    """Extract basic document metadata and make a paper_id."""
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    title = (metadata.get("title") or "Untitled Paper").strip() or "Untitled Paper"
    author = (metadata.get("author") or "Unknown Author").strip() or "Unknown Author"
    paper_id = f"paper_{Path(pdf_path).stem.lower()}"
    doc.close()
    return {
        "paper_id": paper_id,
        "title": title,
        "author": author,
    }


def detect_section_from_text(text):
    """Very simple heuristic detection for section labeling."""
    normalized = (text or "").lower()
    for section in SECTION_HINTS:
        if section in normalized:
            return section.title()
    return "Body"
