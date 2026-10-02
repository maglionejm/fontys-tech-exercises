"""YAML loading, graders and the report."""
from __future__ import annotations

import json
from pathlib import Path

from conftest import response, text_block, tool_use_block

from harness import Agent, EvalCase, Trace, Usage, grade, load_cases, run_evals
from harness.evals import Report, Row, read_results, write_results
from harness.loop import RunResult

CASES = Path(__file__).resolve().parents[1] / "evals" / "cases.yaml"


def fake_result(answer: dict | None, turns=2, tool_names=()) -> RunResult:
    trace = Trace()
    for name in tool_names:
        trace.add("tool", 1, name)
    text = json.dumps(answer) if answer is not None else "plain text"
    return RunResult(text, answer, [], turns, "done", Usage(100, 10), 0.001, trace, "claude-sonnet-5")


def test_cases_load_with_eleven_facts_and_traps():
    cases = load_cases(CASES)
    assert len(cases) >= 12
    traps = [c for c in cases if c.expect.get("found") is False]
    facts = [c for c in cases if c.expect.get("found") is True]
    assert len(facts) >= 11 and len(traps) >= 1
    assert all(c.task and c.name for c in cases)
    assert all("source_file" in c.expect for c in facts)


def test_graders_pass_a_correct_structured_answer():
    case = EvalCase("licence", "licence?", {"contains": ["MIT"], "source_file": "LICENSE", "found": True,
                                            "max_turns": 3, "used_tool": "read_file"})
    ok = fake_result({"answer": "It uses the MIT licence.", "sources": ["./LICENSE"], "found": True},
                     turns=3, tool_names=["list_files", "read_file"])
    assert grade(case, ok) == []


def test_graders_name_every_failure():
    case = EvalCase("licence", "licence?", {"contains": ["MIT"], "not_contains": ["GPL"], "source_file": "LICENSE",
                                            "found": True, "max_turns": 2, "used_tool": "read_file"})
    bad = fake_result({"answer": "GPL, I think", "sources": [], "found": False}, turns=4)
    problems = grade(case, bad)
    assert len(problems) == 6
    assert any("lacks 'MIT'" in p for p in problems) and any("GPL" in p for p in problems)


def test_source_paths_keep_their_leading_dot():
    # Regression: an early grader stripped every leading dot and failed '.github/...' sources.
    case = EvalCase("wf", "python?", {"source_file": ".github/workflows/notebooks.yml"})
    ok = fake_result({"answer": "3.12", "sources": ["./.github/workflows/notebooks.yml"], "found": True})
    assert grade(case, ok) == []
    assert grade(case, fake_result({"answer": "3.12", "sources": ["/LICENSE"], "found": True})) == [
        "sources ['LICENSE'] lack '.github/workflows/notebooks.yml'"]


def test_trap_grader_needs_a_structured_false():
    case = EvalCase("trap", "dean?", {"found": False})
    assert grade(case, fake_result({"answer": "Not in the repository.", "sources": [], "found": False})) == []
    assert grade(case, fake_result({"answer": "Dr X", "sources": [], "found": True})) == ["found=True expected False"]
    assert grade(case, fake_result(None)) == ["no structured answer"]


def test_run_evals_on_a_stub_client(stub_client):
    good = json.dumps({"answer": "MIT licence", "sources": ["LICENSE"], "found": True})

    def factory():
        return Agent(stub_client([
            response([tool_use_block("read_file", {"path": "LICENSE"})], stop_reason="tool_use"),
            response([text_block(good)]),
        ]), tools=[], output_schema={"type": "object"})

    cases = [EvalCase("licence", "licence?", {"contains": ["MIT"], "found": True}),
             EvalCase("trap", "dean?", {"found": False})]
    report = run_evals("B", factory, cases, workers=2)
    assert report.pass_rate == 0.5 and len(report.rows) == 2
    assert report.usage.input_tokens == 400 and report.cost_usd > 0


def test_results_round_trip(tmp_path):
    row = Row("A", "licence", True, [], "MIT", True, ["LICENSE"], 2, "done", 100, 10, 0.001, 1.0)
    path = write_results({"A": Report("A", [row], Usage(100, 10))}, tmp_path / "results.json")
    loaded = read_results(path)
    assert loaded[0]["name"] == "A" and loaded[0]["pass_rate"] == 1.0 and loaded[0]["rows"][0]["case"] == "licence"
