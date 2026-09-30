# M5 - Harness Engineering

Four sessions on the shift from **prompt engineering** (choosing the words you send a model) to **harness engineering** (designing everything around the model that makes it a reliable agent: the loop, tools, context management, skills, guardrails, orchestration and evals).

Everything in this module is real. The agents run on **Claude models through the official Anthropic SDK**, the labs use **Claude Code** itself, skills follow the **Agent Skills** standard, tools are plugged in over **MCP**, and the eval suite runs in **GitHub Actions**. There is no simulated model anywhere: every number a notebook prints came from a real call, and every answer an agent gives can be checked by opening the file it cites.

The agents work on **this repository**. Their two tools, `list_files` and `read_file`, read the course's own files (workflows, requirements, licence, the site's model results), the way a coding agent reads a code base. A question such as "which Python version does the notebook workflow install?" has one right answer, in one file, that a student can open.

## Sessions

| # | Notebook | Lab | What you build |
|---|----------|-----|----------------|
| 01 | [From prompts to harnesses](01-from-prompts-to-harnesses.ipynb) | - | The same question three ways on the raw SDK: a bare call, a careful system prompt, and a forty-line loop with two tools. Then the loop the SDK ships. |
| 02 | [Models, context, tools and skills](02-models-context-tools-and-skills.ipynb) | [Skills and MCP in Claude Code](lab/02-lab-claude-code-skills-and-mcp.md) | Model facts from the API, real token counts and cost, compaction the way real harnesses do it, tool schemas and error messages, the SKILL.md standard measured on the real tokenizer. |
| 03 | [Building a harness](03-building-a-harness.ipynb) | - | The `harness/` package: the loop and its stop conditions, hooks and permissions, the five workflow patterns, a twelve-plus-case eval suite over three harness configurations, traces and the bill. |
| 04 | [Sub-agents, teams and the discipline](04-sub-agents-teams-and-the-discipline.ipynb) | [Subagents, teams, hooks and permissions in Claude Code](lab/04-lab-claude-code-subagents-and-teams.md) | A lead that delegates to fresh workers, orchestrator versus lead, a task board with a team of agents, handoffs, the failure modes, and the working discipline. |

Four decks accompany the sessions in [`../presentations/`](../presentations/).

## What you need

1. **Python 3.10 or newer** with the course requirements (`pip install -r requirements.txt` from the repository root, or the root `.venv`).
2. **An Anthropic API key.** Copy `.env.example` at the repository root to `.env` and fill in `ANTHROPIC_API_KEY=...`. The file is git-ignored. Never paste a key into a notebook cell: the repository's checks reject any notebook that contains something that looks like one. On Google Colab, store the key in the Secrets panel under the same name.
3. **Claude Code** for the two labs: `npm install -g @anthropic-ai/claude-code`, then `claude` inside the `lab/` folder. The labs work with a Claude subscription or with the same API key.
4. **A small budget.** A full run of one notebook costs a few dollars at most; each cell prints what it spent. Main agents use `claude-opus-5`, workers, judges and routers use `claude-sonnet-5`. Override the model ids with `HARNESS_MODEL` and `HARNESS_WORKER_MODEL` in `.env`.

Without a key the setup cell of every notebook stops with one sentence saying what to do. Nothing else runs.

## The `harness/` package

Plain Python on top of the SDK, written to be read in one sitting. Each file is one piece of a harness and none is longer than about two hundred lines.

| File | Piece | What it holds |
|---|---|---|
| `client.py` | the engine | `load_client()` (key from `.env`, the environment or Colab secrets, never printed), model ids, prices, `cost_usd()` |
| `tools.py` | tools | the `@tool` decorator (a JSON schema from a signature and docstring), `ToolRegistry`, risk levels, `deny_risk`, `allow_all` |
| `repo_tools.py` | this module's tools | `list_files`, `read_file` (rooted at the repository, refusing `.env`, `.git`, `.venv`), `write_note`, `read_notes`, `run_shell` (danger) |
| `hooks.py` | guardrails | `Hooks(before_tool, after_tool, validate_answer)`, `deny_paths`, `truncate_result`, `require_sources` |
| `loop.py` | the loop | `Agent.run()`: gather context, take action, verify, repeat; stop conditions done, max turns, budget, refusal; structured output |
| `trace.py` | observability | `Trace` and `Event`: every model call with real token counts, every tool call, denial and validator note |
| `evals.py` | evals | `EvalCase` from `evals/cases.yaml`, graders, `run_evals`, `compare`, reports with pass rate and cost |
| `cli.py` | the terminal | `python -m harness ask`, `eval`, `show` |

Minimal use, from this folder:

```python
from harness import Agent, load_client, list_files, read_file, MAIN_MODEL

client = load_client()
agent = Agent(client, model=MAIN_MODEL, tools=[list_files, read_file],
              system="Answer from the repository and name the file you used.")
result = agent.run("Which licence does this repository use?")
print(result.answer)
result.trace.show()
print(result.usage, result.cost_usd)
```

From the terminal:

```bash
python -m harness ask "Which licence does this repository use?"
python -m harness eval evals/cases.yaml --config all --out results.json
python -m harness show results.json
```

## Evals, tests and CI

- `evals/cases.yaml` holds the eval suite: factual cases about the repository, each with the file that proves the answer, and trap cases the repository cannot answer, where the right result is `found: false` in the agent's structured answer.
- `tests/` holds pytest unit tests for the package (schemas, path guards, hooks, permissions, graders) that run without a key, plus one live test that is skipped without one.
- `.github/workflows/harness.yml` runs the unit tests on every change to the package and runs the eval suite when the repository secret `ANTHROPIC_API_KEY` is present, publishing the scoreboard to the job summary. The Module 5 notebooks are executed in CI by the `module-5` job of `notebooks.yml` under the same condition.

## The `lab/` project

A small project for Claude Code with its configuration committed on purpose: `CLAUDE.md`, skills in `.claude/skills/`, subagents in `.claude/agents/`, hooks and permission rules in `.claude/settings.json`, and sample documents in `docs/`. Open a terminal in `lab/`, run `claude`, and follow the two lab guides. Personal settings (`settings.local.json`) and hook logs stay out of git.

## Safety rules that the code enforces

- The key is read only by `load_client()` and the notebooks' setup cells. It is passed to the SDK explicitly and never exported, printed or written.
- `read_file` refuses any path outside the repository and any credentials file, and says so; the refusal is itself a lesson in guardrails.
- Tools carry a risk level. `run_shell` is `danger` and the default permission denies it before it runs.
- The repository's checks reject notebooks that contain key-shaped strings, and the full git history is scanned for secrets on every push.
