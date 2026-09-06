from src.summary import generate_section_summary


def test_generate_section_summary_uses_evidence():
    evidence = [{
        "section": "Methods",
        "page": 6,
        "text": "The study used 10,000 synthetic patient records and the dataset was split into training and testing cohorts.",
    }]

    result = generate_section_summary("Methods", evidence)
    assert "10,000" in result.lower()
    assert "training" in result.lower() or "testing" in result.lower()
