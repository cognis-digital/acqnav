#!/usr/bin/env python3
"""Demo 2: How pathway recommendations shift as a profile evolves.

Shows the same technology at three points in its life and how the recommended
acquisition pathway changes from SBIR feasibility to a rapid-fielding bridge.
"""

from __future__ import annotations

from acqnav import pathways
from acqnav.profile import ContractType, Maturity, TechProfile, Urgency


STAGES = [
    ("Feasibility (early)", dict(
        trl=3, dollars=250_000, small_business=True, has_sbir_history=False,
        maturity=Maturity.DEVELOPMENTAL, urgency=Urgency.ROUTINE)),
    ("Prototype (mid)", dict(
        trl=5, dollars=1_500_000, small_business=True, has_sbir_history=True,
        maturity=Maturity.ADAPTED_COMMERCIAL, urgency=Urgency.ACCELERATED,
        contract_type=ContractType.OTHER_TRANSACTION)),
    ("Near-production (late)", dict(
        trl=8, dollars=25_000_000, small_business=True, has_sbir_history=True,
        sponsor_identified=True, funding_line_identified=True,
        requirement_doc="CDD", maturity=Maturity.ADAPTED_COMMERCIAL,
        urgency=Urgency.URGENT)),
]


def main() -> int:
    print("=" * 70)
    print("DEMO 2 — Pathway recommendations across a technology's life")
    print("=" * 70)
    for label, kwargs in STAGES:
        prof = TechProfile(name=label, **kwargs)
        ranked = pathways.recommend(prof)
        print(f"\n[{label}] TRL{prof.trl}, ${prof.dollars:,.0f}, "
              f"urgency={prof.urgency.value}")
        for s in ranked[:3]:
            print(f"   [{s.score:5.1f}] {s.pathway.name}")
        if not ranked:
            print("   (no viable pathway)")
    print("\nObserve how the top pathway migrates SBIR I -> OTA/SBIR II -> "
          "APFIT/rapid-fielding as maturity and urgency rise.")
    print("\nDemo 2 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
