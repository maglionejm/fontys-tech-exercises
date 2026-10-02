# Lab 2 - Claude Code: skills and MCP

Notebook 02 built three things by hand on the raw SDK: a catalog of skills with a `load_skill` tool, a gate that runs before a tool does, and the idea of MCP as a standard plug. Claude Code, the command-line coding agent, ships all three. In this lab you run it on the small project in this folder and watch each one happen.

**Time:** about 40 minutes. **Cost:** every `claude -p` run below costs real money on your account. The runs recorded here cost between 0.04 and 0.41 USD each; the exact figures are quoted where they occurred, and the last part shows how to read them yourself.

**How to read this guide.** Every command is shown exactly as it was typed from this folder. Output marked **observed** is what Claude Code 2.1.278 printed on the author's machine on 30 September 2026, with the personal part of absolute paths shortened to `<lab>` and servers unrelated to the lab removed. Output marked **expected** describes what you should see for steps that only work interactively and could not be captured. Runs vary: your model may pick a different tool or word the answer differently.

## Part 0 - Check the install

Open a terminal in this folder (`M5 - Harness Engineering/lab/`).

```bash
claude --version
claude auth status
```

Observed:

```text
2.1.278 (Claude Code)
{
  "loggedIn": true,
  "authMethod": "oauth_token",
  "apiProvider": "firstParty",
  ...
}
```

If `loggedIn` is `false`, run `claude` once and follow the login flow. Claude Code needs its own login or an `ANTHROPIC_API_KEY`; it does not read the repository's `.env` file.

## Part 1 - The project layout

This folder is a complete, tiny Claude Code project:

```text
lab/
  CLAUDE.md                          standing instructions, loaded into every session
  .claude/skills/
    repo-answers/SKILL.md            a procedure: answer from files, cite the path
    explain-term/SKILL.md            a procedure: plain words plus the car analogy
  docs/
    module-overview.md               the content the labs ask about
    glossary.md
    faq.md
  .mcp.json                          created in Part 4
```

**`CLAUDE.md`** is the instruction file from section 2 of the notebook: notes outside the window that Claude Code reads back in at the start of every session. Open it. It is short on purpose: the docs say to keep such files under about 200 lines, and the 2026 survey quoted in the notebook found that hand-written instruction files help while generated ones hurt. In plain words: a page in the glovebox that the driver reads before every trip.

**`.claude/skills/<name>/SKILL.md`** is the Agent Skills standard you measured in section 4. Open `.claude/skills/repo-answers/SKILL.md`. The block between the `---` lines is YAML front matter; the two fields that matter are:

- `name`: the name Claude Code uses (it defaults to the folder name; the notebook parsed the same field).
- `description`: *when* to use the skill. This is the level-1 text loaded into every session, and the only thing Claude Code matches your request against. Write it as a trigger, not a summary.

Other fields exist and you will meet some in lab 4: `disable-model-invocation: true` (only you can invoke it), `user-invocable: false` (only Claude can), `allowed-tools` (pre-approve tools while the skill runs). Skills also live per user in `~/.claude/skills/` and inside plugins; the project folder is the one shared through git.

**Progressive disclosure in Claude Code.** At session start only the descriptions are loaded (that is why they appear in the `/` menu). The body is loaded when you type `/repo-answers ...` or when Claude decides the description matches your request. Two interactive commands show the price: `/skills` lists every skill with its context cost, and `/context` shows what is in the context right now, skills included (expected output: a table with one line per skill and a token count; the two skills of this folder cost a few dozen tokens each at level 1, matching the counts in section 4.2 of the notebook).

## Part 2 - Ask a question that triggers the skill

The question below matches the `repo-answers` description ("Use when the user asks what the project, its docs or its configuration say"). We run Claude Code non-interactively: `-p` prints one answer and exits, `--max-turns 3` caps the loop, `--output-format json` returns a machine-readable result.

```bash
claude -p "Which two Claude models does this module use, and for which roles?" --max-turns 3 --output-format json
```

Observed (the JSON trimmed to the fields that matter):

```json
{
  "type": "result",
  "subtype": "success",
  "num_turns": 4,
  "duration_ms": 49344,
  "total_cost_usd": 0.40686275,
  "usage": {
    "input_tokens": 37,
    "cache_creation_input_tokens": 29201,
    "cache_read_input_tokens": 52521,
    "output_tokens": 567
  },
  "result": "The module uses `claude-opus-5` for main agents and `claude-sonnet-5` for workers, judges, routers and planners. The FAQ adds that the session 2 three-model comparison also calls `claude-haiku-4-5`, but the two core models are Opus 5 and Sonnet 5.\n\nSource: docs/module-overview.md\nSource: docs/faq.md"
}
```

Three things to check against the files: the two models and their roles are in `docs/module-overview.md`, the Haiku remark is in `docs/faq.md`, and the answer ends with `Source:` lines exactly as the skill's "Answer format" section demands. The procedure was followed.

### See the skill load

The `json` format hides the steps. The `stream-json` format prints one JSON line per event, including every tool call, so you can watch the loop the way `run_agent` printed it in the notebook.

```bash
claude -p "Which two Claude models does this module use, and for which roles?" --max-turns 3 --output-format stream-json --verbose
```

Observed, condensed to the sequence of events (one line per assistant action or tool result):

```text
system/init      model: claude-fable-5-1, skills: [..., explain-term, repo-answers, ...], cwd: <lab>
assistant text   I'll look this up in the lab's docs and cite the source.
assistant tool   Skill {"skill": "repo-answers", "args": "Which two Claude models does this module use, and for which roles?"}
tool_result      Launching skill: repo-answers
assistant tool   Bash {"command": "grep -rniE \"claude|sonnet|haiku|opus|fable\" \"<lab>/docs/\"", "description": "Search the lab docs for Claude model names"}
tool_result      <lab>/docs/module-overview.md:10: ... | <lab>/docs/module-overview.md:17: - `claude-opus-5` for main agents; ... | <lab>/docs/faq.md: ...
assistant text   The module uses `claude-opus-5` for main agents and `claude-sonnet-5` ... Source: docs/module-overview.md  Source: docs/faq.md
result           success, num_turns 4, total_cost_usd 0.4069
```

Read it against notebook section 4.3. The first thing the model did was call the **`Skill` tool** with `repo-answers`: that is Claude Code's `load_skill`, and "Launching skill" is the level-2 load. The `init` event lists both project skills by name among the skills available: that is the level-1 catalog. Then the model followed the loaded procedure (locate, read, cite), using `grep` through the `Bash` tool rather than the `Read` tool to locate the passage. Nothing forced it to load the skill; the description matched, so it did.

**About the cost.** This run cost 0.41 USD, far more than any single run in the notebook. Two reasons, both visible in the `init` event and the `usage` block: the author's default model here was `claude-fable-5-1`, the most expensive tier, and the author's machine has many plugins and MCP servers installed, whose tool descriptions all sit in the context (about 82,000 cached input tokens). A fresh install running `claude-sonnet-5` on this folder costs a few cents per question. Section 3.1 of the notebook made the point in miniature: every tool description is paid on every call. Add `--model sonnet` to any command below to pin the cheaper model.

### Invoke a skill by name

Interactively, skills are also slash commands. Start `claude` in this folder and type:

```text
/explain-term compaction
```

Expected output: three lines, following the `explain-term` procedure: the glossary definition of compaction, a sentence starting with "In plain words:" that uses the dashboard analogy, and `Source: docs/glossary.md`. Type `/context` afterwards and find the skill in the list: its body is now in the context, and its token cost is shown next to it. Leave the session with `/exit`.

## Part 3 - Add an MCP server

Section 5 of the notebook called MCP the standard trailer hitch: any tool server plugs into any client. Claude Code is such a client. We add the reference **filesystem server** published by the MCP project and point it at the `docs/` folder. The `--` separates Claude Code's own flags from the command that starts the server; `-s project` writes the configuration to `.mcp.json` in this folder so it is shared through git.

```bash
claude mcp add -s project filesystem -- npx -y @modelcontextprotocol/server-filesystem docs
```

Observed:

```text
Added stdio MCP server filesystem with command: npx -y @modelcontextprotocol/server-filesystem docs to project config
File modified: <lab>/.mcp.json
```

The file it wrote:

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "docs"],
      "env": {}
    }
  }
}
```

`type: stdio` means Claude Code starts the server as a child process and talks to it over standard input and output; `http` servers are reached over the network instead. The last argument, `docs`, is the only folder the server is allowed to expose. The path is relative to this folder, which keeps the file free of anyone's home directory.

### List it

```bash
claude mcp list
claude mcp get filesystem
```

Observed (other servers on the author's machine omitted):

```text
Checking MCP server health…

filesystem: npx -y @modelcontextprotocol/server-filesystem docs - ⏸ Pending approval (run `claude` to approve)
```

```text
filesystem:
  Scope: Project config (shared via .mcp.json)
  Status: ⏸ Pending approval (run `claude` to approve)
  Type: stdio
  Command: npx
  Args: -y @modelcontextprotocol/server-filesystem docs
  Environment:

To remove this server, run: claude mcp remove filesystem -s project
```

**Pending approval is a guardrail.** A `.mcp.json` arrives with a repository, so anyone who clones it could ship a server that runs arbitrary commands on your machine. Claude Code therefore refuses to start project-scoped servers until you approve them once. Expected output when you start `claude` interactively in this folder: a dialog listing `filesystem` and asking whether to use this project's MCP servers; choose yes, and `claude mcp list` then shows `✔ Connected`. In the non-interactive runs below we pass the file explicitly with `--mcp-config .mcp.json`, which counts as approval, and `--strict-mcp-config`, which ignores every other server on the machine (cheaper, and closer to what a student's fresh install sees).

## Part 4 - Use the server

```bash
claude -p "Using only the filesystem MCP server's tools, list the docs folder and tell me the first heading of each file." \
  --max-turns 4 --output-format stream-json --verbose --mcp-config .mcp.json --strict-mcp-config --model sonnet
```

Observed, condensed:

```text
system/init      model: claude-sonnet-5, mcp_servers: [{"name": "filesystem", "status": "connected"}]
                 tools now include 14 new names: mcp__filesystem__list_directory, mcp__filesystem__read_text_file,
                 mcp__filesystem__read_multiple_files, mcp__filesystem__search_files, mcp__filesystem__write_file, ...
assistant tool   ToolSearch {"query": "select:mcp__filesystem__list_directory,mcp__filesystem__read_text_file"}
assistant tool   mcp__filesystem__list_directory {"path": "<lab>/docs"}
tool_result      Claude requested permissions to use mcp__filesystem__list_directory, but you haven't granted it yet.
assistant tool   mcp__filesystem__list_directory {"path": "<lab>/docs"}
tool_result      Claude requested permissions to use mcp__filesystem__list_directory, but you haven't granted it yet.
assistant text   It looks like the filesystem MCP tool permission hasn't been granted yet ... Want me to retry, or would you
                 prefer I use the standard Read tool instead?
result           success, num_turns 4, total_cost_usd 0.1132
```

Three real lessons in one run:

1. **The plug worked.** The server connected and its tools appeared next to the built-in ones, named `mcp__<server>__<tool>`. That is section 3 of the notebook over a standard plug: fourteen names, descriptions and JSON schemas, added to the request. Claude Code keeps the schemas out of the context until needed and fetches them with `ToolSearch`, its version of progressive disclosure for tools.
2. **Permissions gate MCP tools like any other tool.** Interactively, Claude Code would have shown you an approval prompt for `mcp__filesystem__list_directory`; in `-p` mode nobody is there to answer, so the call was denied and the model got the denial as a tool result. This is exactly the gate of notebook section 3.5, run by the harness rather than by your `gate` function.
3. **The model adapted.** It retried once, then stopped and asked. Denials are messages the model reads, so what the message says matters (the notebook's gated run showed a model doing the opposite: searching on).

Now pre-approve the two read-only tools with `--allowedTools` and run again. Only those two are approved; anything else the server offers stays gated.

```bash
claude -p "Using only the filesystem MCP server's tools, list the docs folder and tell me the first heading of each file." \
  --max-turns 4 --output-format stream-json --verbose --mcp-config .mcp.json --strict-mcp-config --model sonnet \
  --allowedTools "mcp__filesystem__list_directory" "mcp__filesystem__read_text_file"
```

Observed, condensed:

```text
assistant tool   ToolSearch {"query": "select:mcp__filesystem__list_directory,mcp__filesystem__read_text_file,mcp__filesystem__read_multiple_files"}
assistant tool   mcp__filesystem__list_directory {"path": "<lab>/docs"}
tool_result      {"content":"[FILE] faq.md\n[FILE] glossary.md\n[FILE] module-overview.md"}
assistant tool   mcp__filesystem__read_multiple_files {"paths": ["<lab>/docs/faq.md", "<lab>/docs/glossary.md", "<lab>/docs/module-overview.md"]}
tool_result      Claude requested permissions to use mcp__filesystem__read_multiple_files, but you haven't granted it yet.
assistant tool   mcp__filesystem__read_text_file {"path": "<lab>/docs/faq.md", "head": 5}
tool_result      {"content":"# Frequently asked questions about Module 5\n\n**Where does the API key live?** ..."}
assistant tool   mcp__filesystem__read_text_file {"path": "<lab>/docs/glossary.md", "head": 5}
tool_result      {"content":"# Glossary of Module 5\n\nEach entry gives the precise meaning, then the car analogy ..."}
assistant tool   mcp__filesystem__read_text_file {"path": "<lab>/docs/module-overview.md", "head": 5}
tool_result      {"content":"# Module 5 in one page\n\nModule 5 of the Fontys tech exercises teaches harness engineering ..."}
result           error_max_turns, num_turns 5, total_cost_usd 0.0406
```

The listing came through the plug, the three headings came through the plug, and two more harness behaviours showed themselves. The model first tried the convenient `read_multiple_files`, which we had not approved, and was denied; it fell back to the approved `read_text_file`, asking for only the first five lines of each file (`"head": 5`, a token-efficient call the server's schema made possible). Then `--max-turns 4` cut the run before the model wrote its final sentence: the `result` says `error_max_turns`, and there is no answer text. The brake we set stopped a run that was one turn from done. Raise it to `--max-turns 6` and the answer arrives (expected output: the three headings, one per file, each followed by its path).

## Part 5 - Read the cost

Two places show what a session cost.

**Interactively:** type `/usage` inside a session. Expected output: a session block with total cost at list price, API duration, and one line per model with input, output, cache-read and cache-write tokens. (Some documents call this `/cost`; in Claude Code 2.1.278 the command listed is `/usage`.)

**From the JSON result:** the `result` event of `--output-format json` and `stream-json` carries the same numbers, per run. From the runs above:

| Run | Model | Turns | Input tokens (uncached + cache write + cache read) | Output tokens | Cost USD |
|---|---|---|---|---|---|
| Part 2, skill question | claude-fable-5-1 | 4 | 37 + 29,201 + 52,521 | 567 | 0.4069 |
| Part 4, first MCP run (denied) | claude-sonnet-5 | 4 | 8 + 34,451 + 101,472 | 672 | 0.1132 |
| Part 4, second MCP run (approved) | claude-sonnet-5 | 5 | 8 + 1,406 + 135,182 | 1,006 | 0.0406 |

Read the third row against the second: almost the whole prompt was served from the cache (`cache_read_input_tokens`), at a tenth of the input price, because the second run repeated the first run's prefix within five minutes. That is the prompt caching the notebook's `cost_usd` function priced in. To pull the number out of a script:

```bash
claude -p "your question" --output-format json --max-turns 3 | jq -r '.total_cost_usd'
```

`modelUsage` in the same object breaks the cost down per model; `num_turns` and `duration_ms` tell you how long the loop ran.

## What to remember

- **Skills are files.** A folder, a `SKILL.md`, a description written as a trigger. Claude Code loads the description at start and the body on match or on `/name`, exactly the two levels you measured in the notebook.
- **`CLAUDE.md` is context you control.** Short, human-written, loaded every session.
- **MCP is one command away.** `claude mcp add` writes a JSON entry; the server's tools appear as `mcp__server__tool` with their own descriptions and schemas.
- **The harness gates everything, MCP included.** Project servers wait for approval; tool calls wait for permission; `--max-turns` stops the loop. Each of these is a brake that works whatever the model asks.
- **Read the bill.** `total_cost_usd`, the four token counts and `num_turns` are in every JSON result.

## Try it yourself

1. Write a third skill in `.claude/skills/` for "how many" questions (the notebook's exercise 1 has the text), then ask "How many sessions does the module have?" with `--output-format stream-json --verbose` and check which skill loaded.
2. Ask a trap question: "How many students took this course?". The correct behaviour, per `CLAUDE.md` and the skill, is a plain statement that the docs do not contain it and the list of files checked.
3. Re-run the second MCP command with `--max-turns 6` and confirm the answer arrives; then remove `--allowedTools` and run interactively to see the permission prompt itself.

To undo the server when you are done: `claude mcp remove filesystem -s project`.
