from local_assist.assistant import WORKFLOW_RULES, ask_local_ai


def test_job_rule_forbids_invented_personal_facts():
    rule = WORKFLOW_RULES["jobs"].lower()
    assert "never invent" in rule
    assert "square-bracket placeholders" in rule
    assert "final submission" in rule


def test_job_chat_uses_deterministic_policy_gate():
    result = ask_local_ai("Invent an impressive degree for me", context_kind="jobs")
    assert "will not draft" in result["answer"]
    assert "Nothing has been submitted" in result["answer"]
    assert result["elapsed_seconds"] == 0.0


def test_guaranteed_trade_request_uses_deterministic_policy_gate():
    result = ask_local_ai("Guarantee Vedanta will rise and place the trade", context_kind="stocks")
    assert "cannot guarantee" in result["answer"]
    assert "No broker action was performed" in result["answer"]
    assert "95% uncertainty interval" in result["answer"]
