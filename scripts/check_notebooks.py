#!/usr/bin/env python3
"""Static checks for every notebook in the repository. No kernel is started.

Checks, per notebook:
  1. valid nbformat 4 structure
  2. committed executed outputs (students read results on GitHub without running)
  3. no error outputs left in place
  4. no secrets or personal paths in sources, outputs or metadata
  5. a level-1 title in the first markdown cell

Exit code 1 when any check fails. Used by `make check` and the CI workflow.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted(ROOT.glob("M*/**/*.ipynb"))

SECRET_PATTERNS = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "OpenAI key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}"),
    "Anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    "env assignment with a value": re.compile(r"ANTHROPIC_API_KEY\s*=\s*\S{8,}"),
    "Hugging Face token": re.compile(r"\bhf_[A-Za-z0-9]{20,}"),
    "GitHub token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"),
    "Google API key": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "Slack token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "private key": re.compile(r"BEGIN (?:RSA|EC|OPENSSH|PGP|DSA) PRIVATE KEY"),
    "JWT": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}"),
    "assigned secret": re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password|passwd)\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']"
    ),
    "local user path": re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/"),
}


def text_of(cell) -> str:
    parts = ["".join(cell.get("source", ""))]
    for out in cell.get("outputs", []) or []:
        if "text" in out:
            parts.append("".join(out["text"]))
        for mime, payload in (out.get("data") or {}).items():
            if mime.startswith("text/") or mime.endswith("json"):
                parts.append(payload if isinstance(payload, str) else json.dumps(payload))
    return "\n".join(parts)


def check(path: Path) -> list[str]:
    problems: list[str] = []
    try:
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
    except Exception as exc:  # noqa: BLE001 - report any structural failure
        return [f"invalid notebook: {exc}"]

    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    with_outputs = [c for c in code_cells if c.get("outputs")]
    if code_cells and not with_outputs:
        problems.append("no executed outputs committed")
    for idx, cell in enumerate(nb.cells):
        for out in cell.get("outputs", []) or []:
            if out.get("output_type") == "error":
                problems.append(f"cell {idx}: error output left in notebook ({out.get('ename')})")
        blob = text_of(cell)
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(blob):
                problems.append(f"cell {idx}: looks like a {name}")

    meta_blob = json.dumps(nb.metadata)
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(meta_blob):
            problems.append(f"metadata: looks like a {name}")

    first_md = next((c for c in nb.cells if c.cell_type == "markdown"), None)
    if first_md is None or not "".join(first_md.source).lstrip().startswith("# "):
        problems.append("first markdown cell is not a level-1 title")
    return problems


def main() -> int:
    if not NOTEBOOKS:
        print("no notebooks found", file=sys.stderr)
        return 1
    failures = 0
    for path in NOTEBOOKS:
        problems = check(path)
        rel = path.relative_to(ROOT)
        if problems:
            failures += 1
            print(f"FAIL  {rel}")
            for p in problems:
                print(f"      - {p}")
        else:
            print(f"ok    {rel}")
    print(f"\n{len(NOTEBOOKS) - failures}/{len(NOTEBOOKS)} notebooks pass")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
