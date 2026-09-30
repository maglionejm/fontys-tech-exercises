"""The two message types every harness passes around.

A conversation is a list of Message objects. The model reads them and returns
the next one. A tool call is the model asking the harness to run a function.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """The model's request to run one tool with JSON arguments."""

    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """One turn in the conversation.

    role is one of "system", "user", "assistant" or "tool". Tool results carry the
    id of the call they answer, so the model can match results to requests.
    """

    role: str
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None
    raw: Any = None            # provider-native content blocks, replayed verbatim on later calls
    usage: dict | None = None  # real token counts reported by a provider, when available

    def as_text(self) -> str:
        """Flat text view, used for token estimates and printing."""
        parts = [self.content] if self.content else []
        for call in self.tool_calls:
            parts.append(f"{call.name}({call.arguments})")
        return "\n".join(parts)


def estimate_tokens(text: str) -> int:
    """Rough token count: about four characters per token for English text."""
    return max(1, len(text) // 4)


def total_tokens(messages: list[Message]) -> int:
    return sum(estimate_tokens(m.as_text()) for m in messages)
