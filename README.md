# Medical Literature Assistant

A lightweight evidence-grounded medical literature assistant built with Streamlit, FAISS, sentence embeddings, and local inference support.

## Features

- Upload a PDF paper
- Extract text and basic metadata
- Split into section-aware chunks with page metadata
- Embed chunks with Sentence Transformers
- Search with hybrid retrieval (semantic + BM25)
- Ask grounded questions with citations
- Summarize Methods / Results / Limitations
- Compare multiple uploaded papers
- Search PubMed for related papers
- Display source cards and expandable evidence

## Project structure

```text
medical-literature-assistant/
├── app.py
├── requirements.txt
├── Dockerfile
├── Procfile
├── render.yaml
├── README.md
├── .env.example
├── data/
│   ├── papers/
│   └── vectorstore/
├── src/
│   ├── __init__.py
│   ├── bm25.py
│   ├── citation.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── llm.py
│   ├── pdf_processor.py
│   ├── pubmed.py
│   ├── reranker.py
│   ├── retriever.py
│   ├── section_detector.py
│   ├── summary.py
│   ├── validator.py
│   └── vector_store.py
├── tests/
│   ├── test_dashboard.py
│   ├── test_hybrid.py
│   ├── test_pipeline.py
│   ├── test_summary.py
│   └── test_validation.py
└── utils/
    └── helpers.py
```

## Local run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Docker run

```bash
docker build -t medical-literature-assistant .
docker run -p 8501:8501 medical-literature-assistant
```

## Deployment targets

This project is ready for simple deployment on platforms such as:

- Render
- Railway
- Fly.io
- a standard container host

## Notes

The app supports local Ollama inference when available, and includes a fallback path if Ollama is unavailable. The architecture is intentionally designed to stay evidence-grounded rather than relying on free-form model memory.
