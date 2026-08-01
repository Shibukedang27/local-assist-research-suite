import pytest

from local_assist.practice import UnsafeAssessmentError, ensure_practice_context, load_item


def test_refuses_live_recruitment_assessment():
    with pytest.raises(UnsafeAssessmentError):
        ensure_practice_context("This is a live recruitment test")


def test_loads_practice_item():
    item = load_item(
        {
            "context": "practice",
            "prompt": "1+1?",
            "options": ["2"],
            "answer": "2",
            "explanation": "addition",
        }
    )
    assert item.answer == "2"
