"""Evals: a task, a grader, an outcome, measured again and again.

Cases live in ``evals/cases.yaml``. Agents under eval answer with a structured
object (``answer``, ``sources``, ``found``) so the graders check fields, not
magic sentences.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from .client import Usage
from .loop import Agent, RunResult

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string", "description": "The fact in one or two sentences, or why it cannot be found."},
        "sources": {"type": "array", "items": {"type": "string"},
                    "description": "Repository-relative paths of the files that support the answer."},
        "found": {"type": "boolean", "description": "true only when the repository contains the answer."},
    },
    "required": ["answer", "sources", "found"],
    "additionalProperties": False,
}

RESEARCHER_SYSTEM = (
    "You answer questions about the code repository you are running in. "
    "Look things up with list_files and read_file before answering; never guess. "
    "Reply with the structured object: put the fact in `answer`, list in `sources` the "
    "repository-relative paths of the files you read that support it, and set `found` to true. "
    "If the repository does not contain the answer, set `found` to false, leave `sources` empty "
    "and say in `answer` that the repository does not contain it. Write numbers as digits."
)
RESEARCHER_SYSTEM_NO_TOOLS = (
    "You answer questions about a code repository, but you have no tools to read it. "
    "Reply with the structured object: `answer`, `sources` (repository-relative paths you are sure "
    "support the answer) and `found` (true only when you are certain the repository contains the answer)."
)


@dataclass
class EvalCase:
    name: str
    task: str
    expect: dict[str, Any] = field(default_factory=dict)


def load_cases(path: str | Path) -> list[EvalCase]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    items = data["cases"] if isinstance(data, dict) else data
    return [EvalCase(item["name"], item["task"], dict(item.get("expect") or {})) for item in items]


def normalise_path(source: Any) -> str:
    """'./LICENSE' and '/LICENSE' become 'LICENSE'; a leading dot in '.github' is kept."""
    text = str(source).strip()
    while text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def grade(case: EvalCase, result: RunResult) -> list[str]:
    """Return the list of failed checks (empty means the case passed)."""
    parsed = result.parsed or {}
    answer = str(parsed.get("answer", result.answer))
    sources = [normalise_path(s) for s in parsed.get("sources", [])]
    problems = []
    for needle in case.expect.get("contains", []):
        if str(needle).lower() not in answer.lower():
            problems.append(f"answer lacks {needle!r}")
    for needle in case.expect.get("not_contains", []):
        if str(needle).lower() in answer.lower():
            problems.append(f"answer mentions {needle!r}")
    if "source_file" in case.expect:
        wanted = case.expect["source_file"]
        if not any(s == wanted or s.endswith("/" + wanted) for s in sources):
            problems.append(f"sources {sources} lack {wanted!r}")
    if "found" in case.expect:
        if not result.parsed:
            problems.append("no structured answer")
        elif bool(parsed.get("found")) != bool(case.expect["found"]):
            problems.append(f"found={parsed.get('found')} expected {case.expect['found']}")
    if "max_turns" in case.expect and result.turns > case.expect["max_turns"]:
        problems.append(f"{result.turns} turns > {case.expect['max_turns']}")
    if "used_tool" in case.expect:
        if not any(e.name == case.expect["used_tool"] for e in result.trace.of_kind("tool")):
            problems.append(f"never called {case.expect['used_tool']!r}")
    return problems


@dataclass
class Row:
    config: str
    case: str
    passed: bool
    failures: list[str]
    answer: str
    found: bool | None
    sources: list[str]
    turns: int
    stopped_because: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    seconds: float


@dataclass
class Report:
    name: str
    rows: list[Row] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)

    @property
    def pass_rate(self) -> float:
        return round(sum(r.passed for r in self.rows) / len(self.rows), 3) if self.rows else 0.0

    @property
    def cost_usd(self) -> float:
        return round(sum(r.cost_usd for r in self.rows), 4)

    def failures(self) -> list[Row]:
        return [r for r in self.rows if not r.passed]

    def show(self) -> None:
        print(f"{self.name}: {sum(r.passed for r in self.rows)}/{len(self.rows)} passed "
              f"({self.pass_rate:.0%}), {self.usage.total_input} in / {self.usage.output_tokens} out tokens, "
              f"${self.cost_usd:.4f}")
        for row in self.rows:
            mark = "ok  " if row.passed else "FAIL"
            note = "; ".join(row.failures) if row.failures else f"found={row.found} sources={row.sources}"
            print(f"  {mark} {row.case:<22} turns={row.turns} ${row.cost_usd:.4f}  {note[:90]}")

    def to_frame(self):
        import pandas as pd

        return pd.DataFrame([asdict(r) for r in self.rows])

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "pass_rate": self.pass_rate, "cost_usd": self.cost_usd,
                "usage": self.usage.as_dict(), "rows": [asdict(r) for r in self.rows]}

    def to_json(self, path: str | Path) -> Path:
        return write_results({self.name: self}, path)


def run_case(name: str, agent_factory: Callable[[], Agent], case: EvalCase) -> tuple[Row, Usage]:
    tick = time.perf_counter()
    result = agent_factory().run(case.task)
    failures = grade(case, result)
    parsed = result.parsed or {}
    row = Row(name, case.name, not failures, failures, str(parsed.get("answer", result.answer))[:400],
              parsed.get("found"), [str(s) for s in parsed.get("sources", [])], result.turns,
              result.stopped_because, result.usage.total_input, result.usage.output_tokens,
              result.cost_usd, round(time.perf_counter() - tick, 1))
    return row, result.usage


def run_evals(name: str, agent_factory: Callable[[], Agent], cases: list[EvalCase], workers: int = 4) -> Report:
    """Run every case on a fresh agent, four at a time; grade; return one Report."""
    report = Report(name)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for row, usage in pool.map(lambda c: run_case(name, agent_factory, c), cases):
            report.rows.append(row)
            report.usage = report.usage + usage
    return report


def compare(factories: dict[str, Callable[[], Agent]], cases: list[EvalCase], workers: int = 4) -> dict[str, Report]:
    """The same cases through several harness configurations, one Report each."""
    return {name: run_evals(name, factory, cases, workers) for name, factory in factories.items()}


def write_results(reports: dict[str, Report], path: str | Path) -> Path:
    target = Path(path)
    target.write_text(json.dumps({"reports": [r.to_dict() for r in reports.values()]}, indent=1), encoding="utf-8")
    return target


def read_results(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["reports"] if "reports" in data else [data]
