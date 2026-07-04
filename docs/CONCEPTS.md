# Concepts acqnav models

`acqnav` encodes concepts from published, unclassified U.S. DoD acquisition
doctrine. This page maps each module to its doctrinal basis so the tool's logic
is auditable.

## Adaptive Acquisition Framework (AAF)

The AAF (DoDI 5000.02) organizes acquisition into multiple *pathways* so a
program can pick the approach that fits its capability, not a one-size-fits-all
process. `acqnav.pathways` models the pathways below and recommends among them.

| Pathway | Authority |
|---|---|
| SBIR/STTR Phase I / II / III | 15 U.S.C. 638; SBA SBIR/STTR Policy Directive |
| Other Transaction (Prototype) | 10 U.S.C. 4022 |
| Commercial Solutions Opening (CSO) | 10 U.S.C. 3458 |
| Middle Tier of Acquisition (Rapid Prototyping / Rapid Fielding) | 10 U.S.C. 4023; DoDI 5000.80 |
| APFIT | 10 U.S.C. 4571 |
| Major Capability Acquisition | DoDI 5000.85 |
| Software Acquisition Pathway | DoDI 5000.87 |
| Defense Business Systems | DoDI 5000.75 |

## Technology & Manufacturing Readiness Levels

- **TRL (1–9)** — from the DoD Technology Readiness Assessment Guidebook.
  TRL 1 is basic principles; TRL 9 is proven in mission operations.
- **MRL (1–10)** — from the DoD Manufacturing Readiness Level Deskbook. MRL
  measures whether the thing can be *produced* at rate, quality, and cost.

`acqnav.readiness` scores both from a structured questionnaire, treating
readiness as monotonic (a gap at level N blocks credit for higher levels) and
lists the evidence needed to advance.

## JCIDS requirement documents

The Joint Capabilities Integration and Development System (JCIDS Manual)
produces the requirement artifacts that justify and shape an acquisition:

- **ICD** — Initial Capabilities Document (documents a gap; supports Milestone A)
- **CDD** — Capability Development Document (validated attributes; supports Milestone B)
- **CPD** — Capability Production Document (production attributes; supports Milestone C)

Capability gaps are analyzed across **DOTMLPF-P** (Doctrine, Organization,
Training, Materiel, Leadership, Personnel, Facilities, Policy) so a non-materiel
solution can be preferred where appropriate. Performance is expressed as
**KPP / KSA / APA** attributes. `acqnav.requirements` implements this.

## Color of money

DoD appropriations ("colors of money," per the DoD Financial Management
Regulation 7000.14-R and annual Appropriations Acts) may only buy certain things
and are available for a fixed number of years:

| Code | Appropriation | Availability |
|---|---|---|
| 3600 | RDT&E | 2 years |
| 3010 / 3020 | Procurement | 3 years |
| 3400 | Operations & Maintenance | 1 year |
| 3080 (BA-8) | Software & Digital Technology | 3 years |

`acqnav.funding` maps intent → correct color and flags classic mistakes (e.g.,
using RDT&E to buy production quantities, or O&M to fund new development).

## Milestones and gates

The Major Capability Acquisition life cycle (DoDI 5000.85) is governed by
decision points — the Materiel Development Decision, Milestones A/B/C, the
Development RFP Release Decision, and the Full-Rate Production Decision — each
gating entry into a phase (MSA, TMRR, EMD, P&D). `acqnav.gates` tracks the
artifacts expected at each gate and rolls up readiness.

## Transition and the valley of death

The gap between a successful prototype and a sustained Program of Record is the
"valley of death." `acqnav.transition` scores transition probability from the
well-understood drivers of that gap, and `acqnav.pilot_to_program` names the
specific valleys a profile faces and generates a bridge plan.
