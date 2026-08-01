"""Run a prompt through the from-scratch checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from local_assist.scratch_model import generate, load_model

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--model", type=Path, default=Path("artifacts/local-assist-tiny"))
    arguments = parser.parse_args()
    model = load_model(arguments.model)
    print(generate(model, f"<user>{arguments.prompt}</user><assistant>"))
