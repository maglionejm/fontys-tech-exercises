"""Evals: a task, a grader, an outcome, measured again and again.

Outcome graders look at the final answer. Trajectory graders look at how the
agent got there: which tools it used, how many turns, how many tokens.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from .agent import Agent, RunResult

Grader = Callable[[RunResult], bool]


def contains(*needles: str) -> Grader:
    """Outcome: the answer mentions every needle (case-insensitive)."""
    return lambda r: all(n.lower() in r.answer.lower() for n in needles)


def matches(pattern: str) -> Grader:
    return lambda r: re.search(pattern, r.answer, flags=re.IGNORECASE) is not None


def cites(doc_id: str | None = None) -> Grader:
    """Outcome: the answer carries a [source: id] tag (optionally a specific one)."""
    return lambda r: (f"[source: {doc_id}]" in r.answer) if doc_id else ("[source:" in r.answer)


def used_tool(name: str) -> Grader:
    """Trajectory: the agent called this tool at least once."""
    return lambda r: any(e.name == name for e in r.trace.tool_calls())


def max_turns(n: int) -> Grader:
    return lambda r: r.turns <= n


def finished() -> Grader:
    return lambda r: r.stopped_because == "done"


def all_of(*graders: Grader) -> Grader:
    return lambda r: all(g(r) for g in graders)


def judged_by(judge: Agent) -> Grader:
    """A model-based grader: the judge agent returns JSON with a 'pass' field."""
    import json

    def grade(r: RunResult) -> bool:
        try:
            return bool(json.loads(judge.run(r.answer).answer).get("pass"))
        except (json.JSONDecodeError, AttributeError):
            return False
    return grade


@dataclass
class EvalCase:
    name: str
    task: str
    grader: Grader
    note: str = ""


@dataclass
class EvalReport:
    config: str
    rows: list[dict[str, Any]] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return sum(r["passed"] for r in self.rows) / len(self.rows) if self.rows else 0.0

    @property
    def tokens(self) -> int:
        return sum(r["tokens"] for r in self.rows)

    def summary(self) -> dict[str, Any]:
        return {"config": self.config, "cases": len(self.rows),
                "pass_rate": round(self.pass_rate, 3),
                "mean_turns": round(sum(r["turns"] for r in self.rows) / len(self.rows), 2) if self.rows else 0,
                "tokens": self.tokens}

    def show(self) -> None:
        print(f"{self.config}: {self.pass_rate:.0%} pass ({sum(r['passed'] for r in self.rows)}"
              f"/{len(self.rows)}), ~{self.tokens} tokens")
        for r in self.rows:
            mark = "pass" if r["passed"] else "FAIL"
            print(f"  {mark}  {r['case']:<28} turns={r['turns']:<2} tools={r['tool_calls']:<2} "
                  f"{r['answer'][:60]!r}")


def run_evals(config: str, factory: Callable[[], Agent], cases: list[EvalCase]) -> EvalReport:
    """Run every case on a fresh agent from the factory and grade it."""
    report = EvalReport(config)
    for case in cases:
        result = factory().run(case.task)
        report.rows.append({"case": case.name, "passed": bool(case.grader(result)),
                            "turns": result.turns, "tool_calls": len(result.trace.tool_calls()),
                            "tokens": result.tokens, "stopped": result.stopped_because,
                            "answer": result.answer})
    return report


def compare(configs: dict[str, Callable[[], Agent]], cases: list[EvalCase]) -> dict[str, EvalReport]:
    """Run the same cases through several harness configurations."""
    return {name: run_evals(name, factory, cases) for name, factory in configs.items()}
