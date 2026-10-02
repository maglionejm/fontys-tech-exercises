#!/usr/bin/env python3
"""PostToolUse hook: append one JSON line per finished tool call to .claude/tool-calls.log.

Claude Code runs this script after every tool call and hands it the call and
its result as JSON on stdin. It never blocks anything: it is the dashboard,
not the brakes. It records what was called and how big the result was, never
the result itself, so a secret can never end up in the log.
"""
import json
import os
import sys
import time
from pathlib import Path

call = json.load(sys.stdin)
project = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
tool_input = call.get("tool_input", {}) or {}
what = (
    tool_input.get("command")
    or tool_input.get("file_path")
    or tool_input.get("pattern")
    or tool_input.get("description")
    or ""
)
entry = {
    "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "session": str(call.get("session_id", ""))[:8],
    "tool": call.get("tool_name"),
    "input": str(what)[:120],
    "result_chars": len(json.dumps(call.get("tool_response", ""))),
}
with open(project / ".claude" / "tool-calls.log", "a", encoding="utf-8") as log:
    log.write(json.dumps(entry) + "\n")
