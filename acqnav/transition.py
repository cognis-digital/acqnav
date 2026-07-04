"""Transparent, explainable transition-probability scoring.

Marcantonio Global's "NINA" advertises a "transition probability score". This
module ships an *open, auditable* equivalent: a 0-100 score assembled from
weighted, individually-visible factors. Every point is traceable to a factor,
so program managers can see exactly why a score is what it is and what to
improve — the opposite of a black box.

The factors are drawn from the well-understood drivers of the DoD "valley of
death": technical readiness, requirement pull, an identified funding line, a
program-of-record sponsor, prior transition track record, manufacturing
readiness, and teaming with an integrator/prime.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .profile import TechProfile


@dataclass
class Factor:
    """One transition-probability factor and its contribution."""

    key: str
    label: str
    weight: float          # max points this factor can contribute
    raw: float             # 0.0-1.0 achievement of the factor
    rationale: str

    @property
    def points(self) -> float:
        return round(self.weight * max(0.0, min(1.0, self.raw)), 2)

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "weight": self.weight,
            "raw": round(self.raw, 3),
            "points": self.points,
            "rationale": self.rationale,
        }


@dataclass
class TransitionScore:
    """A full, explainable transition-probability breakdown."""

    score: float
    band: str
    factors: list[Factor] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 1),
            "band": self.band,
            "factors": [f.to_dict() for f in self.factors],
            "recommendations": list(self.recommendations),
        }

    def explain(self) -> str:
        """Human-readable factor-by-factor breakdown."""
        lines = [f"Transition probability: {self.score:.1f}/100 ({self.band})", ""]
        for f in sorted(self.factors, key=lambda x: -x.weight):
            lines.append(
                f"  {f.label:<32} {f.points:>5.1f} / {f.weight:<4.0f}  {f.rationale}"
            )
        if self.recommendations:
            lines.append("")
            lines.append("Highest-leverage improvements:")
            for r in self.recommendations:
                lines.append(f"  - {r}")
        return "\n".join(lines)


# Default weights (sum to 100). Tunable via ``weights=`` on :func:`score`.
DEFAULT_WEIGHTS: dict[str, float] = {
    "technical_readiness": 22.0,
    "requirement_alignment": 20.0,
    "funding_line": 16.0,
    "sponsor": 16.0,
    "track_record": 10.0,
    "manufacturing_readiness": 8.0,
    "teaming": 8.0,
}


def _band(score: float) -> str:
    if score >= 75:
        return "High"
    if score >= 50:
        return "Moderate"
    if score >= 25:
        return "Low"
    return "Very Low"


def _req_alignment_raw(profile: TechProfile) -> tuple[float, str]:
    doc = profile.requirement_doc
    mapping = {
        "CPD": (1.0, "Capability Production Document in place (production-ready requirement)"),
        "CDD": (0.8, "Capability Development Document in place (validated requirement)"),
        "ICD": (0.55, "Initial Capabilities Document in place (need identified)"),
        "gap": (0.35, "Documented capability gap, no validated requirement yet"),
        "": (0.1, "No requirement document identified"),
    }
    return mapping.get(doc, (0.1, "No requirement document identified"))


def score(
    profile: TechProfile,
    *,
    weights: dict[str, float] | None = None,
) -> TransitionScore:
    """Compute a transparent transition-probability score for a profile.

    Parameters
    ----------
    profile:
        The technology / effort profile.
    weights:
        Optional override of factor weights. Missing keys fall back to
        :data:`DEFAULT_WEIGHTS`. Weights need not sum to 100; the final score is
        normalized to a 0-100 scale by total weight.
    """
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        w.update(weights)

    factors: list[Factor] = []

    # Technical readiness (TRL scaled 1-9 -> 0-1, floor above pure TRL1).
    trl_raw = (profile.trl - 1) / 8.0
    factors.append(Factor(
        "technical_readiness", "Technical readiness (TRL)", w["technical_readiness"],
        trl_raw, f"TRL {profile.trl}/9",
    ))

    # Requirement alignment.
    req_raw, req_msg = _req_alignment_raw(profile)
    factors.append(Factor(
        "requirement_alignment", "Requirement alignment", w["requirement_alignment"],
        req_raw, req_msg,
    ))

    # Funding line identified.
    factors.append(Factor(
        "funding_line", "Funding line identified", w["funding_line"],
        1.0 if profile.funding_line_identified else 0.0,
        "Specific funding line identified" if profile.funding_line_identified
        else "No funding line identified",
    ))

    # Program-of-record sponsor.
    factors.append(Factor(
        "sponsor", "Program-of-record sponsor", w["sponsor"],
        1.0 if profile.sponsor_identified else 0.0,
        "Sponsor / requirement owner identified" if profile.sponsor_identified
        else "No sponsor identified",
    ))

    # Prior transition track record (saturating at 3 prior transitions).
    tr_raw = min(1.0, profile.prior_transitions / 3.0)
    factors.append(Factor(
        "track_record", "Prior transition track record", w["track_record"],
        tr_raw, f"{profile.prior_transitions} prior transition(s)",
    ))

    # Manufacturing readiness (MRL 1-10; 0 = not assessed -> low credit).
    if profile.mrl:
        mrl_raw = (profile.mrl - 1) / 9.0
        mrl_msg = f"MRL {profile.mrl}/10"
    else:
        mrl_raw = 0.15
        mrl_msg = "MRL not assessed"
    factors.append(Factor(
        "manufacturing_readiness", "Manufacturing readiness (MRL)",
        w["manufacturing_readiness"], mrl_raw, mrl_msg,
    ))

    # Teaming with an integrator / prime.
    factors.append(Factor(
        "teaming", "Teaming with integrator/prime", w["teaming"],
        1.0 if profile.teaming else 0.0,
        "Established teaming relationship" if profile.teaming
        else "No teaming relationship identified",
    ))

    total_weight = sum(f.weight for f in factors) or 1.0
    total_points = sum(f.points for f in factors)
    normalized = 100.0 * total_points / total_weight

    # Recommendations: the factors with the largest unrealized weight.
    gaps = sorted(
        factors,
        key=lambda f: -(f.weight - f.points),
    )
    recs: list[str] = []
    for f in gaps:
        unrealized = f.weight - f.points
        if unrealized < 2.0:
            continue
        recs.append(_recommendation_for(f.key, unrealized))
        if len(recs) >= 3:
            break

    return TransitionScore(
        score=round(normalized, 1),
        band=_band(normalized),
        factors=factors,
        recommendations=recs,
    )


def _recommendation_for(key: str, unrealized: float) -> str:
    tips = {
        "technical_readiness":
            "Advance TRL with relevant/operational-environment testing evidence",
        "requirement_alignment":
            "Secure a validated JCIDS requirement (ICD -> CDD -> CPD)",
        "funding_line":
            "Identify a specific funding line (PE/BLI) with a sponsor's comptroller",
        "sponsor":
            "Recruit a program-of-record sponsor / requirement owner",
        "track_record":
            "Build transition track record via a pilot or prototype OTA",
        "manufacturing_readiness":
            "Conduct a formal Manufacturing Readiness Assessment and raise MRL",
        "teaming":
            "Establish a teaming relationship with a prime / integrator",
    }
    base = tips.get(key, f"Improve factor '{key}'")
    return f"{base} (+{unrealized:.1f} pts available)"
