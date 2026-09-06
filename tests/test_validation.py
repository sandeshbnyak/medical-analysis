from src.validator import validate_answer


def test_validate_answer_rejects_unrelated_claim():
    evidence = [{
        "text": "The study used 10,000 synthetic patient records.",
        "section": "Methods",
        "page": 6,
    }]

    assert validate_answer("Random Forest", evidence) is False
    assert validate_answer("10,000 synthetic patient records", evidence) is True
