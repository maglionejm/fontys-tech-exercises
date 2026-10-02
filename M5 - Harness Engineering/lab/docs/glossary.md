# Glossary of Module 5

Each entry gives the precise meaning, then the car analogy the module uses. One family of metaphors only: engine, steering, brakes, dashboard, GPS, glovebox, trailer hitch, convoy.

**Harness.** Everything around a language model that turns it into a reliable agent: the loop, the tools, the context management, the guardrails, the orchestration and the evals. Car: the model is the engine; the harness is the rest of the car.

**Model.** The text-in, text-out engine. Given a system prompt, a conversation and a list of tools, it returns the next message. Car: the engine.

**Context.** Everything the model sees in one call: the system prompt, instruction files, the conversation so far, tool results and retrieved documents. Car: the dashboard, which shows only what fits on it.

**Context engineering.** Deciding what goes into the context, what stays out, and when to summarize. Car: choosing which gauges the dashboard shows.

**Compaction.** Replacing older turns of a conversation with a short summary so the conversation fits in the window again. Car: clearing old trip data from the dashboard and keeping the odometer.

**Tool.** A function the model can ask for by name with JSON arguments; the harness runs it and returns the result as text. Car: the steering and the pedals, the parts the driver can operate.

**Skill.** A folder with a `SKILL.md` file (name, description, instructions) that the agent reads only when a task matches its description. Car: the manual in the glovebox.

**Progressive disclosure.** Loading only a skill's name and description at first, the full instructions when a task matches, and supporting files only while executing. Car: opening the glovebox only when something specific comes up.

**MCP.** The Model Context Protocol, an open standard that lets any tool server plug into any model client. Car: the standard trailer hitch.

**Guardrail.** A check that runs in code outside the model, before or after a tool runs, and cannot be talked out of. Car: the brakes.

**Hook.** A piece of your code that the harness runs at a fixed moment, for example before a tool call or after an answer. Car: the sensor that triggers the brakes.

**Sub-agent.** A separate agent with its own fresh context that a lead agent starts for one sub-task and that returns a short result. Car: a second car in the convoy.

**Eval.** A set of tasks with expected outcomes, run against the harness to measure how often it succeeds and what it costs. Car: the test track.
