import re


def simple_rerank(query, evidence, top_k=5):
    """Lightweight reranker using lexical overlap between the query and each chunk."""
    query_terms = set(re.findall(r"\w+", query.lower()))
    scored = []

    for item in evidence:
        text = item.get("text", "")
        hit_count = 0
        for term in query_terms:
            if len(term) <= 2:
                continue
            if term in text.lower():
                hit_count += 1
        score = hit_count + 0.1 * len(text.split())
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]
