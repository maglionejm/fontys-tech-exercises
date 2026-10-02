# M5 - Harness Engineering

Four sessions on the shift from **prompt engineering** (choosing the words you send a model) to **harness engineering** (designing everything around the model that makes it a reliable agent: the loop, tools, context management, skills, guardrails, orchestration and evals).

Everything in this module is real. The agents run on **Claude models through the official Anthropic SDK**, the labs use **Claude Code** itself, skills follow the **Agent Skills** standard, tools are plugged in over **MCP**, and the eval suite runs in **GitHub Actions**. There is no simulated model anywhere: every number a notebook prints came from a real call, and every answer an agent gives can be checked by opening the file it cites.

The agents work on **this repository**. Their two tools, `list_files` and `read_file`, read the course's own files (workflows, requirements, licence, the site's model results), the way a coding agent reads a code base. A question such as "which Python version does the notebook workflow install?" has one right answer, in one file, that a student can open.

## The four notebooks

**Notebook 1: From prompts to harnesses** (`01-from-prompts-to-harnesses.ipynb`)
- Shows where simple prompting stops: a question whose answer is not in the model's memory.
- Answers the same question three ways on the raw SDK: a bare prompt (no tools, no system prompt), a careful prompt (a system prompt for better behaviour), and a harness (a forty-line loop with two file-reading tools).
- Compares the results and the cost of the three approaches, then shows the loop the SDK ships.

**Notebook 2: Models, context, tools and skills** (`02-models-context-tools-and-skills.ipynb`)
- Reads model facts and prices from the API and compares three Claude models on one question.
- Treats the context window as a budget: real token counts, a growing session, compaction written by the model, notes outside the window.
- Shows how to design tool schemas and error messages an agent can act on, and measures the SKILL.md standard on the real tokenizer.
- Lab 2 runs skills and an MCP server inside Claude Code.

**Notebook 3: Building a harness** (`03-building-a-harness.ipynb`)
- Builds the harness step by step with the `harness/` package: the loop and its stop conditions, hooks and permissions on real behaviour, the five workflow patterns.
- Integrates tools, handles their errors gracefully, and measures the result with an eval suite over three harness configurations, trap cases included.
- Reads traces, counts tokens and turns them into a bill; runs the evals in CI.

**Notebook 4: Sub-agents, teams and the discipline** (`04-sub-agents-teams-and-the-discipline.ipynb`)
- Covers the advanced shapes: a lead that delegates to fresh workers, orchestrator versus lead, a team on a shared task board, handoffs.
- Measures the failure modes on real usage: runaway prevention, context pollution, cost multiplication.
- Introduces harness engineering as a design discipline: instruction files, executable guards, evals in CI, observability, permission design.
- Lab 4 runs subagents, hooks, permission modes and agent teams inside Claude Code.

| # | Notebook | Lab |
|---|----------|-----|
| 01 | [From prompts to harnesses](01-from-prompts-to-harnesses.ipynb) | - |
| 02 | [Models, context, tools and skills](02-models-context-tools-and-skills.ipynb) | [Skills and MCP in Claude Code](lab/02-lab-claude-code-skills-and-mcp.md) |
| 03 | [Building a harness](03-building-a-harness.ipynb) | - |
| 04 | [Sub-agents, teams and the discipline](04-sub-agents-teams-and-the-discipline.ipynb) | [Subagents, teams, hooks and permissions in Claude Code](lab/04-lab-claude-code-subagents-and-teams.md) |

Four decks accompany the sessions in [`../presentations/`](../presentations/).

## Key concepts across the module

- The distinction between the model and the harness in agent design: the model is the engine, the harness is the rest of the car.
- The surrounding machinery moves the result as much as the choice of model does; the notebooks measure that rather than assert it.
- Security when an agent touches files or external systems: path guards, risk levels, permission rules and hooks that run outside the model.
- Cost awareness: every experiment prints its real token usage and price, and the eval suite puts a number on what verification costs.

## What you need

1. **Python 3.10 or newer** with the course requirements (`pip install -r requirements.txt` from the repository root, or the root `.venv`).
2. **An Anthropic API key.** Copy `.env.example` at the repository root to `.env` and fill in `ANTHROPIC_API_KEY=...`. The file is git-ignored. Never paste a key into a notebook cell: the repository's checks reject any notebook that contains something that looks like one. On Google Colab, store the key in the Secrets panel under the same name.
3. **Claude Code** for the two labs: `npm install -g @anthropic-ai/claude-code`, then `claude` inside the `lab/` folder. The labs work with a Claude subscription or with the same API key.
4. **A small budget.** A full run of one notebook costs between about half a dollar and a few dollars; each cell prints what it spent. Main agents use `claude-opus-5`, workers, judges and routers use `claude-sonnet-5`. Override the model ids with `HARNESS_MODEL` and `HARNESS_WORKER_MODEL` in `.env`.

Without a key the setup cell of every notebook stops with one sentence saying what to do. Nothing else runs.

## The `harness/` package

Plain Python on top of the SDK, written to be read in one sitting. Each file is one piece of a harness and none is longer than about two hundred lines.

| File | Piece | What it holds |
|---|---|---|
| `client.py` | the engine | `load_client()` (key from `.env`, the environment or Colab secrets, never printed), model ids, prices, `cost_usd()` |
| `tools.py` | tools | the `@tool` decorator (a JSON schema from a signature and docstring), `ToolRegistry`, risk levels, `deny_risk`, `allow_all` |
| `repo_tools.py` | this module's tools | `list_files`, `read_file` (rooted at the repository, refusing `.env`, `.git`, `.venv`, hiding local scratch), `write_note`, `read_notes`, `run_shell` (danger) |
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

A small project for Claude Code with its configuration committed on purpose: `CLAUDE.md`, skills in `.claude/skills/`, subagents in `.claude/agents/`, hooks and permission rules in `.claude/settings.json`, an MCP server in `.mcp.json`, and sample documents in `docs/`. Open a terminal in `lab/`, run `claude --add-dir ../..` so the subagents may read the wider repository, and follow the two lab guides. Personal settings (`settings.local.json`) and hook logs stay out of git.

## Safety rules that the code enforces

- The key is read only by `load_client()` and the notebooks' setup cells. It is passed to the SDK explicitly and never exported, printed or written.
- `read_file` refuses any path outside the repository and any credentials file, and says so; the refusal is itself a lesson in guardrails.
- Tools carry a risk level. `run_shell` is `danger` and the default permission denies it before it runs.
- The repository's checks reject notebooks that contain key-shaped strings, and the full git history is scanned for secrets on every push.
