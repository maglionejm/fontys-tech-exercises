"""The tools the agents in this module use: they read this very repository.

Every tool is rooted at the repository root, so an answer can be checked by
opening the file it names. The guards in ``_resolve`` are guardrails: code
that runs before the tool does, whatever the model asked for.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from .tools import tool

MODULE_FOLDER = "M5 - Harness Engineering"
BLOCKED_FOLDERS = {".git", ".venv", ".claude", "__pycache__", ".ipynb_checkpoints", ".ruff_cache"}
MAX_CHARS = 20_000

_ROOT_OVERRIDE: Path | None = None
_NOTES_PATH = Path(tempfile.gettempdir()) / "harness-notes.md"


def repo_root(start: str | Path | None = None) -> Path:
    """Walk up from ``start`` (default: the working directory) to the repository root.

    The root is the first folder that holds both ``README.md`` and the module
    folder. ``set_repo_root`` (used on Colab) or the ``HARNESS_REPO_ROOT``
    variable override the search.
    """
    if _ROOT_OVERRIDE is not None:
        return _ROOT_OVERRIDE
    if os.environ.get("HARNESS_REPO_ROOT"):
        return Path(os.environ["HARNESS_REPO_ROOT"]).resolve()
    here = Path(start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        if (folder / "README.md").exists() and (folder / MODULE_FOLDER).is_dir():
            return folder
    raise FileNotFoundError(
        "Could not find the repository root (a folder with README.md and "
        f"'{MODULE_FOLDER}/'). Start the notebook from inside the repository "
        "or call set_repo_root(path)."
    )


def set_repo_root(path: str | Path | None) -> Path | None:
    """Root the tools at ``path`` (Colab downloads the files into ``repo/``)."""
    global _ROOT_OVERRIDE
    _ROOT_OVERRIDE = Path(path).resolve() if path is not None else None
    return _ROOT_OVERRIDE


def _resolve(path: str) -> Path:
    """Turn a repository-relative path into an absolute one, or refuse."""
    root = repo_root()
    target = (root / path).resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"Refused: {path!r} is outside the repository.")
    relative_parts = target.relative_to(root).parts
    blocked = BLOCKED_FOLDERS.intersection(relative_parts)
    if blocked:
        raise ValueError(f"Refused: {path!r} is inside a protected folder ({sorted(blocked)[0]}).")
    name = target.name
    if (name == ".env" or name.endswith(".env") or name.startswith(".env.")) and name != ".env.example":
        raise ValueError(f"Refused: {path!r} looks like a credentials file (.env). This is a guardrail.")
    return target


def _hidden(name: str) -> bool:
    """Dotfiles (except .github), caches and local scratch are not listed."""
    return (name.startswith(".") and name != ".github") or name in {"__pycache__", ".ipynb_checkpoints"} or name.startswith(".codex-")


@tool(risk="read")
def list_files(folder: str = ".") -> str:
    """List the files and folders directly under one repository folder.

    Call this first to discover what the repository contains. Folders end with '/'.
    Hidden entries (names starting with a dot, except .github) and caches are not listed.

    folder: repository-relative folder, for example '.' or '.github/workflows'
    """
    target = _resolve(folder)
    if not target.is_dir():
        raise ValueError(f"{folder!r} is not a folder in the repository.")
    names = [entry.name + "/" if entry.is_dir() else entry.name
             for entry in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
             if not _hidden(entry.name)]
    return "\n".join(names) if names else "(empty folder)"


@tool(risk="read")
def read_file(path: str) -> str:
    """Read one text file from the repository.

    Use it to look up a fact before answering; quote the path you read as a source.
    Long files are cut at 20,000 characters.

    path: repository-relative path, for example README.md or .github/workflows/ci.yml
    """
    target = _resolve(path)
    if not target.is_file():
        raise ValueError(f"{path!r} is not a file in the repository.")
    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path!r} is not a text file.") from exc
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + f"\n[... truncated at {MAX_CHARS} characters of {len(text)}]"
    return text


def set_notes_path(path: str | Path) -> Path:
    """Choose where ``write_note`` appends (default: a file in the temp folder)."""
    global _NOTES_PATH
    _NOTES_PATH = Path(path)
    return _NOTES_PATH


def clear_notes() -> None:
    """Delete the notes file, if it exists."""
    if _NOTES_PATH.exists():
        _NOTES_PATH.unlink()


@tool(risk="write")
def write_note(text: str) -> str:
    """Append one line to a notes file that survives between turns and runs.

    text: the note to remember, one line
    """
    _NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _NOTES_PATH.open("a", encoding="utf-8") as handle:
        handle.write(text.strip().replace("\n", " ") + "\n")
    return f"Saved note ({_NOTES_PATH.name} now has {sum(1 for _ in _NOTES_PATH.open(encoding='utf-8'))} lines)."


@tool(risk="read")
def read_notes() -> str:
    """Return every note saved so far with write_note, one per line."""
    if not _NOTES_PATH.exists():
        return "(no notes yet)"
    return _NOTES_PATH.read_text(encoding="utf-8") or "(no notes yet)"


@tool(risk="danger")
def run_shell(command: str) -> str:
    """Run a shell command inside the repository and return its output.

    command: the command line, for example 'wc -l README.md'
    """
    done = subprocess.run(
        command, shell=True, cwd=repo_root(), capture_output=True, text=True, timeout=30
    )
    output = (done.stdout + done.stderr).strip()
    return output or f"(no output, exit code {done.returncode})"
