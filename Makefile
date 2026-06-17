#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = wired-apart
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python
QUARTO = quarto

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## Install all dependencies (runtime + dev) with uv
.PHONY: install
install:
	uv sync --all-extras
	uv run jupytext --sync 'notebooks/*.py' || true
	uv run python -m ipykernel install --user --name wired-apart --display-name "Python (wired-apart)"

## Sync environment (after pulling new deps)
.PHONY: sync
sync:
	uv sync --all-extras

## Add a new dependency: make add PKG=pandas
.PHONY: add
add:
	uv add $(PKG)

## Remove compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +

## Lint with ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	uv run ruff format --check
	uv run ruff check

## Auto-format with ruff
.PHONY: format
format:
	uv run ruff check --fix
	uv run ruff format

## Run the full analysis pipeline (data → features → analysis → figures)
.PHONY: pipeline
pipeline: clean
	uv run jupyter execute notebooks/0.0-dh-data-acquisition.ipynb
	uv run jupyter execute notebooks/1.0-dh-mtf-cleaning.ipynb
	uv run jupyter execute notebooks/1.1-dh-nsduh-cleaning.ipynb
	uv run jupyter execute notebooks/2.0-dh-eda-mtf.ipynb
	uv run jupyter execute notebooks/2.1-dh-eda-nsduh.ipynb
	uv run jupyter execute notebooks/3.0-dh-analysis.ipynb
	uv run jupyter execute notebooks/4.0-dh-storytelling.ipynb
	uv run jupyter execute notebooks/5.0-dh-solution.ipynb

## Render the Quarto report
.PHONY: report
report:
	uv run $(QUARTO) render informe.qmd --to html
	uv run $(QUARTO) render informe.qmd --to pdf

## Build everything (pipeline + report)
.PHONY: all
all: pipeline report

## Run tests
.PHONY: test
test:
	uv run pytest

#################################################################################
# Self-documenting help                                                         #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)
