#!/usr/bin/env python3
"""Demo 3: Transition-probability sensitivity analysis.

Starts from a weak profile and shows, one improvement at a time, how the
transparent transition score climbs — the opposite of a black box. This is the
direct answer to NINA's opaque "transition probability scoring".
"""

from __future__ import annotations

import copy

from acqnav import transition
from acqnav.profile import TechProfile


IMPROVEMENTS = [
    ("baseline", lambda p: p),
    ("+ identify a funding line", lambda p: setattr(p, "funding_line_identified", True) or p),
    ("+ recruit a PoR sponsor", lambda p: setattr(p, "sponsor_identified", True) or p),
    ("+ validated CDD requirement", lambda p: setattr(p, "requirement_doc", "CDD") or p),
    ("+ advance TRL 5 -> 7", lambda p: setattr(p, "trl", 7) or p),
    ("+ team with a prime", lambda p: setattr(p, "teaming", True) or p),
    ("+ MRL assessment (MRL 8)", lambda p: setattr(p, "mrl", 8) or p),
]


def main() -> int:
    print("=" * 70)
    print("DEMO 3 — Transition-probability sensitivity (explainable scoring)")
    print("=" * 70)
    prof = TechProfile(name="Widget", trl=5)
    prev = None
    for label, mutate in IMPROVEMENTS:
        prof = mutate(prof)
        prof.__post_init__()
        ts = transition.score(prof)
        delta = "" if prev is None else f"  (+{ts.score - prev:.1f})"
        print(f"  {label:<32} {ts.score:5.1f}/100  [{ts.band}]{delta}")
        prev = ts.score

    print("\n  Final factor breakdown:")
    for f in transition.score(prof).factors:
        print(f"    {f.label:<32} {f.points:5.1f}/{f.weight:<4.0f}  {f.rationale}")

    assert prev is not None and prev >= 75, "expected a strong (High-band) final score"
    print("\nEvery point is traceable to a factor. Nothing is hidden.")
    print("\nDemo 3 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
