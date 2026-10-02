# Module 5 in one page

Module 5 of the Fontys tech exercises teaches harness engineering: designing everything around a language model that turns it into a reliable agent. The module has four sessions and two hands-on labs.

## Sessions

| Session | Notebook | Lab |
|---|---|---|
| 1 | From prompts to harnesses | none |
| 2 | Models, context, tools and skills | Claude Code: skills and MCP |
| 3 | Building a harness | none |
| 4 | Sub-agents, teams and the discipline | Claude Code: subagents, agent teams, hooks |

## Components the module uses

- The official Anthropic Python SDK (`anthropic`) with real Claude models.
- `claude-opus-5` for main agents; `claude-sonnet-5` for workers, judges, routers and planners.
- Claude Code, the command-line coding agent, for the two labs.
- The Agent Skills standard: a folder with a `SKILL.md` file that an agent loads on demand.
- MCP, the Model Context Protocol, to connect external tool servers.
- GitHub Actions to run the module's evals in continuous integration.

## The subject the agents work on

The agents that students build read files of the course repository itself, with two read-only tools: `list_files` lists a folder and `read_file` returns the text of one file. Every answer can be checked by opening the file it cites. Three trap questions appear in every eval set, for example "How many students took this course?", and the correct behaviour is to report that the repository does not contain the answer.

## Cost discipline

Each notebook execution is budgeted at about 2 USD. Agent turns use about 2,000 output tokens at most, workers and judges run at low effort, main agents at medium effort, and usage is printed after every experiment.
