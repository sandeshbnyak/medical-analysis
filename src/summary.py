def generate_section_summary(section_name, evidence):
    """Create a concise summary from section-aligned evidence."""
    if not evidence:
        return "No evidence was found for this section."

    texts = [item.get("text", "") for item in evidence if item.get("text")]
    combined = " ".join(texts)
    if not combined:
        return "No evidence was found for this section."

    sentences = []
    for text in texts[:3]:
        cleaned = text.strip()
        if cleaned:
            sentences.append(cleaned)

    summary = " ".join(sentences)
    return f"{section_name}: {summary[:800]}"


def build_abstract_overview(chunks):
    """Extract a short abstract overview from section-aware chunks."""
    if not chunks:
        return "No abstract text available."

    abstract_chunks = []
    for item in chunks:
        section = str(item.get("section", "")).lower()
        if "abstract" in section:
            abstract_chunks.append(item.get("text", ""))

    if not abstract_chunks:
        first = chunks[0].get("text", "")
        if len(first) > 220:
            return first[:220].rstrip() + "..."
        return first

    text = " ".join(abstract_chunks)
    return text[:320].rstrip() + ("..." if len(text) > 320 else "")


def build_comparison_summary(rows):
    """Create a concise multi-paper comparison narrative."""
    if not rows:
        return "No comparison evidence was available for the selected papers."

    parts = ["Comparison summary:"]
    for row in rows:
        parts.append(
            f"- {row['Paper']} reported {row['Evidence']} in the {row['Section']} section (page {row['Page']})."
        )
    return "\n".join(parts)
