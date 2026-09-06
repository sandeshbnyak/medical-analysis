def safe_text(value):
    if value is None:
        return ""
    return str(value).strip()
