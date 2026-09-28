# Session Decks

Five teaching presentations: four for the "M2 - Machine Learning" module and one for "M4 - Prompting and Language Models".

## M2 - Machine Learning

Four teaching presentations for the "M2 - Machine Learning" module. Each session pairs one deck with one notebook. The decks introduce machine learning from zero (including the bridge from M1's descriptive analytics), follow one continuous story — the 891 passengers of the Titanic, with three real passengers from the manifest recurring across all sessions — and use only numbers actually computed in the course notebooks.

| Session | Deck | Companion notebook |
|---------|------|--------------------|
| 1 | `m2-session-1-machine-learning-fundamentals.pptx` | 01, sections 1-3 |
| 2 | `m2-session-2-data-prep-and-feature-engineering.pptx` | 01, sections 4-10 |
| 3 | `m2-session-3-model-selection-and-evaluation.pptx` | 02 |
| 4 | `m2-session-4-optimization-and-deployment.pptx` | 03 |

19-24 slides per deck, each in two parts: **Part 1 - a theory chapter** (frameworks drawn from MIT 6.390, Andrew Ng's courses and Machine Learning Yearning, and Harvard CS109A / ISLR — attributed on the slides; Sessions 1 and 2 also draw on the AI landscape (Goodfellow, Bengio & Courville; Chollet), data-quality and privacy research (Ackoff; Wang & Strong; Sweeney; Sambasivan et al.) and the Titanic's historical record (Encyclopedia Titanica)) followed by **Part 2 - practice on the Titanic**. White and blue design, action titles, real charts; synthetic teaching diagrams are labeled as illustrations.

## M4 - Prompting and Language Models

| Session | Deck | Companion notebook |
|---------|------|--------------------|
| 1 | `m4-session-1-the-power-of-prompting.pptx` | M4 notebook 01 |

Two parts as well: **Part 1 - the theory** (what a prompt is, in-context learning after Brown et al. 2020, the prompt ladder, and self-generation prompting after Zhou et al. 2022 (APE), Madaan et al. 2023 (Self-Refine), Yang et al. 2023 (OPRO) and Khattab et al. 2023 (DSPy), attributed on the slides) followed by **Part 2 - practice**: the notebook's prompt ladder and self-generation loops scored on real passengers of the course dataset, with the dev/test honesty rule. Numbers on the slides are the notebook's executed outputs.

## Regenerating the decks

The decks are fully generated from code in `src/` (shared design system in `src/deck_style.py`, one builder per deck). To rebuild:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install python-pptx matplotlib numpy pandas
cd src
python build_session_1.py   # and 2, 3, 4
python build_m4_session_1.py
```

Each builder regenerates its own charts and diagrams (to a temp folder) and writes the PPTX one level up. External references cited on slides (course syllabi, published papers) are attributed directly on the slides.
