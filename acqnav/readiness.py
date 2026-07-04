"""Technology and Manufacturing Readiness Level scoring.

Implements TRL (1-9) and MRL (1-10) assessment from a structured questionnaire,
computes the readiness gap to a target level, and lists the evidence needed to
advance one level.

Definitions follow the DoD Technology Readiness Assessment Guidebook and the
DoD Manufacturing Readiness Level Deskbook (both unclassified / public).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# TRL definitions
# ---------------------------------------------------------------------------
TRL_DEFINITIONS: dict[int, str] = {
    1: "Basic principles observed and reported",
    2: "Technology concept and/or application formulated",
    3: "Analytical and experimental critical function / proof of concept",
    4: "Component/breadboard validation in a laboratory environment",
    5: "Component/breadboard validation in a relevant environment",
    6: "System/subsystem model or prototype demonstration in a relevant environment",
    7: "System prototype demonstration in an operational environment",
    8: "Actual system completed and qualified through test and demonstration",
    9: "Actual system proven through successful mission operations",
}

# Evidence expected to certify each TRL. Advancing to level N requires the
# evidence listed at level N.
TRL_EVIDENCE: dict[int, tuple[str, ...]] = {
    1: ("Peer-reviewed publications or basic research reports",),
    2: ("Documented concept / application; analytic studies",),
    3: ("Proof-of-concept experiments; analytical predictions validated in lab",),
    4: ("Breadboard integration; laboratory test data for key components",),
    5: (
        "Component validation in a relevant (not lab-benign) environment",
        "Documented relevant-environment definition",
    ),
    6: (
        "Representative prototype tested in a relevant environment",
        "Engineering-scale test data",
    ),
    7: (
        "Prototype demonstrated in an operational environment",
        "Operational test data with representative users",
    ),
    8: (
        "System qualified through developmental test and evaluation (DT&E)",
        "Full system integration and qualification records",
    ),
    9: (
        "Successful mission operations / operational test and evaluation (OT&E)",
        "Sustained operational performance data",
    ),
}

# ---------------------------------------------------------------------------
# MRL definitions (1-10)
# ---------------------------------------------------------------------------
MRL_DEFINITIONS: dict[int, str] = {
    1: "Basic manufacturing implications identified",
    2: "Manufacturing concepts identified",
    3: "Manufacturing proof of concept developed",
    4: "Capability to produce the technology in a laboratory environment",
    5: "Capability to produce prototype components in a production-relevant environment",
    6: "Capability to produce a prototype system/subsystem in a production-relevant environment",
    7: "Capability to produce systems/subsystems in a production-representative environment",
    8: "Pilot line capability demonstrated; ready for low-rate production",
    9: "Low-rate production demonstrated; capability in place for full-rate production",
    10: "Full-rate production demonstrated and lean production practices in place",
}


@dataclass
class ReadinessQuestion:
    """A single yes/no questionnaire item mapped to a level and dimension."""

    key: str
    text: str
    level: int
    dimension: str  # "TRL" or "MRL"


# A compact but representative questionnaire. Each answered "yes" is evidence
# that the corresponding level's exit criteria are met.
TRL_QUESTIONS: tuple[ReadinessQuestion, ...] = (
    ReadinessQuestion("trl1", "Have basic scientific principles been observed and documented?", 1, "TRL"),
    ReadinessQuestion("trl2", "Has a technology concept or application been formulated?", 2, "TRL"),
    ReadinessQuestion("trl3", "Has analytical/experimental proof of concept been demonstrated?", 3, "TRL"),
    ReadinessQuestion("trl4", "Have key components been validated as a breadboard in a lab?", 4, "TRL"),
    ReadinessQuestion("trl5", "Have components been validated in a relevant environment?", 5, "TRL"),
    ReadinessQuestion("trl6", "Has a prototype been demonstrated in a relevant environment?", 6, "TRL"),
    ReadinessQuestion("trl7", "Has a prototype been demonstrated in an operational environment?", 7, "TRL"),
    ReadinessQuestion("trl8", "Has the actual system been qualified through test and demonstration?", 8, "TRL"),
    ReadinessQuestion("trl9", "Has the system been proven in successful mission operations?", 9, "TRL"),
)

MRL_QUESTIONS: tuple[ReadinessQuestion, ...] = (
    ReadinessQuestion("mrl1", "Have basic manufacturing implications been identified?", 1, "MRL"),
    ReadinessQuestion("mrl2", "Have manufacturing concepts been identified?", 2, "MRL"),
    ReadinessQuestion("mrl3", "Has a manufacturing proof of concept been developed?", 3, "MRL"),
    ReadinessQuestion("mrl4", "Can the technology be produced in a laboratory environment?", 4, "MRL"),
    ReadinessQuestion("mrl5", "Can prototype components be produced in a production-relevant environment?", 5, "MRL"),
    ReadinessQuestion("mrl6", "Can a prototype system be produced in a production-relevant environment?", 6, "MRL"),
    ReadinessQuestion("mrl7", "Can systems be produced in a production-representative environment?", 7, "MRL"),
    ReadinessQuestion("mrl8", "Has a pilot line demonstrated readiness for low-rate production?", 8, "MRL"),
    ReadinessQuestion("mrl9", "Has low-rate production been demonstrated?", 9, "MRL"),
    ReadinessQuestion("mrl10", "Has full-rate production with lean practices been demonstrated?", 10, "MRL"),
)


@dataclass
class ReadinessResult:
    """Outcome of a readiness assessment for one dimension (TRL or MRL)."""

    dimension: str
    level: int
    definition: str
    max_level: int
    answered: dict[str, bool] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "level": self.level,
            "definition": self.definition,
            "max_level": self.max_level,
            "notes": list(self.notes),
        }


def _assess(
    questions: tuple[ReadinessQuestion, ...],
    answers: dict[str, bool],
    definitions: dict[int, str],
    dimension: str,
) -> ReadinessResult:
    """Level achieved = highest level for which that level AND all lower levels
    are answered ``True`` (readiness is monotonic; a gap resets progress)."""
    achieved = 0
    notes: list[str] = []
    ordered = sorted(questions, key=lambda q: q.level)
    for q in ordered:
        ans = bool(answers.get(q.key, False))
        if ans and q.level == achieved + 1:
            achieved = q.level
        elif not ans and q.level <= len(ordered):
            if q.level == achieved + 1:
                notes.append(f"Blocked at {dimension} {q.level}: '{q.text}' not yet met")
                break
    achieved = max(1, achieved) if dimension == "TRL" else max(1, achieved)
    return ReadinessResult(
        dimension=dimension,
        level=achieved,
        definition=definitions[achieved],
        max_level=max(definitions),
        answered=dict(answers),
        notes=notes,
    )


def assess_trl(answers: dict[str, bool]) -> ReadinessResult:
    """Assess TRL from questionnaire answers keyed ``trl1``..``trl9``."""
    return _assess(TRL_QUESTIONS, answers, TRL_DEFINITIONS, "TRL")


def assess_mrl(answers: dict[str, bool]) -> ReadinessResult:
    """Assess MRL from questionnaire answers keyed ``mrl1``..``mrl10``."""
    return _assess(MRL_QUESTIONS, answers, MRL_DEFINITIONS, "MRL")


@dataclass
class ReadinessGap:
    """Gap between a current and target level with the evidence to close it."""

    dimension: str
    current: int
    target: int
    steps: list[dict] = field(default_factory=list)

    @property
    def levels_to_advance(self) -> int:
        return max(0, self.target - self.current)

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "current": self.current,
            "target": self.target,
            "levels_to_advance": self.levels_to_advance,
            "steps": list(self.steps),
        }


def trl_gap(current: int, target: int) -> ReadinessGap:
    """Return the evidence needed to move TRL from ``current`` to ``target``."""
    current = max(1, min(9, int(current)))
    target = max(1, min(9, int(target)))
    steps = []
    for lvl in range(current + 1, target + 1):
        steps.append({
            "level": lvl,
            "definition": TRL_DEFINITIONS[lvl],
            "evidence_needed": list(TRL_EVIDENCE.get(lvl, ())),
        })
    return ReadinessGap("TRL", current, target, steps)


def mrl_gap(current: int, target: int) -> ReadinessGap:
    """Return the manufacturing milestones needed to move MRL up."""
    current = max(1, min(10, int(current)))
    target = max(1, min(10, int(target)))
    steps = []
    for lvl in range(current + 1, target + 1):
        steps.append({
            "level": lvl,
            "definition": MRL_DEFINITIONS[lvl],
        })
    return ReadinessGap("MRL", current, target, steps)


def evidence_to_advance(dimension: str, current: int) -> list[str]:
    """Evidence needed to advance exactly one level from ``current``."""
    dimension = dimension.upper()
    if dimension == "TRL":
        nxt = min(9, int(current) + 1)
        return list(TRL_EVIDENCE.get(nxt, ()))
    if dimension == "MRL":
        nxt = min(10, int(current) + 1)
        return [MRL_DEFINITIONS[nxt]]
    raise ValueError(f"unknown dimension: {dimension}")
