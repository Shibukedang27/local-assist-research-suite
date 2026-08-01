# Local Assist Research Suite

A local-first, user-owned toolkit for three intentionally limited workflows:

1. **Job applications** — compare a local candidate profile with a job description and create reviewable application drafts. Final submission always remains a human action.
2. **Aptitude and reasoning practice** — run practice questions with explanations and accessible text output. It is not designed to complete live graded or recruitment assessments.
3. **Vedanta research** — calculate transparent indicators and walk-forward predictions from market data. Outputs are uncertain research signals, not financial advice or autonomous trades.

The project is sized for an Apple M2 Mac with 8 GB RAM. Personal profiles, resumes, cookies, credentials, raw datasets, generated databases, and model artifacts are ignored by Git.

## Quick start

Requires Python 3.11 or newer.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,data]'
.venv/bin/local-assist doctor
.venv/bin/pytest
```

Use synthetic examples only:

```sh
.venv/bin/local-assist jobs-score examples/candidate.example.json examples/job.example.txt
.venv/bin/local-assist practice examples/practice.example.json
.venv/bin/local-assist stock-analyze examples/vedanta.synthetic.csv
```

See [SAFETY.md](SAFETY.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [STATUS.md](STATUS.md).

## Data representation

Operational events use SQLite. Larger tabular datasets can be converted to compressed Parquet through DuckDB. This is compact typed columnar storage—not literal strings of `0` and `1`—and is appropriate for analytics on limited hardware.

## License

Apache-2.0. See [LICENSE](LICENSE).

