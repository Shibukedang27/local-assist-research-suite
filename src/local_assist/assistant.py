"""Ollama-backed local assistant with scoped retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .knowledge import retrieve
from .practice import ensure_practice_context


def ask_local_ai(
    prompt: str,
    context_kind: str = "general",
    database: Path = Path("data/private/knowledge.sqlite3"),
    model: str = "local-assist-ai",
) -> dict:
    if context_kind == "assessment":
        ensure_practice_context(prompt)
    matches = retrieve(database, prompt)
    context = "\n\n".join(f"[{item['topic']}] {item['content']}" for item in matches)
    grounded_prompt = (
        f"USER WORKFLOW: {context_kind}\n"
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
