"""Real models behind the same interface as the ScriptedModel.

The harness does not change when the engine does. Credentials are read from
the environment (ANTHROPIC_API_KEY, loaded from a git-ignored .env file by
harness.runtime); nothing here ever stores or prints a key.
"""
from __future__ import annotations

import json
from typing import Any

from .messages import Message, ToolCall


def _group_tool_results(messages: list[Message]) -> list[list[Message]]:
    """Consecutive tool results belong in one turn for both providers."""
    groups: list[list[Message]] = []
    for m in messages:
        if m.role == "tool" and groups and groups[-1][0].role == "tool":
            groups[-1].append(m)
        else:
            groups.append([m])
    return groups


class AnthropicModel:
    """Claude through the official anthropic SDK (Messages API, manual tool loop).

    Thinking stays on its adaptive default; the model's own content blocks are
    replayed verbatim on later turns so thinking blocks are preserved. effort
    trades depth for speed and cost: "low" for workers, "medium" or "high" for leads.
    """

    def __init__(self, model: str = "claude-opus-5", api_key: str | None = None,
                 max_tokens: int = 4096, effort: str = "medium"):
        import anthropic  # imported here so the course never requires the package

        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.model = model
        self.name = model
        self.max_tokens = max_tokens
        self.effort = effort
        self.calls_made = 0
        self.input_tokens = 0
        self.output_tokens = 0

    @staticmethod
    def _assistant_content(m: Message) -> list[dict[str, Any]]:
        if m.raw:
            return m.raw
        content: list[dict[str, Any]] = []
        if m.content:
            content.append({"type": "text", "text": m.content})
        for c in m.tool_calls:
            content.append({"type": "tool_use", "id": c.id, "name": c.name, "input": c.arguments})
        return content or [{"type": "text", "text": "(no content)"}]

    def _api_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        api: list[dict[str, Any]] = []
        for group in _group_tool_results(messages):
            first = group[0]
            if first.role == "tool":
                api.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": m.tool_call_id, "content": m.content}
                    for m in group]})
            elif first.role == "assistant":
                api.append({"role": "assistant", "content": self._assistant_content(first)})
            else:
                api.append({"role": "user", "content": first.content})
        return api

    def complete(self, system: str, messages: list[Message],
                 tools: list[dict[str, Any]]) -> Message:
        kwargs: dict[str, Any] = {"output_config": {"effort": self.effort}}
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = [{"name": t["name"], "description": t["description"],
                                "input_schema": t["parameters"]} for t in tools]
        response = self.client.messages.create(model=self.model, max_tokens=self.max_tokens,
                                               messages=self._api_messages(messages), **kwargs)
        self.calls_made += 1
        usage = {"input_tokens": response.usage.input_tokens,
                 "output_tokens": response.usage.output_tokens}
        self.input_tokens += usage["input_tokens"]
        self.output_tokens += usage["output_tokens"]
        text = "".join(b.text for b in response.content if b.type == "text")
        calls = [ToolCall(b.id, b.name, dict(b.input)) for b in response.content
                 if b.type == "tool_use"]
        if response.stop_reason == "refusal":
            details = getattr(response, "stop_details", None)
            text = (text + "\n" if text else "") + "[The model declined this request" + \
                   (f": {details.category}" if details and getattr(details, "category", None) else "") + "]"
            calls = []
        elif response.stop_reason == "max_tokens":
            text += "\n[Reply cut at max_tokens; raise max_tokens for longer answers.]"
        raw = [b.model_dump(exclude_none=True) for b in response.content]
        return Message("assistant", text, calls, raw=raw, usage=usage)

    def summary(self) -> dict[str, Any]:
        return {"model": self.model, "calls": self.calls_made,
                "input_tokens": self.input_tokens, "output_tokens": self.output_tokens}


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
        usage = None
        if response.usage:
            usage = {"input_tokens": response.usage.prompt_tokens,
                     "output_tokens": response.usage.completion_tokens}
        return Message("assistant", msg.content or "", calls, usage=usage)


def connect(provider: str = "anthropic", model: str | None = None):
    """Ask for a key interactively and return a real model. The key is never written anywhere."""
    from getpass import getpass

    key = getpass(f"Paste your {provider} API key (input is hidden, kept in memory only): ").strip()
    if not key:
        raise ValueError("No key given. Put ANTHROPIC_API_KEY in a .env file instead; see .env.example.")
    if provider == "anthropic":
        return AnthropicModel(model or "claude-opus-5", api_key=key)
    if provider == "openai":
        return OpenAIModel(model or "gpt-5", api_key=key)
    raise ValueError("provider must be 'anthropic' or 'openai'")
