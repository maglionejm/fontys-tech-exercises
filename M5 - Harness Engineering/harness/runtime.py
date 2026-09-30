"""Which engine sits behind the harness today, and with what instructions.

The notebooks never hard-code a model. They ask model_for(role) and get either
a real Claude model (when ANTHROPIC_API_KEY is available) or the deterministic
ScriptedModel stand-in (when it is not: CI, or Colab without a key), together
with the system prompt that role needs. Same harness, two engines.

Credentials come from the environment. load_env() reads a git-ignored .env
file found in the current folder or any parent, so a key placed once at the
repository root serves every notebook. Nothing here prints or stores a key.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from . import policies
from .models import Model, ScriptedModel

DEFAULT_MAIN_MODEL = "claude-opus-5"
DEFAULT_WORKER_MODEL = "claude-sonnet-5"

# role -> (system prompt for a real model, tier)
ROLES: dict[str, tuple[str, str]] = {
    "bare": ("Answer the question directly from what you already know, in one or two "
             "sentences. You have no tools.", "main"),
    "prompted": ("You are a careful assistant. Answer in one or two sentences. If you are not "
                 "sure, say so plainly instead of guessing, and say what source would settle it.",
                 "main"),
    "research": ("You answer questions using ONLY the course library, through your tools. "
                 "Steps: call search_docs with two to six key terms (never the whole question); "
                 "call read_doc on the best match; draft one or two sentences taken from the "
                 "document; if a check_citation tool exists, call it with your draft AND the "
                 "question, and fix whatever it reports; end your final answer with the tag "
                 "[source: <doc id>]. If the library holds nothing relevant, say exactly that "
                 "instead of guessing. Keep answers short.", "main"),
    "worker": ("You answer ONE focused question using ONLY the course library, through your "
               "tools: search_docs with a few key terms, read_doc on the best match, then answer "
               "in one or two sentences taken from the document, ending with [source: <doc id>]. "
               "If a check_citation tool exists, verify your draft first. If nothing relevant "
               "exists, say so.", "worker"),
    "judge": ('You grade one answer. Reply with JSON only, no prose: {"pass": true or false, '
              '"reason": "..."}. Pass only if the answer carries a [source: id] citation AND '
              "states a concrete date or number.", "worker"),
    "router": ("Classify the request into exactly one of the labels listed in this prompt. "
               "Reply with that single label and nothing else.", "worker"),
    "planner": ("Split the compound question into its independent sub-questions. Reply with a "
                "JSON list of strings only, no prose.", "worker"),
    "synthesizer": ("Combine the findings you are given into one short answer (two to four "
                    "sentences). Keep every [source: id] tag exactly as given. Reply with the "
                    "answer only.", "worker"),
    "calculator": ("Use the calculator tool for any arithmetic; never compute in your head. Then "
                   "report the result together with the expression you evaluated.", "worker"),
    "lead": ("You lead a small research team. Split the question into its independent "
             "sub-questions and call the delegate tool once per sub-question (you may issue "
             "several calls in one turn). Then combine the reports into one answer, keeping "
             "every [source: id] tag. Do not research yourself.", "main"),
}

_ALIASES = {"worker": "research"}      # scripted stand-in policies for roles without one


def load_env(start: str | Path | None = None) -> Optional[Path]:
    """Load KEY=VALUE lines from the nearest .env file into os.environ (existing values win)."""
    here = Path(start or Path.cwd()).resolve()
    for folder in [here, *here.parents]:
        candidate = folder / ".env"
        if candidate.is_file():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            return candidate
    return None


def real_model_available() -> bool:
    load_env()
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def main_model_id() -> str:
    return os.environ.get("HARNESS_MODEL", DEFAULT_MAIN_MODEL)


def worker_model_id() -> str:
    return os.environ.get("HARNESS_WORKER_MODEL", DEFAULT_WORKER_MODEL)


def model_for(role: str, *, real: bool | None = None, effort: str | None = None
              ) -> tuple[Model, str]:
    """The engine and system prompt for a role: real Claude if a key is present, else scripted."""
    if role not in ROLES:
        raise KeyError(f"unknown role '{role}'. Roles: {', '.join(ROLES)}")
    prompt, tier = ROLES[role]
    use_real = real_model_available() if real is None else real
    if use_real:
        from .providers import AnthropicModel

        model_id = main_model_id() if tier == "main" else worker_model_id()
        return AnthropicModel(model_id, effort=effort or ("medium" if tier == "main" else "low")), prompt
    policy = policies.POLICIES[_ALIASES.get(role, role)]
    return ScriptedModel(policy, name=f"scripted-{role}"), prompt


def describe_runtime() -> str:
    """One line for the top of a notebook: which engine will run today."""
    env_path = load_env()
    if os.environ.get("ANTHROPIC_API_KEY"):
        where = f"key loaded from {env_path.name}" if env_path else "key from the environment"
        return (f"Engine: real Claude models - {main_model_id()} for lead agents, "
                f"{worker_model_id()} for workers and judges ({where}; the key is never printed).")
    return ("Engine: ScriptedModel stand-in (no ANTHROPIC_API_KEY found). Copy .env.example to "
            ".env at the repository root and add your key to run every cell on real Claude models.")
