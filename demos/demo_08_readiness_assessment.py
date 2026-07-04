#!/usr/bin/env python3
"""Demo 8: TRL/MRL questionnaire assessment and gap analysis.

Answers the structured readiness questionnaire, computes the achieved level,
shows where progress is blocked, and lists the evidence needed to advance.
"""

from __future__ import annotations

from acqnav import readiness


def main() -> int:
    print("=" * 70)
    print("DEMO 8 — TRL / MRL assessment from a questionnaire")
    print("=" * 70)

    # A technology that has cleared lab validation but not a relevant
    # environment: yes through TRL4, no at TRL5.
    trl_answers = {
        "trl1": True, "trl2": True, "trl3": True, "trl4": True,
        "trl5": False, "trl6": True,  # trl6 'yes' should NOT count past the gap
    }
    res = readiness.assess_trl(trl_answers)
    print(f"\n  Assessed TRL: {res.level} — {res.definition}")
    for note in res.notes:
        print(f"    note: {note}")

    print(f"\n  Evidence to advance TRL {res.level} -> {res.level + 1}:")
    for ev in readiness.evidence_to_advance("TRL", res.level):
        print(f"    - {ev}")

    print("\n  Full gap plan to reach TRL 7:")
    gap = readiness.trl_gap(res.level, 7)
    for step in gap.steps:
        print(f"    TRL {step['level']}: {step['definition']}")
        for ev in step["evidence_needed"]:
            print(f"        - {ev}")

    # MRL side
    mrl_answers = {f"mrl{i}": True for i in range(1, 6)}
    mrl = readiness.assess_mrl(mrl_answers)
    print(f"\n  Assessed MRL: {mrl.level} — {mrl.definition}")
    mrl_gap = readiness.mrl_gap(mrl.level, 8)
    print(f"  MRL milestones to reach pilot-line (MRL 8):")
    for step in mrl_gap.steps:
        print(f"    MRL {step['level']}: {step['definition']}")

    assert res.level == 4, "expected TRL to stop at the gap (level 4)"
    print("\nDemo 8 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
