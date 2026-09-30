"""Deterministic stand-in behaviours for the ScriptedModel.

Each policy is a few lines of Python that decide the next message from what
the model can see. They imitate one behaviour of a real model at a time - a
confident guess, a tool-using researcher, a strict judge, a planner - so the
notebooks can show what the harness changes while the model stays fixed.
"""
from __future__ import annotations

import json
import re

from .demo_tools import MONTHS, keywords, sentences
from .messages import Message
from .models import ModelView, call, calls, say

# A tiny, slightly wrong memory: what a model "remembers" without looking anything up.
MEMORY = {
    "model context protocol": "Anthropic released the Model Context Protocol in 2023 and "
                              "Google adopted it in 2024.",
    "agent skills": "Agent Skills were introduced in 2024 as a plugin format for ChatGPT.",
    "harness": "A harness is another word for a system prompt.",
    "multi-agent": "Anthropic's multi-agent research system used 3 subagents and cut token "
                   "use by half.",
    "function calling": "OpenAI introduced function calling in 2022.",
}


def memory_answer(task: str) -> str:
    low = task.lower()
    for key, fact in MEMORY.items():
        if key in low:
            return fact
    return "I am not sure, but I believe the answer is 2024."


def bare_policy(view: ModelView) -> Message:
    """No tools, no checks: answer from memory, confidently."""
    return say(memory_answer(view.task))


def prompted_policy(view: ModelView) -> Message:
    """Follows a better prompt: hedges when unsure, still cannot look anything up."""
    if "if you are not sure" in view.system.lower() or "say so" in view.system.lower():
        return say("I am not certain. From memory: " + memory_answer(view.task)
                   + " Please verify this against a source.")
    return say(memory_answer(view.task))


def _hits(search_result: str | None) -> list[dict]:
    """Parse search_docs output; a denial or error message counts as no hits."""
    try:
        hits = json.loads(search_result or "[]")
    except json.JSONDecodeError:
        return []
    return hits if isinstance(hits, list) else []


def _doc_id(read_result: str) -> str:
    m = re.match(r"id:\s*([a-z0-9\-]+)", read_result)
    return m.group(1) if m else "unknown"


def compose_answer(task: str, read_result: str, max_sentences: int = 2) -> str:
    """Pick the document sentences that together best cover the question, then cite it."""
    terms = keywords(task)
    header, _, body = read_result.partition("\n\n")
    body = body.split("\n\nSources:")[0]                 # the trailer lists sources, not facts
    title = header.lower()
    anchors = re.findall(r"\b(?:19|20)\d{2}\b", task.lower()) + [m for m in MONTHS if m in task.lower()]
    distinctive = [t for t in terms if t not in title] + anchors

    def weight(term: str) -> int:           # a date beats a rare word beats a title word
        return 3 if any(ch.isdigit() for ch in term) else 1 if term in title else 2

    def covered(s: str) -> set[str]:
        low = s.lower()
        return {t for t in distinctive if t in low}

    def rank(s: str) -> tuple[int, int]:
        low = s.lower()
        score = sum(weight(t) for t in terms if t in low) + (2 if re.search(r"\b(?:19|20)\d{2}\b", low) else 0)
        return (-len(covered(s)), -score)

    cands = [s for s in sentences(body) if any(t in s.lower() for t in terms)]
    if not cands:
        return f"The document says nothing on this. [source: {_doc_id(read_result)}]"
    ranked = sorted(cands, key=rank)
    chosen, seen = [ranked[0]], covered(ranked[0])
    for _ in range(max_sentences - 1):      # add the sentence that covers the most NEW question terms
        rest = [s for s in ranked if s not in chosen]
        best = max(rest, key=lambda s: (len(covered(s) - seen),
                                        sum(1 for a in anchors if a in s.lower()),
                                        -ranked.index(s)), default=None)
        if best is None or not (covered(best) - seen):
            break
        chosen.append(best)
        seen |= covered(best)
    chosen.sort(key=cands.index)             # keep the document's order for readability
    return f"{' '.join(chosen)} [source: {_doc_id(read_result)}]"


def research_policy(view: ModelView) -> Message:
    """Search, read, draft, verify if a checker exists, then answer with a citation."""
    if view.has_tool("search_docs") and not view.called("search_docs"):
        return call("search_docs", query=" ".join(keywords(view.task)[:6]), k=3)
    if view.has_tool("read_doc") and not view.called("read_doc"):
        hits = _hits(view.last_result("search_docs"))
        if hits:
            return call("read_doc", doc_id=hits[0]["id"])
        return say("I searched the library and found nothing relevant, so I cannot answer "
                   "with a source.")
    doc = view.last_result("read_doc")
    if doc is not None and doc.startswith(("Error", "Denied")):
        doc = None
    draft = compose_answer(view.task, doc) if doc else memory_answer(view.task)
    if view.has_tool("check_citation"):
        verdict = view.last_result("check_citation")
        if verdict is None:
            return call("check_citation", answer=draft, question=view.task)
        if verdict.startswith("PROBLEM") and view.times_called("read_doc") < 2:
            hits = _hits(view.last_result("search_docs"))
            if len(hits) > 1:                      # try the runner-up document once
                return call("read_doc", doc_id=hits[1]["id"])
        if verdict.startswith("PROBLEM"):
            return say("I could not verify an answer against the library. " + draft.split(" [source")[0]
                       + " (unverified)")
    return say(draft)


def judge_policy(view: ModelView) -> Message:
    """An evaluator: passes an answer only if it is cited and specific."""
    text = view.task
    has_source = "[source:" in text
    has_year = bool(re.search(r"\b(?:19|20)\d{2}\b", text))
    verdict = {"pass": has_source and has_year,
               "reason": ("cited and specific" if has_source and has_year
                          else "missing a [source: id] citation" if not has_source
                          else "no concrete date or number")}
    return say(json.dumps(verdict))


def router_policy(view: ModelView) -> Message:
    """Classify the task into one of the labels named in the system prompt."""
    labels = re.findall(r"Labels:\s*(.+)", view.system)
    options = [x.strip() for x in labels[0].split(",")] if labels else ["general"]
    low = view.task.lower()
    if any(ch.isdigit() for ch in low) and any(op in low for op in "+-*/%") or "calculate" in low:
        pick = next((o for o in options if "calc" in o or "math" in o), options[0])
    elif "?" in low or any(w in low for w in ("who", "what", "when", "which", "how")):
        pick = next((o for o in options if "research" in o or "question" in o), options[0])
    else:
        pick = options[-1]
    return say(pick)


def calculator_policy(view: ModelView) -> Message:
    """Find the arithmetic in the task, ask the calculator, report the result."""
    if view.has_tool("calculator") and not view.called("calculator"):
        expr = re.search(r"[\d\.\s\+\-\*/\(\)%]{3,}", view.task)
        return call("calculator", expression=expr.group(0).strip() if expr else "0")
    result = view.last_result("calculator")
    return say(f"The result is {result}." if result else "There is nothing to calculate.")


def planner_policy(view: ModelView) -> Message:
    """Split a compound question into independent sub-questions, as a JSON list."""
    parts = re.split(r"\s+and\s+(?=[a-z]*\s*(?:when|what|who|which|how|why))|;\s*|\?\s+", view.task)
    subtasks = [p.strip().rstrip("?") + "?" for p in parts if len(p.strip()) > 8]
    return say(json.dumps(subtasks or [view.task]))


def synthesizer_policy(view: ModelView) -> Message:
    """Combine worker reports (given in the task text) into one answer, keeping citations."""
    reports = [line.strip() for line in view.task.splitlines() if line.strip().startswith("- ")]
    return say(" ".join(r[2:] for r in reports) if reports else view.task)


def echo_policy(view: ModelView) -> Message:
    return say(view.task)


def lead_policy(view: ModelView) -> Message:
    """An orchestrator: split the question, delegate each part, then synthesize the reports."""
    if view.has_tool("delegate") and not view.called("delegate"):
        parts = json.loads(planner_policy(view).content)
        return calls(*[("delegate", {"task": p}) for p in parts])
    reports = [r.content.split("\n(sub-agent")[0] for r in view.results("delegate")]
    if reports:
        return say(" ".join(reports))
    return research_policy(view)


POLICIES = {"bare": bare_policy, "prompted": prompted_policy, "research": research_policy,
            "judge": judge_policy, "router": router_policy, "calculator": calculator_policy,
            "planner": planner_policy, "synthesizer": synthesizer_policy, "echo": echo_policy,
            "lead": lead_policy}
