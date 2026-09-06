from pathlib import Path

import fitz

from src.chunker import chunk_document
from src.embeddings import embed_texts, load_embedder
from src.pdf_processor import extract_document_metadata, extract_pdf_text
from src.vector_store import FAISSVectorStore
from src.retriever import retrieve_evidence


def test_pipeline_basic():
    pdf_path = Path('data/papers/test_sample.pdf')
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), 'Abstract\nThe study used 10,000 synthetic patient records.\n\nMethods\nThe dataset consisted of synthetic records from a hospital cohort.')
    doc.save(pdf_path)
    doc.close()

    pages = extract_pdf_text(str(pdf_path))
    metadata = extract_document_metadata(str(pdf_path))
    chunks = chunk_document(pages, metadata['paper_id'])
    assert len(chunks) >= 1

    embedder = load_embedder()
    embeddings = embed_texts(embedder, [c['text'] for c in chunks])
    store = FAISSVectorStore.from_chunks(chunks, embeddings)
    results = retrieve_evidence(store, 'How many patient records were used?', k=3)
    assert len(results) >= 1
    assert '10,000' in results[0]['text'] or 'patient records' in results[0]['text'].lower()


if __name__ == '__main__':
    test_pipeline_basic()
    print('pipeline ok')
