"""Command-line interface for acqnav.

Subcommands
-----------
- ``assess``        full navigator assessment for a profile (JSON/MD/HTML)
- ``pathways``      rank viable acquisition pathways
- ``transition``    explainable transition-probability score
- ``requirements``  JCIDS alignment + warfighter value narrative
- ``funding``       color-of-money guidance
- ``gates``         milestone / gate readiness rollup
- ``plan``          pilot-to-program transition plan
- ``report``        export a full report to a file

Profiles may be supplied inline via flags or loaded from a JSON file with
``--profile FILE``. The tool makes no network calls.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import (
    __version__,
    funding,
    gates,
    pathways,
    pilot_to_program,
    readiness,
    report,
    requirements,
    transition,
)
from .profile import ContractType, Maturity, TechProfile, Urgency


# ---------------------------------------------------------------------------
# Profile assembly
# ---------------------------------------------------------------------------
def _profile_from_args(args: argparse.Namespace) -> TechProfile:
    if getattr(args, "profile", None):
        with open(args.profile, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        prof = TechProfile.from_dict(data)
    else:
        prof = TechProfile()
    # Inline overrides (only if explicitly provided).
    for attr in ("name", "trl", "mrl", "dollars", "prior_transitions",
                 "requirement_doc"):
        val = getattr(args, attr, None)
        if val is not None:
            setattr(prof, attr, val)
    if getattr(args, "contract_type", None):
        prof.contract_type = ContractType(args.contract_type)
    if getattr(args, "urgency", None):
        prof.urgency = Urgency(args.urgency)
    if getattr(args, "maturity", None):
        prof.maturity = Maturity(args.maturity)
    for flag in ("small_business", "has_sbir_history", "sponsor_identified",
                 "funding_line_identified", "teaming", "dual_use"):
        if getattr(args, flag, False):
            setattr(prof, flag, True)
    prof.__post_init__()  # re-normalize
    return prof


def _emit(obj: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj, indent=2, default=str))
    else:
        _pretty(obj)


def _pretty(obj: Any, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                print(f"{pad}{k}:")
                _pretty(v, indent + 1)
            else:
                print(f"{pad}{k}: {v}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                _pretty(item, indent)
                print()
            else:
                print(f"{pad}- {item}")
    else:
        print(f"{pad}{obj}")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------
def cmd_assess(args: argparse.Namespace) -> int:
    prof = _profile_from_args(args)
    assessment = report.Assessment(prof)
    print(report.render(assessment, args.format))
    return 0


def cmd_pathways(args: argparse.Namespace) -> int:
    prof = _profile_from_args(args)
    ranked = pathways.recommend(prof, include_nonviable=args.all)
    out = [s.to_dict() for s in ranked]
    if args.json:
        _emit(out, True)
    else:
        for s in ranked:
            tag = "" if s.viable else "  [NOT VIABLE]"
            print(f"[{s.score:5.1f}] {s.pathway.name}{tag}")
            for r in s.rationale:
                print(f"         + {r}")
            for d in s.disqualifiers:
                print(f"         x {d}")
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    prof = _profile_from_args(args)
    ts = transition.score(prof)
    if args.json:
        _emit(ts.to_dict(), True)
    else:
        print(ts.explain())
    return 0


def cmd_requirements(args: argparse.Namespace) -> int:
    if args.narrative:
        feats = [
            requirements.Feature(
                name=f, capability_need="(define capability need)",
                measurable_effect="(define measurable effect)")
            for f in (args.feature or [])
        ]
        text = requirements.value_narrative(
            args.name or "Program", args.context or "", feats, doc_type=args.doc)
        print(text)
        return 0
    if args.gap:
        _emit(requirements.classify_gap(args.gap), args.json)
        return 0
    res = requirements.align_to_document(args.doc)
    _emit(res.to_dict(), args.json)
    return 0


def cmd_funding(args: argparse.Namespace) -> int:
    if args.list:
        _emit([a.to_dict() for a in funding.all_appropriations()], args.json)
        return 0
    g = funding.guidance_for(args.intent, proposed_color=args.proposed)
    _emit(g.to_dict(), args.json)
    return 0


def cmd_gates(args: argparse.Namespace) -> int:
    if args.list:
        _emit([g.to_dict() for g in gates.all_gates()], args.json)
        return 0
    completed: dict[str, list[str]] = {}
    if args.completed:
        with open(args.completed, "r", encoding="utf-8") as fh:
            completed = json.load(fh)
    roll = gates.rollup(completed)
    _emit(roll.to_dict(), args.json)
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    prof = _profile_from_args(args)
    plan = pilot_to_program.generate_plan(prof)
    if args.json:
        _emit(plan.to_dict(), True)
    else:
        print(f"Transition plan — {plan.program_name} "
              f"({plan.pct_complete}% steps satisfied, "
              f"score {plan.transition_score:.1f}/100)")
        for s in plan.steps:
            box = "[x]" if s.done else "[ ]"
            print(f"  {box} {s.order}. {s.title}")
            print(f"        {s.detail}")
            print(f"        owner: {s.owner_hint}")
        if plan.applicable_valleys:
            print("\n  Valleys of death to watch:")
            for v in plan.applicable_valleys:
                print(f"    - {v['name']}: {v['symptom']}")
    return 0


def cmd_readiness(args: argparse.Namespace) -> int:
    if args.gap is not None:
        gap = (readiness.trl_gap(args.current, args.gap) if args.dimension == "TRL"
               else readiness.mrl_gap(args.current, args.gap))
        _emit(gap.to_dict(), args.json)
        return 0
    answers: dict[str, bool] = {}
    if args.answers:
        with open(args.answers, "r", encoding="utf-8") as fh:
            answers = json.load(fh)
    res = (readiness.assess_trl(answers) if args.dimension == "TRL"
           else readiness.assess_mrl(answers))
    _emit(res.to_dict(), args.json)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    prof = _profile_from_args(args)
    assessment = report.Assessment(prof)
    text = report.render(assessment, args.format)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote {args.format} report to {args.out}")
    else:
        print(text)
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------
def _add_profile_flags(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--profile", help="Path to a profile JSON file")
    sp.add_argument("--name")
    sp.add_argument("--trl", type=int)
    sp.add_argument("--mrl", type=int)
    sp.add_argument("--dollars", type=float)
    sp.add_argument("--prior-transitions", dest="prior_transitions", type=int)
    sp.add_argument("--requirement-doc", dest="requirement_doc",
                    choices=["ICD", "CDD", "CPD", "gap"])
    sp.add_argument("--contract-type", dest="contract_type",
                    choices=[c.value for c in ContractType])
    sp.add_argument("--urgency", choices=[u.value for u in Urgency])
    sp.add_argument("--maturity", choices=[m.value for m in Maturity])
    sp.add_argument("--small-business", dest="small_business", action="store_true")
    sp.add_argument("--has-sbir-history", dest="has_sbir_history", action="store_true")
    sp.add_argument("--sponsor-identified", dest="sponsor_identified", action="store_true")
    sp.add_argument("--funding-line-identified", dest="funding_line_identified", action="store_true")
    sp.add_argument("--teaming", action="store_true")
    sp.add_argument("--dual-use", dest="dual_use", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acqnav",
        description="Defense Acquisition Navigator — open, self-hostable "
                    "acquisition & program-management navigation. "
                    "Scope: acquisition/program management only.",
    )
    parser.add_argument("--version", action="version", version=f"acqnav {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_assess = sub.add_parser("assess", help="Full navigator assessment")
    _add_profile_flags(p_assess)
    p_assess.add_argument("--format", default="md", choices=["json", "md", "markdown", "html"])
    p_assess.set_defaults(func=cmd_assess)

    p_path = sub.add_parser("pathways", help="Rank acquisition pathways")
    _add_profile_flags(p_path)
    p_path.add_argument("--all", action="store_true", help="Include non-viable pathways")
    p_path.add_argument("--json", action="store_true")
    p_path.set_defaults(func=cmd_pathways)

    p_tr = sub.add_parser("transition", help="Explainable transition-probability score")
    _add_profile_flags(p_tr)
    p_tr.add_argument("--json", action="store_true")
    p_tr.set_defaults(func=cmd_transition)

    p_req = sub.add_parser("requirements", help="JCIDS alignment / value narrative")
    p_req.add_argument("--doc", default="ICD", help="JCIDS doc type (ICD/CDD/CPD)")
    p_req.add_argument("--gap", help="Describe a capability gap to classify")
    p_req.add_argument("--narrative", action="store_true", help="Generate a value narrative")
    p_req.add_argument("--name", help="Program name (narrative)")
    p_req.add_argument("--context", help="Mission context (narrative)")
    p_req.add_argument("--feature", action="append", help="Feature name (narrative; repeatable)")
    p_req.add_argument("--json", action="store_true")
    p_req.set_defaults(func=cmd_requirements)

    p_fund = sub.add_parser("funding", help="Color-of-money guidance")
    p_fund.add_argument("--intent", default="development",
                        help="Intent (development/production/sustainment/software/...)")
    p_fund.add_argument("--proposed", help="Proposed appropriation code to check")
    p_fund.add_argument("--list", action="store_true", help="List all appropriations")
    p_fund.add_argument("--json", action="store_true")
    p_fund.set_defaults(func=cmd_funding)

    p_gate = sub.add_parser("gates", help="Milestone / gate rollup")
    p_gate.add_argument("--list", action="store_true", help="List all gates")
    p_gate.add_argument("--completed", help="JSON file: {gate_key: [artifacts]}")
    p_gate.add_argument("--json", action="store_true")
    p_gate.set_defaults(func=cmd_gates)

    p_plan = sub.add_parser("plan", help="Pilot-to-program transition plan")
    _add_profile_flags(p_plan)
    p_plan.add_argument("--json", action="store_true")
    p_plan.set_defaults(func=cmd_plan)

    p_rl = sub.add_parser("readiness", help="TRL/MRL assessment or gap")
    p_rl.add_argument("--dimension", default="TRL", choices=["TRL", "MRL"])
    p_rl.add_argument("--answers", help="JSON file of questionnaire answers")
    p_rl.add_argument("--current", type=int, default=1, help="Current level (for --gap)")
    p_rl.add_argument("--gap", type=int, help="Target level for a gap analysis")
    p_rl.add_argument("--json", action="store_true")
    p_rl.set_defaults(func=cmd_readiness)

    p_rep = sub.add_parser("report", help="Export a full report to a file")
    _add_profile_flags(p_rep)
    p_rep.add_argument("--format", default="html", choices=["json", "md", "markdown", "html"])
    p_rep.add_argument("--out", help="Output file path")
    p_rep.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
