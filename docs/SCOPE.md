# Scope

`acqnav` is deliberately and permanently scoped to **defense acquisition and
program management** — the business and process side of defense. It helps
programs navigate money, milestones, requirements, readiness, and acquisition
pathways.

## In scope

- Acquisition-pathway selection and comparison
- Technology / manufacturing readiness assessment (TRL / MRL)
- Transition-probability estimation and program transition planning
- Requirement-framework (JCIDS) alignment and value narratives
- Appropriations ("color of money") mapping and fiscal-year phasing
- Milestone / gate artifact tracking
- Report generation for acquisition decision-makers

## Explicitly out of scope

`acqnav` contains nothing — and will accept no contribution — related to:

- Weapons employment, targeting, or weaponeering
- Guidance, navigation, or control of a weapon
- Kill-chains or fire-control
- Autonomous-weapon capability
- Any operational employment detail

The requirements module's "warfighter value narrative" is a **positioning and
decision-framing template only**. It maps a technology's features to a
capability need and a measurable effect for an acquisition audience. It is
OPLAN-agnostic and never describes targeting or employment.

## Enforcement

This scope is enforced in CI. `tests/test_scope_guard.py` scans every source
file and fails the build if an *affirmative* use of an out-of-scope term
appears. Scope **disclaimers** (statements of what the tool does *not* do) are
permitted; any affirmative capability language is not. This makes the boundary a
structural property of the codebase, not just a policy in a README.
