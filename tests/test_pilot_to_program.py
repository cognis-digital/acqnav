from acqnav import pilot_to_program as p2p
from acqnav.profile import TechProfile


def test_valleys_defined():
    assert len(p2p.VALLEYS_OF_DEATH) == 5
    for v in p2p.VALLEYS_OF_DEATH:
        assert v["name"] and v["symptom"] and v["mitigation"]


def test_identify_valleys_weak_profile():
    prof = TechProfile(trl=6, sponsor_identified=False,
                       funding_line_identified=False, requirement_doc="")
    valleys = p2p.identify_valleys(prof)
    names = [v["name"] for v in valleys]
    assert any("transition valley" in n for n in names)
    assert any("Funding" in n for n in names)


def test_identify_valleys_strong_profile():
    prof = TechProfile(trl=9, mrl=9, sponsor_identified=True,
                       funding_line_identified=True, requirement_doc="CPD")
    valleys = p2p.identify_valleys(prof)
    assert valleys == []


def test_valleys_deduplicated():
    prof = TechProfile(trl=8, mrl=3, sponsor_identified=False,
                       funding_line_identified=False, requirement_doc="ICD")
    valleys = p2p.identify_valleys(prof)
    names = [v["name"] for v in valleys]
    assert len(names) == len(set(names))


def test_generate_plan_step_count():
    prof = TechProfile(name="Widget", trl=5)
    plan = p2p.generate_plan(prof)
    assert len(plan.steps) == 8
    assert plan.program_name == "Widget"


def test_plan_steps_ordered():
    plan = p2p.generate_plan(TechProfile(trl=5))
    orders = [s.order for s in plan.steps]
    assert orders == list(range(1, len(orders) + 1))


def test_plan_pct_complete_weak():
    prof = TechProfile(trl=2)
    plan = p2p.generate_plan(prof)
    assert plan.pct_complete < 50


def test_plan_pct_complete_strong():
    prof = TechProfile(trl=8, mrl=9, sponsor_identified=True,
                       funding_line_identified=True, requirement_doc="CPD",
                       has_sbir_history=True, teaming=True)
    plan = p2p.generate_plan(prof)
    assert plan.pct_complete >= 75


def test_plan_includes_transition_score():
    plan = p2p.generate_plan(TechProfile(trl=6, sponsor_identified=True))
    assert 0 <= plan.transition_score <= 100


def test_plan_notes():
    plan = p2p.generate_plan(TechProfile(trl=5))
    assert plan.notes
    assert any("transition-probability" in n for n in plan.notes)


def test_plan_to_dict():
    d = p2p.generate_plan(TechProfile(trl=5)).to_dict()
    assert set(d) >= {"program_name", "transition_score", "pct_complete",
                      "steps", "applicable_valleys", "notes"}


def test_bridge_step_to_dict():
    plan = p2p.generate_plan(TechProfile(trl=6, sponsor_identified=True))
    d = plan.steps[0].to_dict()
    assert set(d) >= {"order", "title", "detail", "owner_hint", "done"}


def test_sponsor_step_done_when_identified():
    plan = p2p.generate_plan(TechProfile(trl=6, sponsor_identified=True))
    sponsor_step = next(s for s in plan.steps if "sponsor" in s.title.lower())
    assert sponsor_step.done


def test_funding_step_done_when_identified():
    plan = p2p.generate_plan(TechProfile(trl=6, funding_line_identified=True))
    step = next(s for s in plan.steps if "funding line" in s.title.lower())
    assert step.done
