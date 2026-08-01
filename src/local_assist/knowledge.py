"""Private local knowledge ingestion and lightweight retrieval."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

WORD = re.compile(r"[a-zA-Z0-9+#.]{2,}")
SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge USING fts5(
    source UNINDEXED,
    topic,
    content,
    tokenize='porter unicode61'
)
"""


def build_index(database: Path, sources: list[Path]) -> dict:
    database.parent.mkdir(parents=True, exist_ok=True)
    inserted = 0
    with sqlite3.connect(database) as connection:
        connection.execute(SCHEMA)
        connection.execute("DELETE FROM knowledge")
        for source in sources:
            if source.suffix.lower() in {".jsonl", ".ndjson"}:
                records = [
                    json.loads(line) for line in source.read_text().splitlines() if line.strip()
                ]
            elif source.suffix.lower() == ".json":
                payload = json.loads(source.read_text())
                records = payload if isinstance(payload, list) else [payload]
            else:
                records = [{"topic": source.stem, "content": source.read_text(encoding="utf-8")}]
            for record in records:
                content = str(record.get("content") or record.get("explanation") or record)
                topic = str(record.get("topic", source.stem))
                connection.execute(
                    "INSERT INTO knowledge(source, topic, content) VALUES (?, ?, ?)",
                    (str(source), topic, content),
                )
                inserted += 1
    return {"database": str(database), "documents": inserted, "sources": len(sources)}


def retrieve(database: Path, query: str, limit: int = 5) -> list[dict]:
    terms = [term for term in WORD.findall(query.lower()) if len(term) > 2][:12]
    if not terms or not database.exists():
        return []
    expression = " OR ".join(f'"{term}"' for term in terms)
    with sqlite3.connect(database) as connection:
        rows = connection.execute(
            "SELECT source, topic, content, bm25(knowledge) AS score FROM knowledge "
            "WHERE knowledge MATCH ? ORDER BY score LIMIT ?",
            (expression, limit),
        ).fetchall()
    return [dict(zip(("source", "topic", "content", "score"), row)) for row in rows]
