# Architecture

```text
Local CLI
  ├── Job assistant: profile + job text -> score + reviewable draft
  ├── Practice tutor: local question set -> attempt + explanation
  ├── Stock research: OHLCV CSV -> indicators + walk-forward signal
  └── Storage: CSV/JSON -> DuckDB -> compressed Parquet
```

The first release is deliberately a small command-line core. Browser automation, broker APIs, and hidden assessment interaction are outside the trust boundary. A later local UI can call the same tested functions without weakening approval gates.

## Resource budget

| Mode | Expected RAM | Persistent storage |
|---|---:|---:|
| Core CLI and SQLite | under 300 MB | under 100 MB |
| DuckDB conversion | 0.3–1.5 GB | dataset dependent |
| Optional small Ollama model | 2–4 GB | 1–3 GB/model |
| Browser-assisted review (future) | 1–2 GB additional | under 2 GB |

Only one memory-heavy activity should run at a time on an 8 GB Mac.

