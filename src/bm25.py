import math
import re


def tokenize(text):
    return re.findall(r"\w+", text.lower())


def bm25_scores(query, documents, k1=1.5, b=0.75):
    q_terms = tokenize(query)
    if not q_terms or not documents:
        return []

    doc_lengths = [len(tokenize(doc.get("text", ""))) for doc in documents]
    avg_len = sum(doc_lengths) / max(len(doc_lengths), 1)

    idf = {}
    df = {}
    for term in set(t for doc in documents for t in tokenize(doc.get("text", ""))):
        df[term] = sum(1 for doc in documents if term in tokenize(doc.get("text", "")))
    for term in set(q_terms):
        idf[term] = math.log((len(documents) - df.get(term, 0) + 0.5) / (df.get(term, 0) + 0.5) + 1.0)

    scores = []
    for idx, doc in enumerate(documents):
        text = doc.get("text", "")
        tokens = tokenize(text)
        doc_len = len(tokens)
        score = 0.0
        for term in q_terms:
            if term not in tokens:
                continue
            tf = tokens.count(term)
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / avg_len if avg_len else 0.0))
            score += idf.get(term, 0.0) * (numerator / denominator)
        scores.append((score, idx))

    return sorted(scores, key=lambda x: x[0], reverse=True)
