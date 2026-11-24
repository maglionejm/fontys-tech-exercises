# Changelog

All notable changes to this repository. Dates are in ISO format. The project does not use version numbers: `main` is always the current course.

## Unreleased

### Added
- Module 4, Generative AI: a lesson notebook on retrieval-augmented generation (the closed-book versus open-book framing, the five-step pipeline built over the course's own documents, TF-IDF versus neural embeddings, hit rate and MRR with trap questions, design choices and failure modes); runs without a key, calls a real model in the last step when one is present.
- Module 4, Generative AI: the module's final project, a 1,500-word paper on generative versus traditional AI applied to a domain of the student's choice, with a documented use of a generative AI tool as an appendix. Full brief with the 100-point rubric and the hand-in rules, a one-page guidelines PDF, and a paper template (.docx and Markdown) preformatted to the required layout.
- Module 3, Natural Language Processing: the course's first final project, a text classification challenge on the SemEval-2018 irony tweets. A starter notebook with the data, a six-tweet quiz, exploration starters, the evaluation protocol (macro-F1 on a hidden test set) and a working baseline; sections for the students' exploration, experiments, error analysis, submission and report; a one-page guidelines PDF with the rubric. The hidden labels and the grading kit stay with the instructor.
- Module 5, Harness Engineering: four notebooks, two Claude Code labs and four decks on the evolution from prompt engineering to harness engineering, built on real components only: the official Anthropic SDK on Claude models, Claude Code for skills, MCP, subagents and agent teams, a small readable `harness/` package (loop, tools with risk levels, hooks, permissions, traces, structured outputs), an eval suite with trap cases (`evals/cases.yaml`) and unit tests, and a `harness.yml` workflow that runs the evals in CI when the `ANTHROPIC_API_KEY` secret is present. The agents read this repository's own files so every answer is checkable. Requires an Anthropic API key in a git-ignored `.env`; an earlier draft with a simulated model was replaced before release.
- Course website on GitHub Pages (`docs/`): the story of the Titanic dataset, example outputs from every module, and a survival model that runs in the browser.
- Enterprise scaffolding: CI (lint, notebook checks, secret scan on full history), weekly notebook execution, Pages deployment, issue and pull request templates, CODEOWNERS, Dependabot, `Makefile`, `requirements-dev.txt`, `.editorconfig`, `.gitattributes`.
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, this changelog.
- `scripts/check_notebooks.py` (format, outputs, secret patterns) and `scripts/run_notebooks.sh` (execute every notebook in a clean kernel).

### Changed
- README rewritten: learning outcomes, start-here paths, site link, badges and the complete repository layout.

## 2026-09-20

### Changed
- Session 1 and 2 decks enriched: AI/ML/DL landscape, rules-versus-data flip, a timeline of the field, where labels come from, sample-to-population bridge (Session 1); data-to-information ladder, data cascades, data-quality dimensions and re-identification (Session 2). All new diagrams drawn natively, all numbers sourced.

## 2026-09-19

### Changed
- Decks restructured into a theory chapter followed by Titanic practice, then simplified for absolute beginners with speaker notes and a clarity pass on every slide.

## 2026-09-18

### Added
- Four generated M2 session decks in `presentations/`, built from Python with a shared design system.

## 2026-09-08

### Changed
- Repository renamed to `fontys-tech-exercises`; README tidied so the repo explains itself.

## 2026-09-06

### Added
- Nine notebooks across three modules: descriptive analytics (M1), machine learning (M2), and ML architectures and deployment (M3), all runnable in Google Colab with zero setup.
