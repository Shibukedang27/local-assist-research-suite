"""Local review ledger; approval is not external submission."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS job_reviews (
    id INTEGER PRIMARY KEY,
    fingerprint TEXT NOT NULL UNIQUE,
    job_source TEXT NOT NULL,
    draft TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'approved')),
    created_at TEXT NOT NULL,
    approved_at TEXT
)
"""


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute(SCHEMA)
    return connection


def create_review(path: Path, job_source: str, draft: str) -> dict:
    fingerprint = hashlib.sha256(f"{job_source}\0{draft}".encode()).hexdigest()[:16]
    now = datetime.now(UTC).isoformat()
    with _connect(path) as connection:
        connection.execute(
            "INSERT OR IGNORE INTO job_reviews "
            "(fingerprint, job_source, draft, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
            (fingerprint, job_source, draft, now),
        )
        row = connection.execute(
            "SELECT id, fingerprint, status, created_at, approved_at FROM job_reviews "
            "WHERE fingerprint = ?",
            (fingerprint,),
        ).fetchone()
    return dict(zip(("id", "fingerprint", "status", "created_at", "approved_at"), row))


def approve_review(path: Path, review_id: int) -> dict:
    now = datetime.now(UTC).isoformat()
    with _connect(path) as connection:
        cursor = connection.execute(
            "UPDATE job_reviews SET status = 'approved', approved_at = ? "
            "WHERE id = ? AND status = 'pending'",
            (now, review_id),
        )
        if cursor.rowcount != 1:
            raise ValueError("Pending review not found")
        row = connection.execute(
            "SELECT id, fingerprint, status, approved_at FROM job_reviews WHERE id = ?",
            (review_id,),
        ).fetchone()
    result = dict(zip(("id", "fingerprint", "status", "approved_at"), row))
    result["submission_performed"] = False
    return result
