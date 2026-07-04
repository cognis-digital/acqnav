"""'Color of money' mapping for DoD appropriations.

Models the major DoD appropriation categories ("colors of money"), what each
can and cannot buy, their period of availability, and the common mistakes
programs make. Grounded in the DoD Financial Management Regulation
(DoD 7000.14-R) and the appropriations categories in Title 10 / annual
Appropriations Acts. Unclassified, doctrinal.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Appropriation:
    """One appropriation category ('color of money')."""

    code: str
    name: str
    availability_years: int         # period of availability (obligation)
    can_buy: tuple[str, ...]
    cannot_buy: tuple[str, ...]
    notes: str

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "availability_years": self.availability_years,
            "can_buy": list(self.can_buy),
            "cannot_buy": list(self.cannot_buy),
            "notes": self.notes,
        }


APPROPRIATIONS: dict[str, Appropriation] = {
    "3600": Appropriation(
        code="3600",
        name="Research, Development, Test & Evaluation (RDT&E)",
        availability_years=2,
        can_buy=(
            "Research and technology development",
            "Prototypes and engineering development",
            "Developmental and operational test & evaluation",
            "Systems engineering prior to a production decision",
        ),
        cannot_buy=(
            "Production quantities for fielding",
            "Sustainment of fielded systems",
        ),
        notes="2-year money. Funds the develop/prove phase, not fielding.",
    ),
    "3010": Appropriation(
        code="3010",
        name="Procurement — Aircraft/Missile/etc. (investment)",
        availability_years=3,
        can_buy=(
            "Production quantities of a proven system",
            "Investment items above the expense/investment threshold",
            "Initial spares tied to procurement",
        ),
        cannot_buy=(
            "Basic research or development",
            "Day-to-day operations and maintenance",
        ),
        notes="3-year money. Buys the thing once it is production-ready.",
    ),
    "3020": Appropriation(
        code="3020",
        name="Procurement — Weapons/Other Procurement (investment)",
        availability_years=3,
        can_buy=(
            "Production quantities of proven equipment",
            "Investment-threshold end items and modifications",
        ),
        cannot_buy=(
            "Research and development",
            "Expenses / consumables below the investment threshold",
        ),
        notes="3-year money. Companion procurement line to 3010.",
    ),
    "3400": Appropriation(
        code="3400",
        name="Operations & Maintenance (O&M)",
        availability_years=1,
        can_buy=(
            "Operating and sustaining fielded capability",
            "Expenses below the investment/expense threshold",
            "Services, training, and maintenance",
        ),
        cannot_buy=(
            "Development of new systems (that is RDT&E)",
            "Investment-threshold end items (that is Procurement)",
        ),
        notes="1-year money; use-it-or-lose-it. Sustains what is already fielded.",
    ),
    "3080": Appropriation(
        code="3080",
        name="Procurement — Software & Digital Technology (BA-8)",
        availability_years=3,
        can_buy=(
            "Software acquisition-pathway efforts under a single BA-8 line",
            "Blended development and fielding of software capability",
        ),
        cannot_buy=(
            "Non-software major end items outside the software pathway",
        ),
        notes="Consolidated software funding enabling continuous delivery.",
    ),
}

# Common color-of-money mistakes to flag.
COMMON_MISTAKES: tuple[dict, ...] = (
    {
        "name": "Using RDT&E to buy production quantities",
        "detail": "RDT&E (3600) funds development and test, not fielding. "
                  "Production must be Procurement.",
        "trigger": lambda intent: intent in {"production", "fielding"},
        "wrong_colors": ("3600",),
    },
    {
        "name": "Using O&M for a new-start development",
        "detail": "O&M (3400) sustains fielded capability; it cannot fund the "
                  "development of a new system.",
        "trigger": lambda intent: intent in {"development", "prototype"},
        "wrong_colors": ("3400",),
    },
    {
        "name": "Using O&M for investment-threshold items",
        "detail": "End items above the expense/investment threshold must be "
                  "Procurement, not O&M.",
        "trigger": lambda intent: intent == "investment_item",
        "wrong_colors": ("3400",),
    },
    {
        "name": "Bona fide need / expiring 1-year money",
        "detail": "O&M is 1-year money; obligate only for a bona fide need in "
                  "the current fiscal year.",
        "trigger": lambda intent: intent == "sustainment",
        "wrong_colors": (),
    },
)

# Which appropriation is appropriate for a given intent.
INTENT_TO_COLOR: dict[str, tuple[str, ...]] = {
    "research": ("3600",),
    "development": ("3600",),
    "prototype": ("3600",),
    "test": ("3600",),
    "production": ("3010", "3020"),
    "fielding": ("3010", "3020"),
    "investment_item": ("3010", "3020"),
    "software": ("3080", "3600"),
    "sustainment": ("3400",),
    "operations": ("3400",),
    "training": ("3400",),
}


@dataclass
class FundingGuidance:
    """Guidance on which color(s) of money fit an intent, with warnings."""

    intent: str
    recommended: list[Appropriation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "recommended": [a.to_dict() for a in self.recommended],
            "warnings": list(self.warnings),
        }


def get_appropriation(code: str) -> Appropriation:
    """Look up an appropriation by code."""
    return APPROPRIATIONS[str(code)]


def all_appropriations() -> list[Appropriation]:
    """Return all appropriation categories in a stable order."""
    return list(APPROPRIATIONS.values())


def guidance_for(intent: str, *, proposed_color: str | None = None) -> FundingGuidance:
    """Recommend the color of money for an intent and flag mistakes.

    Parameters
    ----------
    intent:
        One of the keys in :data:`INTENT_TO_COLOR` (e.g. ``"development"``,
        ``"production"``, ``"sustainment"``, ``"software"``).
    proposed_color:
        Optionally, the appropriation the program is *considering*; if it is a
        known mistake for the intent, a warning is emitted.
    """
    intent = (intent or "").lower().strip()
    codes = INTENT_TO_COLOR.get(intent)
    warnings: list[str] = []
    if codes is None:
        warnings.append(f"Unknown intent {intent!r}; no color-of-money mapping.")
        codes = ()
    recommended = [APPROPRIATIONS[c] for c in codes if c in APPROPRIATIONS]

    for mistake in COMMON_MISTAKES:
        try:
            hit = mistake["trigger"](intent)
        except Exception:
            hit = False
        if hit:
            if proposed_color and proposed_color in mistake["wrong_colors"]:
                warnings.append(
                    f"MISTAKE: {mistake['name']} — {mistake['detail']}"
                )
            elif not mistake["wrong_colors"]:
                warnings.append(f"NOTE: {mistake['name']} — {mistake['detail']}")

    if proposed_color and codes and proposed_color not in codes:
        warnings.append(
            f"Proposed color {proposed_color} is not the typical fit for "
            f"'{intent}' (typical: {', '.join(codes)})."
        )
    return FundingGuidance(intent=intent, recommended=recommended, warnings=warnings)


def phasing_plan(intent_by_fy: dict[int, str]) -> list[dict]:
    """Build a simple fiscal-year phasing plan.

    Parameters
    ----------
    intent_by_fy:
        Mapping of fiscal year -> intent (e.g. ``{2026: "development",
        2028: "production"}``). Returns one row per FY with the recommended
        color(s) and any warnings.
    """
    plan = []
    for fy in sorted(intent_by_fy):
        g = guidance_for(intent_by_fy[fy])
        plan.append({
            "fy": fy,
            "intent": intent_by_fy[fy],
            "colors": [a.code for a in g.recommended],
            "warnings": g.warnings,
        })
    return plan
