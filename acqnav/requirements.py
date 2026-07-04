"""Requirement-framework alignment and warfighter value narrative generation.

Aligns a technology to unclassified requirement frameworks — JCIDS documents
(ICD / CDD / CPD) and capability gaps — and generates an OPLAN-agnostic
"warfighter value narrative" that maps features to a capability need to a
measurable effect.

This module is strictly narrative / positioning. It never touches targeting,
weaponeering, or any operational employment detail. It helps a program describe
*why a capability matters to the acquisition decision*, in the language the
requirements community uses (DOTMLPF-P, KPP/KSA/APA), sourced from the JCIDS
Manual (Manual for the Operation of the Joint Capabilities Integration and
Development System).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# JCIDS document reference
# ---------------------------------------------------------------------------
JCIDS_DOCUMENTS: dict[str, dict[str, str]] = {
    "ICD": {
        "name": "Initial Capabilities Document",
        "purpose": "Documents a capability gap / need and justifies a materiel solution.",
        "stage": "Pre-Materiel Development Decision; supports Analysis of Alternatives.",
        "supports": "Milestone A",
    },
    "CDD": {
        "name": "Capability Development Document",
        "purpose": "Defines validated, measurable performance attributes (KPPs/KSAs/APAs).",
        "stage": "Supports Development RFP Release and engineering development.",
        "supports": "Milestone B",
    },
    "CPD": {
        "name": "Capability Production Document",
        "purpose": "Refines performance attributes for the production decision.",
        "stage": "Supports the production and deployment decision.",
        "supports": "Milestone C",
    },
}

# DOTMLPF-P domains: capability gaps may be materiel or non-materiel.
DOTMLPF_P = (
    "Doctrine", "Organization", "Training", "Materiel", "Leadership",
    "Personnel", "Facilities", "Policy",
)

# Requirement attribute types in JCIDS.
ATTRIBUTE_TYPES = {
    "KPP": "Key Performance Parameter (mandatory; failure may cause program reassessment)",
    "KSA": "Key System Attribute (essential but below KPP threshold)",
    "APA": "Additional Performance Attribute (informative / desired)",
}


@dataclass
class Feature:
    """A single technology feature to be mapped to a capability need."""

    name: str
    capability_need: str
    measurable_effect: str
    attribute_type: str = "APA"   # KPP / KSA / APA

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "capability_need": self.capability_need,
            "measurable_effect": self.measurable_effect,
            "attribute_type": self.attribute_type,
            "attribute_desc": ATTRIBUTE_TYPES.get(self.attribute_type, ""),
        }


@dataclass
class AlignmentResult:
    """The result of aligning a technology to a requirement framework."""

    doc_type: str
    doc_info: dict[str, str]
    readiness_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "doc_type": self.doc_type,
            "doc_info": dict(self.doc_info),
            "readiness_notes": list(self.readiness_notes),
        }


def align_to_document(doc_type: str) -> AlignmentResult:
    """Return reference info and readiness notes for a JCIDS document type."""
    key = (doc_type or "").upper()
    if key not in JCIDS_DOCUMENTS:
        valid = ", ".join(JCIDS_DOCUMENTS)
        raise ValueError(f"unknown JCIDS document {doc_type!r}; expected one of {valid}")
    info = JCIDS_DOCUMENTS[key]
    notes = [
        f"{info['name']} ({key}) supports {info['supports']}.",
        info["purpose"],
        f"Ensure performance attributes are traceable and measurable ({', '.join(ATTRIBUTE_TYPES)}).",
    ]
    return AlignmentResult(key, dict(info), notes)


def classify_gap(description: str) -> dict:
    """Classify a described capability gap across DOTMLPF-P domains.

    A materiel-solution recommendation is made only if the gap language implies
    a materiel need; otherwise the tool flags that a non-materiel solution may
    apply (a key JCIDS discipline that avoids buying hardware for a training or
    doctrine problem).
    """
    text = (description or "").lower()
    materiel_signals = ("system", "sensor", "software", "platform", "equipment",
                        "hardware", "capability to", "tool", "device")
    nonmateriel_signals = ("training", "doctrine", "policy", "organization",
                           "manning", "personnel", "process", "leadership")
    is_materiel = any(s in text for s in materiel_signals)
    is_nonmateriel = any(s in text for s in nonmateriel_signals)
    domains = [d for d in DOTMLPF_P if d.lower() in text]
    if is_materiel and not domains:
        domains = ["Materiel"]
    recommendation = (
        "Materiel solution appears warranted; proceed toward an ICD/AoA."
        if is_materiel and not is_nonmateriel
        else "Consider non-materiel (DOTmLPF-P) solutions before a materiel start."
        if is_nonmateriel and not is_materiel
        else "Mixed indicators — perform a formal capability gap analysis."
    )
    return {
        "description": description,
        "candidate_domains": domains or ["(undetermined)"],
        "materiel_signal": is_materiel,
        "nonmateriel_signal": is_nonmateriel,
        "recommendation": recommendation,
    }


def value_narrative(
    program_name: str,
    mission_context: str,
    features: list[Feature],
    *,
    doc_type: str = "ICD",
) -> str:
    """Generate an OPLAN-agnostic warfighter value narrative template.

    The narrative maps each feature -> capability need -> measurable effect,
    framed for an acquisition audience. It is deliberately generic (no plan,
    target, or employment specifics) and is meant to be edited by the program.
    """
    align = align_to_document(doc_type)
    lines: list[str] = []
    lines.append(f"# Warfighter Value Narrative — {program_name}")
    lines.append("")
    lines.append("_OPLAN-agnostic positioning narrative for acquisition decision-makers._")
    lines.append("")
    lines.append("## 1. Capability Need & Requirement Context")
    lines.append(mission_context.strip() or "(Describe the enduring capability need this supports.)")
    lines.append("")
    lines.append(
        f"Aligned requirement artifact: **{align.doc_info['name']} ({align.doc_type})** "
        f"— {align.doc_info['purpose']}"
    )
    lines.append("")
    lines.append("## 2. Feature -> Capability Need -> Measurable Effect")
    lines.append("")
    lines.append("| Feature | Capability Need Addressed | Measurable Effect | Attribute |")
    lines.append("|---|---|---|---|")
    for f in features:
        lines.append(
            f"| {f.name} | {f.capability_need} | {f.measurable_effect} | {f.attribute_type} |"
        )
    lines.append("")
    lines.append("## 3. Measures of Effectiveness (to be validated with the sponsor)")
    for f in features:
        lines.append(f"- **{f.name}**: {f.measurable_effect}")
    lines.append("")
    lines.append("## 4. Decision Framing")
    lines.append(
        "This capability reduces a documented gap and can be represented as "
        "measurable performance attributes (KPP/KSA/APA) traceable to the "
        f"{align.doc_type}. Non-materiel (DOTMLPF-P) considerations should be "
        "reviewed alongside the materiel contribution."
    )
    lines.append("")
    lines.append("> Template only — replace bracketed guidance and validate all "
                 "attributes with the requirement sponsor before use.")
    return "\n".join(lines)
