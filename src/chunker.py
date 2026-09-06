import re

from src.section_detector import detect_section_name


def chunk_document(pages, paper_id):
    """Split PDF pages into section-aware chunks with metadata."""
    chunks = []

    for page in pages:
        text = page.get("text", "")
        if not text:
            continue

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
        for idx, paragraph in enumerate(paragraphs):
            cleaned = re.sub(r"\s+", " ", paragraph)
            if len(cleaned) < 40:
                continue
            section = detect_section_name(cleaned)
            chunk_id = f"{paper_id}_{section.lower().replace(' ', '_')}_{page['page']}_{idx}"
            chunks.append({
                "paper_id": paper_id,
                "section": section,
                "page": page["page"],
                "chunk_id": chunk_id,
                "text": cleaned,
            })

    return chunks
