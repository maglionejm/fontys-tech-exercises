"""Hooks: your code, run by the harness at fixed points of the loop.

- ``before_tool(request, tool) -> str | None``: return a reason to deny the call.
- ``after_tool(request, tool, result) -> str``: rewrite the result (truncate, redact).
- ``validate_answer(answer) -> str | None``: return a problem to send the answer back.

A hook never asks the model to behave; it decides, and the model reads the outcome.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from .tools import Tool

BeforeHook = Callable[["ToolRequest", Tool | None], str | None]
AfterHook = Callable[["ToolRequest", Tool, str], str]
AnswerHook = Callable[[str], str | None]


@dataclass
class ToolRequest:
    """What the model asked for: which tool, with which input, on which turn."""

    id: str
    name: str
    input: dict[str, Any]
    turn: int


def _as_list(value: Any) -> list:
    if value is None:
        return []
    return list(value) if isinstance(value, (list, tuple)) else [value]


@dataclass
class Hooks:
    """The three hook lists an ``Agent`` runs. Pass one function or a list."""

    before_tool: list[BeforeHook] = field(default_factory=list)
    after_tool: list[AfterHook] = field(default_factory=list)
    validate_answer: list[AnswerHook] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.before_tool = _as_list(self.before_tool)
        self.after_tool = _as_list(self.after_tool)
        self.validate_answer = _as_list(self.validate_answer)

    def check_before(self, request: ToolRequest, candidate: Tool | None) -> str | None:
        """The first denial reason, or None when every hook lets the call through."""
        for hook in self.before_tool:
            reason = hook(request, candidate)
            if reason:
                return reason
        return None

    def apply_after(self, request: ToolRequest, candidate: Tool, result: str) -> str:
        for hook in self.after_tool:
            result = hook(request, candidate, result)
        return result

    def validate(self, answer: str) -> str | None:
        """The first problem a validator finds, or None when the answer is accepted."""
        for hook in self.validate_answer:
            problem = hook(answer)
            if problem:
                return problem
        return None


# Ready-made hooks used by the notebooks and the CLI ------------------------------


def deny_paths(*suffixes: str) -> BeforeHook:
    """Deny ``read_file`` (or any tool with a ``path`` input) on paths ending in ``suffixes``."""

    def hook(request: ToolRequest, candidate: Tool | None) -> str | None:
        path = str(request.input.get("path", ""))
        if path.endswith(suffixes):
            return f"Denied by a before_tool hook: {path!r} is a protected file."
        return None

    hook.__name__ = f"deny_paths{suffixes}"
    return hook


def deny_risk_hook(*levels: str) -> BeforeHook:
    """Deny every tool whose risk label is in ``levels`` (a hook version of ``deny_risk``)."""

    def hook(request: ToolRequest, candidate: Tool | None) -> str | None:
        if candidate is not None and candidate.risk in levels:
            return f"Denied by a before_tool hook: {candidate.name!r} has risk {candidate.risk!r}."
        return None

    hook.__name__ = f"deny_risk_hook{levels}"
    return hook


def truncate_result(max_chars: int = 4000) -> AfterHook:
    """Cut long tool results so one file cannot flood the context window."""

    def hook(request: ToolRequest, candidate: Tool, result: str) -> str:
        if len(result) <= max_chars:
            return result
        return result[:max_chars] + f"\n[... cut by an after_tool hook at {max_chars} characters]"

    hook.__name__ = f"truncate_result({max_chars})"
    return hook


def require_sources(answer: str) -> str | None:
    """Validator for the structured answer: when ``found`` is true, ``sources`` must not be empty."""
    try:
        data = json.loads(answer)
    except (json.JSONDecodeError, TypeError):
        return "The answer must be the JSON object described by the output schema."
    if data.get("found") and not data.get("sources"):
        return "You claim the fact was found but list no sources. Add the repository paths you read, or set found to false."
    return None
