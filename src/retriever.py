from src.bm25 import bm25_scores
from src.embeddings import load_embedder
from src.reranker import simple_rerank


def retrieve_evidence(vector_store, question, k=4):
    embedder = load_embedder()
    q_embedding = embedder.encode(question, convert_to_numpy=True, normalize_embeddings=True)
    semantic_results = vector_store.search(q_embedding, k=max(k * 3, 5))

    if not semantic_results:
        return []

    bm25_ranked = bm25_scores(question, semantic_results)
    bm25_items = [semantic_results[idx] for _, idx in bm25_ranked[:k]]
    reranked = simple_rerank(question, semantic_results + bm25_items, top_k=k)
    deduped = []
    seen = set()
    for item in reranked:
        key = item.get("chunk_id") or item.get("text")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped[:k]
