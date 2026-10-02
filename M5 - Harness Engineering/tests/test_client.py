"""Key resolution order and the cost function."""
from __future__ import annotations

import pytest

from harness import MissingKeyError, Usage, cost_usd, load_client, price_for


def test_env_file_wins_over_process_environment(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("ANTHROPIC_API_KEY=from-the-file\n", encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "from-the-environment")
    assert load_client(env_file).api_key == "from-the-file"


def test_process_environment_is_the_second_source(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "from-the-environment")
    assert load_client(tmp_path / "missing.env").api_key == "from-the-environment"


def test_missing_key_is_one_clear_sentence(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(MissingKeyError, match="copy .env.example to .env"):
        load_client(tmp_path / "missing.env")


def test_cost_uses_list_prices_and_cache_discount():
    usage = Usage(input_tokens=1_000_000, output_tokens=100_000, cache_read_input_tokens=1_000_000)
    assert cost_usd(usage, "claude-sonnet-5") == pytest.approx(2.0 + 1.0 + 0.2)
    assert price_for("claude-opus-5-20261001") == price_for("claude-opus-5")
    with pytest.raises(KeyError):
        price_for("gpt-5")
