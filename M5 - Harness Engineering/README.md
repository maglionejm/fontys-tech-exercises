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

Every notebook runs in Google Colab or local Jupyter with **no API key**. The last section of each notebook optionally connects a real model (Anthropic or OpenAI) through `harness.providers.connect`, which asks for a key at run time and never stores it.

## The `harness/` library

Plain Python, standard library only, written to be read in one sitting. Each file is one piece of a harness:

| File | Piece | What it holds |
|---|---|---|
| `messages.py` | the conversation | `Message`, `ToolCall`, token estimates |
| `models.py` | the model | the `Model` interface, `ScriptedModel` (a deterministic stand-in), `ModelView` |
| `providers.py` | real models | `AnthropicModel`, `OpenAIModel`, `connect()` (optional) |
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
