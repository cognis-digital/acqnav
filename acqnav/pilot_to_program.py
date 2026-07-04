"""Pilot / prototype -> Program of Record transition modeling.

Models converting a pilot or prototype into a sustained Program of Record (POR):
the bridge steps, the well-known "valleys of death", and a transition-plan
generator. This is the heart of surviving the gap between a successful
prototype and durable, funded fielding.

All content is program-management doctrine (transition planning, funding
bridges, requirement validation, sustainment planning). Nothing operational.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .profile import TechProfile
from . import transition as _transition


# The classic "valleys of death" between a prototype and a program of record.
VALLEYS_OF_DEATH: tuple[dict, ...] = (
    {
        "name": "Technology-to-transition valley",
        "symptom": "A successful prototype has no committed customer to receive it.",
        "mitigation": "Identify a program-of-record sponsor and requirement owner "
                      "before the prototype completes.",
    },
    {
        "name": "Funding-color / timing valley",
        "symptom": "RDT&E ends but no Procurement/O&M line exists to field or sustain.",
        "mitigation": "Get a funding line into the POM/budget cycle 2+ years ahead; "
                      "confirm the correct color of money.",
    },
    {
        "name": "Requirement-validation valley",
        "symptom": "No validated JCIDS requirement, so no basis to program funds.",
        "mitigation": "Mature a documented gap into a validated ICD/CDD with the "
                      "requirements sponsor.",
    },
    {
        "name": "Production / manufacturing valley",
        "symptom": "Prototype cannot be produced at rate, quality, or cost.",
        "mitigation": "Raise MRL via a Manufacturing Readiness Assessment; plan LRIP.",
    },
    {
        "name": "Sustainment valley",
        "symptom": "Fielded item has no sustainment tail (spares, training, support).",
        "mitigation": "Author a Life-Cycle Sustainment Plan and secure O&M funding.",
    },
)


@dataclass
class BridgeStep:
    """One step in a pilot-to-program transition plan."""

    order: int
    title: str
    detail: str
    owner_hint: str
    done: bool = False

    def to_dict(self) -> dict:
        return {
            "order": self.order,
            "title": self.title,
            "detail": self.detail,
            "owner_hint": self.owner_hint,
            "done": self.done,
        }


@dataclass
class TransitionPlan:
    """A generated pilot-to-program transition plan."""

    program_name: str
    steps: list[BridgeStep] = field(default_factory=list)
    applicable_valleys: list[dict] = field(default_factory=list)
    transition_score: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def pct_complete(self) -> float:
        if not self.steps:
            return 0.0
        return round(100.0 * sum(1 for s in self.steps if s.done) / len(self.steps), 1)

    def to_dict(self) -> dict:
        return {
            "program_name": self.program_name,
            "transition_score": self.transition_score,
            "pct_complete": self.pct_complete,
            "steps": [s.to_dict() for s in self.steps],
            "applicable_valleys": list(self.applicable_valleys),
            "notes": list(self.notes),
        }


def identify_valleys(profile: TechProfile) -> list[dict]:
    """Return the valleys of death most likely to threaten this effort."""
    hits: list[dict] = []
    if not profile.sponsor_identified:
        hits.append(VALLEYS_OF_DEATH[0])
    if not profile.funding_line_identified:
        hits.append(VALLEYS_OF_DEATH[1])
    if profile.requirement_doc in ("", "gap", "ICD"):
        hits.append(VALLEYS_OF_DEATH[2])
    if profile.mrl and profile.mrl < 8:
        hits.append(VALLEYS_OF_DEATH[3])
    elif not profile.mrl:
        hits.append(VALLEYS_OF_DEATH[3])
    if profile.trl >= 7 and profile.requirement_doc != "CPD":
        hits.append(VALLEYS_OF_DEATH[4])
    # De-duplicate while preserving order.
    seen = set()
    unique = []
    for h in hits:
        if h["name"] not in seen:
            seen.add(h["name"])
            unique.append(h)
    return unique


def generate_plan(profile: TechProfile) -> TransitionPlan:
    """Generate a tailored pilot-to-program transition plan for a profile."""
    steps: list[BridgeStep] = []
    order = 1

    def add(title: str, detail: str, owner: str, done: bool) -> None:
        nonlocal order
        steps.append(BridgeStep(order, title, detail, owner, done))
        order += 1

    add(
        "Confirm the prototype success criteria are met",
        "Document demonstrated performance against the objectives that motivated "
        "the pilot; capture test evidence.",
        "Program / engineering lead",
        profile.trl >= 6,
    )
    add(
        "Secure a program-of-record sponsor",
        "Identify the requirement owner / PEO willing to receive the capability.",
        "Requirements sponsor / PEO",
        profile.sponsor_identified,
    )
    add(
        "Mature the requirement (gap -> ICD -> CDD/CPD)",
        "Validate a JCIDS requirement so funds can be programmed against a need.",
        "Requirements community (J8 / capability sponsor)",
        profile.requirement_doc in ("CDD", "CPD"),
    )
    add(
        "Identify and program a funding line",
        "Get the correct color of money into the POM/budget cycle (RDT&E -> "
        "Procurement -> O&M as the effort matures).",
        "Comptroller / financial manager",
        profile.funding_line_identified,
    )
    add(
        "Select the transition acquisition pathway",
        "Choose the vehicle to sustain the capability (e.g., SBIR Phase III "
        "sole-source bridge, OT follow-on production, APFIT, or MTA rapid fielding).",
        "Contracting officer / PM",
        profile.has_sbir_history or profile.teaming,
    )
    add(
        "Raise manufacturing readiness",
        "Conduct a Manufacturing Readiness Assessment and plan LRIP as needed.",
        "Manufacturing / production lead",
        bool(profile.mrl and profile.mrl >= 8),
    )
    add(
        "Author the sustainment plan",
        "Produce a Life-Cycle Sustainment Plan (spares, training, support) with "
        "O&M funding identified.",
        "Product support manager",
        profile.requirement_doc == "CPD",
    )
    add(
        "Establish teaming for scale",
        "Team with a prime / integrator if scale or integration demands it.",
        "Business development / PM",
        profile.teaming,
    )

    tscore = _transition.score(profile).score
    valleys = identify_valleys(profile)
    notes = [
        f"Current transition-probability score: {tscore:.1f}/100.",
        f"{sum(1 for s in steps if s.done)} of {len(steps)} bridge steps already satisfied.",
    ]
    if valleys:
        notes.append(
            f"{len(valleys)} valley(s) of death likely apply — see applicable_valleys."
        )
    return TransitionPlan(
        program_name=profile.name,
        steps=steps,
        applicable_valleys=valleys,
        transition_score=tscore,
        notes=notes,
    )
