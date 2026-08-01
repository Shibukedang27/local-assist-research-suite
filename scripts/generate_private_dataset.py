"""Generate license-safe synthetic practice/training context locally."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


def generate(destination: Path, count: int, seed: int = 20260801) -> None:
    random.seed(seed)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for index in range(count):
            left, right = random.randint(2, 150), random.randint(2, 40)
            operation = index % 3
            if operation == 0:
                prompt, answer = f"What is {left} + {right}?", left + right
                method = "Add the two quantities."
            elif operation == 1:
                prompt, answer = f"What is {left} × {right}?", left * right
                method = "Multiply the two quantities."
            else:
                product = left * right
                prompt, answer = f"What is {product} ÷ {right}?", left
                method = "Division reverses multiplication."
            record = {
                "topic": "quantitative aptitude practice",
                "content": f"Practice: {prompt} Answer: {answer}. Explanation: {method}",
                "synthetic": True,
                "seed": seed,
            }
            handle.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/private/practice.jsonl"))
    parser.add_argument("--count", type=int, default=600)
    arguments = parser.parse_args()
    generate(arguments.output, arguments.count)
