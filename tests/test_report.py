import json

import pytest

from acqnav import report
from acqnav.profile import TechProfile, Urgency, Maturity


def _profile():
    return TechProfile(name="TestProg", trl=6, mrl=5, dollars=2_000_000,
                       urgency=Urgency.ACCELERATED, maturity=Maturity.ADAPTED_COMMERCIAL,
                       small_business=True, has_sbir_history=True,
                       sponsor_identified=True, requirement_doc="CDD", teaming=True)


def test_assessment_build_shape():
    a = report.Assessment(_profile())
    d = a.build()
    assert set(d) >= {"generated", "tool", "profile", "pathways",
                      "transition", "plan", "appropriations_reference"}
    assert d["tool"] == "acqnav"


def test_to_json_valid():
    a = report.Assessment(_profile())
    parsed = json.loads(report.to_json(a))
    assert parsed["profile"]["name"] == "TestProg"


def test_to_markdown_contains_sections():
    md = report.to_markdown(report.Assessment(_profile()))
    assert "# acqnav Assessment" in md
    assert "## Transition Probability" in md
    assert "## Recommended Acquisition Pathways" in md
    assert "## Pilot-to-Program Transition Plan" in md


def test_to_html_self_contained():
    html = report.to_html(report.Assessment(_profile()))
    assert html.startswith("<!doctype html>")
    assert "<style>" in html
    # No JavaScript
    assert "<script" not in html.lower()
    assert "javascript:" not in html.lower()
    # No external asset references
    assert "http://" not in html
    assert "https://" not in html
    assert "src=" not in html


def test_html_escapes_name():
    prof = _profile()
    prof.name = "<script>alert(1)</script>"
    prof.__post_init__()
    html = report.to_html(report.Assessment(prof))
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_render_json():
    out = report.render(report.Assessment(_profile()), "json")
    json.loads(out)


def test_render_md_alias():
    assert report.render(report.Assessment(_profile()), "markdown").startswith("#")


def test_render_html():
    assert report.render(report.Assessment(_profile()), "html").startswith("<!doctype")


def test_render_unknown_format():
    with pytest.raises(ValueError):
        report.render(report.Assessment(_profile()), "pdf")


def test_html_has_transition_meter():
    html = report.to_html(report.Assessment(_profile()))
    assert "meter" in html


def test_generated_timestamp():
    a = report.Assessment(_profile())
    assert "T" in a.generated  # ISO 8601
