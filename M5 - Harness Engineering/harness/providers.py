"""Real models behind the same interface as the ScriptedModel.

Optional. Nothing in the course needs these; they exist to show that the
harness does not change when the engine does. Keys are asked for at run time
with getpass and kept only in memory; never paste a key into a notebook.
"""
from __future__ import annotations

import json
from typing import Any

from .messages import Message, ToolCall


def _group_tool_results(messages: list[Message]) -> list[list[Message]]:
    """Consecutive tool results belong in one turn for both providers."""
    groups: list[list[Message]] = []
    for m in messages:
        if m.role == "tool" and groups and groups[-1] and groups[-1][0].role == "tool":
            groups[-1].append(m)
        else:
            groups.append([m])
    return groups


class AnthropicModel:
    """Claude through the official anthropic SDK (Messages API, manual tool loop)."""

    def __init__(self, model: str = "claude-opus-5", api_key: str | None = None,
                 max_tokens: int = 4096):
        import anthropic  # imported here so the course never requires the package

        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.model = model
        self.name = model
        self.max_tokens = max_tokens

    def complete(self, system: str, messages: list[Message],
                 tools: list[dict[str, Any]]) -> Message:
        api_messages: list[dict[str, Any]] = []
        for group in _group_tool_results(messages):
            first = group[0]
            if first.role == "tool":
                api_messages.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": m.tool_call_id, "content": m.content}
                    for m in group]})
            elif first.role == "assistant":
                content: list[dict[str, Any]] = []
                if first.content:
                    content.append({"type": "text", "text": first.content})
                for c in first.tool_calls:
                    content.append({"type": "tool_use", "id": c.id, "name": c.name,
                                    "input": c.arguments})
                api_messages.append({"role": "assistant", "content": content})
            else:
                api_messages.append({"role": "user", "content": first.content})
        kwargs: dict[str, Any] = {}
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = [{"name": t["name"], "description": t["description"],
                                "input_schema": t["parameters"]} for t in tools]
        response = self.client.messages.create(model=self.model, max_tokens=self.max_tokens,
                                               messages=api_messages, **kwargs)
        text = "".join(b.text for b in response.content if b.type == "text")
        calls = [ToolCall(b.id, b.name, dict(b.input)) for b in response.content
                 if b.type == "tool_use"]
        return Message("assistant", text, calls)


class OpenAIModel:
    """An OpenAI model through the official openai SDK (chat completions with tools)."""

    def __init__(self, model: str = "gpt-5", api_key: str | None = None):
        from openai import OpenAI  # imported here so the course never requires the package

        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.model = model
        self.name = model

    def complete(self, system: str, messages: list[Message],
                 tools: list[dict[str, Any]]) -> Message:
        api_messages: list[dict[str, Any]] = []
        if system:
            api_messages.append({"role": "system", "content": system})
        for m in messages:
            if m.role == "tool":
                api_messages.append({"role": "tool", "tool_call_id": m.tool_call_id,
                                     "content": m.content})
            elif m.role == "assistant":
                entry: dict[str, Any] = {"role": "assistant", "content": m.content or None}
                if m.tool_calls:
                    entry["tool_calls"] = [{"id": c.id, "type": "function", "function": {
                        "name": c.name, "arguments": json.dumps(c.arguments)}} for c in m.tool_calls]
                api_messages.append(entry)
            else:
                api_messages.append({"role": "user", "content": m.content})
        kwargs: dict[str, Any] = {}
        if tools:
            kwargs["tools"] = [{"type": "function", "function": {
                "name": t["name"], "description": t["description"], "parameters": t["parameters"]}}
                for t in tools]
        response = self.client.chat.completions.create(model=self.model, messages=api_messages,
                                                       **kwargs)
        msg = response.choices[0].message
        calls = [ToolCall(tc.id, tc.function.name, json.loads(tc.function.arguments or "{}"))
                 for tc in (msg.tool_calls or [])]
        return Message("assistant", msg.content or "", calls)


def connect(provider: str = "anthropic", model: str | None = None):
    """Ask for a key interactively and return a real model. The key is never written anywhere."""
    from getpass import getpass

    key = getpass(f"Paste your {provider} API key (input is hidden, kept in memory only): ").strip()
    if not key:
        raise ValueError("No key given. The course runs fully without one; this step is optional.")
    if provider == "anthropic":
        return AnthropicModel(model or "claude-opus-5", api_key=key)
    if provider == "openai":
        return OpenAIModel(model or "gpt-5", api_key=key)
    raise ValueError("provider must be 'anthropic' or 'openai'")
