"""Transparent market indicators and simple walk-forward research signals."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev


@dataclass(frozen=True)
class ResearchSignal:
    as_of: str
    direction: str
    probability_up: float
    expected_daily_return: float
    uncertainty_95: tuple[float, float]
    observations: int
    warning: str = "Research only; not financial advice or an autonomous trade."


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
