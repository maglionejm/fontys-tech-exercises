# Frequently asked questions about Module 5

**Where does the API key live?** In a file called `.env` at the root of the course repository, which git ignores. The template `.env.example` is tracked; the real file never is. Never paste a key into a notebook cell: the repository's checks reject notebooks that contain anything that looks like a key.

**How is the key loaded in the notebooks?** With `python-dotenv`: `dotenv_values(path)` reads the file into a dictionary and the key is passed to the client explicitly as `anthropic.Anthropic(api_key=...)`. The notebooks never export the key into the process environment.

**What does one notebook execution cost?** The budget is about 2 USD per notebook. Usage is printed after every experiment so students can see where the money went.

**Which models are used?** `claude-opus-5` for main agents and `claude-sonnet-5` for workers, judges, routers and planners. The three-model comparison in session 2 also calls `claude-haiku-4-5`.

**Which two tools do the agents use?** `list_files(folder)` returns the names directly under a repository folder; `read_file(path)` returns the text of one repository file. Both refuse paths that escape the repository root, paths inside `.git`, `.venv` and `.claude`, and any file named `.env` or ending in `.env`.

**What do the labs need?** Claude Code installed and signed in. Lab 2 covers `CLAUDE.md`, skills and one MCP server; lab 4 covers subagents, agent teams, hooks and permission modes.

**Can the notebooks run without a key?** No. The setup cell stops with one sentence that explains where to put the key, and nothing else runs.
