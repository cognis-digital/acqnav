# CLI reference

The `acqnav` command exposes the whole navigator. All subcommands accept a
common set of **profile flags**; most also accept `--json` for machine output.
The tool makes no network calls.

## Profile flags

Applies to `assess`, `pathways`, `transition`, `plan`, `report`:

| Flag | Meaning |
|---|---|
| `--profile FILE` | Load a profile from JSON (flags below override individual fields) |
| `--name NAME` | Program / technology name |
| `--trl N` | Technology Readiness Level 1–9 |
| `--mrl N` | Manufacturing Readiness Level 0–10 (0 = not assessed) |
| `--dollars N` | Near-term effort value (USD) |
| `--prior-transitions N` | Count of prior successful transitions |
| `--requirement-doc {ICD,CDD,CPD,gap}` | JCIDS artifact in hand |
| `--contract-type ...` | `firm_fixed_price`, `cost_plus`, `other_transaction`, `idiq`, `baa_grant`, `unknown` |
| `--urgency {routine,accelerated,urgent}` | Delivery urgency |
| `--maturity {commercial,adapted_commercial,developmental}` | Offering character |
| `--small-business` | Offeror qualifies as a small business |
| `--has-sbir-history` | Prior SBIR/STTR award (enables Phase III bridge) |
| `--sponsor-identified` | A program-of-record sponsor exists |
| `--funding-line-identified` | A specific funding line (PE/BLI) exists |
| `--teaming` | Established prime/integrator teaming |
| `--dual-use` | Technology has a commercial dual-use market |

## Subcommands

### `assess`
Full navigator assessment. `--format {json,md,html}` (default `md`).
```bash
acqnav assess --trl 6 --small-business --requirement-doc CDD --format md
```

### `pathways`
Rank acquisition pathways. `--all` includes non-viable ones; `--json` for JSON.
```bash
acqnav pathways --trl 5 --dollars 1500000 --small-business --has-sbir-history
```

### `transition`
Explainable transition-probability score with factor breakdown.
```bash
acqnav transition --trl 7 --sponsor-identified --funding-line-identified --json
```

### `requirements`
JCIDS alignment, gap classification, or value narrative.
```bash
acqnav requirements --doc CDD                       # alignment info
acqnav requirements --gap "Need a fusion system"    # DOTMLPF-P classification
acqnav requirements --narrative --name Sentinel --context "..." \
    --feature "Fusion" --feature "Offline mode"     # value narrative template
```

### `funding`
Color-of-money guidance and mistake detection.
```bash
acqnav funding --list                               # all appropriations
acqnav funding --intent production --proposed 3600  # flags the mistake
```

### `gates`
Milestone / gate tracking.
```bash
acqnav gates --list                                 # gates + expected artifacts
acqnav gates --completed completed.json --json      # readiness rollup
```
`completed.json` maps gate keys to lists of completed artifact names, e.g.
`{"mdd": ["Initial Capabilities Document (ICD)"]}`.

### `readiness`
TRL/MRL assessment or gap analysis.
```bash
acqnav readiness --dimension TRL --current 4 --gap 7 --json   # evidence to advance
acqnav readiness --dimension TRL --answers answers.json       # questionnaire
```

### `plan`
Pilot-to-program transition plan.
```bash
acqnav plan --trl 6 --sponsor-identified --requirement-doc ICD
```

### `report`
Export a full report to a file. `--format {json,md,html}` (default `html`).
```bash
acqnav report --trl 6 --small-business --format html --out assessment.html
```
The HTML report is fully self-contained (inline CSS, no JavaScript, no external
assets) and safe to open on an air-gapped machine.
