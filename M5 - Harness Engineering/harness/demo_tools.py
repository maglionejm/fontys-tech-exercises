"""The module's demo tools: a tiny document library plus a few utilities.

The library (harness/corpus/*.md) holds the module's own reading material, so
the agent researches harness engineering while you study harness engineering.
"""
from __future__ import annotations

import ast
import io
import json
import math
import operator
import re
from contextlib import redirect_stdout
from pathlib import Path

from .context import Notes
from .tools import Tool, ToolRegistry, tool

CORPUS_DIR = Path(__file__).parent / "corpus"
STOPWORDS = set("""a an and are as at be by for from has have how in into is it its of on or that the
this to was were what when where which who why will with does did do you your we our they their than
then there these those also can could should would may might one two three year years""".split())


def keywords(text: str) -> list[str]:
    """Lowercase content words, in order of first appearance."""
    seen: list[str] = []
    for w in re.findall(r"[a-z0-9][a-z0-9\-]+", text.lower()):
        if len(w) > 2 and w not in STOPWORDS and w not in seen:
            seen.append(w)
    return seen


def load_corpus(directory: str | Path = CORPUS_DIR) -> dict[str, dict[str, str]]:
    docs: dict[str, dict[str, str]] = {}
    for path in sorted(Path(directory).glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        first, _, rest = text.partition("\n")
        docs[path.stem] = {"id": path.stem, "title": first.lstrip("# ").strip(),
                           "text": rest.strip()}
    return docs


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]


@tool
def search_docs(query: str, k: int = 3) -> str:
    """Search the course library for documents about a topic. Returns the best matches as JSON with id, title, score and a snippet; call read_doc with an id to get the full text.

    query: the key terms to look for, a few words, no full sentences
    k: how many results to return, default 3
    """
    terms = keywords(query)
    corpus = load_corpus()
    doc_freq = {t: sum(1 for d in corpus.values() if t in (d["title"] + " " + d["text"]).lower())
                for t in terms}
    scored = []
    for doc in corpus.values():
        body = (doc["title"] + " " + doc["text"]).lower()
        title = doc["title"].lower()
        # rare terms count more than common ones; a hit in the title counts extra
        score = round(sum((1 + 2 * (t in title)) * math.log(1 + len(corpus) / doc_freq[t])
                          for t in terms if t in body), 2)
        if score:
            hit = next((s for s in sentences(doc["text"]) if any(t in s.lower() for t in terms)), "")
            scored.append({"id": doc["id"], "title": doc["title"], "score": score,
                           "snippet": hit[:160]})
    scored.sort(key=lambda d: (-d["score"], d["id"]))
    return json.dumps(scored[: max(1, int(k))], ensure_ascii=False)


@tool
def read_doc(doc_id: str) -> str:
    """Read one document from the course library in full.

    doc_id: the id returned by search_docs
    """
    doc = load_corpus().get(doc_id)
    if doc is None:
        return f"Error: no document with id '{doc_id}'. Use search_docs to find ids."
    return f"id: {doc['id']}\ntitle: {doc['title']}\n\n{doc['text']}"


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.USub: operator.neg, ast.UAdd: operator.pos}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("only numbers and + - * / ** % are allowed")


@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression exactly. Use it for any calculation instead of estimating.

    expression: numbers and the operators + - * / ** % with parentheses, for example (891 - 179) / 891
    """
    value = _eval(ast.parse(expression, mode="eval").body)
    return f"{value:g}" if isinstance(value, float) else str(value)


_notes = Notes("outputs/notes.md")


@tool(risk="write")
def write_note(text: str) -> str:
    """Save a fact or decision to the persistent notes file so it survives context compaction.

    text: one line, the fact itself, with its source if you have one
    """
    return _notes.append(text)


@tool
def read_notes() -> str:
    """Read everything saved with write_note so far."""
    return _notes.read() or "(no notes yet)"


CITATION = re.compile(r"\[source:\s*([a-z0-9\-]+)\]")


MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december")


@tool
def check_citation(answer: str, question: str = "") -> str:
    """Verify a draft answer before giving it: it must cite a library document as [source: id], the document must contain the answer's key terms and every year in it, and it must address the question. Returns OK or PROBLEM with the reason.

    answer: the full draft answer including its [source: id] tag
    question: the question being answered, so the check can see whether the answer addresses it
    """
    ids = CITATION.findall(answer)
    if not ids:
        return "PROBLEM: the answer has no [source: id] citation."
    docs = load_corpus()
    missing = [i for i in ids if i not in docs]
    if missing:
        return f"PROBLEM: cited document(s) {missing} do not exist in the library."
    claim_terms = [t for t in keywords(CITATION.sub("", answer)) if not t.isdigit()]
    for i in ids:
        body = docs[i]["text"].lower()
        supported = sum(1 for t in claim_terms if t in body)
        if claim_terms and supported < max(2, len(claim_terms) // 3):
            return f"PROBLEM: document '{i}' does not support the answer's key terms."
        for y in re.findall(r"\b(?:19|20)\d{2}\b", CITATION.sub("", answer)):
            if y not in body:
                return f"PROBLEM: the year {y} does not appear in '{i}'."
        if question:
            q_terms = [t for t in keywords(question) if len(t) > 3 and not t.isdigit()]
            missing = [t for t in q_terms if t not in body and t.rstrip("s") not in body]
            if q_terms and len(missing) > len(q_terms) // 2:
                return (f"PROBLEM: document '{i}' does not address the question; it never "
                        f"mentions {missing}.")
            anchors = re.findall(r"\b(?:19|20)\d{2}\b", question) + [m for m in MONTHS
                                                                    if m in question.lower()]
            unmet = [a for a in anchors if a.lower() not in answer.lower()]
            if unmet:
                return f"PROBLEM: the question asks about {unmet}, but the answer never mentions it."
    return f"OK: {len(ids)} citation(s) checked against the library."


@tool(risk="danger")
def run_python(code: str) -> str:
    """Run a short Python snippet and return what it prints. Dangerous: it executes arbitrary code on this machine.

    code: the Python source to execute
    """
    buffer = io.StringIO()
    scope: dict = {}
    with redirect_stdout(buffer):
        exec(code, scope)  # noqa: S102 - intentionally unsafe; the harness must gate it
    return buffer.getvalue() or "(no output)"


ALL_TOOLS: list[Tool] = [search_docs, read_doc, calculator, write_note, read_notes,
                         check_citation, run_python]


def demo_registry(*names: str) -> ToolRegistry:
    """A registry with the named tools, or all of them."""
    chosen = [t for t in ALL_TOOLS if not names or t.name in names]
    return ToolRegistry(chosen)
