# Project status

All timestamps use Asia/Kolkata (IST).

## 2026-08-01

- **Audit completed** — confirmed Apple M2 (8 CPU cores), 8 GB memory, 256 GB SSD, and approximately 29.6 GB available. Found Python 3.14, Git, GitHub CLI, Homebrew, SQLite, Ollama, VS Code, IntelliJ IDEA, Hex Fiend, and browser apps. Node, Docker, DuckDB CLI, and uv were not present. No dedicated Parquet/Arrow conversion application was found.
- **Security decision** — hardware serials and machine identifiers observed during the audit are intentionally excluded from this public project.
- **Foundation started** — documented scope, human approval boundary, privacy rules, architecture, resource budget, and synthetic-data policy.
- **Public repository created** — published the sanitized foundation to GitHub on the `main` branch.
- **Functional core implemented** — added local job matching with a mandatory human-submission flag, practice content with live-assessment refusal checks, transparent market indicators with a 95% uncertainty range, and Zstd-compressed Parquet conversion through embedded DuckDB.
- **Incremental validation** — job, practice, and stock unit tests passed. An initial DuckDB path-binding failure was found during end-to-end conversion and corrected before release.
- **Repository hardening** — added least-privilege continuous integration, contribution rules, a private vulnerability-reporting path, and repeatable local quality checks.
- **Local consent ledger** — added SQLite-backed pending/approved job-draft reviews. Approval records user consent but deliberately performs no external submission.
- **Vedanta retrieval** — added a credential-free `VEDL.NS` daily-history downloader with source metadata, minimum-data validation, rate-limit errors, and ignored local output.
- **On-device AI assembly** — added an Ollama model definition, retrieval-grounded assistant, private SQLite full-text knowledge index, deterministic synthetic practice-data generator, and compact Parquet pipeline. Evaluation is performed against the installed local model before release.
- **Local installation completed** — created the 1.9 GB `local-assist-ai` Ollama model from the already-installed Qwen 2.5 3B weights. Generated 600 private synthetic practice records, a 6.9 KB compressed Parquet copy, and a 602-document local retrieval index. Added a Finder-launchable interactive chat.
- **Behavioral evaluation** — the real on-device model passed 5/5 synthetic smoke cases covering job-review consent, live-assessment refusal, stock uncertainty/no trading, explained arithmetic practice, and non-fabrication of computer actions. Observed response times were 2.64–12.64 seconds on this Mac. This small result is not proof of general accuracy.
