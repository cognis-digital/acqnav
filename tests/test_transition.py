from acqnav import transition
from acqnav.profile import TechProfile


def test_score_range():
    prof = TechProfile(trl=5)
    ts = transition.score(prof)
    assert 0.0 <= ts.score <= 100.0


def test_low_profile_low_band():
    prof = TechProfile(trl=1)
    ts = transition.score(prof)
    assert ts.band in {"Very Low", "Low"}


def test_strong_profile_high_band():
    prof = TechProfile(trl=9, mrl=9, prior_transitions=3,
                       sponsor_identified=True, funding_line_identified=True,
                       requirement_doc="CPD", teaming=True)
    ts = transition.score(prof)
    assert ts.band == "High"
    assert ts.score >= 90


def test_factor_count():
    ts = transition.score(TechProfile(trl=5))
    assert len(ts.factors) == 7


def test_factors_sum_matches_score():
    prof = TechProfile(trl=6, mrl=5, sponsor_identified=True,
                       funding_line_identified=True, requirement_doc="CDD")
    ts = transition.score(prof)
    total_w = sum(f.weight for f in ts.factors)
    total_p = sum(f.points for f in ts.factors)
    expected = 100.0 * total_p / total_w
    assert abs(ts.score - round(expected, 1)) < 0.2


def test_transparency_each_factor_has_rationale():
    ts = transition.score(TechProfile(trl=5))
    for f in ts.factors:
        assert f.rationale
        assert 0.0 <= f.raw <= 1.0
        assert f.points <= f.weight + 0.001


def test_funding_line_contributes():
    base = transition.score(TechProfile(trl=5, funding_line_identified=False))
    better = transition.score(TechProfile(trl=5, funding_line_identified=True))
    assert better.score > base.score


def test_sponsor_contributes():
    base = transition.score(TechProfile(trl=5, sponsor_identified=False))
    better = transition.score(TechProfile(trl=5, sponsor_identified=True))
    assert better.score > base.score


def test_requirement_doc_ordering():
    scores = {}
    for doc in ("", "gap", "ICD", "CDD", "CPD"):
        scores[doc] = transition.score(TechProfile(trl=5, requirement_doc=doc)).score
    assert scores[""] <= scores["gap"] <= scores["ICD"] <= scores["CDD"] <= scores["CPD"]


def test_prior_transitions_saturate():
    s3 = transition.score(TechProfile(trl=5, prior_transitions=3)).score
    s10 = transition.score(TechProfile(trl=5, prior_transitions=10)).score
    assert abs(s3 - s10) < 0.01


def test_recommendations_present_for_weak():
    ts = transition.score(TechProfile(trl=2))
    assert ts.recommendations
    assert len(ts.recommendations) <= 3


def test_recommendations_include_points_available():
    ts = transition.score(TechProfile(trl=2))
    assert any("pts available" in r for r in ts.recommendations)


def test_custom_weights():
    prof = TechProfile(trl=5, teaming=True)
    ts = transition.score(prof, weights={"teaming": 40.0})
    teaming = next(f for f in ts.factors if f.key == "teaming")
    assert teaming.weight == 40.0


def test_explain_string():
    ts = transition.score(TechProfile(trl=5))
    text = ts.explain()
    assert "Transition probability" in text
    assert "Technical readiness" in text


def test_to_dict_shape():
    d = transition.score(TechProfile(trl=5)).to_dict()
    assert set(d) == {"score", "band", "factors", "recommendations"}
    assert isinstance(d["factors"], list)


def test_mrl_not_assessed_low_credit():
    no_mrl = transition.score(TechProfile(trl=5, mrl=0))
    with_mrl = transition.score(TechProfile(trl=5, mrl=8))
    assert with_mrl.score > no_mrl.score


def test_band_thresholds():
    assert transition._band(80) == "High"
    assert transition._band(60) == "Moderate"
    assert transition._band(30) == "Low"
    assert transition._band(10) == "Very Low"
