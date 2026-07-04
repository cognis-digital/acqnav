#!/usr/bin/env python3
"""Demo 4: Color-of-money guidance and common mistakes.

Walks the appropriation categories and demonstrates the tool catching the two
classic color-of-money errors: RDT&E for production, and O&M for development.
"""

from __future__ import annotations

from acqnav import funding


def main() -> int:
    print("=" * 70)
    print("DEMO 4 — Color of money: what each appropriation can/can't buy")
    print("=" * 70)

    for a in funding.all_appropriations():
        print(f"\n{a.code} — {a.name} ({a.availability_years}-yr money)")
        print(f"   CAN buy:    {a.can_buy[0]}")
        print(f"   CANNOT buy: {a.cannot_buy[0] if a.cannot_buy else '(none listed)'}")
        print(f"   note: {a.notes}")

    print("\n--- Mistake detection ---")
    cases = [
        ("production", "3600", "Trying to buy production with RDT&E"),
        ("development", "3400", "Trying to fund development with O&M"),
        ("investment_item", "3400", "Buying an investment-threshold item with O&M"),
        ("production", "3010", "Correct: procurement for production"),
    ]
    for intent, proposed, desc in cases:
        g = funding.guidance_for(intent, proposed_color=proposed)
        print(f"\n  {desc} (intent={intent}, proposed={proposed})")
        rec = ", ".join(a.code for a in g.recommended) or "(none)"
        print(f"    recommended: {rec}")
        for w in g.warnings:
            print(f"    ! {w}")
        if not g.warnings:
            print("    (no warnings — appropriate use)")

    print("\nDemo 4 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
