# Contributing

Thank you for helping students learn. This repository is teaching material first and code second, so most rules below are about clarity for absolute beginners.

## Ground rules for notebooks

- **Audience: absolute beginners.** Explain every technical term the first time it appears, in plain words, before any formula or metaphor.
- **Shape: theory, then practice.** Short theory blocks followed by immediate hands-on cells. Every notebook ends with **Key takeaways**, **Practice exercises** and **Solutions**.
- **Runs everywhere with zero setup.** Every notebook must run top to bottom in Google Colab (`Runtime > Run all`) and in local Jupyter. Datasets come from public URLs or are bundled with a package. The first code cell installs anything missing.
- **No secrets, ever.** No API keys, tokens, passwords, `.env` files or absolute local paths in code, outputs or metadata. Cloud and Hugging Face follow-alongs are taught through their web UIs. CI scans every commit and the full history.
- **Committed with outputs.** Notebooks ship executed so students can read every chart and table on GitHub. Re-execute after any change, then commit.
- **Reproducible.** `random_state=42` for every split, model and search. Keep the canonical M2 preparation (Title, FamilySize, IsAlone; median-and-scale numerics; most-frequent-and-one-hot categoricals; 80/20 stratified split) unless the change is the point of the notebook.
- **Charts.** No pie or doughnut charts with more than three categories; use horizontal bars. Every chart has a title, labeled axes and a one-line "how to read it".
- **Style.** No emojis. Runtime artifacts go to an `outputs/` folder next to the notebook (git ignores it). Code must work on pandas 2.x and 3.x.

## Decks

The decks in `presentations/` (four for M2, one for M4) are **generated**. Never edit a `.pptx` by hand: change the builder in `presentations/src/`, rebuild with `make decks`, and commit both the builder and the deck. Every number on a slide comes from an executed notebook, a computation on the course dataset, or a source cited on the slide. Synthetic diagrams carry an "illustration" caption.

## Workflow

1. Open an issue (bug or content suggestion) or pick an existing one.
2. Branch from `main`: `feat/…`, `fix/…` or `docs/…`.
3. Make the change, then run `make check` (lint, notebook format, outputs, secret patterns). For notebook changes also run `make test-notebooks`, or let the *Execute notebooks* workflow run on your pull request.
4. Open a pull request and fill in the template. CI must be green; the maintainer reviews and squash-merges.

Commit messages: imperative mood, one line under 72 characters, optional body explaining *why*.

## Repository layout

| Path | Purpose |
|---|---|
| `M1 - Descriptive analytics/`, `M2 - Machine Learning/`, `M3 - ML Architectures and Deployment/`, `M4 - Prompting and Language Models/` | The ten notebooks |
| `presentations/` | Generated M2 and M4 decks and their builders (`src/`) |
| `docs/` | The course site published with GitHub Pages |
| `scripts/` | Maintainer checks used by `make` and CI |
| `.github/` | CI workflows, issue and pull request templates, CODEOWNERS, Dependabot |

## Local setup for maintainers

```bash
make setup          # .venv with runtime + tooling (requirements-dev.txt)
make check          # fast: ruff + notebook static checks
make test-notebooks # slow: execute every notebook into a temp folder
make decks          # rebuild the PowerPoint decks
make site           # preview docs/ on http://localhost:8000
```

Students never need any of this: the README's Colab badges are the supported path.
