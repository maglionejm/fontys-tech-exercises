# Designing tools for agents

A tool is a function the model can request by name with JSON arguments; the harness runs it and pastes the result back into the context. Anthropic's post "Writing effective tools for agents" (September 2025) treats tool design as prompt engineering for machines. Descriptions must say when to use the tool and what it returns; names should share a prefix when tools belong together (namespacing); results should return meaningful context, not raw dumps; and responses should stay token-efficient by filtering, truncating and paginating.

Small changes matter. When Anthropic launched its web search tool, the model kept appending the year 2025 to queries; rewriting the tool description fixed it. Fewer tools often work better than more: in 2026 Vercel removed eighty percent of the tools from one of its agents, success rose from eighty percent to one hundred percent, token use halved, and latency fell from 724 seconds to 141 seconds.

Errors are part of the interface. A tool that fails should return a message that tells the model what went wrong and what to try instead, because the model will read that message and act on it.

Sources: Anthropic, "Writing effective tools for agents", September 2025. Marmelab, "The State of AI Harness Engineering 2026", 24 September 2026.
