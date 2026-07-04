import json

import pytest

from acqnav import cli


def run(args):
    return cli.main(args)


def test_version(capsys):
    with pytest.raises(SystemExit) as ei:
        run(["--version"])
    assert ei.value.code == 0
    assert "acqnav" in capsys.readouterr().out


def test_no_command_errors():
    with pytest.raises(SystemExit):
        run([])


def test_assess_md(capsys):
    rc = run(["assess", "--trl", "6", "--small-business", "--format", "md"])
    assert rc == 0
    assert "# acqnav Assessment" in capsys.readouterr().out


def test_assess_json(capsys):
    rc = run(["assess", "--trl", "6", "--format", "json"])
    assert rc == 0
    json.loads(capsys.readouterr().out)


def test_assess_html(capsys):
    rc = run(["assess", "--trl", "6", "--format", "html"])
    assert rc == 0
    assert "<!doctype html>" in capsys.readouterr().out


def test_pathways(capsys):
    rc = run(["pathways", "--trl", "5", "--small-business", "--has-sbir-history",
              "--dollars", "1000000"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "[" in out


def test_pathways_json(capsys):
    rc = run(["pathways", "--trl", "5", "--small-business", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)


def test_pathways_all(capsys):
    rc = run(["pathways", "--trl", "5", "--all"])
    assert rc == 0


def test_transition(capsys):
    rc = run(["transition", "--trl", "7", "--sponsor-identified",
              "--funding-line-identified"])
    assert rc == 0
    assert "Transition probability" in capsys.readouterr().out


def test_transition_json(capsys):
    rc = run(["transition", "--trl", "5", "--json"])
    assert rc == 0
    d = json.loads(capsys.readouterr().out)
    assert "score" in d


def test_requirements_align(capsys):
    rc = run(["requirements", "--doc", "CDD"])
    assert rc == 0
    assert "CDD" in capsys.readouterr().out


def test_requirements_gap(capsys):
    rc = run(["requirements", "--gap", "Need a sensor fusion system"])
    assert rc == 0
    assert "candidate_domains" in capsys.readouterr().out


def test_requirements_narrative(capsys):
    rc = run(["requirements", "--narrative", "--name", "X",
              "--context", "context", "--feature", "F1", "--feature", "F2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Warfighter Value Narrative" in out
    assert "F1" in out


def test_funding(capsys):
    rc = run(["funding", "--intent", "production", "--proposed", "3600"])
    assert rc == 0
    assert "MISTAKE" in capsys.readouterr().out


def test_funding_list(capsys):
    rc = run(["funding", "--list", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) >= 5


def test_gates_list(capsys):
    rc = run(["gates", "--list", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 6


def test_gates_rollup(capsys):
    rc = run(["gates", "--json"])
    assert rc == 0
    d = json.loads(capsys.readouterr().out)
    assert d["overall_pct"] == 0.0


def test_plan(capsys):
    rc = run(["plan", "--trl", "6", "--sponsor-identified"])
    assert rc == 0
    assert "Transition plan" in capsys.readouterr().out


def test_plan_json(capsys):
    rc = run(["plan", "--trl", "6", "--json"])
    assert rc == 0
    json.loads(capsys.readouterr().out)


def test_readiness_gap(capsys):
    rc = run(["readiness", "--dimension", "TRL", "--current", "4", "--gap", "7", "--json"])
    assert rc == 0
    d = json.loads(capsys.readouterr().out)
    assert d["levels_to_advance"] == 3


def test_report_to_file(tmp_path, capsys):
    out = tmp_path / "r.html"
    rc = run(["report", "--trl", "6", "--format", "html", "--out", str(out)])
    assert rc == 0
    assert out.exists()
    assert "<!doctype html>" in out.read_text(encoding="utf-8")


def test_profile_from_file(tmp_path, capsys):
    pf = tmp_path / "p.json"
    pf.write_text(json.dumps({"name": "FromFile", "trl": 7, "small_business": True}),
                  encoding="utf-8")
    rc = run(["transition", "--profile", str(pf), "--json"])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["score"] > 0


def test_profile_file_with_override(tmp_path, capsys):
    pf = tmp_path / "p.json"
    pf.write_text(json.dumps({"name": "Base", "trl": 3}), encoding="utf-8")
    rc = run(["assess", "--profile", str(pf), "--trl", "8", "--format", "json"])
    assert rc == 0
    d = json.loads(capsys.readouterr().out)
    assert d["profile"]["trl"] == 8
