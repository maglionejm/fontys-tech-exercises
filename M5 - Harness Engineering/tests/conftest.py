"""Test helpers. The stub client below is engineering practice for unit tests
only: it never appears in a notebook or a lab. It replays canned responses in
the exact shapes the Messages API returns, so the loop is tested without a key."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

MODULE_DIR = Path(__file__).resolve().parents[1]
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_use_block(name: str, input: dict, id: str = "toolu_01"):
    return SimpleNamespace(type="tool_use", name=name, input=input, id=id)


def response(content, stop_reason="end_turn", input_tokens=100, output_tokens=20):
    usage = SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens,
                            cache_read_input_tokens=0, cache_creation_input_tokens=0)
    return SimpleNamespace(content=content, stop_reason=stop_reason, usage=usage)


class StubMessages:
    """Replays a queue of responses; records every request it received."""

    def __init__(self, responses, token_count=50):
        self.queue = list(responses)
        self.requests: list[dict] = []
        self.token_count = token_count

    def create(self, **kwargs):
        self.requests.append(kwargs)
        if not self.queue:
            raise AssertionError("stub client ran out of canned responses")
        return self.queue.pop(0)

    def count_tokens(self, **kwargs):
        return SimpleNamespace(input_tokens=self.token_count)


class StubClient:
    def __init__(self, responses, token_count=50):
        self.messages = StubMessages(responses, token_count)


@pytest.fixture
def stub_client():
    return StubClient
