"""The trace: a flight recorder for one run.

Every model call, tool call, denial, validator note and budget stop becomes an
``Event``. ``show()`` prints the step log, ``summary()`` gives the totals and
``to_frame()`` returns a pandas DataFrame for charts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

KINDS = ("model", "tool", "denied", "validator", "compact", "budget")


@dataclass
class Event:
    kind: str
    turn: int
    name: str
    detail: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0


def short(value: Any, width: int = 70) -> str:
    """One line, at most ``width`` characters, for logs."""
    text = " ".join(str(value).split())
    return text if len(text) <= width else text[: width - 3] + "..."


@dataclass
class Trace:
    events: list[Event] = field(default_factory=list)

    def add(self, kind: str, turn: int, name: str, detail: str = "", **counts: Any) -> Event:
        if kind not in KINDS:
            raise ValueError(f"unknown event kind {kind!r}; use one of {KINDS}")
        event = Event(kind, turn, name, detail, **counts)
        self.events.append(event)
        return event

    def __iter__(self):
        return iter(self.events)

    def __len__(self) -> int:
        return len(self.events)

    def of_kind(self, kind: str) -> list[Event]:
        return [event for event in self.events if event.kind == kind]

    def summary(self) -> dict[str, Any]:
        """Totals: calls per kind, tokens and wall-clock seconds."""
        return {
            "model_calls": len(self.of_kind("model")),
            "tool_calls": len(self.of_kind("tool")),
            "denied": len(self.of_kind("denied")),
            "validator_notes": len(self.of_kind("validator")),
            "compactions": len(self.of_kind("compact")),
            "budget_stops": len(self.of_kind("budget")),
            "input_tokens": sum(e.input_tokens for e in self.events),
            "output_tokens": sum(e.output_tokens for e in self.events),
            "seconds": round(sum(e.seconds for e in self.events), 2),
        }

    def show(self, width: int = 90) -> None:
        """Print the step log, one line per event."""
        print(f"{'turn':>4}  {'kind':<9} {'name':<22} {'in/out tokens':>14} {'s':>6}  detail")
        for event in self.events:
            tokens = f"{event.input_tokens}/{event.output_tokens}" if event.kind == "model" else ""
            seconds = f"{event.seconds:.1f}" if event.seconds else ""
            print(
                f"{event.turn:>4}  {event.kind:<9} {short(event.name, 22):<22} {tokens:>14} "
                f"{seconds:>6}  {short(event.detail, width)}"
            )

    def to_frame(self):
        """The events as a pandas DataFrame (pandas is imported only here)."""
        import pandas as pd

        return pd.DataFrame([asdict(event) for event in self.events], columns=list(Event.__dataclass_fields__))
