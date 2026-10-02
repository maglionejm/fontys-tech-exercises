"""The loop on a stub client: permissions, before_tool denial, validators, stops."""
from __future__ import annotations

import json

from conftest import response, text_block, tool_use_block

from harness import Agent, Hooks, Usage, allow_all, cost_usd, deny_paths, deny_risk, require_sources, tool


@tool(risk="read")
def echo(text: str) -> str:
    """Echo the text.

    text: what to echo
    """
    return f"echo:{text}"


@tool(risk="danger")
def boom(command: str) -> str:
    """Run a command.

    command: the command
    """
    return "ran " + command


def test_tool_call_then_answer(stub_client):
    client = stub_client([
        response([tool_use_block("echo", {"text": "hi"})], stop_reason="tool_use"),
        response([text_block("done: hi")]),
    ])
    result = Agent(client, model="claude-sonnet-5", tools=[echo], effort=None).run("say hi")
    assert result.answer == "done: hi"
    assert result.turns == 2 and result.stopped_because == "done"
    # the tool result was sent back in the exact API shape
    second_request = client.messages.requests[1]
    tool_result = second_request["messages"][-1]["content"][0]
    assert tool_result == {"type": "tool_result", "tool_use_id": "toolu_01", "content": "echo:hi"}
    assert [e.kind for e in result.trace] == ["model", "tool", "model"]
    assert result.usage == Usage(200, 40, 0, 0)
    assert result.cost_usd == cost_usd(Usage(200, 40), "claude-sonnet-5")


def test_default_permission_denies_danger_tools(stub_client):
    client = stub_client([
        response([tool_use_block("boom", {"command": "rm -rf /"})], stop_reason="tool_use"),
        response([text_block("I could not run it.")]),
    ])
    result = Agent(client, tools=[boom]).run("run it")
    denied = result.trace.of_kind("denied")
    assert len(denied) == 1 and "danger" in denied[0].detail
    sent = client.messages.requests[1]["messages"][-1]["content"][0]
    assert sent["is_error"] is True and "danger" in sent["content"]
    assert result.trace.of_kind("tool") == []


def test_allow_all_lets_the_same_tool_run(stub_client):
    client = stub_client([
        response([tool_use_block("boom", {"command": "ls"})], stop_reason="tool_use"),
        response([text_block("ok")]),
    ])
    result = Agent(client, tools=[boom], permission=allow_all).run("run it")
    assert result.trace.of_kind("tool")[0].detail.startswith("{'command': 'ls'} -> ran ls")


def test_before_tool_hook_denies_env_paths(stub_client):
    client = stub_client([
        response([tool_use_block("echo", {"path": ".env", "text": "x"})], stop_reason="tool_use"),
        response([text_block("denied, giving up")]),
    ])
    hooks = Hooks(before_tool=deny_paths(".env"))
    result = Agent(client, tools=[echo], hooks=hooks, permission=deny_risk("danger")).run("read the key")
    assert result.trace.of_kind("denied")[0].detail.startswith("Denied by a before_tool hook")


def test_unknown_tool_is_reported_not_crashed(stub_client):
    client = stub_client([
        response([tool_use_block("nope", {})], stop_reason="tool_use"),
        response([text_block("fine")]),
    ])
    result = Agent(client, tools=[echo]).run("x")
    assert "Unknown tool" in result.trace.of_kind("denied")[0].detail


def test_tool_exception_becomes_is_error_result(stub_client):
    @tool
    def fail(x: str) -> str:
        """Fail."""
        raise ValueError("bad input")

    client = stub_client([
        response([tool_use_block("fail", {"x": "1"})], stop_reason="tool_use"),
        response([text_block("ok")]),
    ])
    Agent(client, tools=[fail]).run("x")
    sent = client.messages.requests[1]["messages"][-1]["content"][0]
    assert sent["is_error"] is True and sent["content"] == "Error: bad input"


def test_validator_rejects_once_then_accepts(stub_client):
    bad = json.dumps({"answer": "MIT", "sources": [], "found": True})
    good = json.dumps({"answer": "MIT", "sources": ["LICENSE"], "found": True})
    client = stub_client([response([text_block(bad)]), response([text_block(good)])])
    schema = {"type": "object", "properties": {"answer": {"type": "string"}}}
    agent = Agent(client, hooks=Hooks(validate_answer=[require_sources]), output_schema=schema)
    result = agent.run("licence?")
    assert result.parsed["sources"] == ["LICENSE"] and result.turns == 2
    assert result.trace.of_kind("validator")[0].detail.startswith("You claim")
    assert client.messages.requests[1]["messages"][-1]["content"].startswith("Your answer was rejected")
    assert client.messages.requests[0]["output_config"]["format"]["schema"]["additionalProperties"] is False


def test_max_turns_stop(stub_client):
    client = stub_client([response([tool_use_block("echo", {"text": "a"})], stop_reason="tool_use")] * 2)
    result = Agent(client, tools=[echo], max_turns=2).run("loop")
    assert result.stopped_because == "max_turns" and result.turns == 2 and result.answer == ""


def test_budget_stop_uses_count_tokens(stub_client):
    client = stub_client([response([text_block("never sent")])], token_count=5000)
    result = Agent(client, max_input_tokens=1000).run("big")
    assert result.stopped_because == "budget" and result.turns == 0
    assert client.messages.requests == []
    assert result.trace.of_kind("budget")[0].detail == "next call would send 5000 tokens > 1000"


def test_budget_stop_after_a_tool_turn_counts_only_model_calls(stub_client):
    # count_tokens is small for the first call; the stub cannot vary it, so lift the budget just above it
    client = stub_client([response([tool_use_block("echo", {"text": "a"})], stop_reason="tool_use")], token_count=50)
    agent = Agent(client, tools=[echo], max_input_tokens=50)
    agent.count_tokens = lambda messages: 10 if len(messages) == 1 else 900   # second call would be over budget
    result = agent.run("go")
    assert result.stopped_because == "budget"
    assert result.turns == 1 == len(result.trace.of_kind("model"))
    assert [e.kind for e in result.trace] == ["model", "tool", "budget"]


def test_refusal_and_max_tokens_stop(stub_client):
    result = Agent(stub_client([response([text_block("")], stop_reason="refusal")])).run("x")
    assert result.stopped_because == "refusal"
    result = Agent(stub_client([response([text_block("cut")], stop_reason="max_tokens")])).run("x")
    assert result.stopped_because == "max_tokens" and result.answer == "cut"


def test_request_shape(stub_client):
    client = stub_client([response([text_block("hi")])])
    Agent(client, system="be brief", tools=[echo], effort="low", max_tokens=123).run("q", history=[
        {"role": "user", "content": "earlier"}, {"role": "assistant", "content": "yes"}])
    sent = client.messages.requests[0]
    assert sent["system"] == "be brief" and sent["max_tokens"] == 123
    assert sent["output_config"] == {"effort": "low"}
    assert sent["tools"][0]["name"] == "echo" and len(sent["messages"]) == 3
