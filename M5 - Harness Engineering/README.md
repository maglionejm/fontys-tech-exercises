# M5 - Harness Engineering

Four notebooks and four decks on the shift from **prompt engineering** (choosing the words you send a model) to **harness engineering** (designing everything around the model that makes it a reliable agent: the loop, tools, context management, skills, guardrails, orchestration and evals).

The module does not use the Titanic dataset. Its agents research the module's own reading material, a small library of ten documents in `harness/corpus/`, so the students learn the subject twice: once by reading it and once by watching an agent look it up, cite it and get checked.

## Notebooks

| # | Notebook | Session |
|---|----------|---------|
| 01 | From prompts to harnesses | the timeline, the definitions, the eight pieces, the same question three ways |
| 02 | Models, context, tools and skills | one model interface, context as a budget, tool design, permissions, progressive disclosure |
| 03 | Building a harness | the loop and its exits, hooks, the five workflow patterns, evals across three harness configurations, traces and cost |
| 04 | Sub-agents, teams and the discipline | isolated sub-agents, orchestrator-workers, agent teams, handoffs, failure modes, the working discipline |

## Real Claude models, safely

The notebooks run on **real Claude models by default** when a key is available, and on the deterministic `ScriptedModel` stand-in when it is not (continuous integration, or Colab without a key). One line decides, in every notebook: `model, system = model_for("research")`.

1. Copy `.env.example` (repository root) to `.env` and put your key in `ANTHROPIC_API_KEY=...`. `.env` is git-ignored; never commit it, never paste a key into a notebook cell.
2. Run any notebook. The first cells print which engine is active. Lead agents use `claude-opus-5`, workers, judges and routers use `claude-sonnet-5`; override with `HARNESS_MODEL` and `HARNESS_WORKER_MODEL` in `.env`.
3. Real runs cost money and vary between runs. Each notebook also keeps a clearly labelled reference run on the stand-in (`model_for(role, real=False)`) so the numbers quoted in the decks stay reproducible.

The repository's checks reject any notebook whose cells or outputs contain something that looks like a key.

## The `harness/` library

Plain Python, standard library only, written to be read in one sitting. Each file is one piece of a harness:

| File | Piece | What it holds |
|---|---|---|
| `messages.py` | the conversation | `Message`, `ToolCall`, token estimates |
| `models.py` | the model | the `Model` interface, `ScriptedModel` (a deterministic stand-in), `ModelView` |
| `providers.py` | real models | `AnthropicModel` (thinking blocks replayed, real token usage), `OpenAIModel` |
| `runtime.py` | the engine switch | `load_env()`, `model_for(role)`, role prompts, `describe_runtime()` |
| `policies.py` | stand-in behaviours | bare, prompted, research, judge, router, planner, synthesizer, lead |
| `tools.py` | tools | the `@tool` decorator (JSON schema from a signature), `ToolRegistry`, risk levels |
| `demo_tools.py` | the module's tools | `search_docs`, `read_doc`, `check_citation`, `calculator`, notes, `run_python` (danger) |
| `context.py` | context | `ContextWindow` (budget + compaction), `Notes` (memory outside the window) |
| `skills.py` | skills | `SkillIndex`: SKILL.md folders with three-level progressive disclosure |
| `agent.py` | the loop | `Agent`, `Hooks`, permissions, `RunResult` |
| `trace.py` | observability | `Trace`, `Event`, cost estimate |
| `patterns.py` | orchestration | chain, route, parallel, vote, orchestrate, evaluate_optimize |
| `multi.py` | multi-agent | `SubAgentPool` and its delegate tool, `TaskBoard`, `Mailbox`, `Team`, `handoff` |
| `evals.py` | evals | `EvalCase`, graders (outcome and trajectory), `run_evals`, `compare` |
| `corpus/` | the library | ten short documents on harness engineering, each with its sources |
| `skills/` | sample skills | `cite-sources`, `summarize-brief`, `safe-calculations` |

Minimal use:

```python
from harness import Agent, ScriptedModel
from harness.demo_tools import search_docs, read_doc, check_citation
from harness.policies import research_policy

agent = Agent(ScriptedModel(research_policy), tools=[search_docs, read_doc, check_citation])
result = agent.run("When did Anthropic open-source the Model Context Protocol?")
print(result.answer)
result.trace.show()
```

## Extending the module

- Add a document: drop a Markdown file in `harness/corpus/` whose first line is `# Title`; `search_docs` indexes it on the next call.
- Add a skill: create `harness/skills/<name>/SKILL.md` with `name:` and `description:` front matter and step-by-step instructions; optional files next to it become level-3 resources.
- Add a behaviour: write a function `policy(view: ModelView) -> Message` in `policies.py` using `say`, `call` and `calls`.
- Add a guardrail: a `Hooks.before_tool` function returning a denial reason, or a `Hooks.validate_answer` function returning a problem.

Sources for every claim in the corpus and the decks are listed at the end of each document and on each slide.
