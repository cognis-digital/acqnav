# How the transition-probability score works

`acqnav.transition.score()` returns a 0–100 estimate of how likely a technology
is to transition into a sustained, funded Program of Record. Unlike brokered
"transition probability" products, the entire computation is open and every
point is attributable to a named factor.

## The factors

The score is a weighted sum of seven factors. Each factor produces a *raw*
achievement in `[0, 1]`, multiplied by its weight to yield *points*. The final
score normalizes total points against total weight to a 0–100 scale, so custom
weights need not sum to 100.

| Factor | Default weight | How `raw` is derived |
|---|---:|---|
| Technical readiness (TRL) | 22 | `(TRL - 1) / 8` |
| Requirement alignment | 20 | CPD 1.0 · CDD 0.8 · ICD 0.55 · gap 0.35 · none 0.1 |
| Funding line identified | 16 | 1.0 if a specific funding line exists, else 0.0 |
| Program-of-record sponsor | 16 | 1.0 if a sponsor/requirement owner exists, else 0.0 |
| Prior transition track record | 10 | `min(1.0, prior_transitions / 3)` |
| Manufacturing readiness (MRL) | 8 | `(MRL - 1) / 9`; 0.15 if MRL not assessed |
| Teaming with integrator/prime | 8 | 1.0 if a teaming relationship exists, else 0.0 |

## Bands

| Score | Band |
|---|---|
| ≥ 75 | High |
| 50–74 | Moderate |
| 25–49 | Low |
| < 25 | Very Low |

## Recommendations

The score also returns up to three **highest-leverage improvements** — the
factors with the most *unrealized* weight (weight minus points), each with the
number of points still available. This turns the score from a verdict into a
to-do list.

## Tuning the weights

Weights are a policy choice. A program office that considers a validated
requirement paramount can raise its weight:

```python
from acqnav import transition
from acqnav.profile import TechProfile

ts = transition.score(
    TechProfile(trl=6, requirement_doc="CDD"),
    weights={"requirement_alignment": 35.0},
)
```

Missing keys fall back to `transition.DEFAULT_WEIGHTS`. Because the score is
normalized by total weight, you can emphasize factors without having to keep the
weights summing to 100.

## Why this beats a black box

Every number in the output can be traced to an input and a weight. A program can
(a) see exactly why its score is what it is, (b) simulate the effect of an
improvement before making it, and (c) adjust the weighting to match its
command's transition philosophy — none of which is possible with an opaque,
brokered score.
