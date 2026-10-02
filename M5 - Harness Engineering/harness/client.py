"""The key, the models and the prices: one place for everything that costs money.

The key is read from the git-ignored ``.env`` at the repository root with
``dotenv_values`` and passed to the SDK explicitly. It is never exported into
``os.environ`` and never printed.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import anthropic
from dotenv import dotenv_values

from .repo_tools import repo_root

DEFAULT_MAIN_MODEL = "claude-opus-5"
DEFAULT_WORKER_MODEL = "claude-sonnet-5"

# USD per million tokens (Claude API reference, 2026). Cache reads cost one
# tenth of a normal input token; writing to the cache costs 1.25 times.
PRICES: dict[str, dict[str, float]] = {
    "claude-opus-5": {"input": 5.00, "output": 25.00},
    "claude-sonnet-5": {"input": 2.00, "output": 10.00},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
}
CACHE_READ_FACTOR = 0.10
CACHE_WRITE_FACTOR = 1.25


class MissingKeyError(RuntimeError):
    """Raised when no ANTHROPIC_API_KEY can be found."""


def _env_file(env_path: str | Path | None = None) -> dict[str, str | None]:
    """The variables in ``.env`` as a dict, without touching ``os.environ``."""
    try:
        path = Path(env_path) if env_path else repo_root() / ".env"
    except FileNotFoundError:
        return {}
    return dotenv_values(path) if path.exists() else {}


def _setting(name: str, default: str) -> str:
    return _env_file().get(name) or os.environ.get(name) or default


MAIN_MODEL: str = _setting("HARNESS_MODEL", DEFAULT_MAIN_MODEL)
WORKER_MODEL: str = _setting("HARNESS_WORKER_MODEL", DEFAULT_WORKER_MODEL)


def _colab_secret(name: str) -> str | None:
    try:
        from google.colab import userdata  # type: ignore[import-not-found]

        return userdata.get(name)
    except Exception:  # noqa: BLE001 - not on Colab, or the secret is not set
        return None


def load_client(env_path: str | Path | None = None) -> anthropic.Anthropic:
    """Return an Anthropic client, or raise one clear sentence when there is no key.

    Looks, in this order and stopping at the first hit: ``.env`` at the repository
    root (or ``env_path``), the process environment (how the CI job passes the
    repository secret), then the Colab secrets.
    """
    key = _env_file(env_path).get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    key = key or _colab_secret("ANTHROPIC_API_KEY")
    if not key:
        raise MissingKeyError(
            "No ANTHROPIC_API_KEY found: copy .env.example to .env at the repository "
            "root and put your key in it (on Colab, add it under Secrets)."
        )
    return anthropic.Anthropic(api_key=key)


@dataclass
class Usage:
    """Token counts, summed over a run or a suite. Adds with ``+``."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0

    @classmethod
    def from_response(cls, usage: Any) -> "Usage":
        """Read the ``usage`` object of a Messages API response."""
        return cls(
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0,
            cache_read_input_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
            cache_creation_input_tokens=getattr(usage, "cache_creation_input_tokens", 0) or 0,
        )

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            self.input_tokens + other.input_tokens,
            self.output_tokens + other.output_tokens,
            self.cache_read_input_tokens + other.cache_read_input_tokens,
            self.cache_creation_input_tokens + other.cache_creation_input_tokens,
        )

    @property
    def total_input(self) -> int:
        """Everything the model read, cached or not."""
        return self.input_tokens + self.cache_read_input_tokens + self.cache_creation_input_tokens

    def as_dict(self) -> dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_input_tokens": self.cache_read_input_tokens,
            "cache_creation_input_tokens": self.cache_creation_input_tokens,
        }


def price_for(model: str) -> dict[str, float]:
    """Prices for a model id; falls back on the family name (opus, sonnet, haiku)."""
    if model in PRICES:
        return PRICES[model]
    for known, price in PRICES.items():
        family = known.split("-")[1]
        if family in model:
            return price
    raise KeyError(f"No price known for model {model!r}; add it to harness.client.PRICES.")


def cost_usd(usage: Any, model: str) -> float:
    """Turn real token counts into dollars with the PRICES table."""
    used = usage if isinstance(usage, Usage) else Usage.from_response(usage)
    price = price_for(model)
    per_input = price["input"] / 1_000_000
    return round(
        used.input_tokens * per_input
        + used.cache_read_input_tokens * per_input * CACHE_READ_FACTOR
        + used.cache_creation_input_tokens * per_input * CACHE_WRITE_FACTOR
        + used.output_tokens * price["output"] / 1_000_000,
        6,
    )
