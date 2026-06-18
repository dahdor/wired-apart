#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = wired-apart
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python3
QUARTO = quarto

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## Install all dependencies (runtime + dev) with uv
## Also installs TinyTeX (LaTeX distribution needed for PDF report).
## Quarto must be installed separately; see README "Requirements".
.PHONY: install
install:
	uv sync --all-extras
	uv run jupytext --sync 'notebooks/*.py' || true
	uv run python -m ipykernel install --user --name wired-apart --display-name "Python (wired-apart)"
	@if command -v quarto >/dev/null 2>&1; then \
		quarto install tinytex --quiet || true; \
	else \
		echo "WARNING: 'quarto' not in PATH. Install Quarto >= 1.9 from"; \
		echo "  https://quarto.org/docs/get-started/ and re-run 'make install'"; \
		echo "  to install TinyTeX for PDF rendering."; \
	fi

## Sync environment (after pulling new deps)
.PHONY: sync
sync:
	uv sync --all-extras

## Add a new dependency: make add PKG=pandas
.PHONY: add
add:
	uv add $(PKG)

## Install TinyTeX (LaTeX distribution for PDF report).
## Idempotent: if already installed, just reports status.
.PHONY: install-tinytex
install-tinytex:
	@if command -v quarto >/dev/null 2>&1; then \
		quarto install tinytex; \
	else \
		echo "ERROR: 'quarto' not in PATH. Install Quarto >= 1.9 first:"; \
		echo "  https://quarto.org/docs/get-started/"; \
		exit 1; \
	fi

## Download raw data (YRBS .mdb from CDC + NCHS Socrata)
## Idempotent: skips files that exist and match expected SHA-256.
.PHONY: download
download:
	uv run python scripts/download_data.py

## Download only Socrata (NCHS mortality) — for when YRBS is already local.
.PHONY: download-socrata
download-socrata:
	uv run python scripts/download_data.py --socrata-only

## Validate end-to-end: download → pipeline → report → tests.
## Use this for CI and for sanity-checking after big changes.
## Pass EXTRA="--skip-pdf" to skip PDF rendering + TinyTeX install
## (useful on machines without LaTeX or to avoid the ~1 GB download).
.PHONY: validate
validate:
	uv run python scripts/validate_pipeline.py $(EXTRA)

## Quick validation: just tests + check outputs exist (skip pipeline).
.PHONY: validate-quick
validate-quick:
	uv run python scripts/validate_pipeline.py --quick

## Validate WITHOUT PDF (HTML only, no TinyTeX install).
## Use this on machines without LaTeX or when you only need the HTML.
.PHONY: validate-no-pdf
validate-no-pdf:
	uv run python scripts/validate_pipeline.py --skip-pdf

## Remove compiled Python files (cross-platform: usa Python, no `find`)
.PHONY: clean
clean:
	uv run python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.ipynb_checkpoints')]; [p.unlink(missing_ok=True) for p in pathlib.Path('.').rglob('*.py[co]')]"
	@echo "Cleaned: __pycache__, .ipynb_checkpoints, *.pyc, *.pyo"

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
## IMPORTANT: uses jupyter nbconvert --execute --inplace (not jupyter execute)
## because the latter doesn't save outputs to the .ipynb file on Windows.
.PHONY: pipeline
pipeline: clean
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/0.0-dh-data-acquisition.ipynb
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/1.0-dh-yrbs-cleaning.ipynb
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/1.1-dh-wonder-cleaning.ipynb
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/2.0-dh-eda-yrbs.ipynb
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/2.1-dh-eda-wonder.ipynb
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/3.0-dh-analysis.ipynb
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/4.0-dh-storytelling.ipynb
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/5.0-dh-solution.ipynb

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
