#!/usr/bin/env bash
#
# acqnav installer for macOS / Linux.
#
# Creates a local virtual environment (.venv), installs acqnav in editable
# mode with its dev extras, and verifies the CLI runs. Idempotent: re-running
# reuses an existing .venv.
#
set -euo pipefail

# Resolve the repo root (directory containing this script) so the installer
# works regardless of the caller's current working directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Locate a Python 3 interpreter --------------------------------------------
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.10+ is required but was not found on PATH." >&2
    echo "       Install it from https://www.python.org/downloads/ and retry." >&2
    exit 1
fi

echo ">> Using $("$PYTHON" --version) ($(command -v "$PYTHON"))"

# --- Create / reuse the virtual environment -----------------------------------
VENV_DIR="$SCRIPT_DIR/.venv"
if [ -d "$VENV_DIR" ]; then
    echo ">> Reusing existing virtual environment at .venv"
else
    echo ">> Creating virtual environment at .venv"
    "$PYTHON" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# --- Install ------------------------------------------------------------------
echo ">> Upgrading pip"
python -m pip install --upgrade pip >/dev/null

echo ">> Installing acqnav (editable) with dev extras"
python -m pip install -e ".[dev]"

# --- Verify -------------------------------------------------------------------
echo ">> Verifying the CLI"
acqnav --version

cat <<EOF

============================================================
 acqnav is installed. Next steps:

   1. Activate the environment:
        source .venv/bin/activate

   2. Run the CLI:
        acqnav --help
        acqnav transition --trl 6 --sponsor-identified --funding-line-identified

   3. Run the demos:
        python demos/run_all.py

   4. Run the tests:
        python -m pytest -q
============================================================
EOF
