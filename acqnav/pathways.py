"""DoD acquisition pathway model and recommender.

This module encodes the real, unclassified U.S. DoD acquisition pathways and,
given a :class:`~acqnav.profile.TechProfile`, ranks the viable pathways with a
transparent rationale.

Sources (all unclassified / public): DoDI 5000.02 (Adaptive Acquisition
Framework), DoDI 5000.80 (Middle Tier of Acquisition), DoDI 5000.85 (Major
Capability Acquisition), DoDI 5000.87 (Software Acquisition Pathway), DoDI
5000.75 (Defense Business Systems), 15 U.S.C. 638 / SBA SBIR-STTR Policy
Directive, 10 U.S.C. 4022 (Other Transactions), and DAU pathway guidance.

Nothing here concerns weapons employment; it concerns *how programs are bought
and transitioned*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .profile import ContractType, Maturity, TechProfile, Urgency


@dataclass(frozen=True)
class Pathway:
    """A single acquisition pathway definition."""

    key: str
    name: str
    authority: str
    entry_criteria: tuple[str, ...]
    typical_timeline: str
    funding_vehicle: tuple[str, ...]
    exit_transition: str
    pros: tuple[str, ...]
    cons: tuple[str, ...]
    # Machine-usable envelope for scoring
    trl_min: int = 1
    trl_max: int = 9
    dollar_min: float = 0.0
    dollar_max: float = float("inf")
    favors_small_business: bool = False
    favors_commercial: bool = False
    favors_urgent: bool = False

    def dollar_band_str(self) -> str:
        lo = f"${self.dollar_min:,.0f}" if self.dollar_min else "$0"
        hi = "no ceiling" if self.dollar_max == float("inf") else f"${self.dollar_max:,.0f}"
        return f"{lo} – {hi}"


@dataclass
class PathwayScore:
    """Result of scoring one pathway against a profile."""

    pathway: Pathway
    score: float
    rationale: list[str] = field(default_factory=list)
    disqualifiers: list[str] = field(default_factory=list)

    @property
    def viable(self) -> bool:
        return not self.disqualifiers

    def to_dict(self) -> dict:
        return {
            "key": self.pathway.key,
            "name": self.pathway.name,
            "score": round(self.score, 1),
            "viable": self.viable,
            "rationale": list(self.rationale),
            "disqualifiers": list(self.disqualifiers),
        }


# ---------------------------------------------------------------------------
# Pathway catalog
# ---------------------------------------------------------------------------
PATHWAYS: dict[str, Pathway] = {
    "sbir_phase_i": Pathway(
        key="sbir_phase_i",
        name="SBIR/STTR Phase I",
        authority="15 U.S.C. 638; SBA SBIR/STTR Policy Directive",
        entry_criteria=(
            "Small business (<500 employees) offeror",
            "Feasibility-stage technology (typically TRL 1-4)",
            "Response to an open SBIR/STTR topic or a direct-to-Phase-II pathway",
        ),
        typical_timeline="6-12 months (feasibility)",
        funding_vehicle=("SBIR/STTR set-aside (RDT&E-funded topic)",),
        exit_transition="Successful feasibility -> compete for Phase II",
        pros=(
            "Non-dilutive; no repayment",
            "Retains data rights for the small business",
            "Low barrier to entry for early technology",
        ),
        cons=(
            "Small dollar value; feasibility only",
            "No guarantee of Phase II",
            "Topic-driven; must match a solicitation",
        ),
        trl_min=1, trl_max=4, dollar_min=50_000, dollar_max=350_000,
        favors_small_business=True,
    ),
    "sbir_phase_ii": Pathway(
        key="sbir_phase_ii",
        name="SBIR/STTR Phase II",
        authority="15 U.S.C. 638; SBA SBIR/STTR Policy Directive",
        entry_criteria=(
            "Prior Phase I award (or direct-to-Phase-II authority)",
            "Prototype-stage development (typically TRL 4-6)",
            "Small business offeror",
        ),
        typical_timeline="18-24 months (prototype)",
        funding_vehicle=("SBIR/STTR (RDT&E); may add matching funds",),
        exit_transition="Prototype demonstration -> Phase III commercialization",
        pros=(
            "Substantial prototype funding",
            "Preserves SBIR data-rights protections",
            "Positions for Phase III sole-source bridge",
        ),
        cons=(
            "Requires prior Phase I unless direct-to-II",
            "Still not a program of record",
            "Bridge to fielding is the classic valley of death",
        ),
        trl_min=4, trl_max=6, dollar_min=500_000, dollar_max=2_000_000,
        favors_small_business=True,
    ),
    "sbir_phase_iii": Pathway(
        key="sbir_phase_iii",
        name="SBIR/STTR Phase III (sole-source bridge)",
        authority="15 U.S.C. 638(r); SBA Policy Directive (Phase III)",
        entry_criteria=(
            "Work derives from a prior SBIR/STTR Phase I or II award",
            "Small business retains SBIR data rights lineage",
            "A buyer (program office) wants the matured capability",
        ),
        typical_timeline="Negotiated; no competition required",
        funding_vehicle=(
            "ANY appropriation (RDT&E, Procurement, O&M) — not SBIR set-aside",
        ),
        exit_transition="Sole-source production / sustainment contract",
        pros=(
            "Sole-source authority — no re-competition",
            "Any color of money can fund it",
            "Direct path into a program of record",
        ),
        cons=(
            "Requires genuine SBIR lineage traceability",
            "Still needs a sponsor with funding to execute",
        ),
        trl_min=6, trl_max=9, dollar_min=1_000_000,
        favors_small_business=True,
    ),
    "ota_prototype": Pathway(
        key="ota_prototype",
        name="Other Transaction (Prototype)",
        authority="10 U.S.C. 4022",
        entry_criteria=(
            "Prototype project relevant to enhancing DoD mission effectiveness",
            "Meaningful nontraditional participation OR 1/3 cost share",
            "Awarded via consortium or direct OT agreement",
        ),
        typical_timeline="Weeks to months to award; execution varies",
        funding_vehicle=("RDT&E (prototype); flexible OT terms",),
        exit_transition="Successful prototype -> OT follow-on production (4022(f))",
        pros=(
            "Not subject to the FAR — flexible IP and terms",
            "Fast award via consortia (CMFs)",
            "Attracts nontraditional / commercial firms",
        ),
        cons=(
            "Requires nontraditional participation or cost share",
            "Less familiar to some contracting shops",
            "Follow-on production requires competitive-prototype basis",
        ),
        trl_min=3, trl_max=7, dollar_min=1_000_000,
        favors_commercial=True, favors_urgent=True,
    ),
    "cso": Pathway(
        key="cso",
        name="Commercial Solutions Opening (CSO)",
        authority="10 U.S.C. 3458; DoD CSO guidance",
        entry_criteria=(
            "Innovative commercial items, technologies, or services",
            "Competitive selection via merit-based process",
            "Solutions offered by the market (not a rigid government spec)",
        ),
        typical_timeline="Months; solution-brief driven",
        funding_vehicle=("RDT&E or Procurement depending on maturity",),
        exit_transition="FAR or OT contract award for the selected solution",
        pros=(
            "Buys innovation the way the commercial market sells it",
            "Merit-based, solution-brief lightweight entry",
            "Good for adapted-commercial technology",
        ),
        cons=(
            "Best for commercial / near-commercial items",
            "Downstream contract still needed",
        ),
        trl_min=5, trl_max=9, dollar_min=250_000,
        favors_commercial=True,
    ),
    "mta_rapid_prototyping": Pathway(
        key="mta_rapid_prototyping",
        name="Middle Tier of Acquisition — Rapid Prototyping",
        authority="10 U.S.C. 4023; DoDI 5000.80",
        entry_criteria=(
            "Fieldable prototype within 5 years of an approved requirement",
            "Not intended to satisfy full JCIDS at entry",
            "Demonstrated technology that can be rapidly prototyped",
        ),
        typical_timeline="Complete within 5 years",
        funding_vehicle=("RDT&E; may transition to Procurement",),
        exit_transition="Residual operational capability -> rapid fielding or MCA",
        pros=(
            "Bypasses the full JCIDS / 5000.85 documentation burden",
            "Speed-oriented; abbreviated requirements",
            "Delivers a residual operational prototype",
        ),
        cons=(
            "5-year clock is firm",
            "Sustainment tail must be planned separately",
        ),
        trl_min=5, trl_max=8, dollar_min=10_000_000,
        favors_urgent=True,
    ),
    "mta_rapid_fielding": Pathway(
        key="mta_rapid_fielding",
        name="Middle Tier of Acquisition — Rapid Fielding",
        authority="10 U.S.C. 4023; DoDI 5000.80",
        entry_criteria=(
            "Proven technology / mature product",
            "Begin production within 6 months, complete fielding within 5 years",
            "Minimal development required",
        ),
        typical_timeline="Production start <=6 months; fielding <=5 years",
        funding_vehicle=("Procurement (and RDT&E for minor development)",),
        exit_transition="Fielded capability -> sustainment (O&M)",
        pros=(
            "Fastest path for mature / proven products",
            "Abbreviated documentation",
            "Rapid delivery to the operator",
        ),
        cons=(
            "Requires already-proven technology (high TRL)",
            "Not for developmental efforts",
        ),
        trl_min=7, trl_max=9, dollar_min=10_000_000,
        favors_urgent=True,
    ),
    "apfit": Pathway(
        key="apfit",
        name="APFIT (Accelerate the Procurement and Fielding of Innovative Technologies)",
        authority="10 U.S.C. 4571 (APFIT program)",
        entry_criteria=(
            "Technology at or near production readiness needing a fielding push",
            "Typically from a small business / nontraditional",
            "Selected by the department for accelerated procurement funding",
        ),
        typical_timeline="1-2 fiscal years (procurement acceleration)",
        funding_vehicle=("Dedicated APFIT Procurement funding",),
        exit_transition="Fielded quantity -> program of record adoption",
        pros=(
            "Bridges the valley of death with procurement dollars",
            "Targets mature small-business technology",
            "Signals departmental demand",
        ),
        cons=(
            "Highly competitive, limited annual funding",
            "Requires near-production maturity",
        ),
        trl_min=7, trl_max=9, dollar_min=5_000_000, dollar_max=50_000_000,
        favors_small_business=True, favors_urgent=True,
    ),
    "mca": Pathway(
        key="mca",
        name="Major Capability Acquisition (MCA)",
        authority="DoDI 5000.85",
        entry_criteria=(
            "Large, complex, or enduring capability need",
            "Full JCIDS requirement (ICD/CDD/CPD)",
            "Milestone A/B/C decision governance",
        ),
        typical_timeline="Many years across TMRR, EMD, and P&D phases",
        funding_vehicle=("RDT&E -> Procurement -> O&M across the life cycle",),
        exit_transition="Full-rate production and sustained program of record",
        pros=(
            "Appropriate for large, enduring systems",
            "Rigorous cost, schedule, and performance governance",
            "Durable funding line once established",
        ),
        cons=(
            "Slow; heavy documentation",
            "High oversight burden",
            "Poor fit for fast-moving commercial technology",
        ),
        trl_min=4, trl_max=9, dollar_min=50_000_000,
    ),
    "software_pathway": Pathway(
        key="software_pathway",
        name="Software Acquisition Pathway",
        authority="DoDI 5000.87",
        entry_criteria=(
            "Software-intensive capability (applications or embedded)",
            "Modern iterative / DevSecOps delivery approach",
            "User agreement and value assessment in place",
        ),
        typical_timeline="Continuous; MVP/MVCR within ~1 year",
        funding_vehicle=(
            "RDT&E and/or a single 'BA-8 Software and Digital Technology' line",
        ),
        exit_transition="Continuous delivery; no traditional MDD/MS structure",
        pros=(
            "Purpose-built for software; no MS A/B/C waterfall",
            "Continuous value delivery to users",
            "Supports agile / DevSecOps",
        ),
        cons=(
            "Requires disciplined product management and metrics",
            "Cultural shift for traditional program offices",
        ),
        trl_min=4, trl_max=9, dollar_min=1_000_000,
        favors_commercial=True,
    ),
    "dbs": Pathway(
        key="dbs",
        name="Defense Business Systems (DBS)",
        authority="DoDI 5000.75",
        entry_criteria=(
            "Business system (finance, logistics, HR, acquisition IT)",
            "Business Process Reengineering completed",
            "Commercial-off-the-shelf preference",
        ),
        typical_timeline="Iterative authority-to-proceed reviews",
        funding_vehicle=("RDT&E / Procurement / O&M as appropriate",),
        exit_transition="Deployed business capability -> sustainment",
        pros=(
            "Tailored governance for business IT",
            "Strong COTS preference",
            "Fits ERP / enterprise software",
        ),
        cons=(
            "Only for business systems, not warfighting capability",
            "Requires business-process reengineering",
        ),
        trl_min=5, trl_max=9, dollar_min=1_000_000,
        favors_commercial=True,
    ),
}


def all_pathways() -> list[Pathway]:
    """Return every pathway in a stable order."""
    return list(PATHWAYS.values())


def get_pathway(key: str) -> Pathway:
    """Look up a pathway by key, raising ``KeyError`` if unknown."""
    return PATHWAYS[key]


# ---------------------------------------------------------------------------
# Scoring / recommendation
# ---------------------------------------------------------------------------
def _score_pathway(p: Pathway, profile: TechProfile) -> PathwayScore:
    score = 50.0
    rationale: list[str] = []
    disq: list[str] = []

    # --- TRL envelope ---
    if profile.trl < p.trl_min:
        disq.append(
            f"TRL {profile.trl} below pathway minimum TRL {p.trl_min}"
        )
    elif profile.trl > p.trl_max:
        # Over-mature is a soft penalty, not a hard disqualifier.
        score -= 12
        rationale.append(
            f"TRL {profile.trl} above typical ceiling TRL {p.trl_max} "
            f"(pathway aimed at less-mature work)"
        )
    else:
        score += 15
        rationale.append(
            f"TRL {profile.trl} sits within the pathway band "
            f"(TRL {p.trl_min}-{p.trl_max})"
        )

    # --- Dollar envelope ---
    if profile.dollars:
        if profile.dollars < p.dollar_min:
            score -= 15
            rationale.append(
                f"Effort {profile.dollars:,.0f} below typical floor "
                f"{p.dollar_min:,.0f}"
            )
        elif profile.dollars > p.dollar_max:
            score -= 18
            rationale.append(
                f"Effort {profile.dollars:,.0f} above typical ceiling "
                f"{p.dollar_max:,.0f}"
            )
        else:
            score += 10
            rationale.append(
                f"Dollar value fits the pathway band ({p.dollar_band_str()})"
            )

    # --- Small business fit ---
    if p.favors_small_business:
        if profile.small_business:
            score += 12
            rationale.append("Small-business offeror aligns with this pathway")
        else:
            disq.append("Pathway requires a small-business offeror")

    # --- Commercial fit ---
    if p.favors_commercial:
        if profile.maturity in (Maturity.COMMERCIAL, Maturity.ADAPTED_COMMERCIAL):
            score += 10
            rationale.append("Commercial / adapted-commercial maturity fits")
        else:
            score -= 6
            rationale.append(
                "Pathway favors commercial items; effort is developmental"
            )

    # --- Urgency fit ---
    if p.favors_urgent:
        if profile.urgency in (Urgency.URGENT, Urgency.ACCELERATED):
            score += 12
            rationale.append("Urgency matches a speed-oriented pathway")
        else:
            score -= 4
            rationale.append("Speed-oriented pathway with only routine urgency")
    elif profile.urgency == Urgency.URGENT:
        score -= 8
        rationale.append(
            "Effort is URGENT but this pathway is not speed-optimized"
        )

    # --- SBIR lineage specifics ---
    if p.key == "sbir_phase_iii" and not profile.has_sbir_history:
        disq.append("Phase III requires prior SBIR/STTR award lineage")
    if p.key == "sbir_phase_ii" and not (
        profile.has_sbir_history or "direct_to_phase_ii" in profile.tags
    ):
        rationale.append(
            "No prior Phase I on record — needs direct-to-Phase-II authority"
        )
        score -= 8

    # --- Contract type alignment ---
    if p.key.startswith("ota") and profile.contract_type == ContractType.OTHER_TRANSACTION:
        score += 8
        rationale.append("Seeking an Other Transaction — direct fit")

    # --- Sponsor presence helps fielding pathways ---
    if p.key in {"apfit", "mta_rapid_fielding", "sbir_phase_iii"}:
        if profile.sponsor_identified:
            score += 8
            rationale.append("Identified sponsor strengthens a fielding pathway")
        else:
            score -= 6
            rationale.append("No sponsor identified — fielding pathway at risk")

    score = max(0.0, min(100.0, score))
    return PathwayScore(pathway=p, score=score, rationale=rationale, disqualifiers=disq)


def recommend(
    profile: TechProfile,
    *,
    include_nonviable: bool = False,
    candidates: Iterable[Pathway] | None = None,
) -> list[PathwayScore]:
    """Rank acquisition pathways for a profile.

    Parameters
    ----------
    profile:
        The technology / effort profile.
    include_nonviable:
        If True, also return pathways with hard disqualifiers (sorted last).
    candidates:
        Optionally restrict scoring to a subset of pathways.

    Returns
    -------
    list[PathwayScore]
        Sorted best-first. Viable pathways always sort ahead of nonviable ones.
    """
    pool = list(candidates) if candidates is not None else all_pathways()
    scored = [_score_pathway(p, profile) for p in pool]
    if not include_nonviable:
        scored = [s for s in scored if s.viable]
    # Viable first, then by score, then stable by name.
    scored.sort(key=lambda s: (not s.viable, -s.score, s.pathway.name))
    return scored


def top_recommendation(profile: TechProfile) -> PathwayScore | None:
    """Return the single best viable pathway, or ``None`` if none are viable."""
    ranked = recommend(profile)
    return ranked[0] if ranked else None
