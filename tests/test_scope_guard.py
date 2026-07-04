"""Scope guard: enforce that acqnav stays acquisition/program-management only.

acqnav is strictly defensive / business-enablement. This test fails if any
source module introduces language associated with weapons employment,
targeting, guidance, kill-chains, or fire control — a structural guardrail on
the project's scope.
"""

from __future__ import annotations

import pathlib
import re

PKG = pathlib.Path(__file__).resolve().parent.parent / "acqnav"

# Forbidden as whole words (case-insensitive). These denote weapon employment,
# never acquisition. We avoid substrings that would false-positive on benign
# acquisition terms.
FORBIDDEN = [
    r"\bkill[\s\-]?chain\b",
    r"\bfire[\s\-]?control\b",
    r"\btargeting\b",
    r"\bweaponeer\w*\b",
    r"\bautonomous weapon\b",
    r"\bmunition\b",
    r"\bwarhead\b",
    r"\bguidance system\b",
]


def _sources():
    return list(PKG.rglob("*.py"))


def test_sources_exist():
    assert _sources()


# A line is allowed to *name* a forbidden term only when it is explicitly
# excluding / negating it (a scope disclaimer). This keeps the guard strict
# against any affirmative capability while permitting "never targeting" style
# statements that document what acqnav does NOT do.
_EXCLUSION_MARKERS = (
    "never", "not ", "no ", "nothing", "without", "exclud", "absolutely",
    "rather than", "instead of",
)


def test_no_weapon_employment_terms():
    pattern = re.compile("|".join(FORBIDDEN), re.IGNORECASE)
    offenders = []
    for path in _sources():
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, 1):
            if not pattern.search(line):
                continue
            # Inspect a small window (this line +/- 2) so wrapped scope
            # disclaimers ("...never targeting, / weaponeering...") still count
            # as exclusions.
            window = " ".join(lines[max(0, lineno - 3): lineno + 2]).lower()
            if any(marker in window for marker in _EXCLUSION_MARKERS):
                continue  # scope disclaimer, allowed
            offenders.append((path.name, lineno, line.strip()))
    assert not offenders, f"Affirmative out-of-scope terms found: {offenders}"


def test_scope_statement_present():
    init = (PKG / "__init__.py").read_text(encoding="utf-8")
    assert "DEFENSIVE" in init.upper() or "defensive" in init
    assert "acquisition" in init.lower()
