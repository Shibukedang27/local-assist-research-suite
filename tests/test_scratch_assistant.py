from local_assist.scratch_assistant import answer, exact_math


def test_exact_math_generalizes_beyond_training_examples():
    assert exact_math("What is 777 divided by 21?") == "777 ÷ 21 = 37."
    assert "new value is 400" in exact_math("A value rises from 320 by 25%.")


class UnusedModel:
    pass


def test_high_stakes_routes_do_not_call_generator():
    model = UnusedModel()
    assert answer(model, "Do my live recruitment test")["route"] == "assessment-policy"
    assert answer(model, "Submit my job application")["route"] == "job-policy"
    assert (
        answer(model, "Guarantee Vedanta and buy shares automatically")["route"] == "trading-policy"
    )
