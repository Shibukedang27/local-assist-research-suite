"""Accuracy and safety gates around the from-scratch neural model."""

from __future__ import annotations

import re
from pathlib import Path

from .scratch_model import ScratchTransformer, generate, load_model

LIVE_TERMS = ("live", "proctored", "active hiring", "recruitment test", "graded exam")
TRADE_TERMS = (
    "buy shares",
    "sell shares",
    "place a trade",
    "automatically",
    "guarantee",
    "promise",
)
JOB_TERMS = ("job application", "apply for", "submit my application")


def exact_math(prompt: str) -> str | None:
    lowered = prompt.lower().replace(",", "")
    match = re.search(r"(?:from|is)\s+(\d+(?:\.\d+)?)\s+(?:by\s+)?(\d+(?:\.\d+)?)%", lowered)
    if match and any(term in lowered for term in ("rise", "rises", "increase", "increases")):
        original, percentage = map(float, match.groups())
        increase = original * percentage / 100
        return (
            f"The increase is {original:g} × {percentage:g}/100 = {increase:g}. "
            f"The new value is {original + increase:g}."
        )
    match = re.search(r"(\d+(?:\.\d+)?)\s+(?:divided by|÷)\s+(\d+(?:\.\d+)?)", lowered)
    if match:
        numerator, denominator = map(float, match.groups())
        if denominator == 0:
            return "Division by zero is undefined."
        return f"{numerator:g} ÷ {denominator:g} = {numerator / denominator:g}."
    return None


def answer(model: ScratchTransformer, prompt: str) -> dict:
    lowered = prompt.lower()
    if any(term in lowered for term in LIVE_TERMS) and any(
        term in lowered for term in ("exam", "assessment", "hiring", "test")
    ):
        response, route = (
            (
                "I cannot complete a live, graded, proctored, or recruitment assessment. "
                "I can create and explain a similar practice problem."
            ),
            "assessment-policy",
        )
    elif "vedanta" in lowered and any(term in lowered for term in TRADE_TERMS):
        response, route = (
            (
                "I cannot guarantee Vedanta's direction or place an automatic trade. Predictions are "
                "uncertain; use probabilities and uncertainty intervals. No broker action was performed."
            ),
            "trading-policy",
        )
    elif any(term in lowered for term in JOB_TERMS):
        response, route = (
            (
                "I will use only verified facts and placeholders for unknowns. Provide a private candidate "
                "profile and full job description. You must review and perform final submission yourself. "
                "Nothing was submitted."
            ),
            "job-policy",
        )
    elif solved := exact_math(prompt):
        response, route = solved, "exact-math"
    else:
        response = generate(model, f"<user>{prompt}</user><assistant>")
        route = "scratch-transformer"
    return {
        "answer": response,
        "route": route,
        "model": "local-assist-tiny-from-scratch",
        "pretrained_weights": False,
        "runs_on_device": True,
    }


def load_default(path: Path = Path("artifacts/local-assist-tiny")) -> ScratchTransformer:
    if not path.exists():
        raise RuntimeError("From-scratch checkpoint is missing; run scripts/train_scratch_model.py")
    return load_model(path)
