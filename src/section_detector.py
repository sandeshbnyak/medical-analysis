import re

SECTION_KEYWORDS = {
    "abstract": ["abstract"],
    "introduction": ["introduction"],
    "methods": ["methods", "materials and methods", "experimental design", "study design"],
    "results": ["results"],
    "discussion": ["discussion"],
    "conclusion": ["conclusion", "conclusions"],
    "limitations": ["limitations", "limitations of the study"],
    "references": ["references", "bibliography"],
}


def detect_section_name(text):
    if not text:
        return "Body"

    normalized = text.strip().lower()
    for section, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", normalized):
                return section.title()

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:10]:
        small = line.lower()
        if small.startswith("abstract"):
            return "Abstract"
        if small.startswith("introduction"):
            return "Introduction"
        if small.startswith("methods"):
            return "Methods"
        if small.startswith("results"):
            return "Results"
        if small.startswith("discussion"):
            return "Discussion"
        if small.startswith("conclusion"):
            return "Conclusion"
        if small.startswith("limitations"):
            return "Limitations"
        if small.startswith("references"):
            return "References"

    return "Body"
