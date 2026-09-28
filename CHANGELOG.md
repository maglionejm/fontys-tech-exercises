# Changelog

All notable changes to this repository. Dates are in ISO format. The project does not use version numbers: `main` is always the current course.

## Unreleased

### Added
- Module 4, *Prompting and Language Models*: notebook `01-the-power-of-prompting` runs a small open language model locally (no key), scores a five-rung prompt ladder on real passengers with a dev/test split, and teaches self-generation prompting (self-written examples, self-refine, APE, OPRO) plus an optional, off-by-default frontier-model author. A generated teaching deck accompanies it in `presentations/`.
- `torch` and `transformers` in `requirements.txt` (only needed for M4); the notebook-execution workflow installs the CPU build of torch.
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
