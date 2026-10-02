"""harness: a small, readable agent harness on the official Anthropic SDK.

    from harness import Agent, tool, load_client, list_files, read_file

    agent = Agent(load_client(), tools=[list_files, read_file])
    result = agent.run("Which licence does this repository use?")
    print(result.answer); result.trace.show()

One file per piece: client (key, models, prices), tools (schemas, risk levels),
hooks (your code inside the loop), trace (the flight recorder), loop (the
agent), repo_tools (the tools of this module), evals (cases, graders,
reports), cli (python -m harness).
"""
from .client import (MAIN_MODEL, PRICES, WORKER_MODEL, MissingKeyError, Usage, cost_usd, load_client,
                     price_for)
from .evals import ANSWER_SCHEMA, RESEARCHER_SYSTEM, EvalCase, Report, compare, grade, load_cases, run_evals
from .hooks import Hooks, ToolRequest, deny_paths, deny_risk_hook, require_sources, truncate_result
from .loop import Agent, RunResult, text_of
from .repo_tools import (clear_notes, list_files, read_file, read_notes, repo_root, run_shell, set_notes_path,
                         set_repo_root, write_note)
from .tools import Tool, ToolRegistry, allow_all, deny_risk, schema_from_function, tool
from .trace import Event, Trace

__all__ = [
    "Agent", "RunResult", "Trace", "Event", "Hooks", "ToolRequest", "tool", "Tool", "ToolRegistry",
    "deny_risk", "allow_all", "deny_paths", "deny_risk_hook", "require_sources", "truncate_result",
    "load_client", "MissingKeyError", "MAIN_MODEL", "WORKER_MODEL", "PRICES", "Usage", "cost_usd", "price_for",
    "repo_root", "set_repo_root", "list_files", "read_file", "write_note", "read_notes", "run_shell",
    "set_notes_path", "clear_notes", "EvalCase", "Report", "ANSWER_SCHEMA", "RESEARCHER_SYSTEM",
    "load_cases", "grade", "run_evals", "compare", "schema_from_function", "text_of",
]
