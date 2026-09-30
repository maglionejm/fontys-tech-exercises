# Lab 4 - Claude Code: subagents, agent teams, hooks and permissions

In notebook 04 you built a convoy by hand: a lead agent with a `delegate` tool, workers with fresh contexts, a task board shared by a team, hooks that run before and after every tool call, and a permission rule that decides which tools may run at all. Claude Code ships every one of those pieces. This lab shows where each one lives, lets you switch them on in a real project folder, and records what actually happened when we did.

| You built this in the notebook | Claude Code calls it | Where it lives in this folder |
|---|---|---|
| a worker `Agent` started by the lead's `delegate` tool | a **subagent**, started by the `Agent` tool | `.claude/agents/<name>.md` |
| the `TaskBoard` and the thread pool of teammates | an **agent team** with a shared task list and a mailbox | switched on in `.claude/settings.json` |
| `Hooks(before_tool=..., after_tool=...)` | **hooks** on `PreToolUse` and `PostToolUse` | `.claude/settings.json` plus two scripts in `.claude/hooks/` |
| `permission=deny_risk("danger")` | **permission rules and modes** | `permissions` in `.claude/settings.json`, `--permission-mode` |
| `result.cost_usd` | **`/usage`** (alias `/cost`) | the session, or `total_cost_usd` in the JSON of a `-p` run |

In plain words: the notebook taught you what the parts are for. The lab shows the same parts as a product, so you recognise them when you meet them at work.

Everything marked **observed** below is the real output of a run on 30 September 2026 with Claude Code 2.1.278. Everything marked **expected** describes behaviour documented at [code.claude.com/docs](https://code.claude.com/docs/en/overview) that needs an interactive terminal, which the recorded runs (non-interactive `claude -p`) cannot show. Your wording, token counts and costs will differ; the shape will not.

## 0. Before you start

Check the install and open the lab folder:

```bash
claude --version          # 2.1.278 (Claude Code) in the run recorded here
cd "M5 - Harness Engineering/lab"
```

The folder is small on purpose so that every answer can be checked by opening a file:

```text
lab/
  CLAUDE.md                          project instructions, read at the start of every session (lab 2)
  docs/                              the three files the labs ask about (lab 2)
  .claude/skills/repo-answers/       a skill, loaded on demand (lab 2)
  .claude/agents/repo-researcher.md  a read-only subagent (this lab)
  .claude/agents/fact-checker.md     a second read-only subagent (this lab)
  .claude/hooks/block_env_access.py  PreToolUse hook: the brakes
  .claude/hooks/log_tool_calls.py    PostToolUse hook: the dashboard
  .claude/settings.json              permission rules and the hook wiring (this lab)
```

Start Claude Code **in this folder**, because Claude Code reads `.claude/settings.json` and `.claude/agents/` from the folder it starts in. Give it the repository root as an extra working directory, so the subagent may read files two levels up (workflows, README, LICENSE) without a permission prompt for every file:

```bash
claude --add-dir ../..
```

The first time you start Claude Code in a repository it shows a trust dialog. Accept it: the `allow` rules in a project's `settings.json` only apply after that step (the `deny` rules apply right away).

## 1. Subagents

A **subagent** is a separate Claude Code agent with its own context window, its own tool list and its own instructions. The main agent hands it one task through the `Agent` tool, waits, and gets a short report back. The subagent's file reads, searches and reasoning never enter the main context. That is exactly what the notebook's `delegate` tool did with a fresh worker `Agent`.

### 1.1 The definition file

Project subagents live in `.claude/agents/`. Each one is a Markdown file: YAML front matter, then the system prompt. This is `.claude/agents/repo-researcher.md`:

```markdown
---
name: repo-researcher
description: Answers factual questions about this repository by reading its files. Use it whenever the user asks what a workflow, notebook, README, licence or changelog in this repository says. Read-only; it reports the file it used.
tools: Read, Grep, Glob
model: sonnet
maxTurns: 10
---

You answer questions about this repository, and only from its files.

Rules:
1. Find the file first (Glob or Grep), then read only the part you need. Do not read whole folders.
2. Answer in at most five sentences. Quote the exact line you relied on and give the repository-relative path of the file, for example `.github/workflows/notebooks.yml`.
3. If the repository does not contain the answer, say exactly that: "The repository does not contain this." Do not guess and do not use outside knowledge.
4. Never open a file named `.env` or ending in `.env`, and never print anything that looks like a key or a token. Say that the file is off limits.
5. You have no tools that edit files or run code. If a task needs them, say so and stop.
```

The front matter fields, and the notebook idea each one maps to:

| Field | What it does | In the notebook |
|---|---|---|
| `name` | the identifier you use to call it (required) | `Agent(name="worker")` |
| `description` | tells the main agent **when** to delegate to it (required); this is the tool description of the notebook, written for a machine | the `delegate` tool's docstring |
| `tools` | an allow-list; omit it and the subagent inherits every tool | `tools=[list_files, read_file]` |
| `model` | `sonnet`, `opus`, `haiku`, a full model id, or `inherit` | `model=WORKER_MODEL` |
| `maxTurns` | stop after this many agentic turns | `max_turns=` |

Other fields exist (`disallowedTools`, `permissionMode`, `effort`, `skills`, `memory`, `background`, `isolation: worktree`); the reference is the [subagents page](https://code.claude.com/docs/en/sub-agents). Two facts worth knowing: the `Task` tool was renamed `Agent` in v2.1.63 (old `Task(...)` references still work), and Claude Code ships built-in subagents named `Explore`, `Plan` and `general-purpose`.

### 1.2 Calling it

Name it in plain language, or force it with an `@` mention:

```text
Use the repo-researcher subagent to find out which Python version the notebook workflow of this repository uses, and which file says so.
@agent-repo-researcher which licence does this repository use?
```

`claude --agent repo-researcher` makes it the main agent for a whole session.

**Observed.** We ran the first prompt non-interactively so that the whole exchange lands in one JSON document:

```bash
claude -p "Use the repo-researcher subagent to find out which Python version the notebook workflow of this repository uses, and which file says so." --max-turns 4 --output-format json --add-dir ../..
```

The `result` field of the JSON:

```text
The notebook workflow uses Python 3.12. The file that says so is the repository's GitHub Actions
workflow for executing notebooks, `.github/workflows/notebooks.yml`, which pins the version in its
setup-python step for both jobs.

    45:          python-version: "3.12"
    60:          python-version: "3.12"

Source: .github/workflows/notebooks.yml
```

The accounting fields of the same JSON, trimmed:

```text
num_turns = 2
total_cost_usd = 0.1709
modelUsage:
  claude-fable-5-1  (the main agent)  inputTokens 34   outputTokens 685   cacheRead 46,296  costUSD 0.1168
  claude-sonnet-5   (the subagent)    inputTokens 8    outputTokens 2,226 cacheRead 23,657  costUSD 0.0541
```

Read it the way you read the notebook's trace. The main agent made two model calls: one to call `Agent`, one to write the answer. The subagent ran on `sonnet` because the front matter said so, and its calls are billed separately. The log written by our `PostToolUse` hook (section 2) shows what the main agent never saw, one line per finished tool call (the absolute path is shortened here):

```text
{"tool": "Grep",  "input": "python-version",               "result_chars": 458}
{"tool": "Glob",  "input": ".github/workflows/*.yaml",      "result_chars": 116}
{"tool": "Glob",  "input": ".github/workflows/*.yml",       "result_chars": 367}
{"tool": "Grep",  "input": "python-version",               "result_chars": 174}
{"tool": "Grep",  "input": "python-version",               "result_chars": 174}
{"tool": "Grep",  "input": "python-version",               "result_chars": 174}
{"tool": "Read",  "input": "<repository>/.github/workflows/notebooks.yml", "result_chars": 2583}
{"tool": "Agent", "input": "Find notebook workflow Python version",        "result_chars": 3284}
```

Seven tool calls happened inside the subagent, including a 2,583-character file read. The main agent received one result of 3,284 characters. That is the whole argument of notebook 04, section 1, in eight log lines.

**Observed.** A trap question, the kind the eval suite of notebook 03 insists on:

```bash
claude -p "Use the repo-researcher subagent to answer: who is the dean of Fontys ICT?" --max-turns 4 --output-format json --add-dir ../..
```

```text
The answer is not in the repository. The repo-researcher subagent searched for "dean", "Dean",
"director" and "Fontys" across the whole lab folder, and the only match was the word "Fontys" in the
opening line of the module overview. No file names a dean of Fontys ICT.

Files checked: `docs/module-overview.md`, `docs/glossary.md`, `docs/faq.md`, plus a grep across the
rest of the lab directory.
```

`total_cost_usd` was 0.2455, of which the subagent's `sonnet` share was 0.0186. Note that the subagent searched the lab folder, not the parent repository: the `--add-dir` flag allows the read, it does not tell the model where to look. A better task description ("search the whole repository, two levels up") would have widened the search. That is "teach the orchestrator how to delegate" in practice.

### 1.3 `/agents`

**Expected.** Since v2.1.198, `/agents` no longer opens a creation wizard. It prints a reminder to ask Claude to create or manage subagents, or to edit `.claude/agents/` (project) or `~/.claude/agents/` (user) directly. So the way to make a subagent is the way you just saw: write the file.

### 1.4 Exercise: chain two subagents

The second file, `.claude/agents/fact-checker.md`, verifies one claim against one file and only has `Read` and `Grep`. Ask:

```text
Use the repo-researcher subagent to find which licence this repository uses. Then use the fact-checker subagent to verify the exact line it quoted, in the file it named.
```

What to look for: two `Agent` calls in the main agent, two entries in `modelUsage` or `/usage`, and a verdict that starts with `SUPPORTED` and a line number. This is the chain pattern of notebook 03 (researcher, then judge) built from two files and no code.

## 2. Hooks

A **hook** is a command Claude Code runs at a fixed point of its loop: before a tool call (`PreToolUse`), after it (`PostToolUse`), when a session starts, when a subagent stops, before compaction, and about twenty other events. The command receives the event as JSON on standard input. A `PreToolUse` hook can **block** the call: exit code 2, and whatever it printed to standard error goes back to the model as the reason. A `PostToolUse` hook cannot block; it observes.

In plain words: `PreToolUse` is the brake pedal, `PostToolUse` is the dashboard. Notebook 03 gave them the names `before_tool` and `after_tool`.

### 2.1 The wiring

Hooks are declared in `.claude/settings.json`. The file in this folder:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(ls *)", "Bash(cat *)", "Bash(head *)", "Bash(wc *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(**/.env)", "Read(**/.env.*)"]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/block_env_access.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/log_tool_calls.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

`matcher` names the tool: `"Bash"` exactly, `"Edit|Write"` for several, `"*"` for every tool. `$CLAUDE_PROJECT_DIR` is the folder Claude Code started in, which is why the folder must be the lab. Settings files are strict JSON: a comment or a trailing comma breaks the file.

### 2.2 The brake: block every Bash command that touches `.env`

`.claude/hooks/block_env_access.py`:

```python
#!/usr/bin/env python3
"""PreToolUse hook: refuse any Bash command that touches a .env file."""
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
```

Twelve lines, no model involved. Compare it with the sentence in `CLAUDE.md` that says "Never read or print `.env` files": the sentence is a request, the hook is a control. The Marmelab survey quoted in notebook 04 found that only 4.4 percent of the security rules written in instruction files were backed by a control like this one.

**Observed, first attempt.** We asked for the file outright:

```bash
claude -p 'Run the shell command `cat ../../.env` and show me its output.' --max-turns 3 --output-format json
```

```text
I won't run that. The project's CLAUDE.md rule says never read or print `.env` files, since keys live
outside this folder, and printing the file would expose those secrets in this session's transcript.
```

`num_turns = 1`, no tool call, so the hook never ran. The instruction file did its job. That is the first layer, and on its own it is the weakest: a differently worded request, a long session or a compaction can make the model forget a sentence.

**Observed, second attempt.** We asked for something that sounds harmless:

```bash
claude -p 'Use a shell command to check whether the file ../../.env exists and how many bytes it has. Do not print its contents.' --max-turns 3 --output-format json
```

This time the model tried. It built a Bash command that tested the path and called `stat` on it to report the byte size. The hook saw `.env` in the command and exited with code 2. The JSON of the run lists the refused call under `permission_denials` (tool `Bash`, the command, the model's own description "Check whether .env exists and report its byte size only"), and the `result` reads:

```text
The command was blocked before it ran, so I could not check the file.

The project's pre-tool hook at `.claude/hooks/block_env_access.py` rejects any shell command that
references a `.env` path, including metadata-only calls like `stat`. It returned this message:

    Blocked by .claude/hooks/block_env_access.py: Bash commands may not touch .env files.
    The key is loaded by code and never read by the agent.

I did not try to route around it by listing the parent directory or using globs. The hook is the
guardrail this lab sets up on purpose, and the CLAUDE.md rule points the same way.
```

`num_turns = 2`, `total_cost_usd = 0.2522`. Two things to notice. The model read the denial and adapted (it offered to let the user run the command themselves or to relax the hook) instead of retrying; that is the `is_error` tool result of notebook 03 in product form. And the log file has **no line** for the blocked call: a call that never ran never reaches `PostToolUse`. The brakes and the dashboard are different instruments.

### 2.3 The dashboard: log every tool call

`.claude/hooks/log_tool_calls.py` appends one JSON line per finished tool call to `.claude/tool-calls.log`:

```python
#!/usr/bin/env python3
"""PostToolUse hook: append one JSON line per finished tool call to .claude/tool-calls.log."""
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
```

It records the **size** of every result and never the result itself. A log that copies tool output is a second place where a secret can leak; a log that records sizes is a trace you can commit to a ticket. You saw its output in section 1.2: the hook fired for the subagent's tool calls too, because hooks in the project settings apply to every agent in the session.

The log is a local artefact: it holds absolute paths from your machine, so the repository's `.gitignore` already ignores every `*.log` under the lab folder. The file does not ship with the repository; the hook creates it on the first tool call of your first session and appends from then on. Delete it whenever you like.

### 2.4 `/hooks`

**Expected.** `/hooks` lists every configured hook with the file it came from. Claude Code watches the settings files, so an edit applies to the running session without a restart. The full list of events and the JSON each one receives is on the [hooks reference](https://code.claude.com/docs/en/hooks).

## 3. Permission rules and permission modes

Hooks are code you write. Permission **rules** are declarations Claude Code enforces for you, and permission **modes** set the baseline for a whole session. Together they are the `permission=` argument of the notebook's `Agent`, with more shapes.

### 3.1 Rules

The `permissions` block in `.claude/settings.json` above has two lists:

- `allow`: `Bash(ls *)`, `Bash(cat *)`, `Bash(head *)`, `Bash(wc *)` run without a prompt. The `*` after the command is a prefix wildcard; `Bash(git log *)` would allow only `git log` commands.
- `deny`: `Read(./.env)`, `Read(./.env.*)` and their `**/` forms block the file tools on the key file. A `Read` deny rule also blocks `Edit` and `Write` on the same path, and Claude Code applies it to file commands it recognises inside Bash (`cat`, `head`, `tail`, `sed`, `tee`) and to redirections such as `< .env`.

Three rules of precedence, all documented and all worth remembering:

1. **Deny wins.** A deny rule blocks in every mode, including `bypassPermissions`, and an allow rule cannot carve an exception out of it.
2. **A blocking hook beats an allow rule.** `Bash(cat *)` is allowed above, yet `cat ../../.env` is stopped, because a hook that exits with code 2 runs before the rules are evaluated.
3. **Allow rules in a project file wait for trust.** Until you accept the trust dialog for the repository, project `allow` rules and `additionalDirectories` are ignored (a `-p` run prints a "workspace has not been trusted" warning to stderr). `deny` and `ask` rules apply immediately.

**Expected.** `/permissions` opens a dialog that lists every rule and the settings file it came from, and lets you add or remove rules while Claude is working.

### 3.2 Modes

| Mode (config value) | What runs without asking | Use it for |
|---|---|---|
| `default` (shown as **Manual** in the CLI) | reads only | reviewing every action yourself, sensitive work |
| `acceptEdits` | reads, file edits, common filesystem commands | iterating on code you are reviewing |
| `plan` | reads; Claude proposes a plan and edits nothing until you approve | exploring before changing anything |
| `auto` | everything, with a second model (a classifier) reviewing actions | long tasks, prompt fatigue |
| `dontAsk` | reads and pre-approved tools; anything that would prompt is denied | locked-down CI and scripts |
| `bypassPermissions` | everything | isolated containers and VMs only |

The CLI accepts `manual` as an alias for `default` (v2.1.200 or later). In a session, `Shift+Tab` cycles `default`, `acceptEdits`, `plan`; the status bar shows the active mode. From the command line:

```bash
claude --permission-mode plan --add-dir ../..
```

**Expected.** Ask that session to "add a line to docs/faq.md that says the lab has two subagents". Claude reads, writes a plan and stops. Nothing changes on disk until you approve the plan; the mode blocks the edit, not the model's good will.

The mode that matters for automation is `dontAsk`, combined with an exact allow-list. This is how you run Claude Code in a script or a CI job:

```bash
claude -p "Which files are in docs/?" --permission-mode dontAsk --allowedTools "Read" "Glob" "Grep"
```

Anything outside the list is denied, not asked, because there is nobody to ask. This is the `deny_risk("danger")` default of the notebook: the harness refuses, the model reads the refusal and works with what it has.

## 4. Agent teams

**Subagents are hierarchical**: the main agent starts them, they report back, they never talk to each other. **Agent teams are flat**: several Claude Code sessions run in parallel, share one task list, message each other directly, and a lead assigns work and synthesises the results. The notebook's `TaskBoard` with three teammate threads is a small model of the second shape.

Agent teams are experimental and off by default. Enable them exactly as the documentation says, by setting one environment variable to `1` in a settings file:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Add that `env` block to `.claude/settings.json` in this folder (project scope) or to `~/.claude/settings.json` (every project). Claude Code re-applies settings-file `env` values to the running session when you save.

Two documented consequences to know before you switch it on:

- **Teams need an interactive terminal.** In non-interactive mode (`claude -p`, and the Agent SDK) Claude does not spawn teammates; a named subagent runs as an ordinary subagent. That is why this section is marked expected: the recorded runs of this lab were non-interactive and could not form a team.
- **Named subagents become teammates.** While the variable is `1`, any subagent that Claude gives a name launches as a teammate, so a team can form even when you did not ask for one. Set the variable to `"0"` to get plain subagents back.

### 4.1 A two-teammate task

**Expected.** In an interactive session started in this folder with teams enabled:

```text
Spawn two teammates using the repo-researcher agent type, named overview and terms.
overview answers: what does docs/module-overview.md say this module is about?
terms answers: how does docs/glossary.md define a harness?
Wait for both, then combine their answers and keep their Source lines.
```

What the documentation says you will see:

- The **agent panel** under the prompt lists `overview` and `terms`. Up and down arrows select a teammate; Enter opens its transcript and lets you message it directly; `x` stops it.
- `Ctrl+T` toggles the **shared task list**. Tasks move through pending, in progress and completed; a teammate that finishes one can claim the next unassigned task on its own. Claiming uses file locking so two teammates never take the same task.
- When a teammate finishes it goes idle and **notifies the lead** with its final answer. The lead combines the two answers.
- Each teammate is a full session with its own context window. It loads `CLAUDE.md`, skills and MCP servers, but **not** the lead's conversation; everything it needs must be in the spawn prompt. The subagent definition supplies its `tools` (Claude Code adds `SendMessage` and the task tools) and its `model`.
- To end a teammate: "Ask the overview teammate to shut down". The teammate approves or explains why not. The team's directories under `~/.claude/teams/` are removed when the session ends.

### 4.2 What it costs

The cost page of the documentation says agent teams use roughly seven times the tokens of a plain session when teammates run in plan mode, because every teammate is a separate Claude instance with its own context. Its advice is the notebook's advice: use `sonnet` for teammates, keep teams small (three to five), keep spawn prompts focused, and shut teammates down when their work is done. Section 5.3 of notebook 04 measured the same multiplication on our small harness.

Compare the shapes before you pick one. A subagent is enough when only the result matters; a team earns its cost when teammates must share findings or challenge each other (a parallel code review with one reviewer per concern, or competing hypotheses in a debugging session). The documentation's own limitations list is candid: one team per session, no nested teams, teammates cannot be resumed after `/resume`, and task status can lag.

## 5. `/usage`

`/usage` is the command that shows what a session used; the commands reference lists `/cost` and `/stats` as its aliases. **Expected** (it needs an interactive session): its Session block shows the total cost of the current session, the API and wall-clock durations, the lines changed, and the tokens per model, computed locally at list price:

```text
Total cost:            $0.55
Total duration (API):  6m 20s
Total duration (wall): 6h 33m 10s
Total code changes:    0 lines added, 0 lines removed
Usage by model:
   claude-sonnet-5:  1.2k input, 5.3k output, 940.0k cache read, 50.0k cache write ($0.55)
```

(That block is the documentation's example, not one of our runs.) On a Pro, Max, Team or Enterprise subscription the dollar figure is informational, because usage is included in the plan; on an API key it is your bill. The totals reset when `/clear` starts a new session.

Non-interactive runs put the same numbers in the JSON: `total_cost_usd`, `duration_ms`, `num_turns`, a `usage` object with `input_tokens`, `output_tokens`, `cache_read_input_tokens` and `cache_creation_input_tokens` (the same four fields the notebook's `Usage` class sums), and `modelUsage` with a `costUSD` per model. The four runs recorded in this lab, as reported by that field:

| Run | Turns | Total cost (USD) |
|---|---|---|
| 1. subagent, Python version of the workflow | 2 | 0.1709 |
| 2. `cat ../../.env`, refused by the model | 1 | 0.1500 |
| 3. subagent, trap question about the dean | 2 | 0.2455 |
| 4. size of `.env`, blocked by the hook | 2 | 0.2522 |
| **Total** | | **0.8186** |

How to read it: a `-p` run pays for the whole system prompt, `CLAUDE.md`, the skill catalog and the tool schemas on every call, so even a one-turn refusal costs about fifteen cents at list price. Most of it is cache reads at one tenth of the input price; the `usage` object of run 1 shows 46,296 cache-read tokens against 34 fresh input tokens. Notebook 02 explained why that ratio is the number to watch.

## 6. What you saw, in the words of the module

| Notebook 04 idea | Where it appeared in this lab |
|---|---|
| a worker with a clean context and a short report back | seven tool calls inside `repo-researcher`, one 3,284-character result for the main agent |
| teach the orchestrator how to delegate | the trap question: the subagent searched the lab folder because nobody told it to go two levels up |
| `before_tool` denies, the model reads the reason and adapts | run 4: `stat` on `.env` blocked with exit code 2, the model reported the block and offered alternatives |
| `after_tool` observes | the `PostToolUse` log, sizes only, one line per call, none for blocked calls |
| instruction files are the weakest layer | run 2: `CLAUDE.md` held; the survey's 4.4 percent says why you still write the hook |
| permission by declaration | `allow` and `deny` rules; deny wins; a blocking hook beats an allow rule |
| the team's board and mailbox | the shared task list and the agent panel of agent teams (interactive only) |
| the bill | `/usage`, `total_cost_usd`, `modelUsage` per model |

## 7. Clean up

- `.claude/tool-calls.log` is git-ignored and holds paths from your machine. Delete it when you are done; the hook recreates it on the first tool call of the next session.
- If you added the `env` block for agent teams to `.claude/settings.json`, decide whether it stays: with it on, named subagents become teammates in every session in this folder.
- Never commit `.claude/settings.local.json`. Claude Code writes your personal "don't ask again" approvals there; it adds the file to your global git excludes the first time it creates it, but if you create it by hand you must ignore it yourself.
