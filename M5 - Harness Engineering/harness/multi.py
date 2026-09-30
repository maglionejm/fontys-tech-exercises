"""Sub-agents, agent teams and handoffs.

Sub-agent: a fresh agent with a clean context, one focused task, a short
report back. Team: several agents working a shared task board in parallel
and messaging each other; a lead synthesizes. Handoff: one agent passes the
whole conversation to another.
"""
from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable

from .agent import Agent, RunResult
from .messages import Message
from .tools import Tool, tool


class SubAgentPool:
    """Creates isolated sub-agents on demand and remembers what each one did."""

    def __init__(self, factory: Callable[[], Agent], summary_chars: int = 600):
        self.factory = factory
        self.summary_chars = summary_chars
        self.records: list[RunResult] = []

    def run(self, task: str) -> str:
        result = self.factory().run(task)
        self.records.append(result)
        report = result.answer[: self.summary_chars]
        return f"{report}\n(sub-agent used {result.turns} turns, ~{result.tokens} tokens)"

    def delegate_tool(self, name: str = "delegate",
                      description: str | None = None) -> Tool:
        """A tool the lead agent can call to hand one focused task to a sub-agent."""
        pool = self

        @tool(name=name, description=description or (
            "Delegate one focused sub-question to a fresh sub-agent with its own clean "
            "context. It searches and reads on its own and returns a short cited report. "
            "Use one call per sub-question."))
        def delegate(task: str) -> str:
            """task: one self-contained sub-question"""
            return pool.run(task)

        return delegate

    @property
    def tokens(self) -> int:
        return sum(r.tokens for r in self.records)


@dataclass
class TaskItem:
    id: int
    description: str
    status: str = "todo"        # todo -> doing -> done
    owner: str | None = None
    result: str | None = None


class TaskBoard:
    """The shared to-do list of an agent team. Thread-safe."""

    def __init__(self, tasks: list[str] = ()):
        self._lock = threading.Lock()
        self.items = [TaskItem(i + 1, t) for i, t in enumerate(tasks)]
        self.log: list[str] = []

    def add(self, description: str) -> TaskItem:
        with self._lock:
            item = TaskItem(len(self.items) + 1, description)
            self.items.append(item)
            return item

    def claim(self, owner: str) -> TaskItem | None:
        with self._lock:
            for item in self.items:
                if item.status == "todo":
                    item.status, item.owner = "doing", owner
                    self.log.append(f"{owner} claimed #{item.id}")
                    return item
            return None

    def complete(self, item: TaskItem, result: str) -> None:
        with self._lock:
            item.status, item.result = "done", result
            self.log.append(f"{item.owner} finished #{item.id}")

    def done(self) -> list[TaskItem]:
        return [i for i in self.items if i.status == "done"]

    def show(self) -> None:
        for i in self.items:
            print(f"#{i.id} [{i.status:<5}] {i.owner or '-':<8} {i.description[:70]}")


class Mailbox:
    """Direct messages between teammates."""

    def __init__(self):
        self._lock = threading.Lock()
        self.messages: list[dict[str, str]] = []

    def send(self, sender: str, to: str, text: str) -> None:
        with self._lock:
            self.messages.append({"from": sender, "to": to, "text": text})

    def read(self, name: str) -> list[dict[str, str]]:
        with self._lock:
            return [m for m in self.messages if m["to"] in (name, "all")]


@dataclass
class Team:
    """A flat team: teammates pull tasks from the board; the lead synthesizes."""

    lead: Agent
    teammates: dict[str, Callable[[], Agent]]
    board: TaskBoard
    mailbox: Mailbox = field(default_factory=Mailbox)
    results: dict[str, list[RunResult]] = field(default_factory=dict)

    def _work(self, name: str) -> None:
        factory = self.teammates[name]
        while (item := self.board.claim(name)) is not None:
            result = factory().run(item.description)
            self.results.setdefault(name, []).append(result)
            self.board.complete(item, result.answer)
            self.mailbox.send(name, self.lead.name, f"Task #{item.id} done: {result.answer[:200]}")

    def run(self) -> RunResult:
        with ThreadPoolExecutor(max_workers=len(self.teammates)) as pool:
            list(pool.map(self._work, list(self.teammates)))
        report = "\n".join(f"- {i.result}" for i in self.board.done())
        return self.lead.run(f"Combine these findings into one answer:\n{report}")

    @property
    def tokens(self) -> int:
        return sum(r.tokens for rs in self.results.values() for r in rs)


def handoff(to_agent: Agent, history: list[Message], instruction: str) -> RunResult:
    """Transfer control: the next agent continues from the same conversation."""
    return to_agent.run(instruction, history=history)


def context_size(result: RunResult) -> dict[str, Any]:
    """How big the lead agent's own context got: messages and estimated tokens."""
    from .messages import total_tokens
    return {"messages": len(result.messages), "tokens": total_tokens(result.messages)}
