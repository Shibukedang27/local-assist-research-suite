"""Ollama-backed local assistant with scoped retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .knowledge import retrieve
from .practice import ensure_practice_context

WORKFLOW_RULES = {
    "jobs": (
        "Write application prose, not software code. Never invent a name, contact detail, employer, "
        "degree, year, skill, or achievement. Use explicit square-bracket placeholders for every "
        "unknown fact. Mention only facts present in the request or local context. End by requiring "
        "the user to verify all facts and perform final submission."
    ),
    "practice": "Teach step by step and give the answer for self-study practice.",
    "assessment": "Only support practice; never answer an active graded or recruitment assessment.",
    "stocks": (
        "Separate observations from estimates, state uncertainty, and never claim to place a trade."
    ),
    "general": "Do not invent personal facts or claim unconfirmed computer actions.",
}


def ask_local_ai(
    prompt: str,
    context_kind: str = "general",
    database: Path = Path("data/private/knowledge.sqlite3"),
    model: str = "local-assist-ai",
) -> dict:
    if context_kind == "jobs":
        return {
            "model": "local-assist-ai + deterministic job policy gate",
            "answer": (
                "I will not draft from an unstructured message because that can invent qualifications. "
                "Save your verified facts in a private candidate JSON file and the complete job "
                "description in a text file, then run: local-assist jobs-score "
                "<candidate.json> <job.txt> --review-db data/private/reviews.sqlite3. "
                "The result will use supplied facts, require your review, and leave final submission "
                "to you. Nothing has been submitted."
            ),
            "context_documents": 0,
            "elapsed_seconds": 0.0,
            "runs_on_device": True,
        }
    if context_kind == "stocks" and any(
        phrase in prompt.lower()
        for phrase in (
            "guarantee",
            "guaranteed",
            "place the trade",
            "buy it for me",
            "sell it for me",
        )
    ):
        return {
            "model": "local-assist-ai + deterministic trading policy gate",
            "answer": (
                "I cannot guarantee Vedanta's direction or place a trade. Market predictions are "
                "uncertain and can lose money. I can retrieve historical VEDL.NS data and report a "
                "research signal with its probability and 95% uncertainty interval; you must make "
                "any investment decision yourself. No broker action was performed."
            ),
            "context_documents": 0,
            "elapsed_seconds": 0.0,
            "runs_on_device": True,
        }
    if context_kind == "assessment":
        ensure_practice_context(prompt)
    matches = retrieve(database, prompt)
    context = "\n\n".join(f"[{item['topic']}] {item['content']}" for item in matches)
    grounded_prompt = (
        f"USER WORKFLOW: {context_kind}\n"
        f"MANDATORY WORKFLOW RULE: {WORKFLOW_RULES[context_kind]}\n"
        f"LOCAL CONTEXT:\n{context or '[no matching local context]'}\n\n"
        f"REQUEST:\n{prompt}\n\n"
        "Answer only within the configured scope. Clearly label uncertainty and required human actions."
    )
    body = json.dumps(
        {"model": model, "prompt": grounded_prompt, "stream": False, "keep_alive": "5m"}
    ).encode()
    request = Request(
        "http://127.0.0.1:11434/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=180) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Ollama returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Ollama is unavailable; open Ollama and retry") from exc
    return {
        "model": result.get("model", model),
        "answer": result.get("response", "").strip(),
        "context_documents": len(matches),
        "elapsed_seconds": round(result.get("total_duration", 0) / 1_000_000_000, 2),
        "runs_on_device": True,
    }
