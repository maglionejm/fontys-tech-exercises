# From prompt engineering to harness engineering: a timeline

In 2020 GPT-3 showed that a few examples in the prompt could steer a model, and prompt engineering was born: the words were the lever. In January 2022 chain-of-thought prompting (Wei and colleagues) showed that asking a model to reason step by step improved its answers. In October 2022 the ReAct paper (Yao and colleagues) interleaved reasoning with actions, the seed of the agent loop.

On 13 June 2023 OpenAI shipped function calling, which turned tool use into a product feature: the model returns a structured request and the developer's code runs the function. On 25 November 2024 Anthropic open-sourced the Model Context Protocol so that tools could be plugged into any model client. On 19 December 2024 Anthropic published "Building effective agents", separating workflows from agents and naming five workflow patterns.

In June 2025 the industry adopted the phrase context engineering: Andrej Karpathy called it "the delicate art and science of filling the context window with just the right information for the next step". On 29 September 2025 Anthropic published "Effective context engineering for AI agents" and the Claude Agent SDK, whose loop is gather context, take action, verify work, repeat. On 16 October 2025 Agent Skills arrived. In January 2026 came "Demystifying evals for AI agents". On 11 February 2026 OpenAI named the discipline harness engineering.

Sources: Wei et al., arXiv 2201.11903 (2022). Yao et al., arXiv 2210.03629 (2022). OpenAI, "Function calling and other API updates", 13 June 2023. Anthropic engineering blog, 2024 to 2026. Karpathy on X, 25 June 2025.
