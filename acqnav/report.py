"""Report generation and export (Markdown / HTML / JSON).

Assembles a full navigator assessment for a :class:`~acqnav.profile.TechProfile`
and exports it as JSON, Markdown, or a self-contained HTML document (inline CSS,
no JavaScript, no external assets — air-gap friendly).
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import funding, pathways, pilot_to_program, transition
from .profile import TechProfile


@dataclass
class Assessment:
    """A complete navigator assessment for a profile."""

    profile: TechProfile
    generated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))

    def build(self) -> dict:
        prof = self.profile
        ranked = pathways.recommend(prof, include_nonviable=True)
        tscore = transition.score(prof)
        plan = pilot_to_program.generate_plan(prof)
        return {
            "generated": self.generated,
            "tool": "acqnav",
            "profile": prof.to_dict(),
            "pathways": [s.to_dict() for s in ranked],
            "transition": tscore.to_dict(),
            "plan": plan.to_dict(),
            "appropriations_reference": [a.to_dict() for a in funding.all_appropriations()],
        }


def to_json(assessment: Assessment, *, indent: int = 2) -> str:
    """Serialize an assessment to a JSON string."""
    return json.dumps(assessment.build(), indent=indent, sort_keys=False)


def to_markdown(assessment: Assessment) -> str:
    """Render an assessment as Markdown."""
    data = assessment.build()
    p = data["profile"]
    lines: list[str] = []
    lines.append(f"# acqnav Assessment — {p['name']}")
    lines.append("")
    lines.append(f"_Generated {data['generated']} — Defense Acquisition Navigator_")
    lines.append("")

    lines.append("## Profile")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    for k in ("trl", "mrl", "contract_type", "dollars", "urgency", "maturity",
              "small_business", "has_sbir_history", "sponsor_identified",
              "funding_line_identified", "requirement_doc", "teaming"):
        lines.append(f"| {k} | {p.get(k)} |")
    lines.append("")

    t = data["transition"]
    lines.append(f"## Transition Probability: {t['score']}/100 ({t['band']})")
    lines.append("")
    lines.append("| Factor | Points | Weight | Rationale |")
    lines.append("|---|---|---|---|")
    for f in t["factors"]:
        lines.append(f"| {f['label']} | {f['points']} | {f['weight']} | {f['rationale']} |")
    if t["recommendations"]:
        lines.append("")
        lines.append("**Highest-leverage improvements:**")
        for r in t["recommendations"]:
            lines.append(f"- {r}")
    lines.append("")

    lines.append("## Recommended Acquisition Pathways")
    lines.append("")
    for s in data["pathways"]:
        tag = "" if s["viable"] else " _(not currently viable)_"
        lines.append(f"### {s['name']} — score {s['score']}{tag}")
        for r in s["rationale"]:
            lines.append(f"- {r}")
        for d in s["disqualifiers"]:
            lines.append(f"- :no_entry: {d}")
        lines.append("")

    plan = data["plan"]
    lines.append(f"## Pilot-to-Program Transition Plan ({plan['pct_complete']}% steps satisfied)")
    lines.append("")
    for step in plan["steps"]:
        box = "[x]" if step["done"] else "[ ]"
        lines.append(f"- {box} **{step['title']}** — {step['detail']} _(owner: {step['owner_hint']})_")
    if plan["applicable_valleys"]:
        lines.append("")
        lines.append("### Valleys of Death to Watch")
        for v in plan["applicable_valleys"]:
            lines.append(f"- **{v['name']}**: {v['symptom']} — _Mitigation:_ {v['mitigation']}")
    lines.append("")
    return "\n".join(lines)


_HTML_CSS = """
:root { color-scheme: light dark; }
body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
  max-width: 960px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }
h1 { border-bottom: 3px solid #1f4e79; padding-bottom: .3rem; }
h2 { color: #1f4e79; margin-top: 2rem; }
h3 { color: #2e6da4; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th, td { border: 1px solid #ccc; padding: .4rem .6rem; text-align: left; vertical-align: top; }
th { background: #1f4e79; color: #fff; }
tr:nth-child(even) { background: rgba(127,127,127,.08); }
.badge { display: inline-block; padding: .15rem .6rem; border-radius: .8rem; font-weight: 600; }
.high { background:#2e7d32; color:#fff; } .moderate { background:#f9a825; color:#000; }
.low { background:#ef6c00; color:#fff; } .verylow { background:#c62828; color:#fff; }
.meter { background:#e0e0e0; border-radius:.4rem; overflow:hidden; height:1.2rem; }
.meter > span { display:block; height:100%; background:#1f4e79; }
.muted { color:#777; font-size:.9rem; }
.done { color:#2e7d32; } .todo { color:#c62828; }
ul { margin: .3rem 0; }
footer { margin-top:3rem; border-top:1px solid #ccc; padding-top:.5rem; }
""".strip()


def _band_class(band: str) -> str:
    return {"High": "high", "Moderate": "moderate", "Low": "low", "Very Low": "verylow"}.get(band, "low")


def to_html(assessment: Assessment) -> str:
    """Render a self-contained HTML report (inline CSS, no JavaScript)."""
    data = assessment.build()
    p = data["profile"]
    t = data["transition"]
    plan = data["plan"]
    e = html.escape

    parts: list[str] = []
    parts.append("<!doctype html><html lang='en'><head><meta charset='utf-8'>")
    parts.append("<meta name='viewport' content='width=device-width, initial-scale=1'>")
    parts.append(f"<title>acqnav — {e(p['name'])}</title>")
    parts.append(f"<style>{_HTML_CSS}</style></head><body>")
    parts.append(f"<h1>acqnav Assessment — {e(p['name'])}</h1>")
    parts.append(f"<p class='muted'>Generated {e(data['generated'])} · Defense Acquisition Navigator</p>")

    # Profile
    parts.append("<h2>Profile</h2><table><tr><th>Field</th><th>Value</th></tr>")
    for k in ("trl", "mrl", "contract_type", "dollars", "urgency", "maturity",
              "small_business", "has_sbir_history", "sponsor_identified",
              "funding_line_identified", "requirement_doc", "teaming"):
        parts.append(f"<tr><td>{e(k)}</td><td>{e(str(p.get(k)))}</td></tr>")
    parts.append("</table>")

    # Transition
    bc = _band_class(t["band"])
    parts.append("<h2>Transition Probability "
                 f"<span class='badge {bc}'>{t['score']}/100 &middot; {e(t['band'])}</span></h2>")
    parts.append(f"<div class='meter'><span style='width:{min(100, max(0, t['score']))}%'></span></div>")
    parts.append("<table><tr><th>Factor</th><th>Points</th><th>Weight</th><th>Rationale</th></tr>")
    for f in t["factors"]:
        parts.append(
            f"<tr><td>{e(f['label'])}</td><td>{f['points']}</td>"
            f"<td>{f['weight']}</td><td>{e(f['rationale'])}</td></tr>"
        )
    parts.append("</table>")
    if t["recommendations"]:
        parts.append("<p><strong>Highest-leverage improvements:</strong></p><ul>")
        for r in t["recommendations"]:
            parts.append(f"<li>{e(r)}</li>")
        parts.append("</ul>")

    # Pathways
    parts.append("<h2>Recommended Acquisition Pathways</h2>")
    for s in data["pathways"]:
        tag = "" if s["viable"] else " <span class='muted'>(not currently viable)</span>"
        parts.append(f"<h3>{e(s['name'])} &mdash; score {s['score']}{tag}</h3><ul>")
        for r in s["rationale"]:
            parts.append(f"<li>{e(r)}</li>")
        for d in s["disqualifiers"]:
            parts.append(f"<li class='todo'>&#9940; {e(d)}</li>")
        parts.append("</ul>")

    # Plan
    parts.append(f"<h2>Pilot-to-Program Transition Plan "
                 f"<span class='muted'>({plan['pct_complete']}% satisfied)</span></h2><ul>")
    for step in plan["steps"]:
        cls = "done" if step["done"] else "todo"
        mark = "&#10003;" if step["done"] else "&#9744;"
        parts.append(
            f"<li class='{cls}'>{mark} <strong>{e(step['title'])}</strong> — "
            f"{e(step['detail'])} <span class='muted'>(owner: {e(step['owner_hint'])})</span></li>"
        )
    parts.append("</ul>")
    if plan["applicable_valleys"]:
        parts.append("<h3>Valleys of Death to Watch</h3><ul>")
        for v in plan["applicable_valleys"]:
            parts.append(
                f"<li><strong>{e(v['name'])}</strong>: {e(v['symptom'])} "
                f"<em>Mitigation:</em> {e(v['mitigation'])}</li>"
            )
        parts.append("</ul>")

    parts.append("<footer class='muted'>Generated by acqnav — open, self-hostable "
                 "Defense Acquisition Navigator. Scope: acquisition &amp; "
                 "program management only.</footer>")
    parts.append("</body></html>")
    return "".join(parts)


def render(assessment: Assessment, fmt: str) -> str:
    """Render an assessment in ``fmt`` (one of ``json``, ``md``, ``html``)."""
    fmt = fmt.lower()
    if fmt == "json":
        return to_json(assessment)
    if fmt in ("md", "markdown"):
        return to_markdown(assessment)
    if fmt == "html":
        return to_html(assessment)
    raise ValueError(f"unknown format {fmt!r}; expected json, md, or html")
