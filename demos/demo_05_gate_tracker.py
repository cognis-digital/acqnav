#!/usr/bin/env python3
"""Demo 5: Milestone / gate tracking and readiness rollup.

Simulates a program progressing through the acquisition life cycle, filling in
gate artifacts and watching the readiness rollup advance the "next gate".
"""

from __future__ import annotations

from acqnav import gates


def main() -> int:
    print("=" * 70)
    print("DEMO 5 — Milestone / gate tracker & readiness rollup")
    print("=" * 70)

    print("\nLife-cycle gates and their artifacts:")
    for g in gates.all_gates():
        print(f"\n  {g.name}  (enters: {g.phase_entered})")
        for art in g.artifacts:
            print(f"     - {art}")

    # Simulate progress: MDD fully complete, MS A half complete.
    mdd = gates.get_gate("mdd")
    ms_a = gates.get_gate("ms_a")
    completed = {
        "mdd": list(mdd.artifacts),
        "ms_a": list(ms_a.artifacts)[:2],
    }
    roll = gates.rollup(completed)

    print("\n--- Rollup after early progress ---")
    for st in roll.statuses:
        flag = "READY" if st.ready else "pending"
        print(f"  {st.gate.name:<40} {st.pct_complete:5.1f}%  [{flag}]")
    print(f"\n  Overall program completeness: {roll.overall_pct}%")
    print(f"  Next gate to close: {roll.next_gate.gate.name}")
    print(f"  Missing for next gate:")
    for m in roll.next_gate.missing:
        print(f"     - {m}")

    print("\nDemo 5 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
