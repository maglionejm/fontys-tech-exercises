# Evals and observability

An eval is a test for an AI system: give the agent a task, apply grading logic to the result, and record the outcome. Anthropic's "Demystifying evals for AI agents" (January 2026) frames every eval as task plus graders plus outcome, distinguishes outcome grading (was the final answer right) from trajectory grading (did the agent take sensible steps, use the right tools, stay within budget), and warns that model-based judges must be calibrated against human labels. Evals run like tests in continuous integration, so a change to a prompt, a tool or a model shows its effect before users see it.

Observability is the dashboard: a trace records every model call, tool call, token count and second, so a run's cost and failures can be explained. OpenAI's harness team made the repository the system of record and enforced its rules with linters and structural tests, noting that corrections are cheap and waiting is expensive.

The field is behind on both. Marmelab's 2026 survey found that sixty percent of harnesses ship without tests or evals, that only 4.4 percent of written security rules are backed by a real control, and that 93 percent of permission prompts get approved, which makes an approval gate a weak guardrail on its own.

Sources: Anthropic, "Demystifying evals for AI agents", January 2026. OpenAI, "Harness engineering", 11 February 2026. Marmelab, "The State of AI Harness Engineering 2026", 24 September 2026.
