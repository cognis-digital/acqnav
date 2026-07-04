#!/usr/bin/env python3
"""Demo 1: A small AI-fusion startup at TRL5 seeking rapid fielding.

Walks the entire navigator end-to-end for a realistic small business:
pathways -> transition score -> requirements alignment -> funding ->
gates -> pilot-to-program plan -> full report.
"""

from __future__ import annotations

from acqnav import (
    funding,
    gates,
    pathways,
    pilot_to_program,
    readiness,
    report,
    requirements,
    transition,
)
from acqnav.profile import ContractType, Maturity, TechProfile, Urgency


def main() -> int:
    print("=" * 70)
    print("DEMO 1 — Small AI-fusion startup, TRL5, seeking rapid fielding")
    print("=" * 70)

    prof = TechProfile(
        name="Sentinel Fusion (multi-source data fusion for situational awareness)",
        trl=5, mrl=4, dollars=1_800_000,
        contract_type=ContractType.OTHER_TRANSACTION,
        urgency=Urgency.URGENT,
        maturity=Maturity.ADAPTED_COMMERCIAL,
        small_business=True, has_sbir_history=True,
        sponsor_identified=True, funding_line_identified=False,
        requirement_doc="ICD", teaming=False, dual_use=True,
        tags=["ai", "data_fusion", "software"],
    )

    print("\n--- 1. Recommended acquisition pathways ---")
    for s in pathways.recommend(prof)[:4]:
        print(f"  [{s.score:5.1f}] {s.pathway.name}")
        print(f"           authority: {s.pathway.authority}")
        print(f"           timeline:  {s.pathway.typical_timeline}")
        print(f"           top reason: {s.rationale[0] if s.rationale else '-'}")

    print("\n--- 2. Transition-probability score (explainable) ---")
    print(transition.score(prof).explain())

    print("\n--- 3. Readiness: what evidence advances TRL5 -> TRL7? ---")
    gap = readiness.trl_gap(5, 7)
    for step in gap.steps:
        print(f"  TRL {step['level']}: {step['definition']}")
        for ev in step["evidence_needed"]:
            print(f"      - {ev}")

    print("\n--- 4. Requirement alignment (ICD) ---")
    align = requirements.align_to_document(prof.requirement_doc)
    for note in align.readiness_notes:
        print(f"  {note}")

    print("\n--- 5. Funding: color of money by phase ---")
    for row in funding.phasing_plan({2026: "prototype", 2028: "production", 2030: "sustainment"}):
        print(f"  FY{row['fy']}: {row['intent']:12s} -> {', '.join(row['colors'])}")

    print("\n--- 6. Gate readiness (nothing complete yet) ---")
    roll = gates.rollup({})
    print(f"  Overall: {roll.overall_pct}% ; next gate: {roll.next_gate.gate.name}")

    print("\n--- 7. Pilot-to-program transition plan ---")
    plan = pilot_to_program.generate_plan(prof)
    print(f"  {plan.pct_complete}% of bridge steps satisfied "
          f"(transition score {plan.transition_score:.1f}/100)")
    for v in plan.applicable_valleys:
        print(f"  VALLEY: {v['name']} -> {v['mitigation']}")

    print("\n--- 8. Full report (JSON size sanity) ---")
    doc = report.to_json(report.Assessment(prof))
    print(f"  JSON report generated: {len(doc):,} bytes")

    print("\nDemo 1 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
