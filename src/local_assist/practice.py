"""Practice-only question presentation with assessment safeguards."""

from __future__ import annotations

from dataclasses import dataclass

LIVE_MARKERS = {
    "live": "live assessment",
    "proctored": "proctored assessment",
    "recruitment test": "recruitment assessment",
    "graded": "graded assessment",
    "exam in progress": "active exam",
}


class UnsafeAssessmentError(ValueError):
    pass


@dataclass(frozen=True)
class PracticeItem:
    prompt: str
    options: tuple[str, ...]
    answer: str
    explanation: str


def ensure_practice_context(context: str) -> None:
    lowered = context.lower()
    for marker, label in LIVE_MARKERS.items():
        if marker in lowered:
            raise UnsafeAssessmentError(
                f"Refusing {label}. This tool supports self-study and accessibility practice only."
            )


def load_item(data: dict) -> PracticeItem:
    ensure_practice_context(str(data.get("context", "practice")))
    required = ("prompt", "options", "answer", "explanation")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Missing practice fields: {', '.join(missing)}")
    return PracticeItem(
        prompt=str(data["prompt"]),
        options=tuple(map(str, data["options"])),
        answer=str(data["answer"]),
        explanation=str(data["explanation"]),
    )
