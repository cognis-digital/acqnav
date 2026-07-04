#!/usr/bin/env python3
"""Demo 7: Export a full assessment to JSON, Markdown, and self-contained HTML.

Writes all three formats to a local output directory and verifies the HTML is
self-contained (no JavaScript, no external assets) — air-gap friendly.
"""

from __future__ import annotations

import pathlib

from acqnav import report
from acqnav.profile import Maturity, TechProfile, Urgency


def main() -> int:
    print("=" * 70)
    print("DEMO 7 — Report export (JSON / Markdown / self-contained HTML)")
    print("=" * 70)

    prof = TechProfile(
        name="Aegis Logistics Optimizer",
        trl=7, mrl=6, dollars=12_000_000,
        urgency=Urgency.ACCELERATED, maturity=Maturity.ADAPTED_COMMERCIAL,
        small_business=True, has_sbir_history=True,
        sponsor_identified=True, funding_line_identified=True,
        requirement_doc="CDD", teaming=True, prior_transitions=1,
    )
    assessment = report.Assessment(prof)

    out_dir = pathlib.Path(__file__).resolve().parent / "_output"
    out_dir.mkdir(exist_ok=True)

    for fmt, ext in (("json", "json"), ("md", "md"), ("html", "html")):
        text = report.render(assessment, fmt)
        path = out_dir / f"assessment.{ext}"
        path.write_text(text, encoding="utf-8")
        print(f"  wrote {path.name:<20} {len(text):>8,} bytes")

    html = report.to_html(assessment)
    assert "<script" not in html.lower(), "HTML must contain no JavaScript"
    assert "http://" not in html and "https://" not in html, "no external assets"
    print("\n  Verified: HTML is self-contained (no JS, no external assets).")

    print("\nDemo 7 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
