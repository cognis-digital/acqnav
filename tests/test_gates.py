import pytest

from acqnav import gates


def test_all_gates():
    keys = [g.key for g in gates.all_gates()]
    assert keys == ["mdd", "ms_a", "dev_rfp", "ms_b", "ms_c", "frp"]


def test_get_gate():
    g = gates.get_gate("ms_b")
    assert "Milestone B" in g.name
    assert g.artifacts


def test_get_gate_unknown():
    with pytest.raises(KeyError):
        gates.get_gate("ms_z")


def test_gate_status_empty():
    st = gates.gate_status("ms_a", [])
    assert st.pct_complete == 0.0
    assert not st.ready
    assert st.missing == list(gates.get_gate("ms_a").artifacts)


def test_gate_status_full():
    g = gates.get_gate("mdd")
    st = gates.gate_status("mdd", list(g.artifacts))
    assert st.pct_complete == 100.0
    assert st.ready
    assert st.missing == []


def test_gate_status_partial():
    g = gates.get_gate("ms_b")
    half = list(g.artifacts)[: len(g.artifacts) // 2]
    st = gates.gate_status("ms_b", half)
    assert 0 < st.pct_complete < 100


def test_gate_status_ignores_invalid_artifacts():
    st = gates.gate_status("mdd", ["Not a real artifact"])
    assert st.pct_complete == 0.0


def test_rollup_empty():
    roll = gates.rollup({})
    assert roll.overall_pct == 0.0
    assert roll.next_gate.gate.key == "mdd"


def test_rollup_first_gate_done():
    g = gates.get_gate("mdd")
    roll = gates.rollup({"mdd": list(g.artifacts)})
    assert roll.next_gate.gate.key == "ms_a"
    assert roll.overall_pct > 0


def test_rollup_all_done():
    completed = {g.key: list(g.artifacts) for g in gates.all_gates()}
    roll = gates.rollup(completed)
    assert roll.overall_pct == 100.0
    assert roll.next_gate is None


def test_rollup_to_dict():
    d = gates.rollup({}).to_dict()
    assert set(d) >= {"overall_pct", "next_gate", "gates"}
    assert len(d["gates"]) == 6


def test_gate_to_dict():
    d = gates.get_gate("ms_c").to_dict()
    assert d["key"] == "ms_c"
    assert "Capability Production Document (CPD)" in d["artifacts"]


def test_status_to_dict():
    d = gates.gate_status("ms_a", []).to_dict()
    assert set(d) >= {"gate", "name", "pct_complete", "ready", "missing"}


def test_each_gate_has_artifacts():
    for g in gates.all_gates():
        assert len(g.artifacts) >= 1
        assert g.phase_entered
        assert g.description
