# Sub-agents, agent teams and handoffs

Anthropic's post "How we built our multi-agent research system" (13 June 2025) describes an orchestrator-workers design: a lead agent plans, spawns three to five sub-agents in parallel, each with its own context window and tools, and synthesizes their findings, with a separate citation pass. On an internal research evaluation the multi-agent system beat a single-agent setup by 90.2 percent, at roughly fifteen times the tokens of a normal chat. Two lessons: teach the orchestrator how to delegate with clear task descriptions, and scale effort to the complexity of the query.

Sub-agents are hierarchical. A sub-agent is a fresh agent with a clean context and a focused task; it never talks to other sub-agents and returns a short report upward. Agent teams, available in Claude Code as a research preview from February 2026, are flat: several agents work in parallel from a shared task list, message one another directly, and a lead assigns tasks and synthesizes results. A handoff, in OpenAI's vocabulary, is a one-way transfer of control of the conversation from one agent to another.

Multi-agent systems fail in known ways. Marmelab's 2026 survey reports that problems requiring more than four handoffs almost always failed, and that adding a reviewer agent lowered the success rate by eight percent in one setup. Cost multiplies with every agent that reads the same material.

Sources: Anthropic, "How we built our multi-agent research system", 13 June 2025. Anthropic, Claude Code documentation on subagents and agent teams, 2025 to 2026. OpenAI, "A practical guide to building agents", April 2025. Marmelab, September 2026.
