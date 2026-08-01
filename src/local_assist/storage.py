"""Compact columnar conversion helpers."""

from __future__ import annotations

from pathlib import Path


def to_parquet(source: Path, destination: Path) -> None:
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("Install the data extra: pip install -e '.[data]'") from exc
    suffix = source.suffix.lower()
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with duckdb.connect() as connection:
            if suffix == ".csv":
                relation = connection.read_csv(str(source))
            elif suffix in {".json", ".jsonl", ".ndjson"}:
                relation = connection.read_json(str(source))
            else:
                raise ValueError("Source must be CSV, JSON, JSONL, or NDJSON")
            relation.write_parquet(str(destination), compression="zstd")
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Conversion failed: {exc}") from exc
