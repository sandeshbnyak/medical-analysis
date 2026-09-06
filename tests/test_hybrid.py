from src.retriever import retrieve_evidence
from src.summary import build_comparison_summary


def test_hybrid_retrieval_keeps_relevant_hits():
    class FakeStore:
        def __init__(self):
            self.chunks = [
                {"chunk_id": "a", "section": "Methods", "page": 1, "text": "The study used 10,000 synthetic patient records."},
                {"chunk_id": "b", "section": "Results", "page": 2, "text": "The model achieved strong accuracy in diagnosis."},
            ]

        def search(self, query_embedding, k=5):
            return [
                {"chunk_id": "a", "section": "Methods", "page": 1, "text": "The study used 10,000 synthetic patient records."},
                {"chunk_id": "b", "section": "Results", "page": 2, "text": "The model achieved strong accuracy in diagnosis."},
            ]

    fake_store = FakeStore()
    results = retrieve_evidence(fake_store, "How many patient records were used?", k=2)
    assert len(results) >= 1
    assert "10,000" in results[0]["text"]


def test_build_comparison_summary_reads_like_research_summary():
    rows = [
        {"Paper": "Paper A", "Section": "Methods", "Page": 6, "Evidence": "The study used 10,000 synthetic patient records."},
        {"Paper": "Paper B", "Section": "Methods", "Page": 7, "Evidence": "The study included 8,500 de-identified records."},
    ]
    summary = build_comparison_summary(rows)
    assert "Paper A" in summary
    assert "Paper B" in summary
    assert "10,000" in summary or "8,500" in summary
