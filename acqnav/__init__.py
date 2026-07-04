"""acqnav — Defense Acquisition Navigator.

An open, self-hostable library and CLI for navigating the U.S. Department of
Defense acquisition and program-management process. It models the real,
unclassified DoD acquisition pathways, scores technology readiness (TRL/MRL),
produces transparent and explainable transition-probability estimates, aligns
technology to requirement frameworks (JCIDS), maps "color of money", tracks
milestone gates, and generates pilot-to-program transition plans.

SCOPE: This project is strictly DEFENSIVE / acquisition / program-management /
business-enablement. It navigates money, milestones, requirements, and
acquisition pathways. It contains nothing related to weapons, targeting,
guidance, kill-chains, fire-control, or autonomous-weapon capability.

All data is drawn from published, unclassified acquisition doctrine concepts
(DoDI 5000.02, DoDI 5000.85, DoDI 5000.87, DAU guidance, JCIDS manual,
SBIR/STTR policy, Financial Management Regulation DoD 7000.14-R). No network
calls are made at runtime; the tool is air-gap friendly.
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = [
    "pathways",
    "readiness",
    "transition",
    "requirements",
    "funding",
    "gates",
    "pilot_to_program",
    "report",
    "profile",
]

from . import (  # noqa: E402
    funding,
    gates,
    pathways,
    pilot_to_program,
    profile,
    readiness,
    report,
    requirements,
    transition,
)
