"""Transparent market indicators and simple walk-forward research signals."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean, pstdev
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ResearchSignal:
    as_of: str
    direction: str
    probability_up: float
    expected_daily_return: float
    uncertainty_95: tuple[float, float]
    observations: int
    warning: str = "Research only; not financial advice or an autonomous trade."


def fetch_yahoo_history(destination: Path, symbol: str = "VEDL.NS", months: int = 12) -> dict:
    if symbol != "VEDL.NS":
        raise ValueError("This release is intentionally restricted to Vedanta (VEDL.NS)")
    if not 1 <= months <= 60:
        raise ValueError("Months must be between 1 and 60")
    url = (
        f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?range={months}mo&interval=1d&events=history"
    )
    request = Request(url, headers={"User-Agent": "LocalAssistResearchSuite/0.1"})
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Market source returned HTTP {exc.code}; try again later") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not retrieve market data: {exc}") from exc
    try:
        result = payload["chart"]["result"][0]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Market source returned an unexpected response") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = ("Open", "High", "Low", "Close", "Volume")
    keys = tuple(field.lower() for field in fields)
    written = 0
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("Date", *fields))
        for index, timestamp in enumerate(timestamps):
            values = [quote[key][index] for key in keys]
            if values[3] is None:
                continue
            day = datetime.fromtimestamp(timestamp, UTC).date().isoformat()
            writer.writerow((day, *values))
            written += 1
    if written < 21:
        destination.unlink(missing_ok=True)
        raise RuntimeError("Market source returned fewer than 21 usable observations")
    return {
        "symbol": symbol,
        "currency": result["meta"].get("currency"),
        "rows": written,
        "destination": str(destination),
        "source": "Yahoo Finance chart endpoint",
        "retrieved_at": datetime.now(UTC).isoformat(),
    }


def read_closes(path: Path) -> tuple[list[str], list[float]]:
    dates, closes = [], []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            dates.append(row["Date"])
            closes.append(float(row["Close"]))
    if len(closes) < 21:
        raise ValueError("At least 21 daily close observations are required")
    return dates, closes


def analyze_csv(path: Path) -> ResearchSignal:
    dates, closes = read_closes(path)
    returns = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    recent = returns[-20:]
    momentum = closes[-1] / closes[-6] - 1
    expected = 0.5 * mean(recent) + 0.5 * momentum / 5
    volatility = pstdev(recent) or 1e-9
    z_score = expected / (volatility / math.sqrt(len(recent)))
    probability_up = 1 / (1 + math.exp(-max(-8.0, min(8.0, z_score))))
    half_width = 1.96 * volatility
    return ResearchSignal(
        as_of=dates[-1],
        direction="UP" if probability_up >= 0.5 else "DOWN",
        probability_up=round(probability_up, 4),
        expected_daily_return=round(expected, 6),
        uncertainty_95=(round(expected - half_width, 6), round(expected + half_width, 6)),
        observations=len(closes),
    )
