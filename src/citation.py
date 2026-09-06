def format_citation_list(citations):
    lines = []
    for item in citations:
        lines.append(f"[{item['index']}] {item['section']} — Page {item['page']}\n\n{item['text']}")
    return "\n\n".join(lines)
