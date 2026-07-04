#!/usr/bin/env python3
"""Demo 6: Warfighter value narrative + capability-gap classification.

Generates an OPLAN-agnostic value narrative that maps features to capability
needs to measurable effects, and demonstrates DOTMLPF-P gap classification
that avoids buying materiel for a training/doctrine problem.
"""

from __future__ import annotations

from acqnav import requirements


def main() -> int:
    print("=" * 70)
    print("DEMO 6 — Warfighter value narrative & gap classification")
    print("=" * 70)

    print("\n--- Gap classification (DOTMLPF-P) ---")
    gaps = [
        "Need a software system to fuse multi-source data for a common picture",
        "Operators lack training and there is no doctrine for the new process",
        "Need a new sensor plus updated training and organization changes",
    ]
    for g in gaps:
        res = requirements.classify_gap(g)
        print(f"\n  Gap: {g}")
        print(f"    domains:        {', '.join(res['candidate_domains'])}")
        print(f"    recommendation: {res['recommendation']}")

    print("\n--- Value narrative template ---")
    features = [
        requirements.Feature(
            "On-prem multi-source fusion",
            "Timely common operating picture from disparate feeds",
            "Reduce analyst time-to-insight by a measurable percentage",
            "KPP"),
        requirements.Feature(
            "Air-gap / offline operation",
            "Operate in disconnected environments",
            "Full functionality with zero external connectivity",
            "KSA"),
        requirements.Feature(
            "Open, self-hostable deployment",
            "Reduce vendor lock and sustainment cost",
            "Deployable by the program office without a broker",
            "APA"),
    ]
    narrative = requirements.value_narrative(
        "Sentinel Fusion",
        "Enduring need for rapid, on-premise fusion of unclassified multi-source "
        "data to support situational awareness for decision-makers.",
        features, doc_type="CDD")
    print()
    print(narrative)

    print("\nDemo 6 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
