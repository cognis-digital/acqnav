# acqnav — cross-platform developer tasks.
#
# Uses `python -m` invocations so the same targets work on Windows, macOS, and
# Linux. Override the interpreter with `make PYTHON=python3.12 install`.

PYTHON ?= python

.DEFAULT_GOAL := help
.PHONY: help install test demo lint clean

help:  ## Show this help.
	@echo "acqnav make targets:"
	@echo "  install   Install acqnav (editable) with dev extras"
	@echo "  test      Run the test suite (pytest)"
	@echo "  demo      Run every demo end-to-end"
	@echo "  lint      Byte-compile all sources (or ruff if available)"
	@echo "  clean     Remove venv, build artifacts, and caches"

install:  ## Install acqnav (editable) with dev extras.
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"
	$(PYTHON) -m acqnav --version

test:  ## Run the test suite.
	$(PYTHON) -m pytest -q

demo:  ## Run all demos.
	$(PYTHON) demos/run_all.py

lint:  ## Lint sources (ruff if installed, else byte-compile check).
	@$(PYTHON) -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('ruff') else 1)" \
		&& $(PYTHON) -m ruff check acqnav demos tests \
		|| $(PYTHON) -m compileall -q acqnav demos tests

clean:  ## Remove venv, build artifacts, and caches.
	$(PYTHON) -c "import shutil,glob,os; [shutil.rmtree(p,ignore_errors=True) for p in ['.venv','build','dist','.pytest_cache','.mypy_cache','demos/_output'] + glob.glob('*.egg-info') + glob.glob('**/__pycache__',recursive=True)]"
