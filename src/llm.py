import os
import re

import requests

from src.summary import generate_section_summary
from src.validator import validate_answer


def call_ollama(prompt, model=None, base_url=None):
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    url = f"{base_url.rstrip('/')}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }

    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def validate_answer(answer, evidence):
    """A light-weight evidence validator: reject answers that do not appear in the evidence."""
    lower_answer = answer.lower()
    if not lower_answer:
        return False

    for item in evidence:
        text = item.get("text", "")
        if re.search(re.escape(lower_answer), text.lower()):
            return True
    return False


def fallback_answer(question, evidence):
    """Generate a concise answer directly from the most relevant piece of evidence."""
    if not evidence:
        return "The provided evidence does not contain this information."

    best = evidence[0]
    text = best.get("text", "")
    cleaned = text.strip()
    if not cleaned:
        return "The provided evidence does not contain this information."

    if any(word in question.lower() for word in ["how many", "what dataset", "dataset", "number", "count"]):
        match = re.search(r"(\d[\d,\s]*\.?\d*)", cleaned)
        if match:
            return f"The evidence indicates {match.group(1).strip()}. [1]"

    return f"Based on the evidence, the relevant finding is: {cleaned} [1]"


def generate_grounded_answer(question, evidence, model=None, base_url=None):
    evidence_text = "\n\n".join(
        [
            f"[Evidence {idx + 1}]\nSection: {item['section']}\nPage: {item['page']}\n{item['text']}"
            for idx, item in enumerate(evidence)
        ]
    )

    prompt = f"""
    You are a careful evidence-grounded assistant.
    Answer using only the provided evidence.
    If the answer is not present in the evidence, say:
    "The provided evidence does not contain this information."

    Question:
    {question}

    Evidence:
    {evidence_text}

    Respond with a concise answer and include inline citations like [1], [2].
    Keep the answer grounded to the provided evidence.
    """

    citations = [
        {
            "index": idx + 1,
            "section": item["section"],
            "page": item["page"],
            "text": item["text"],
        }
        for idx, item in enumerate(evidence)
    ]

    try:
        answer_text = call_ollama(prompt, model=model, base_url=base_url)
    except Exception:
        answer_text = fallback_answer(question, evidence)

    cleaned_text = answer_text.replace("[1]", "").replace("[2]", "").replace("[3]", "").strip()
    if not validate_answer(cleaned_text, evidence):
        answer_text = fallback_answer(question, evidence)

    return {
        "answer": answer_text,
        "citations": citations,
    }


def generate_section_summary_for_question(section_name, evidence):
    return generate_section_summary(section_name, evidence)
