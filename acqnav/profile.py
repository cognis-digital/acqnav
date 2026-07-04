"""Shared input profile used across acqnav modules.

The :class:`TechProfile` is the single, structured description of a technology /
program effort that the navigator reasons over. Every field maps to an
unclassified acquisition concept so the tool stays fully explainable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class ContractType(str, Enum):
    """Contract vehicle the effort is seeking."""

    FIRM_FIXED_PRICE = "firm_fixed_price"
    COST_PLUS = "cost_plus"
    OTHER_TRANSACTION = "other_transaction"
    IDIQ = "idiq"
    BAA_GRANT = "baa_grant"
    UNKNOWN = "unknown"


class Maturity(str, Enum):
    """Whether the offering is commercial-off-the-shelf or developmental."""

    COMMERCIAL = "commercial"
    ADAPTED_COMMERCIAL = "adapted_commercial"
    DEVELOPMENTAL = "developmental"


class Urgency(str, Enum):
    """How fast the capability is needed."""

    ROUTINE = "routine"          # normal program timelines
    ACCELERATED = "accelerated"  # faster than routine, planned
    URGENT = "urgent"            # rapid fielding, months not years


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


@dataclass
class TechProfile:
    """A structured description of a technology / acquisition effort.

    Attributes
    ----------
    name:
        Short program or technology name.
    trl:
        Technology Readiness Level, 1-9.
    mrl:
        Manufacturing Readiness Level, 1-10. ``0`` means "not assessed".
    contract_type:
        The contract vehicle sought.
    dollars:
        Approximate dollar value of the near-term effort, in USD.
    urgency:
        Delivery urgency.
    maturity:
        Commercial vs. developmental character of the offering.
    small_business:
        True if the offeror qualifies as a small business (SBIR/STTR relevant).
    has_sbir_history:
        True if the offeror has prior SBIR/STTR Phase I/II awards (enables the
        Phase III sole-source bridge).
    prior_transitions:
        Count of prior successful transitions to a program of record.
    sponsor_identified:
        True if a program-of-record sponsor / requirement owner is identified.
    funding_line_identified:
        True if a specific funding line (PE/BLI) has been identified.
    requirement_doc:
        Which JCIDS-style requirement artifact exists, if any
        (one of "", "ICD", "CDD", "CPD", "gap").
    teaming:
        True if there is an established prime/integrator teaming relationship.
    dual_use:
        True if the technology has a commercial dual-use market.
    """

    name: str = "Unnamed effort"
    trl: int = 1
    mrl: int = 0
    contract_type: ContractType = ContractType.UNKNOWN
    dollars: float = 0.0
    urgency: Urgency = Urgency.ROUTINE
    maturity: Maturity = Maturity.DEVELOPMENTAL
    small_business: bool = False
    has_sbir_history: bool = False
    prior_transitions: int = 0
    sponsor_identified: bool = False
    funding_line_identified: bool = False
    requirement_doc: str = ""
    teaming: bool = False
    dual_use: bool = False
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.trl = _clamp(int(self.trl), 1, 9)
        self.mrl = _clamp(int(self.mrl), 0, 10)
        self.prior_transitions = max(0, int(self.prior_transitions))
        self.dollars = max(0.0, float(self.dollars))
        if not isinstance(self.contract_type, ContractType):
            self.contract_type = ContractType(str(self.contract_type))
        if not isinstance(self.urgency, Urgency):
            self.urgency = Urgency(str(self.urgency))
        if not isinstance(self.maturity, Maturity):
            self.maturity = Maturity(str(self.maturity))
        rd = (self.requirement_doc or "").upper()
        if rd and rd not in {"ICD", "CDD", "CPD", "GAP"}:
            raise ValueError(f"unknown requirement_doc: {self.requirement_doc!r}")
        self.requirement_doc = rd if rd != "GAP" else "gap"

    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["contract_type"] = self.contract_type.value
        d["urgency"] = self.urgency.value
        d["maturity"] = self.maturity.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TechProfile":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        clean = {k: v for k, v in data.items() if k in known}
        return cls(**clean)
