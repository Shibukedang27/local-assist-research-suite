"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
from dataclasses import asdict
from pathlib import Path

from .jobs import score_job
from .practice import UnsafeAssessmentError, load_item
from .stocks import analyze_csv
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
    practice = commands.add_parser("practice", help="show a practice item and explanation")
    practice.add_argument("question", type=Path)
    stock = commands.add_parser("stock-analyze", help="analyze a local OHLCV CSV")
    stock.add_argument("csv", type=Path)
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
            emit(asdict(score_job(profile, args.job.read_text(encoding="utf-8"))))
        elif args.command == "practice":
            emit(asdict(load_item(json.loads(args.question.read_text(encoding="utf-8")))))
        elif args.command == "stock-analyze":
            emit(asdict(analyze_csv(args.csv)))
        elif args.command == "convert":
            to_parquet(args.source, args.destination)
            emit({"created": str(args.destination), "format": "Parquet/Zstd"})
        return 0
    except (ValueError, RuntimeError, UnsafeAssessmentError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
