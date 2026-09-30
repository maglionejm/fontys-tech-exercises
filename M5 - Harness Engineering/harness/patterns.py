"""The five workflow patterns from "Building effective agents", as small functions.

A workflow is a path you wrote in code with model steps inside. These helpers
compose Agents (or any callable that maps text to text) into those paths.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from .agent import Agent, RunResult

Step = Callable[[str], str]


def as_step(agent: Agent, template: str = "{input}") -> Step:
    """Turn an agent into a text-to-text step; the template places the input."""
    return lambda text: agent.run(template.format(input=text)).answer


def chain(steps: list[Step], task: str) -> list[str]:
    """Prompt chaining: each step consumes the previous step's output."""
    outputs: list[str] = []
    current = task
    for step in steps:
        current = step(current)
        outputs.append(current)
    return outputs


def route(classifier: Agent, routes: dict[str, Agent], task: str,
          default: Agent | None = None) -> tuple[str, RunResult]:
    """Routing: classify first, then send the task to a specialist."""
    label = classifier.run(task).answer.strip().strip('"').lower()
    target = routes.get(label) or default or next(iter(routes.values()))
    return label, target.run(task)


def parallel(factory: Callable[[], Agent], tasks: list[str],
             max_workers: int = 4) -> list[RunResult]:
    """Parallelization (sectioning): independent tasks, fresh agent each, run at once."""
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(lambda t: factory().run(t), tasks))


def vote(factory: Callable[[], Agent], task: str, n: int = 3) -> tuple[str, list[RunResult]]:
    """Parallelization (voting): the same task several times, majority answer wins."""
    results = parallel(factory, [task] * n)
    answers = [r.answer for r in results]
    winner = max(set(answers), key=answers.count)
    return winner, results


def orchestrate(planner: Agent, worker_factory: Callable[[], Agent], synthesizer: Agent,
                task: str) -> dict[str, Any]:
    """Orchestrator-workers: plan subtasks at run time, delegate, synthesize."""
    plan_text = planner.run(task).answer
    try:
        subtasks = json.loads(plan_text)
    except json.JSONDecodeError:
        subtasks = [line.strip("- ").strip() for line in plan_text.splitlines() if line.strip()]
    results = parallel(worker_factory, subtasks)
    report = "\n".join(f"- {r.answer}" for r in results)
    final = synthesizer.run(f"Combine these findings into one answer:\n{report}")
    return {"subtasks": subtasks, "worker_results": results, "final": final,
            "tokens": sum(r.tokens for r in results) + final.tokens}


def evaluate_optimize(generator: Agent, evaluator: Agent, task: str,
                      max_rounds: int = 3) -> dict[str, Any]:
    """Evaluator-optimizer: draft, judge, revise until the judge passes or rounds run out."""
    history: list[dict[str, Any]] = []
    prompt = task
    for round_no in range(1, max_rounds + 1):
        draft = generator.run(prompt)
        verdict_text = evaluator.run(draft.answer).answer
        try:
            verdict = json.loads(verdict_text)
        except json.JSONDecodeError:
            verdict = {"pass": "pass" in verdict_text.lower(), "reason": verdict_text}
        history.append({"round": round_no, "draft": draft.answer, "verdict": verdict})
        if verdict.get("pass"):
            return {"answer": draft.answer, "rounds": round_no, "history": history, "passed": True}
        prompt = f"{task}\n\nYour previous draft was rejected: {verdict.get('reason')}. Improve it."
    return {"answer": history[-1]["draft"], "rounds": max_rounds, "history": history,
            "passed": False}
