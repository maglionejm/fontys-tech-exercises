# Fontys Tech Exercises

[![CI](https://github.com/maglionejm/fontys-tech-exercises/actions/workflows/ci.yml/badge.svg)](https://github.com/maglionejm/fontys-tech-exercises/actions/workflows/ci.yml)
[![Notebooks execute](https://github.com/maglionejm/fontys-tech-exercises/actions/workflows/notebooks.yml/badge.svg)](https://github.com/maglionejm/fontys-tech-exercises/actions/workflows/notebooks.yml)
[![Course site](https://github.com/maglionejm/fontys-tech-exercises/actions/workflows/pages.yml/badge.svg)](https://maglionejm.github.io/fontys-tech-exercises/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-1E5EF3.svg)](requirements.txt)
[![License: MIT](https://img.shields.io/badge/license-MIT-0A2540.svg)](LICENSE)

A hands-on Python course for learning data analytics, machine learning and, in its newest module, harness engineering for AI agents, from zero. Four modules, thirteen notebooks, eight teaching decks, and one guiding principle: **keep it simple**. Every notebook balances short theory blocks with immediate practice, explains every technical term the first time it appears, and ends with exercises plus worked solutions.

Everything runs **in Google Colab with one click** or **locally**. No accounts, no API keys, no configuration files. All datasets load automatically from public sources.

**Course site:** [maglionejm.github.io/fontys-tech-exercises](https://maglionejm.github.io/fontys-tech-exercises/) tells the story of the dataset behind the course, shows example outputs from every module, and runs the course's final model in your browser.

## Start here

| You are | Do this |
|---|---|
| **A student** | Click an *Open in Colab* badge below, choose **Runtime > Run all**, read top to bottom. Start with M1 notebook 1. |
| **A teacher** | Read the [course site](https://maglionejm.github.io/fontys-tech-exercises/) for the storyline, then use the [M2 decks](presentations/) alongside the notebooks. |
| **A contributor** | Read [CONTRIBUTING.md](CONTRIBUTING.md), run `make setup && make check`, open a pull request. |

## One dataset, nine notebooks

Every module works the same passenger list: 891 passengers of the Titanic, twelve columns, 342 survivors. Module 1 cleans and describes it. Module 2 trains a model that predicts who survives and judges it honestly on rows it never saw (test accuracy 0.838). Module 3 puts that model behind an API, into a container, into the cloud, and into an application that calls it. Three real passengers, Owen, Florence and Frankie, return in every session so the numbers always have faces.

Module 5 leaves the ship. It teaches **harness engineering**: everything around a language model that turns it into a reliable agent. Its four notebooks build and run a small agent harness (a loop, tools, skills, context management, guardrails, sub-agents, teams and evals) with a deterministic stand-in model, so they run without any API key, and let you plug in a real model at the end.

## Course structure

### M1 - Descriptive analytics

| # | Notebook | What you learn | Open in Colab |
|---|----------|----------------|---------------|
| 1 | [Data cleaning](M1%20-%20Descriptive%20analytics/01-data-cleaning.ipynb) | Finding and fixing missing values, duplicates, wrong types, inconsistent text and outliers, with a heavy focus on loops and pandas/numpy | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M1%20-%20Descriptive%20analytics/01-data-cleaning.ipynb) |
| 2 | [Descriptive statistics](M1%20-%20Descriptive%20analytics/02-descriptive-statistics.ipynb) | Describing data with numbers: central tendency, spread, distribution shape, frequencies, group comparisons and correlation. Nothing predictive | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M1%20-%20Descriptive%20analytics/02-descriptive-statistics.ipynb) |
| 3 | [Visualization and dashboards](M1%20-%20Descriptive%20analytics/03-visualization-and-dashboards.ipynb) | Matplotlib, seaborn and interactive Plotly charts; chart-choice rules and design principles; static and interactive dashboards exported as shareable HTML | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M1%20-%20Descriptive%20analytics/03-visualization-and-dashboards.ipynb) |

### M2 - Machine Learning

The three notebooks tell one continuous story, predicting Titanic survival, but each one is self-contained and can be run on its own. Four generated teaching decks accompany this module in [`presentations/`](presentations/).

| # | Notebook | What you learn | Open in Colab |
|---|----------|----------------|---------------|
| 1 | [Data prep and feature engineering](M2%20-%20Machine%20Learning/01-data-prep-and-feature-engineering.ipynb) | Train/test splits and data leakage, imputation, encoding, scaling, feature engineering, and scikit-learn pipelines | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M2%20-%20Machine%20Learning/01-data-prep-and-feature-engineering.ipynb) |
| 2 | [Model selection](M2%20-%20Machine%20Learning/02-model-selection.ipynb) | Comparing six models fairly with cross-validation, confusion matrices, precision/recall/F1, ROC-AUC, overfitting vs underfitting, and how to choose a model in real life | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M2%20-%20Machine%20Learning/02-model-selection.ipynb) |
| 3 | [Model optimization and deployment](M2%20-%20Machine%20Learning/03-model-optimization-and-deployment.ipynb) | Hyperparameter tuning with grid and random search, saving models with joblib, wrapping the model in a Gradio web app, and deploying it free on Hugging Face Spaces | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M2%20-%20Machine%20Learning/03-model-optimization-and-deployment.ipynb) |

### M3 - ML Architectures and Deployment

Goes deeper: how machine learning fits into real tech architectures, how to run models in a real cloud, and how applications actually use them. Each notebook is self-contained.

| # | Notebook | What you learn | Open in Colab |
|---|----------|----------------|---------------|
| 1 | [ML system architectures](M3%20-%20ML%20Architectures%20and%20Deployment/01-ml-system-architectures.ipynb) | The components around a model that turn it into a product: data and training pipelines, model registries, the four serving patterns (batch, real-time API, streaming, embedded), drift monitoring and the retraining loop, where ML sits in a product architecture, and build vs buy. Every component simulated with working code | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M3%20-%20ML%20Architectures%20and%20Deployment/01-ml-system-architectures.ipynb) |
| 2 | [Deploying models in the cloud](M3%20-%20ML%20Architectures%20and%20Deployment/02-deploying-models-in-the-cloud.ipynb) | Turning a model into a real prediction API with FastAPI, testing it before shipping, packaging it with Docker, and deploying the same container to Google Cloud Run and AWS App Runner, with step-by-step walkthroughs, cost hygiene and cleanup | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M3%20-%20ML%20Architectures%20and%20Deployment/02-deploying-models-in-the-cloud.ipynb) |
| 3 | [Consuming models from applications](M3%20-%20ML%20Architectures%20and%20Deployment/03-consuming-models-from-applications.ipynb) | The last mile: calling a model API from Python with timeouts, error handling and retries; batch prediction; a working web app that calls the model (usable inside Colab too); CORS; and how third-party AI APIs and their keys fit in. The notebook runs a real server and consumes it over real HTTP | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M3%20-%20ML%20Architectures%20and%20Deployment/03-consuming-models-from-applications.ipynb) |

### M5 - Harness Engineering

From prompt engineering to harness engineering: what sits around a model to make it an agent, and how to build it. The notebooks share a small, readable library in [`M5 - Harness Engineering/harness/`](M5%20-%20Harness%20Engineering/) that runs with no API key. Four decks accompany the module in [`presentations/`](presentations/).

| # | Notebook | What you learn | Open in Colab |
|---|----------|----------------|---------------|
| 1 | [From prompts to harnesses](M5%20-%20Harness%20Engineering/01-from-prompts-to-harnesses.ipynb) | The timeline from few-shot prompts to harness engineering, what a harness is (agent = model + harness), the eight pieces, and the same question answered by a bare model, a better prompt and a harness with tools and verification | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M5%20-%20Harness%20Engineering/01-from-prompts-to-harnesses.ipynb) |
| 2 | [Models, context, tools and skills](M5%20-%20Harness%20Engineering/02-models-context-tools-and-skills.ipynb) | The model behind one interface, context as a budget (compaction, notes), tool design and MCP, permissions and risk levels, skills and progressive disclosure | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M5%20-%20Harness%20Engineering/02-models-context-tools-and-skills.ipynb) |
| 3 | [Building a harness](M5%20-%20Harness%20Engineering/03-building-a-harness.ipynb) | The agent loop and its stop conditions, hooks and guardrails, the five workflow patterns, evals (task, grader, outcome) comparing three harness configurations, traces and cost | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M5%20-%20Harness%20Engineering/03-building-a-harness.ipynb) |
| 4 | [Sub-agents, teams and the discipline](M5%20-%20Harness%20Engineering/04-sub-agents-teams-and-the-discipline.ipynb) | Isolated sub-agents, orchestrator-workers, agent teams with a shared task board, handoffs, failure modes, and the working discipline of harness engineering | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M5%20-%20Harness%20Engineering/04-sub-agents-teams-and-the-discipline.ipynb) |

Recommended order: M1, then M2, then M3, each top to bottom. M1 notebook 1, all of M2 and most of M3 use the same Titanic dataset, so concepts carry over naturally. M5 stands alone and can be taken after M2.

## Teaching decks

[`presentations/`](presentations/) holds eight white-and-blue decks: four for the M2 sessions and four for the M5 sessions, 18 to 24 slides each, in two parts: a theory chapter (frameworks from MIT 6.390, Andrew Ng's courses and Harvard CS109A, plus data-quality and privacy research, all attributed on the slides) followed by practice on the Titanic. The decks are **generated** from Python in `presentations/src/`; every number on a slide comes from an executed notebook or a computation on the course dataset. Rebuild them with `make decks`.

## How to run

### Option A - Google Colab (zero setup)

1. Click any *Open In Colab* badge above.
2. In Colab, choose **Runtime > Run all**.

The first cell of every notebook installs anything missing (on Colab almost everything is preinstalled), and datasets download automatically.

### Option B - Locally

Requirements: Python 3.10 or newer (the repository's own environment uses 3.14) and an internet connection (datasets are downloaded from public URLs on first run).

```bash
git clone https://github.com/maglionejm/fontys-tech-exercises.git
cd fontys-tech-exercises

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

jupyter lab
```

Open any notebook and run it top to bottom. Each notebook is independent.

Maintainers: `make setup` creates the one `.venv` at the repository root with the runtime packages and the tooling from `requirements-dev.txt`; `make help` lists every task. Point your editor's notebook kernel at `.venv/bin/python`.

## Datasets

All datasets are small, public, and load automatically:

- **Titanic passenger list** (891 rows), loaded from a public GitHub URL. Used in M1 notebook 1 and throughout M2 and M3.
- **Palmer Penguins, tips, Anscombe's quartet**, loaded through `seaborn.load_dataset()`.
- **Gapminder**, bundled with Plotly.

## Repository layout

```
fontys-tech-exercises/
├── M1 - Descriptive analytics/            3 notebooks
├── M2 - Machine Learning/                 3 notebooks
├── M3 - ML Architectures and Deployment/  3 notebooks
├── M5 - Harness Engineering/              4 notebooks + the harness/ teaching library
├── presentations/                         8 generated decks (M2, M5) + builders (src/)
├── docs/                                  the course site (GitHub Pages)
├── scripts/                               maintainer checks: notebook format, outputs, secrets, execution
├── .github/                               CI, notebook execution, Pages deploy, templates, CODEOWNERS, Dependabot
├── Makefile                               setup, check, test-notebooks, decks, site, clean
├── requirements.txt                       what students need
├── requirements-dev.txt                   what maintainers need
├── CONTRIBUTING.md  SECURITY.md  CODE_OF_CONDUCT.md  CHANGELOG.md
├── LICENSE                                MIT
└── .gitignore  .gitattributes  .editorconfig  ruff.toml
```

When you run the notebooks, they create an `outputs/` folder next to themselves (cleaned data, saved models, dashboards, deployment files). Those files are yours to keep or delete; the notebooks recreate them on every run, and git ignores them on purpose.

## Quality and security

- **Every notebook is executed** in a clean environment by the *Execute notebooks* workflow: on pull requests that touch notebooks, weekly, and on demand.
- **Every commit is scanned** for secrets across the full history, and a static check rejects notebooks whose code, outputs or metadata contain key patterns or local paths.
- **No secrets by design.** Nothing here needs an API key, a `.env` file or a login. Module 5 runs its agents on a deterministic stand-in model; connecting a real model is optional and asks for a key at run time without storing it. The optional *publish to the internet* guides (Hugging Face Spaces in M2, Google Cloud and AWS in M3) use the providers' web consoles and never embed tokens. See [SECURITY.md](SECURITY.md).
- **Notebooks ship with outputs**, so every chart and table is readable on GitHub without running anything. Interactive Plotly charts render when you run the notebook.

## Contributing

Issues and pull requests are welcome, from a clearer sentence to a new exercise. [CONTRIBUTING.md](CONTRIBUTING.md) explains the conventions (absolute-beginner tone, theory then practice, Colab-first, no secrets) and the workflow. All participants follow the [code of conduct](CODE_OF_CONDUCT.md).

## License

MIT. Use, copy and adapt these materials freely for your own learning or teaching.
