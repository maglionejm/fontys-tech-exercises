"""Traces: the record of every step an agent takes.

Observability is the dashboard of the harness: without it you cannot tell
why a run cost what it cost or where it went wrong.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Event:
    kind: str            # "model", "tool", "denied", "compact", "final", "note"
    turn: int
    name: str
    detail: str
    tokens: int = 0
    seconds: float = 0.0


@dataclass
class Trace:
    agent: str = "agent"
    events: list[Event] = field(default_factory=list)
    started: float = field(default_factory=time.time)

    def add(self, kind: str, turn: int, name: str, detail: str,
            tokens: int = 0, seconds: float = 0.0) -> Event:
        ev = Event(kind, turn, name, detail[:400], tokens, seconds)
        self.events.append(ev)
        return ev

    def tool_calls(self) -> list[Event]:
        return [e for e in self.events if e.kind == "tool"]

    def model_calls(self) -> list[Event]:
        return [e for e in self.events if e.kind == "model"]

    @property
    def tokens(self) -> int:
        """Estimated tokens sent to the model across all calls."""
        return sum(e.tokens for e in self.model_calls())

    @property
    def turns(self) -> int:
        return len(self.model_calls())

    def summary(self) -> dict:
        return {"agent": self.agent, "model_calls": self.turns,
                "tool_calls": len(self.tool_calls()),
                "denied": sum(1 for e in self.events if e.kind == "denied"),
                "estimated_tokens": self.tokens,
                "seconds": round(time.time() - self.started, 3)}

    def cost(self, usd_per_million_tokens: float = 3.0) -> float:
        """Rough cost if these tokens had gone to a paid model."""
        return round(self.tokens / 1_000_000 * usd_per_million_tokens, 6)

    def show(self, width: int = 88) -> None:
        """Print a compact, readable log of the run."""
        print(f"trace of '{self.agent}': {self.turns} model calls, "
              f"{len(self.tool_calls())} tool calls, ~{self.tokens} tokens")
        for e in self.events:
            detail = e.detail.replace("\n", " ")
            if len(detail) > width - 28:
                detail = detail[: width - 31] + "..."
            print(f"  {e.turn:>2}  {e.kind:<8} {e.name:<18} {detail}")
