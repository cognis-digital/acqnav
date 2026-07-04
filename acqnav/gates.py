"""Milestone / gate tracker for the acquisition life cycle.

Models the major decision points and phases of the Major Capability Acquisition
life cycle (DoDI 5000.85): the Materiel Development Decision (MDD), Milestones
A/B/C, and the TMRR / EMD / P&D phases. For each gate it lists the artifacts
expected and produces a readiness rollup from which artifacts are complete.

This is a program-management artifact tracker. It concerns documentation and
decision governance, not operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Gate:
    """A milestone / decision point and its expected artifacts."""

    key: str
    name: str
    phase_entered: str
    description: str
    artifacts: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "phase_entered": self.phase_entered,
            "description": self.description,
            "artifacts": list(self.artifacts),
        }


# Ordered life-cycle gates.
GATES: tuple[Gate, ...] = (
    Gate(
        "mdd", "Materiel Development Decision (MDD)",
        "Materiel Solution Analysis (MSA)",
        "Formal entry point; decision to conduct an Analysis of Alternatives.",
        ("Initial Capabilities Document (ICD)",
         "AoA Study Guidance and Study Plan",
         "Draft Concept of Operations"),
    ),
    Gate(
        "ms_a", "Milestone A",
        "Technology Maturation & Risk Reduction (TMRR)",
        "Approves entry into TMRR; commits to risk-reduction prototyping.",
        ("Analysis of Alternatives (AoA) results",
         "Draft Capability Development Document (CDD)",
         "Technology Readiness Assessment (TRA)",
         "Acquisition Strategy",
         "Cost estimate (program office / independent)"),
    ),
    Gate(
        "dev_rfp", "Development RFP Release Decision",
        "TMRR (late)",
        "Authorizes release of the Development RFP prior to Milestone B.",
        ("Validated Capability Development Document (CDD)",
         "Draft Request for Proposal (RFP)",
         "Preliminary Design Review (PDR) report",
         "Updated Acquisition Strategy"),
    ),
    Gate(
        "ms_b", "Milestone B",
        "Engineering & Manufacturing Development (EMD)",
        "Program initiation; commits to EMD with defined baselines.",
        ("Acquisition Program Baseline (APB)",
         "Systems Engineering Plan (SEP)",
         "Test and Evaluation Master Plan (TEMP)",
         "Life-Cycle Sustainment Plan (LCSP)",
         "Independent Cost Estimate (ICE)",
         "Manufacturing Readiness Assessment (MRA)"),
    ),
    Gate(
        "ms_c", "Milestone C",
        "Production & Deployment (P&D)",
        "Authorizes Low-Rate Initial Production (LRIP).",
        ("Capability Production Document (CPD)",
         "Developmental Test & Evaluation (DT&E) report",
         "Production readiness / MRL assessment",
         "LRIP quantity justification"),
    ),
    Gate(
        "frp", "Full-Rate Production Decision",
        "Production & Deployment (P&D)",
        "Authorizes full-rate production and deployment.",
        ("Initial Operational Test & Evaluation (IOT&E) report",
         "Full-rate production cost estimate",
         "Sustainment readiness confirmation"),
    ),
)

GATE_BY_KEY: dict[str, Gate] = {g.key: g for g in GATES}


@dataclass
class GateStatus:
    """Completion status of a gate given which artifacts are complete."""

    gate: Gate
    completed_artifacts: list[str] = field(default_factory=list)

    @property
    def missing(self) -> list[str]:
        done = set(self.completed_artifacts)
        return [a for a in self.gate.artifacts if a not in done]

    @property
    def pct_complete(self) -> float:
        total = len(self.gate.artifacts)
        if not total:
            return 100.0
        done = sum(1 for a in self.gate.artifacts if a in set(self.completed_artifacts))
        return round(100.0 * done / total, 1)

    @property
    def ready(self) -> bool:
        return not self.missing

    def to_dict(self) -> dict:
        return {
            "gate": self.gate.key,
            "name": self.gate.name,
            "pct_complete": self.pct_complete,
            "ready": self.ready,
            "completed": list(self.completed_artifacts),
            "missing": self.missing,
        }


def get_gate(key: str) -> Gate:
    """Look up a gate by key."""
    return GATE_BY_KEY[key]


def all_gates() -> list[Gate]:
    """Return the life-cycle gates in order."""
    return list(GATES)


def gate_status(key: str, completed_artifacts: list[str]) -> GateStatus:
    """Compute the completion status for one gate."""
    gate = get_gate(key)
    # Normalize: only count artifacts that actually belong to the gate.
    valid = [a for a in completed_artifacts if a in gate.artifacts]
    return GateStatus(gate=gate, completed_artifacts=valid)


@dataclass
class ProgramRollup:
    """A readiness rollup across all tracked gates."""

    statuses: list[GateStatus] = field(default_factory=list)

    @property
    def next_gate(self) -> GateStatus | None:
        for s in self.statuses:
            if not s.ready:
                return s
        return None

    @property
    def overall_pct(self) -> float:
        if not self.statuses:
            return 0.0
        return round(sum(s.pct_complete for s in self.statuses) / len(self.statuses), 1)

    def to_dict(self) -> dict:
        return {
            "overall_pct": self.overall_pct,
            "next_gate": self.next_gate.gate.key if self.next_gate else None,
            "gates": [s.to_dict() for s in self.statuses],
        }


def rollup(completed_by_gate: dict[str, list[str]]) -> ProgramRollup:
    """Build a program-wide rollup from per-gate completed-artifact lists.

    Gates not present in ``completed_by_gate`` are treated as having no
    completed artifacts (0%).
    """
    statuses = []
    for g in GATES:
        completed = completed_by_gate.get(g.key, [])
        statuses.append(gate_status(g.key, completed))
    return ProgramRollup(statuses=statuses)
