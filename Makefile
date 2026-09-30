# Maintainer tasks for the Fontys Tech Exercises repository.
# Students do not need this file: the notebooks run in Colab or plain Jupyter.
#
#   make setup           create .venv with runtime + maintainer tooling
#   make check           fast checks: notebook format/outputs/secrets + lint
#   make test-notebooks  execute every notebook top to bottom (slow, ~10 min)
#   make decks           regenerate the four M2 PowerPoint decks
#   make site            preview the GitHub Pages site on http://localhost:8000
#   make clean           remove generated outputs and caches

PY      ?= python3
VENV    ?= .venv
BIN      = $(VENV)/bin

.PHONY: help setup check lint check-notebooks test-notebooks decks site clean

help:
	@grep -E '^#   make' Makefile | sed 's/^#   //'

setup: $(BIN)/activate

$(BIN)/activate: requirements.txt requirements-dev.txt
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements-dev.txt
	@touch $(BIN)/activate

check: lint check-notebooks

lint: setup
	$(BIN)/ruff check presentations/src scripts "M5 - Harness Engineering/harness"

check-notebooks: setup
	$(BIN)/python scripts/check_notebooks.py

test-notebooks: setup
	PATH="$(abspath $(BIN)):$$PATH" scripts/run_notebooks.sh

decks: setup
	cd presentations/src && for n in 1 2 3 4; do ../../$(BIN)/python build_session_$$n.py; done
	cd presentations/src && for n in 1 2 3 4; do ../../$(BIN)/python build_m5_session_$$n.py; done

site:
	$(PY) -m http.server 8000 --directory docs

clean:
	find . -name outputs -type d -prune -exec rm -rf {} +
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	find . -name .ipynb_checkpoints -type d -prune -exec rm -rf {} +
	rm -rf docs/.cache
