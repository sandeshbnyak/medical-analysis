import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.chunker import chunk_document
from src.citation import format_citation_list
from src.embeddings import embed_texts, load_embedder
from src.pdf_processor import extract_document_metadata, extract_pdf_text
from src.pubmed import search_pubmed
from src.retriever import retrieve_evidence
from src.summary import build_abstract_overview, build_comparison_summary
from src.vector_store import FAISSVectorStore
from src.llm import generate_grounded_answer, generate_section_summary_for_question


def compare_papers(paper_contexts, question):
    """Compare extracted evidence across multiple uploaded papers."""
    comparison_rows = []
    for context in paper_contexts:
        vector_store = context["vector_store"]
        evidence = retrieve_evidence(vector_store, question, k=2)
        if evidence:
            first = evidence[0]
            comparison_rows.append({
                "paper": context["title"],
                "author": context["author"],
                "evidence": first["text"],
                "section": first["section"],
                "page": first["page"],
            })
    return comparison_rows


def build_comparison_dashboard(paper_contexts, question):
    """Return compact comparison rows for a lightweight dashboard."""
    rows = []
    for context in paper_contexts:
        evidence = retrieve_evidence(context["vector_store"], question, k=3)
        if not evidence:
            continue
        best = evidence[0]
        rows.append({
            "Paper": context["title"],
            "Author": context["author"],
            "Section": best["section"],
            "Page": best["page"],
            "Evidence": best["text"],
        })
    return rows

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
PAPERS_DIR = DATA_DIR / "papers"
PAPERS_DIR.mkdir(parents=True, exist_ok=True)


@st.cache_resource
def get_embedder():
    return load_embedder()


def ensure_session_state():
    if "paper_context" not in st.session_state:
        st.session_state.paper_context = None
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None
    if "multi_papers" not in st.session_state:
        st.session_state.multi_papers = []


def process_pdf(uploaded_file):
    if uploaded_file is None:
        return None

    safe_name = uploaded_file.name.replace(" ", "_")
    pdf_path = PAPERS_DIR / safe_name
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    pages = extract_pdf_text(str(pdf_path))
    metadata = extract_document_metadata(str(pdf_path))

    chunks = chunk_document(pages, paper_id=metadata.get("paper_id", safe_name))
    if not chunks:
        st.error("No readable text was found in the uploaded PDF.")
        return None

    embedder = get_embedder()
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(embedder, texts)
    vector_store = FAISSVectorStore.from_chunks(chunks, embeddings)

    st.session_state.paper_context = {
        "title": metadata.get("title") or uploaded_file.name,
        "author": metadata.get("author") or "Unknown author",
        "pages": len(pages),
        "chunks": chunks,
        "vector_store": vector_store,
        "pdf_path": str(pdf_path),
    }
    st.session_state.uploaded_filename = uploaded_file.name

    return st.session_state.paper_context


def render_current_paper():
    context = st.session_state.paper_context
    if not context:
        st.info("Upload a PDF paper to begin.")
        return

    st.subheader("Current Paper")
    meta_col, overview_col = st.columns([1, 2])

    with meta_col:
        st.markdown(f"**Title:** {context['title']}")
        st.markdown(f"**Author:** {context['author']}")
        st.markdown(f"**Pages:** {context['pages']}")
        st.markdown(f"**Chunks indexed:** {len(context['chunks'])}")

    with overview_col:
        st.markdown("**Abstract overview**")
        st.write(build_abstract_overview(context["chunks"]))


def render_source_cards(evidence):
    if not evidence:
        st.info("No evidence sources are available.")
        return

    for idx, item in enumerate(evidence, start=1):
        with st.container():
            st.markdown(f"### Source [{idx}]")
            st.markdown(f"**Section:** {item['section']} | **Page:** {item['page']}")
            st.write(item["text"])
            st.markdown("---")


def render_pubmed_search():
    st.subheader("PubMed Research")
    pubmed_query = st.text_input("Search PubMed", value="diabetes machine learning")
    if st.button("Search PubMed"):
        with st.spinner("Querying PubMed..."):
            try:
                results = search_pubmed(pubmed_query, max_results=5)
            except Exception as exc:
                st.warning(f"PubMed query failed: {exc}")
                results = []

        if not results:
            st.info("No PubMed results were returned for that query.")
            return

        for item in results:
            with st.container():
                st.markdown(f"### {item['title']}")
                st.caption(f"PMID: {item['pmid']} | {item['journal']} | {item['year']}")
                if item.get("abstract"):
                    st.write(item["abstract"][:500] + "..." if len(item["abstract"]) > 500 else item["abstract"])
                st.markdown("---")


def render_answer(question: str, mode: str = "General"):
    context = st.session_state.paper_context
    if not context:
        st.warning("Please upload a paper before asking a question.")
        return

    vector_store = context["vector_store"]
    evidence = retrieve_evidence(vector_store, question, k=4)

    if mode != "General":
        filtered = [
            item for item in evidence
            if item.get("section", "").lower() == mode.lower()
        ]
        if filtered:
            evidence = filtered

    if not evidence:
        st.warning("No relevant evidence was found in the uploaded paper.")
        return

    answer = generate_grounded_answer(question, evidence)

    st.subheader("Answer")
    st.markdown(answer["answer"])

    if answer.get("citations"):
        st.markdown("**Sources**")
        st.markdown(format_citation_list(answer["citations"]))

    with st.expander("Source cards and evidence"):
        render_source_cards(evidence)


def render_comparison():
    paper_contexts = st.session_state.get("multi_papers", [])
    if not paper_contexts:
        st.info("Upload more than one PDF to compare them.")
        return

    st.subheader("Lightweight Comparison Dashboard")
    comparison_question = st.text_input("Comparison question", value="What dataset was used?", key="comparison_question")
    if st.button("Compare") and comparison_question.strip():
        with st.spinner("Comparing papers..."):
            rows = build_comparison_dashboard(paper_contexts, comparison_question.strip())
        if not rows:
            st.warning("No comparison evidence was found across the uploaded papers.")
            return

        st.markdown(build_comparison_summary(rows))

        for row in rows:
            with st.container():
                st.markdown(
                    f"### {row['Paper']}\n"
                    f"**Section:** {row['Section']} | **Page:** {row['Page']}\n\n"
                    f"{row['Evidence']}"
                )
                st.markdown("---")

        st.table(rows)


def render_section_summary():
    context = st.session_state.paper_context
    if not context:
        st.info("Upload a PDF to summarize a section.")
        return

    st.subheader("Section Summary")
    section_name = st.selectbox("Select section", ["Methods", "Results", "Discussion", "Conclusion", "Limitations"])
    if st.button("Summarize Section"):
        evidence = retrieve_evidence(context["vector_store"], section_name, k=4)
        if not evidence:
            st.warning("No matching section evidence was found.")
            return

        summary = generate_section_summary_for_question(section_name, evidence)
        st.markdown(summary)


def main():
    st.set_page_config(page_title="Medical Literature Assistant", layout="wide")
    ensure_session_state()
    st.title("Medical Literature Assistant")

    with st.sidebar:
        st.header("Research")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file is not None:
            process_pdf(uploaded_file)

        multi_files = st.file_uploader("Upload papers for comparison", type=["pdf"], accept_multiple_files=True)
        if multi_files:
            paper_contexts = []
            for uploaded in multi_files:
                context = process_pdf(uploaded)
                if context:
                    paper_contexts.append(context)
            st.session_state.multi_papers = paper_contexts

        st.markdown("---")
        st.caption("Local LLM")
        st.caption(f"Ollama: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
        st.caption(f"Model: {os.getenv('OLLAMA_MODEL', 'llama3.2')}")

    render_current_paper()

    st.markdown("---")
    mode_options = ["General", "Methods", "Results", "Limitations"]
    selected_mode = st.radio("Question mode", mode_options, horizontal=True)
    default_question_map = {
        "General": "What dataset was used in this study?",
        "Methods": "What methods were used in this study?",
        "Results": "What were the main results or findings?",
        "Limitations": "What are the limitations of this study?",
    }
    question = st.text_area(
        "Ask a question about the paper",
        height=120,
        value=default_question_map[selected_mode],
        placeholder="Example: What dataset was used in this study?",
    )

    if st.button("Ask") and question.strip():
        render_answer(question.strip(), mode=selected_mode)

    st.markdown("---")
    render_section_summary()
    st.markdown("---")
    render_comparison()
    st.markdown("---")
    render_pubmed_search()


if __name__ == "__main__":
    main()
