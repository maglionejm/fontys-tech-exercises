# Workflows, agents and guardrails

Anthropic's "Building effective agents" (19 December 2024) separates two kinds of agentic systems. Workflows are systems where language models and tools are orchestrated through predefined code paths. Agents are systems where the model dynamically directs its own process and tool use. The building block of both is the augmented LLM: a model with retrieval, tools and memory.

The post names five workflow patterns. Prompt chaining runs steps in sequence, each consuming the previous output. Routing classifies an input and sends it to a specialized path. Parallelization runs independent pieces at once, either by sectioning a task or by voting with several attempts. Orchestrator-workers lets a central model split a task into subtasks it did not know in advance, delegate them and synthesize. Evaluator-optimizer pairs a generator with a critic in a loop. The three design principles are simplicity, transparency of the plan, and investing in the agent-computer interface.

OpenAI's "A practical guide to building agents" (April 2025) adds two multi-agent shapes, the manager pattern (agents as tools of a central manager) and the decentralized pattern (agents hand off control to one another), and lists seven guardrail types: relevance classifier, safety classifier, personal data filter, moderation, tool safeguards with risk ratings, rules-based protections and output validation, with human escalation on failure thresholds and high-risk actions.

Sources: Anthropic, "Building effective agents", 19 December 2024. OpenAI, "A practical guide to building agents", April 2025.
