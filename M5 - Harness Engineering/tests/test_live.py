"""One live call against the real API. Skipped when no key is available."""
from __future__ import annotations

import pytest

from harness import Agent, MissingKeyError, WORKER_MODEL, list_files, load_client, read_file

try:
    CLIENT = load_client()
except MissingKeyError:
    CLIENT = None

pytestmark = pytest.mark.skipif(CLIENT is None, reason="no ANTHROPIC_API_KEY in .env or the environment")


def test_researcher_finds_the_licence_with_a_source():
    agent = Agent(CLIENT, model=WORKER_MODEL, tools=[list_files, read_file], effort="low", max_turns=5,
                  output_schema={"type": "object", "properties": {"answer": {"type": "string"},
                                 "sources": {"type": "array", "items": {"type": "string"}}},
                                 "required": ["answer", "sources"]},
                  system="Read the repository to answer; list the files you read in sources.")
    result = agent.run("Which licence does this repository use? Read the LICENSE file.")
    assert result.stopped_because == "done"
    assert "MIT" in result.parsed["answer"]
    assert any(s.endswith("LICENSE") for s in result.parsed["sources"])
    assert result.usage.input_tokens > 0 and result.cost_usd > 0
