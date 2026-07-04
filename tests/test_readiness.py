import pytest

from acqnav import readiness


def test_trl_definitions_complete():
    assert set(readiness.TRL_DEFINITIONS) == set(range(1, 10))


def test_mrl_definitions_complete():
    assert set(readiness.MRL_DEFINITIONS) == set(range(1, 11))


def test_assess_trl_all_yes():
    answers = {f"trl{i}": True for i in range(1, 10)}
    res = readiness.assess_trl(answers)
    assert res.level == 9


def test_assess_trl_partial():
    answers = {f"trl{i}": True for i in range(1, 5)}
    res = readiness.assess_trl(answers)
    assert res.level == 4


def test_assess_trl_gap_stops_progress():
    # yes 1-3, no 4, yes 5 -> should stop at 3
    answers = {"trl1": True, "trl2": True, "trl3": True, "trl4": False, "trl5": True}
    res = readiness.assess_trl(answers)
    assert res.level == 3
    assert res.notes


def test_assess_trl_none():
    res = readiness.assess_trl({})
    assert res.level == 1


def test_assess_mrl():
    answers = {f"mrl{i}": True for i in range(1, 6)}
    res = readiness.assess_mrl(answers)
    assert res.level == 5


def test_trl_gap_steps():
    gap = readiness.trl_gap(4, 7)
    assert gap.levels_to_advance == 3
    assert len(gap.steps) == 3
    assert gap.steps[0]["level"] == 5


def test_trl_gap_has_evidence():
    gap = readiness.trl_gap(5, 6)
    assert gap.steps[0]["evidence_needed"]


def test_trl_gap_clamps():
    gap = readiness.trl_gap(0, 99)
    assert gap.current == 1
    assert gap.target == 9


def test_mrl_gap_steps():
    gap = readiness.mrl_gap(6, 9)
    assert gap.levels_to_advance == 3
    assert len(gap.steps) == 3


def test_no_gap_when_at_target():
    gap = readiness.trl_gap(7, 7)
    assert gap.levels_to_advance == 0
    assert gap.steps == []


def test_evidence_to_advance_trl():
    ev = readiness.evidence_to_advance("TRL", 5)
    assert ev  # evidence for TRL6


def test_evidence_to_advance_mrl():
    ev = readiness.evidence_to_advance("MRL", 4)
    assert ev


def test_evidence_to_advance_at_max():
    assert readiness.evidence_to_advance("TRL", 9) == list(readiness.TRL_EVIDENCE[9])


def test_evidence_unknown_dimension():
    with pytest.raises(ValueError):
        readiness.evidence_to_advance("XRL", 3)


def test_result_to_dict():
    d = readiness.assess_trl({"trl1": True, "trl2": True}).to_dict()
    assert set(d) >= {"dimension", "level", "definition", "max_level"}


def test_gap_to_dict():
    d = readiness.trl_gap(3, 5).to_dict()
    assert d["levels_to_advance"] == 2


def test_questions_defined():
    assert len(readiness.TRL_QUESTIONS) == 9
    assert len(readiness.MRL_QUESTIONS) == 10
