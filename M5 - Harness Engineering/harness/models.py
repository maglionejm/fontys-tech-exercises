"""Models: anything that maps a context to the next message.

The harness never cares what is behind the interface. In this module the
default is a ScriptedModel: a small Python policy that plays the model's part
deterministically, so the mechanics of a harness can be studied without an
API key. providers.py adds adapters for real models behind the same interface.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from .messages import Message, ToolCall


class Model(Protocol):
    """The whole contract between a harness and a model."""

    name: str

    def complete(self, system: str, messages: list[Message],
                 tools: list[dict[str, Any]]) -> Message: ...


_ids = itertools.count(1)


def new_call_id() -> str:
    return f"call_{next(_ids):04d}"


@dataclass
class ModelView:
    """What a policy may look at: exactly what a real model would see."""

    system: str
    messages: list[Message]
    tools: list[dict[str, Any]]

    @staticmethod
    def _is_task(m: Message) -> bool:
        return m.role == "user" and not m.content.startswith(("[Context compacted", "Your answer was rejected"))

    @property
    def task_index(self) -> int:
        """Position of the current task: the last real user message."""
        for i in range(len(self.messages) - 1, -1, -1):
            if self._is_task(self.messages[i]):
                return i
        return 0

    @property
    def task(self) -> str:
        """The current task: the last user message that is not a harness note."""
        return self.messages[self.task_index].content if self.messages else ""

    @property
    def last(self) -> Message:
        return self.messages[-1]

    def tool_names(self) -> list[str]:
        return [t["name"] for t in self.tools]

    def has_tool(self, name: str) -> bool:
        return name in self.tool_names()

    def results(self, name: str | None = None) -> list[Message]:
        """Tool results for the current task, optionally for one tool."""
        return [m for m in self.messages[self.task_index:]
                if m.role == "tool" and (name is None or m.name == name)]

    def called(self, name: str) -> bool:
        return bool(self.results(name))

    def times_called(self, name: str) -> int:
        return len(self.results(name))

    def last_result(self, name: str) -> str | None:
        found = self.results(name)
        return found[-1].content if found else None

    def user_messages(self) -> list[str]:
        return [m.content for m in self.messages if m.role == "user"]


def say(text: str) -> Message:
    """A final text reply."""
    return Message("assistant", text)


def call(name: str, /, **arguments: Any) -> Message:
    """A request to run one tool. The tool name is positional, so a tool argument may also be called name."""
    return Message("assistant", tool_calls=[ToolCall(new_call_id(), name, arguments)])


def calls(*requests: tuple[str, dict[str, Any]]) -> Message:
    """Several tool requests in one turn (parallel tool use)."""
    return Message("assistant", tool_calls=[ToolCall(new_call_id(), n, a) for n, a in requests])


@dataclass
class ScriptedModel:
    """A stand-in for a language model.

    Same interface as a real model, no network, no key, no randomness. The
    policy function reads a ModelView and returns the next Message. It lets us
    change the harness and see exactly what changed, because the model never does.
    """

    policy: Callable[[ModelView], Message]
    name: str = "scripted"
    calls_made: int = 0

    def complete(self, system: str, messages: list[Message],
                 tools: list[dict[str, Any]]) -> Message:
        self.calls_made += 1
        return self.policy(ModelView(system, list(messages), list(tools)))
