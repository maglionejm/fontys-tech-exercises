# What a harness is

An agent is a model plus a harness. The harness is the runtime that couples a language model to the world through a loop, tools, context management, safety controls, orchestration and extension surfaces. Harness engineering, named as a discipline in early 2026, is the design and evolution of that runtime. In plain words: the model is the engine, and the harness is the rest of the car.

The formula "Agent = Model + Harness" is credited to Birgitta Bockeler and quoted in Marmelab's survey "The State of AI Harness Engineering 2026" (24 September 2026). OpenAI's Ryan Lopopolo described harness engineering on 11 February 2026 as building deterministic scaffolding around probabilistic model steps: in a five-month experiment his team shipped about one million lines of production code with zero lines written by hand, using the repository as the system of record for design documents, decision records and execution plans, and enforcing its rules with custom linters and structural tests in continuous integration.

A source-code study of eleven coding agents (Claude Code, Codex CLI, Gemini CLI, Aider, OpenHands, mini-SWE-agent and others), published in July 2026, found that the field runs on hand-rolled asynchronous loops and deterministic retrieval rather than general frameworks.

Sources: Barbaste, Darrigol, Vu and Wiltberger, "Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents", arXiv 2609.00006, July 2026. Lopopolo, "Harness engineering: leveraging Codex in an agent-first world", OpenAI, 11 February 2026. Zaninotto, "The State of AI Harness Engineering 2026", Marmelab, 24 September 2026.
