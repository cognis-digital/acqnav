# acqnav — Defense Acquisition Navigator

**Open, self-hostable software for navigating the U.S. Department of Defense acquisition and program-management process.** `acqnav` models the real, unclassified DoD acquisition pathways, scores technology readiness (TRL/MRL), produces a *transparent, explainable* transition-probability estimate, aligns technology to requirement frameworks (JCIDS), maps "color of money," tracks milestone gates, and generates pilot-to-program transition plans.

Where brokered "navigator" products score your transition probability behind a black box, `acqnav` ships the actual working software — every point of every score is traceable to a named, weighted factor you can inspect, tune, and self-host. No accounts, no network calls, no vendor lock. Runs air-gapped on the Python standard library.

> **Scope.** `acqnav` is strictly for **acquisition and program management** — money, milestones, requirements, and pathways. It contains **nothing** related to weapons, targeting, guidance, kill-chains, fire-control, or autonomous-weapon capability. A CI test (`tests/test_scope_guard.py`) enforces this at the source level.

---

## Why acqnav

Getting a technology from a good prototype to a funded, fielded Program of Record is the hard part of defense — the "valley of death." The bottleneck is rarely the technology; it's knowing *which pathway to use, what the transition really depends on, which color of money can pay for it, and which artifacts each gate needs.* `acqnav` puts that navigation logic in your hands, in the open.

- **Transparent transition scoring.** A 0–100 score assembled from seven visible, weighted factors (readiness, requirement alignment, funding line, sponsor, track record, manufacturing readiness, teaming) — with a factor-by-factor breakdown and the highest-leverage improvements. Not a black box.
- **Real pathway model.** SBIR/STTR I/II/III, Other Transactions, CSO, MTA rapid-prototyping / rapid-fielding, APFIT, Major Capability Acquisition, the Software Acquisition Pathway, and Defense Business Systems — each with entry criteria, timeline, funding vehicle, exit/transition, and pros/cons, plus a recommender that ranks the viable options for your profile.
- **Grounded in public doctrine.** DoDI 5000.02 / .80 / .85 / .87 / .75, the JCIDS Manual, SBIR/STTR policy, 10 U.S.C. 4022, and the DoD Financial Management Regulation. All unclassified.
- **Offline & self-hostable.** Pure standard library. No network calls at runtime.

## Install

```bash
git clone https://github.com/cognis-digital/acqnav
cd acqnav
python -m pip install -e ".[dev]"
```

Requires Python 3.10+.

## Quick start (CLI)

```bash
# Rank acquisition pathways for a small-business prototype
acqnav pathways --trl 5 --dollars 1500000 --small-business --has-sbir-history \
    --urgency urgent --maturity adapted_commercial --contract-type other_transaction

# Explainable transition-probability score
acqnav transition --trl 6 --sponsor-identified --funding-line-identified \
    --requirement-doc CDD --teaming

# Color-of-money check (catches the classic mistakes)
acqnav funding --intent production --proposed 3600     # flags RDT&E-for-production

# Milestone gate rollup
acqnav gates --list

# Pilot-to-program transition plan
acqnav plan --trl 6 --sponsor-identified --requirement-doc ICD

# Full assessment, exported as a self-contained HTML report
acqnav report --trl 6 --small-business --has-sbir-history --sponsor-identified \
    --requirement-doc CDD --format html --out assessment.html
```

Example — the transition score is fully broken out:

```
Transition probability: 71.0/100 (Moderate)

  Requirement alignment            16.0 / 20    Capability Development Document in place
  Funding line identified          16.0 / 16    Specific funding line identified
  Program-of-record sponsor        16.0 / 16    Sponsor / requirement owner identified
  Technical readiness (TRL)        13.8 / 22    TRL 6/9
  Teaming with integrator/prime     8.0 / 8     Established teaming relationship
  Prior transition track record     0.0 / 10    0 prior transition(s)
  Manufacturing readiness (MRL)     1.2 / 8     MRL not assessed

Highest-leverage improvements:
  - Build transition track record via a pilot or prototype OTA (+10.0 pts available)
  - Advance TRL with relevant/operational-environment testing evidence (+8.2 pts available)
  - Conduct a formal Manufacturing Readiness Assessment and raise MRL (+6.8 pts available)
```

## Quick start (library)

```python
from acqnav.profile import TechProfile, Urgency, Maturity, ContractType
from acqnav import pathways, transition, report

prof = TechProfile(
    name="Sentinel Fusion",
    trl=5, mrl=4, dollars=1_800_000,
    contract_type=ContractType.OTHER_TRANSACTION,
    urgency=Urgency.URGENT, maturity=Maturity.ADAPTED_COMMERCIAL,
    small_business=True, has_sbir_history=True,
    sponsor_identified=True, requirement_doc="ICD",
)

best = pathways.top_recommendation(prof)
print(best.pathway.name, best.score)          # e.g. "Other Transaction (Prototype)" 97.0

ts = transition.score(prof)
print(ts.score, ts.band)                       # 40.7 Low
print(ts.explain())                            # full factor breakdown

# Export a self-contained HTML report (no JS, no external assets)
html = report.to_html(report.Assessment(prof))
```

## Modules

| Module | What it does |
|---|---|
| `acqnav.pathways` | Real DoD acquisition-pathway catalog + profile-based recommender |
| `acqnav.readiness` | TRL (1–9) / MRL (1–10) questionnaire scoring, gaps, evidence-to-advance |
| `acqnav.transition` | Transparent, weighted transition-probability score with breakdown |
| `acqnav.requirements` | JCIDS (ICD/CDD/CPD) alignment, DOTMLPF-P gap classification, value narrative |
| `acqnav.funding` | "Color of money" mapping, mistake detection, fiscal-year phasing |
| `acqnav.gates` | Milestone/gate (MDD, MS A/B/C, FRP) artifact tracker + readiness rollup |
| `acqnav.pilot_to_program` | Valleys-of-death identification + transition-plan generator |
| `acqnav.report` | JSON / Markdown / self-contained HTML report export |
| `acqnav.cli` | `acqnav` command-line interface |

## Demos

Nine runnable, end-to-end scenarios live in [`demos/`](demos/). Run them all:

```bash
python demos/run_all.py
```

Highlights: a small AI-fusion startup walking the whole navigator (`demo_01`), a transition-score sensitivity analysis showing every point's origin (`demo_03`), color-of-money mistake detection (`demo_04`), and a commercial dual-use vendor walkthrough (`demo_09`).

## Documentation

- [`docs/CONCEPTS.md`](docs/CONCEPTS.md) — the acquisition concepts acqnav models, with sources
- [`docs/PATHWAYS.md`](docs/PATHWAYS.md) — the pathway catalog in detail
- [`docs/TRANSITION_SCORING.md`](docs/TRANSITION_SCORING.md) — how the score is computed (and how to tune it)
- [`docs/CLI.md`](docs/CLI.md) — full CLI reference
- [`docs/SCOPE.md`](docs/SCOPE.md) — the defensive-only scope and its enforcement

## Testing

```bash
python -m pytest -q          # 160+ tests
python demos/run_all.py      # all demos must exit 0
```

## Disclaimer

`acqnav` is a decision-support and educational tool built entirely from published, unclassified acquisition doctrine. It is **not** official DoD guidance, does not produce authoritative determinations, and does not replace a contracting officer, comptroller, or requirements sponsor. Validate all outputs against current regulation and your program's authorities before acting.

## License

Cognis Open Collaboration License (COCL) v1.0. See [LICENSE](LICENSE). © Cognis Digital LLC.
