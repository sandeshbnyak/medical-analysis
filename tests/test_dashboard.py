from src.summary import build_abstract_overview


def test_abstract_overview_works_with_sections():
    chunks = [
        {"section": "Abstract", "text": "The study used 10,000 synthetic patient records and evaluated a new model."},
        {"section": "Methods", "text": "We used synthetic patient records in a prospective study."},
    ]
    overview = build_abstract_overview(chunks)
    assert "10,000" in overview
    assert "synthetic" in overview.lower()
