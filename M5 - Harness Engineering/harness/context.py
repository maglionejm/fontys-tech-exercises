"""Context engineering: the window is a budget, not a bucket.

Two tools from the field: compaction (summarize old turns into one note when
the budget is near) and structured notes (write facts to a file outside the
window so they survive compaction and restarts).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .messages import Message, estimate_tokens, total_tokens


def default_summary(middle: list[Message]) -> str:
    """A deterministic summary: which tools ran, what came back, what was said."""
    lines: list[str] = []
    for m in middle:
        if m.role == "assistant" and m.tool_calls:
            for c in m.tool_calls:
                args = ", ".join(f"{k}={str(v)[:40]!r}" for k, v in c.arguments.items())
                lines.append(f"- called {c.name}({args})")
        elif m.role == "assistant" and m.content:
            lines.append(f"- said: {m.content[:160]}")
        elif m.role == "tool":
            first = m.content.strip().splitlines()[0] if m.content.strip() else ""
            lines.append(f"- {m.name} returned: {first[:120]}")
        elif m.role == "user":
            lines.append(f"- user: {m.content[:120]}")
    return "\n".join(lines) or "- (nothing to summarize)"


@dataclass
class ContextWindow:
    """A token budget with a compaction rule."""

    budget_tokens: int = 6000
    keep_last: int = 6
    compactions: int = 0

    def tokens(self, system: str, messages: list[Message]) -> int:
        return estimate_tokens(system) + total_tokens(messages)

    def over_budget(self, system: str, messages: list[Message]) -> bool:
        return self.tokens(system, messages) > self.budget_tokens

    def compact(self, messages: list[Message],
                summarizer: Callable[[list[Message]], str] | None = None
                ) -> tuple[list[Message], str]:
        """Keep the task and the last few turns; fold the middle into one note."""
        if len(messages) <= 1 + self.keep_last:
            return messages, ""
        head, middle, tail = messages[:1], messages[1:-self.keep_last], messages[-self.keep_last:]
        if not middle:
            return messages, ""
        summary = (summarizer or default_summary)(middle)
        note = Message("user", f"[Context compacted: {len(middle)} earlier messages "
                               f"summarized]\n{summary}")
        self.compactions += 1
        return head + [note] + tail, summary


class Notes:
    """Structured note-taking: memory that lives outside the context window."""

    def __init__(self, path: str | Path = "outputs/notes.md"):
        self.path = Path(path)

    def append(self, text: str) -> str:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(text.rstrip() + "\n")
        return f"Noted ({estimate_tokens(text)} tokens)."

    def read(self) -> str:
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def tokens(self) -> int:
        return estimate_tokens(self.read())
