#!/usr/bin/env python3
"""Demo 9: End-to-end navigator for a dual-use commercial firm.

A second full-scenario walkthrough (contrasting Demo 1's startup) for a
commercial software vendor entering defense via a Commercial Solutions Opening,
then bridging to a program of record through the Software Acquisition Pathway.
"""

from __future__ import annotations

from acqnav import (
    funding,
    gates,
    pathways,
    pilot_to_program,
    report,
    requirements,
    transition,
)
from acqnav.profile import ContractType, Maturity, TechProfile, Urgency


def main() -> int:
    print("=" * 70)
    print("DEMO 9 — Commercial dual-use software vendor, full walkthrough")
    print("=" * 70)

    prof = TechProfile(
        name="OpenLogix (commercial supply-chain analytics adapted for DoD)",
        trl=8, mrl=7, dollars=8_000_000,
        contract_type=ContractType.FIRM_FIXED_PRICE,
        urgency=Urgency.ACCELERATED,
        maturity=Maturity.COMMERCIAL,
        small_business=False, has_sbir_history=False,
        sponsor_identified=True, funding_line_identified=True,
        requirement_doc="CDD", teaming=True, prior_transitions=2,
        dual_use=True, tags=["software", "commercial", "analytics"],
    )

    print("\n[1] Pathways (commercial-friendly should lead)")
    ranked = pathways.recommend(prof)
    for s in ranked[:4]:
        print(f"    [{s.score:5.1f}] {s.pathway.name}")
    top = pathways.top_recommendation(prof)
    assert top is not None
    print(f"    -> top pick: {top.pathway.name}")

    print("\n[2] Transition probability")
    ts = transition.score(prof)
    print(f"    {ts.score}/100 ({ts.band})")
    for r in ts.recommendations:
        print(f"      improve: {r}")

    print("\n[3] Requirement alignment (CDD)")
    for note in requirements.align_to_document("CDD").readiness_notes:
        print(f"    {note}")

    print("\n[4] Funding — software pathway color of money")
    g = funding.guidance_for("software")
    print(f"    recommended: {', '.join(a.code for a in g.recommended)}")

    print("\n[5] Gate rollup with early artifacts")
    completed = {
        "mdd": list(gates.get_gate("mdd").artifacts),
        "ms_a": list(gates.get_gate("ms_a").artifacts),
        "dev_rfp": list(gates.get_gate("dev_rfp").artifacts)[:2],
    }
    roll = gates.rollup(completed)
    print(f"    overall {roll.overall_pct}% ; next: {roll.next_gate.gate.name}")

    print("\n[6] Pilot-to-program plan")
    plan = pilot_to_program.generate_plan(prof)
    print(f"    {plan.pct_complete}% steps satisfied, "
          f"{len(plan.applicable_valleys)} valley(s) remaining")

    print("\n[7] Report")
    md = report.to_markdown(report.Assessment(prof))
    print(f"    Markdown report: {len(md):,} bytes")

    print("\nDemo 9 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
