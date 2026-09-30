# Session Decks

Eight teaching presentations: four for the "M2 - Machine Learning" module and four for the "M5 - Harness Engineering" module.

## M2 - Machine Learning

Four teaching presentations for the "M2 - Machine Learning" module. Each session pairs one deck with one notebook. The decks introduce machine learning from zero (including the bridge from M1's descriptive analytics), follow one continuous story — the 891 passengers of the Titanic, with three real passengers from the manifest recurring across all sessions — and use only numbers actually computed in the course notebooks.

| Session | Deck | Companion notebook |
|---------|------|--------------------|
| 1 | `m2-session-1-machine-learning-fundamentals.pptx` | 01, sections 1-3 |
| 2 | `m2-session-2-data-prep-and-feature-engineering.pptx` | 01, sections 4-10 |
| 3 | `m2-session-3-model-selection-and-evaluation.pptx` | 02 |
| 4 | `m2-session-4-optimization-and-deployment.pptx` | 03 |

19-24 slides per deck, each in two parts: **Part 1 - a theory chapter** (frameworks drawn from MIT 6.390, Andrew Ng's courses and Machine Learning Yearning, and Harvard CS109A / ISLR — attributed on the slides; Sessions 1 and 2 also draw on the AI landscape (Goodfellow, Bengio & Courville; Chollet), data-quality and privacy research (Ackoff; Wang & Strong; Sweeney; Sambasivan et al.) and the Titanic's historical record (Encyclopedia Titanica)) followed by **Part 2 - practice on the Titanic**. White and blue design, action titles, real charts; synthetic teaching diagrams are labeled as illustrations.

## M5 - Harness Engineering

Four decks on the evolution from prompt engineering to harness engineering, each pairing with one M5 notebook. Part 1 of every deck is theory drawn from Anthropic's and OpenAI's engineering posts and the 2026 harness-engineering literature (attributed on the slides); Part 2 walks through what the notebook builds and the numbers it prints.

| Session | Deck | Companion notebook |
|---------|------|--------------------|
| 1 | `m5-session-1-from-prompts-to-harnesses.pptx` | 01 |
| 2 | `m5-session-2-models-context-tools-and-skills.pptx` | 02 |
| 3 | `m5-session-3-building-a-harness.pptx` | 03 |
| 4 | `m5-session-4-sub-agents-teams-and-the-discipline.pptx` | 04 |

## Regenerating the decks

The decks are fully generated from code in `src/` (shared design system in `src/deck_style.py`, one builder per deck). To rebuild:

Use the repository's single environment (created at the root by `make setup` from `requirements-dev.txt`, which includes python-pptx and matplotlib), then:

```bash
make decks                     # rebuilds all eight decks
# or one at a time, from presentations/src:
../../.venv/bin/python build_session_1.py      # M2, and 2, 3, 4
../../.venv/bin/python build_m5_session_1.py   # M5, and 2, 3, 4
```

Do not create a second virtual environment inside `presentations/`; one `.venv` at the repository root serves the notebooks, the checks and the decks.

Each builder regenerates its own charts and diagrams (to a temp folder) and writes the PPTX one level up. External references cited on slides (course syllabi, published papers) are attributed directly on the slides.
