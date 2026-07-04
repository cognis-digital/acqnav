# The acquisition pathway catalog

`acqnav.pathways` models the DoD acquisition pathways below. Each `Pathway`
carries: entry criteria, typical timeline, funding vehicle, exit/transition,
pros and cons, plus a machine-usable envelope (TRL band, dollar band, and
small-business / commercial / urgency preferences) used by the recommender.

## Catalog

| Key | Pathway | Authority | Typical TRL |
|---|---|---|---|
| `sbir_phase_i` | SBIR/STTR Phase I | 15 U.S.C. 638 | 1–4 |
| `sbir_phase_ii` | SBIR/STTR Phase II | 15 U.S.C. 638 | 4–6 |
| `sbir_phase_iii` | SBIR/STTR Phase III (sole-source bridge) | 15 U.S.C. 638(r) | 6–9 |
| `ota_prototype` | Other Transaction (Prototype) | 10 U.S.C. 4022 | 3–7 |
| `cso` | Commercial Solutions Opening | 10 U.S.C. 3458 | 5–9 |
| `mta_rapid_prototyping` | MTA — Rapid Prototyping | 10 U.S.C. 4023 | 5–8 |
| `mta_rapid_fielding` | MTA — Rapid Fielding | 10 U.S.C. 4023 | 7–9 |
| `apfit` | APFIT | 10 U.S.C. 4571 | 7–9 |
| `mca` | Major Capability Acquisition | DoDI 5000.85 | 4–9 |
| `software_pathway` | Software Acquisition Pathway | DoDI 5000.87 | 4–9 |
| `dbs` | Defense Business Systems | DoDI 5000.75 | 5–9 |

## The SBIR-to-Phase-III bridge

A particularly powerful (and under-used) route: work derived from a prior
SBIR/STTR Phase I or II award can be continued via a **Phase III** contract that
requires **no competition** and can be funded by **any** appropriation
(RDT&E, Procurement, or O&M). `acqnav` recognizes SBIR lineage
(`has_sbir_history`) as a prerequisite and boosts this pathway when a sponsor is
identified.

## How recommendation works

`recommend(profile)` scores each pathway from a 50-point baseline:

1. **TRL envelope** — inside the band adds points; below the minimum is a hard
   disqualifier; above the ceiling is a soft penalty (the pathway targets
   less-mature work).
2. **Dollar envelope** — inside the band adds points; outside penalizes.
3. **Small-business / commercial / urgency fit** — pathways that favor those
   attributes reward matching profiles and penalize (or disqualify) mismatches.
4. **Pathway-specific rules** — e.g. Phase III requires SBIR lineage; fielding
   pathways reward an identified sponsor; an OT-seeking contract type matches
   the OT pathway.

Scores are clamped to `[0, 100]`. Viable pathways (no hard disqualifiers) always
sort ahead of non-viable ones. Use `include_nonviable=True` to see everything
with the disqualifiers spelled out.

```python
from acqnav import pathways
from acqnav.profile import TechProfile, Urgency

prof = TechProfile(trl=8, dollars=20_000_000, small_business=True,
                   has_sbir_history=True, sponsor_identified=True,
                   urgency=Urgency.URGENT)
for s in pathways.recommend(prof)[:3]:
    print(s.score, s.pathway.name)
```
