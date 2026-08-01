"""Local-only job matching and draft generation."""

from __future__ import annotations

import re
from dataclasses import dataclass

TOKEN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}")
STOP_WORDS = {
    "and",
    "are",
    "for",
    "from",
    "have",
    "job",
    "our",
    "the",
    "this",
    "to",
    "with",
    "will",
    "you",
    "your",
    "years",
    "role",
    "work",
    "team",
    "that",
    "we",
    "a",
    "an",
}


def keywords(text: str) -> set[str]:
    return {word.lower() for word in TOKEN.findall(text) if word.lower() not in STOP_WORDS}


@dataclass(frozen=True)
class MatchResult:
    score: int
    matched: tuple[str, ...]
    missing: tuple[str, ...]
    draft: str
    requires_human_submission: bool = True


def score_job(profile: dict, job_text: str) -> MatchResult:
    candidate_text = " ".join(
        str(value) if not isinstance(value, list) else " ".join(map(str, value))
        for value in profile.values()
    )
    candidate = keywords(candidate_text)
    requested = keywords(job_text)
    matched = sorted(candidate & requested)
    missing = sorted(requested - candidate)
    score = round(100 * len(matched) / max(1, len(requested)))
    name = profile.get("display_name", "Candidate")
    top_matches = ", ".join(matched[:8]) or "transferable skills"
    draft = (
        f"Application draft for {name}\n\n"
        f"I am interested in this opportunity. My relevant background includes {top_matches}. "
        "I would welcome a conversation about how my experience aligns with the role.\n\n"
        "REVIEW REQUIRED: Verify every statement and submit the application yourself."
    )
    return MatchResult(score, tuple(matched), tuple(missing[:20]), draft)
