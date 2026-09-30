# Agent Skills and progressive disclosure

A skill is a folder that teaches an agent a procedure. It contains a SKILL.md file with a name, a one-line description and step-by-step instructions, plus optional scripts, reference documents and templates. Anthropic introduced Agent Skills on 16 October 2025 in the post "Equipping agents for the real world with Agent Skills" and published the format as an open standard on 18 December 2025; by 2026 more than forty platforms support it.

Skills work through progressive disclosure, in three levels. At level one the agent sees only each skill's name and description, a few dozen tokens per skill, so a large library costs almost nothing. At level two, when a task matches a description, the agent loads the full instructions. At level three, while executing, it reads the supporting files or runs the scripts it needs.

Skills, tools and prompts do different jobs. A prompt gives the task. A tool gives an ability, such as searching or running code. A skill gives a procedure: how to use the abilities well for a recurring kind of work.

Sources: Zhang, Lazuka and Murag, "Equipping agents for the real world with Agent Skills", Anthropic, 16 October 2025. Agent Skills open standard, 18 December 2025.
