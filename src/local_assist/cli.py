"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
from dataclasses import asdict
from pathlib import Path

from .approvals import approve_review, create_review
from .jobs import score_job
from .practice import UnsafeAssessmentError, load_item
from .stocks import analyze_csv, fetch_yahoo_history
from .storage import to_parquet


def emit(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(prog="local-assist")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="check the lightweight local runtime")
    jobs = commands.add_parser("jobs-score", help="score a job and write a reviewable draft")
    jobs.add_argument("profile", type=Path)
    jobs.add_argument("job", type=Path)
    jobs.add_argument("--review-db", type=Path)
    approve = commands.add_parser("jobs-approve", help="approve a local draft without submitting")
    approve.add_argument("review_id", type=int)
    approve.add_argument("--review-db", type=Path, default=Path("data/private/reviews.sqlite3"))
    practice = commands.add_parser("practice", help="show a practice item and explanation")
    practice.add_argument("question", type=Path)
    stock = commands.add_parser("stock-analyze", help="analyze a local OHLCV CSV")
    stock.add_argument("csv", type=Path)
    fetch = commands.add_parser("stock-fetch", help="download Vedanta daily history locally")
    fetch.add_argument("--months", type=int, default=12)
    fetch.add_argument("--output", type=Path, default=Path("data/raw/vedanta.csv"))
    convert = commands.add_parser("convert", help="convert tabular input to Zstd Parquet")
    convert.add_argument("source", type=Path)
    convert.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            emit(
                {
                    "python": platform.python_version(),
                    "ollama": bool(shutil.which("ollama")),
                    "git": bool(shutil.which("git")),
                    "privacy_mode": "local-first",
                }
            )
        elif args.command == "jobs-score":
            profile = json.loads(args.profile.read_text(encoding="utf-8"))
            result = score_job(profile, args.job.read_text(encoding="utf-8"))
            output = asdict(result)
            if args.review_db:
                output["review"] = create_review(args.review_db, str(args.job), result.draft)
            emit(output)
        elif args.command == "jobs-approve":
            emit(approve_review(args.review_db, args.review_id))
        elif args.command == "practice":
            emit(asdict(load_item(json.loads(args.question.read_text(encoding="utf-8")))))
        elif args.command == "stock-analyze":
            emit(asdict(analyze_csv(args.csv)))
        elif args.command == "stock-fetch":
            emit(fetch_yahoo_history(args.output, months=args.months))
        elif args.command == "convert":
            to_parquet(args.source, args.destination)
            emit({"created": str(args.destination), "format": "Parquet/Zstd"})
        return 0
    except (ValueError, RuntimeError, UnsafeAssessmentError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
