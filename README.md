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

Create a local job-review entry (the approval command records consent but never submits):

```sh
.venv/bin/local-assist jobs-score examples/candidate.example.json examples/job.example.txt \
  --review-db data/private/reviews.sqlite3
.venv/bin/local-assist jobs-approve 1
```

Retrieve and analyze recent Vedanta daily data:

```sh
.venv/bin/local-assist stock-fetch --months 12
.venv/bin/local-assist stock-analyze data/raw/vedanta.csv
```

The downloader uses Yahoo Finance's chart endpoint without credentials. Availability is not guaranteed; source outages and rate limits are reported rather than silently replaced with invented data.

## Legacy adapted model (not from scratch)

The earlier Ollama workflow adapts `qwen2.5:3b` and therefore does **not** meet the from-scratch definition. It is retained only for reproducibility and is not the default launcher. The default is `Local Assist Tiny` below.

To reproduce the older adapted experiment:

```sh
ollama create local-assist-ai -f Modelfile
.venv/bin/python scripts/generate_private_dataset.py --count 600
.venv/bin/local-assist convert data/private/practice.jsonl data/processed/practice.parquet
.venv/bin/local-assist knowledge-build \
  data/private/practice.jsonl SAFETY.md docs/ARCHITECTURE.md
.venv/bin/local-assist ask --workflow practice "Teach me a percentage shortcut"
```

The legacy session command is:

```sh
.venv/bin/local-assist chat
```

The generated dataset uses a fixed seed and is synthetic, so it carries no copied question-bank or personal data. Parquet is the compact binary/columnar copy; the SQLite FTS index supports fast local retrieval. The model and both stores remain on the Mac.

Run the local behavioral benchmark:

```sh
.venv/bin/python scripts/evaluate_local_ai.py
```

The benchmark checks a small set of essential boundaries and publishes its responses for inspection. It is a smoke test, not evidence that every future answer will be correct.

## From-scratch default model

`Local Assist Tiny` uses a transformer and byte tokenizer implemented in this repository. Its weights begin random and are trained locally; it imports no pretrained checkpoint.

```sh
.venv/bin/python -m pip install -e '.[scratch]'
.venv/bin/python scripts/generate_scratch_corpus.py --count 18000
.venv/bin/python scripts/train_scratch_model.py --steps 1500
.venv/bin/python scripts/run_scratch_model.py "Explain 84 divided by 2 as practice."
.venv/bin/python scripts/chat_scratch_model.py
```

This small experiment can learn narrow patterns but cannot match a foundation model trained on billions of tokens. The deterministic policy gates remain authoritative for job submission, active assessments, and trading.

Double-click `launch_local_ai.command` in Finder to start this from-scratch model. Training outputs remain local under `artifacts/`; compact metrics and acceptance results are published under `benchmarks/`.

See [SAFETY.md](SAFETY.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [STATUS.md](STATUS.md).

## Data representation

Operational events use SQLite. Larger tabular datasets can be converted to compressed Parquet through DuckDB. This is compact typed columnar storage—not literal strings of `0` and `1`—and is appropriate for analytics on limited hardware.

## License

Apache-2.0. See [LICENSE](LICENSE).
