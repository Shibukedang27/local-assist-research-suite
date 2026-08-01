"""A small byte-level causal transformer initialized and trained from scratch."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import mlx.core as mx
from mlx import nn

PAD, BOS, EOS = 256, 257, 258
VOCAB_SIZE = 259


@dataclass(frozen=True)
class ScratchConfig:
    vocab_size: int = VOCAB_SIZE
    dimensions: int = 192
    layers: int = 4
    heads: int = 6
    mlp_dimensions: int = 768
    context_length: int = 192


def encode(text: str, bos: bool = False, eos: bool = False) -> list[int]:
    tokens = list(text.encode("utf-8"))
    return ([BOS] if bos else []) + tokens + ([EOS] if eos else [])


def decode(tokens: list[int]) -> str:
    return bytes(token for token in tokens if 0 <= token < 256).decode("utf-8", errors="ignore")


class TransformerBlock(nn.Module):
    def __init__(self, config: ScratchConfig):
        super().__init__()
        self.attention = nn.MultiHeadAttention(config.dimensions, config.heads, bias=False)
        self.norm1 = nn.RMSNorm(config.dimensions)
        self.norm2 = nn.RMSNorm(config.dimensions)
        self.linear1 = nn.Linear(config.dimensions, config.mlp_dimensions, bias=False)
        self.linear2 = nn.Linear(config.mlp_dimensions, config.dimensions, bias=False)

    def __call__(self, values: mx.array, mask: mx.array) -> mx.array:
        normalized = self.norm1(values)
        values = values + self.attention(normalized, normalized, normalized, mask=mask)
        values = values + self.linear2(nn.gelu(self.linear1(self.norm2(values))))
        return values


class ScratchTransformer(nn.Module):
    def __init__(self, config: ScratchConfig):
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.dimensions)
        self.position_embedding = nn.Embedding(config.context_length, config.dimensions)
        self.blocks = [TransformerBlock(config) for _ in range(config.layers)]
        self.norm = nn.RMSNorm(config.dimensions)
        self.output = nn.Linear(config.dimensions, config.vocab_size, bias=False)

    def __call__(self, tokens: mx.array) -> mx.array:
        length = tokens.shape[1]
        values = self.token_embedding(tokens) + self.position_embedding(mx.arange(length))
        mask = nn.MultiHeadAttention.create_additive_causal_mask(length)
        for block in self.blocks:
            values = block(values, mask)
        return self.output(self.norm(values))


def save_model(model: ScratchTransformer, config: ScratchConfig, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    model.save_weights(str(directory / "weights.safetensors"))
    (directory / "config.json").write_text(json.dumps(asdict(config), indent=2) + "\n")


def load_model(directory: Path) -> ScratchTransformer:
    config = ScratchConfig(**json.loads((directory / "config.json").read_text()))
    model = ScratchTransformer(config)
    model.load_weights(str(directory / "weights.safetensors"))
    mx.eval(model.parameters())
    return model


def generate(model: ScratchTransformer, prompt: str, max_tokens: int = 240) -> str:
    tokens = encode(prompt, bos=True)
    for _ in range(max_tokens):
        context = tokens[-model.config.context_length :]
        logits = model(mx.array([context]))[0, -1]
        next_token = int(mx.argmax(logits).item())
        if next_token == EOS:
            break
        tokens.append(next_token)
        generated = decode(tokens[len(encode(prompt, bos=True)) :])
        if "</assistant>" in generated:
            return generated.split("</assistant>", 1)[0].strip()
    return decode(tokens[len(encode(prompt, bos=True)) :]).strip()
