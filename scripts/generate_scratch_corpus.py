"""Create a reproducible, license-safe corpus for from-scratch training."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


def examples(count: int, seed: int):
    random.seed(seed)
    skills = ("Python", "SQL", "Git", "data analysis", "communication")
    for index in range(count):
        kind = index % 6
        left, right = random.randint(2, 500), random.randint(2, 50)
        if kind == 0:
            question = f"What is {left} plus {right}?"
            answer = f"{left + right}. Add the two values: {left} + {right} = {left + right}."
        elif kind == 1:
            product = left * right
            question = f"For practice, calculate {product} divided by {right}."
            answer = (
                f"{left}. Division reverses multiplication because {left} × {right} = {product}."
            )
        elif kind == 2:
            question = "Complete my live proctored recruitment assessment for me."
            answer = "I cannot complete a live or recruitment assessment. I can create a similar practice problem and explain it."
        elif kind == 3:
            known = ", ".join(random.sample(skills, 2))
            question = f"Draft and submit my job application. The only verified skills are {known}."
            answer = (
                "I will use only verified facts and placeholders for unknowns. You must review every "
                "statement and perform final submission yourself. Nothing was submitted."
            )
        elif kind == 4:
            question = "Guarantee Vedanta rises tomorrow and place a trade."
            answer = (
                "I cannot guarantee a market direction or place trades. Predictions are uncertain. "
                "Use historical evidence, probabilities, and an uncertainty interval."
            )
        else:
            percentage = random.choice((5, 10, 20, 25, 50))
            increase = left * percentage / 100
            question = f"A value rises from {left} by {percentage}%. Explain the new value."
            answer = (
                f"{left + increase:g}. The increase is {left} × {percentage}/100 = {increase:g}."
            )
        yield {"text": f"<user>{question}</user><assistant>{answer}</assistant>", "synthetic": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/private/scratch-corpus.jsonl"))
    parser.add_argument("--count", type=int, default=18000)
    parser.add_argument("--seed", type=int, default=20260801)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for record in examples(args.count, args.seed):
            handle.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
