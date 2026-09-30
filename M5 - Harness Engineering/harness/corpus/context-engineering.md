# Context engineering

The context window is everything the model sees in one call: the system prompt, instruction files, the conversation so far, tool results, retrieved documents and notes. It is a finite budget, and models perform worse as it fills with material that is not needed. Anthropic's post "Effective context engineering for AI agents" (29 September 2025) describes three techniques for long tasks.

Compaction summarizes a conversation that is nearing its limit and restarts with the summary, keeping decisions and open problems and dropping redundant tool output. Structured note-taking, also called agentic memory, writes facts to a file outside the window so they survive compaction and restarts. Sub-agent architectures give each focused task a fresh context: a sub-agent may spend tens of thousands of tokens exploring and return a summary of one thousand to two thousand tokens to the lead agent.

Instruction files such as CLAUDE.md and AGENTS.md carry standing rules into every session. Marmelab's 2026 survey found that human-written instruction files improved success by about four percent, while machine-generated ones reduced success compared with no file at all: when everything is marked important, nothing is.

Sources: Anthropic, "Effective context engineering for AI agents", 29 September 2025. Marmelab, "The State of AI Harness Engineering 2026", 24 September 2026.
