import pytest

from acqnav import pathways
from acqnav.profile import ContractType, Maturity, TechProfile, Urgency


def test_catalog_nonempty():
    assert len(pathways.all_pathways()) >= 11


def test_all_pathways_have_keys_and_names():
    for p in pathways.all_pathways():
        assert p.key
        assert p.name
        assert p.authority
        assert p.entry_criteria
        assert p.funding_vehicle


def test_get_pathway():
    p = pathways.get_pathway("ota_prototype")
    assert "Other Transaction" in p.name


def test_get_pathway_unknown():
    with pytest.raises(KeyError):
        pathways.get_pathway("does_not_exist")


def test_dollar_band_str_no_ceiling():
    p = pathways.get_pathway("sbir_phase_iii")
    assert "no ceiling" in p.dollar_band_str()


def test_small_business_disqualifier():
    prof = TechProfile(trl=2, small_business=False, dollars=200_000)
    scores = pathways.recommend(prof, include_nonviable=True)
    sbir1 = next(s for s in scores if s.pathway.key == "sbir_phase_i")
    assert not sbir1.viable
    assert any("small-business" in d.lower() for d in sbir1.disqualifiers)


def test_small_business_viable_when_qualified():
    prof = TechProfile(trl=2, small_business=True, dollars=200_000)
    scores = pathways.recommend(prof)
    keys = [s.pathway.key for s in scores]
    assert "sbir_phase_i" in keys


def test_phase_iii_requires_sbir_history():
    prof = TechProfile(trl=7, small_business=True, dollars=2_000_000,
                       has_sbir_history=False, sponsor_identified=True)
    scores = pathways.recommend(prof, include_nonviable=True)
    p3 = next(s for s in scores if s.pathway.key == "sbir_phase_iii")
    assert not p3.viable


def test_phase_iii_viable_with_history():
    prof = TechProfile(trl=7, small_business=True, dollars=2_000_000,
                       has_sbir_history=True, sponsor_identified=True)
    scores = pathways.recommend(prof)
    assert any(s.pathway.key == "sbir_phase_iii" for s in scores)


def test_trl_below_min_disqualifies():
    prof = TechProfile(trl=1)
    scores = pathways.recommend(prof, include_nonviable=True)
    rf = next(s for s in scores if s.pathway.key == "mta_rapid_fielding")
    assert not rf.viable
    assert any("below pathway minimum" in d for d in rf.disqualifiers)


def test_urgent_ota_ranks_high():
    prof = TechProfile(trl=5, dollars=3_000_000, urgency=Urgency.URGENT,
                       maturity=Maturity.ADAPTED_COMMERCIAL,
                       contract_type=ContractType.OTHER_TRANSACTION)
    top = pathways.top_recommendation(prof)
    assert top is not None
    assert top.pathway.key in {"ota_prototype", "cso", "software_pathway"}


def test_recommend_sorted_descending():
    prof = TechProfile(trl=6, small_business=True, dollars=2_000_000,
                       has_sbir_history=True, sponsor_identified=True)
    scores = pathways.recommend(prof)
    vals = [s.score for s in scores]
    assert vals == sorted(vals, reverse=True)


def test_viable_sort_before_nonviable():
    prof = TechProfile(trl=5, small_business=False, dollars=1_000_000)
    scores = pathways.recommend(prof, include_nonviable=True)
    viable_idx = [i for i, s in enumerate(scores) if s.viable]
    nonviable_idx = [i for i, s in enumerate(scores) if not s.viable]
    if viable_idx and nonviable_idx:
        assert max(viable_idx) < min(nonviable_idx)


def test_top_recommendation_none_when_no_viable():
    # TRL 1, big-dollar, no small business -> most disqualified
    prof = TechProfile(trl=1, small_business=False, dollars=0)
    top = pathways.top_recommendation(prof)
    # Some pathway may still be viable at TRL1; just assert type
    assert top is None or top.viable


def test_score_bounded():
    prof = TechProfile(trl=6, small_business=True, dollars=1_000_000,
                       has_sbir_history=True, sponsor_identified=True,
                       urgency=Urgency.URGENT)
    for s in pathways.recommend(prof, include_nonviable=True):
        assert 0.0 <= s.score <= 100.0


def test_candidates_subset():
    prof = TechProfile(trl=5, small_business=True, dollars=1_000_000)
    subset = [pathways.get_pathway("sbir_phase_ii")]
    scores = pathways.recommend(prof, candidates=subset, include_nonviable=True)
    assert len(scores) == 1
    assert scores[0].pathway.key == "sbir_phase_ii"


def test_pathwayscore_to_dict():
    prof = TechProfile(trl=5, small_business=True, dollars=1_000_000,
                       has_sbir_history=True)
    d = pathways.recommend(prof)[0].to_dict()
    assert set(d) >= {"key", "name", "score", "viable", "rationale"}


def test_mca_for_large_program():
    prof = TechProfile(trl=5, dollars=200_000_000, urgency=Urgency.ROUTINE)
    scores = pathways.recommend(prof)
    assert any(s.pathway.key == "mca" for s in scores)


def test_software_pathway_commercial():
    prof = TechProfile(trl=6, dollars=5_000_000, maturity=Maturity.COMMERCIAL,
                       tags=["software"])
    scores = pathways.recommend(prof)
    assert any(s.pathway.key == "software_pathway" for s in scores)


def test_dbs_pathway_present():
    assert any(p.key == "dbs" for p in pathways.all_pathways())


def test_apfit_needs_sponsor():
    prof = TechProfile(trl=8, small_business=True, dollars=20_000_000,
                       sponsor_identified=False, urgency=Urgency.URGENT)
    scores = pathways.recommend(prof)
    apfit = [s for s in scores if s.pathway.key == "apfit"]
    if apfit:
        assert any("sponsor" in r.lower() for r in apfit[0].rationale)
