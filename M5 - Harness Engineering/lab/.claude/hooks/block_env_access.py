#!/usr/bin/env python3
"""PreToolUse hook: refuse any Bash command that touches a .env file.

Claude Code runs this script before every Bash call and hands it the call as
JSON on stdin. Exit code 2 blocks the call and sends whatever we print to
stderr back to the model as the reason. Exit code 0 means "no opinion": the
normal permission flow decides.
"""
import json
import re
import sys

call = json.load(sys.stdin)
command = call.get("tool_input", {}).get("command", "")

if re.search(r"\.env\b", command) and ".env.example" not in command:
    print(
        "Blocked by .claude/hooks/block_env_access.py: Bash commands may not touch "
        ".env files. The key is loaded by code and never read by the agent.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
