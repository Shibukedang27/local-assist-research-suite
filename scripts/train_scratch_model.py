"""Train Local Assist Tiny from random initialization on Apple Metal."""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path

import mlx.core as mx
import mlx.optimizers as optim
from mlx import nn

from local_assist.scratch_model import ScratchConfig, ScratchTransformer, encode, save_model


def load_corpus(path: Path) -> list[int]:
    texts = [json.loads(line)["text"] for line in path.read_text().splitlines() if line]
    return encode("\n".join(texts), bos=True, eos=True)


def batch(tokens: list[int], batch_size: int, length: int, rng: random.Random):
    starts = [rng.randrange(0, len(tokens) - length - 1) for _ in range(batch_size)]
    inputs = mx.array([tokens[start : start + length] for start in starts])
    targets = mx.array([tokens[start + 1 : start + length + 1] for start in starts])
    return inputs, targets


def loss_fn(model, inputs, targets):
    logits = model(inputs)
    return nn.losses.cross_entropy(logits, targets, reduction="mean")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=Path("data/private/scratch-corpus.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/local-assist-tiny"))
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--batch-size", type=int, default=12)
    parser.add_argument("--seed", type=int, default=20260801)
    args = parser.parse_args()
    random.seed(args.seed)
    mx.random.seed(args.seed)
    tokens = load_corpus(args.corpus)
    split = int(len(tokens) * 0.95)
    train_tokens, validation_tokens = tokens[:split], tokens[split:]
    config = ScratchConfig()
    model = ScratchTransformer(config)
    mx.eval(model.parameters())
    optimizer = optim.AdamW(learning_rate=3e-4, weight_decay=0.01)
    loss_and_grad = nn.value_and_grad(model, loss_fn)
    rng = random.Random(args.seed)
    started = time.monotonic()
    history = []
    for step in range(1, args.steps + 1):
        inputs, targets = batch(train_tokens, args.batch_size, config.context_length, rng)
        loss, gradients = loss_and_grad(model, inputs, targets)
        optimizer.update(model, gradients)
        mx.eval(model.parameters(), optimizer.state, loss)
        if step == 1 or step % 100 == 0:
            validation_inputs, validation_targets = batch(
                validation_tokens, args.batch_size, config.context_length, rng
            )
            validation_loss = loss_fn(model, validation_inputs, validation_targets)
            mx.eval(validation_loss)
            point = {
                "step": step,
                "train_loss": round(float(loss.item()), 4),
                "validation_loss": round(float(validation_loss.item()), 4),
                "validation_perplexity": round(math.exp(min(20, float(validation_loss.item()))), 2),
                "elapsed_seconds": round(time.monotonic() - started, 1),
            }
            history.append(point)
            print(json.dumps(point), flush=True)
    save_model(model, config, args.output)
    parameter_count = sum(value.size for _, value in nn.utils.tree_flatten(model.parameters()))
    report = {
        "model": "local-assist-tiny-from-scratch",
        "random_initialization": True,
        "pretrained_weights": False,
        "tokenizer": "fixed UTF-8 byte vocabulary built into this project",
        "parameters": parameter_count,
        "training_tokens": len(train_tokens),
        "validation_tokens": len(validation_tokens),
        "steps": args.steps,
        "batch_size": args.batch_size,
        "seed": args.seed,
        "device": str(mx.default_device()),
        "history": history,
    }
    (args.output / "training-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {key: report[key] for key in ("model", "parameters", "steps", "device")}, indent=2
        )
    )


if __name__ == "__main__":
    main()
