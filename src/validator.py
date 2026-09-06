import re


def validate_answer(answer, evidence):
    if not answer or not evidence:
        return False

    answer_text = answer.strip()
    if not answer_text:
        return False

    for item in evidence:
        text = (item.get("text") or "").lower()
        normalized_answer = answer_text.lower()
        if normalized_answer in text:
            return True
        if re.search(re.escape(normalized_answer), text):
            return True
        if len(normalized_answer.split()) <= 4 and any(token in text for token in normalized_answer.split()):
            return True

    return False
