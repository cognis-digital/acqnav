import pytest

from acqnav import requirements


def test_jcids_documents():
    assert set(requirements.JCIDS_DOCUMENTS) == {"ICD", "CDD", "CPD"}


def test_align_icd():
    res = requirements.align_to_document("ICD")
    assert res.doc_type == "ICD"
    assert "Milestone A" in res.doc_info["supports"]
    assert res.readiness_notes


def test_align_lowercase():
    res = requirements.align_to_document("cdd")
    assert res.doc_type == "CDD"


def test_align_unknown():
    with pytest.raises(ValueError):
        requirements.align_to_document("XYZ")


def test_classify_gap_materiel():
    res = requirements.classify_gap("Need a system to fuse multi-source sensor data")
    assert res["materiel_signal"] is True
    assert "Materiel" in res["candidate_domains"]


def test_classify_gap_nonmateriel():
    res = requirements.classify_gap("Gap is in operator training and doctrine")
    assert res["nonmateriel_signal"] is True
    assert "non-materiel" in res["recommendation"].lower()


def test_classify_gap_mixed():
    res = requirements.classify_gap("Need a software tool plus new training doctrine")
    assert res["materiel_signal"] and res["nonmateriel_signal"]
    assert "gap analysis" in res["recommendation"].lower()


def test_classify_gap_domains_detected():
    res = requirements.classify_gap("Organization and Personnel shortfalls in the unit")
    assert "Organization" in res["candidate_domains"]
    assert "Personnel" in res["candidate_domains"]


def test_value_narrative_contains_features():
    feats = [
        requirements.Feature("Sensor fusion", "Common operating picture",
                             "Reduce time-to-insight by 50%", "KPP"),
        requirements.Feature("Offline mode", "Air-gap operation",
                             "100% functionality disconnected", "KSA"),
    ]
    text = requirements.value_narrative("FusionKit", "Situational awareness", feats)
    assert "Sensor fusion" in text
    assert "Offline mode" in text
    assert "Warfighter Value Narrative" in text
    assert "KPP" in text


def test_value_narrative_default_doc():
    text = requirements.value_narrative("X", "context", [])
    assert "Initial Capabilities Document" in text


def test_value_narrative_cpd():
    text = requirements.value_narrative("X", "context", [], doc_type="CPD")
    assert "Capability Production Document" in text


def test_feature_to_dict():
    f = requirements.Feature("A", "need", "effect", "KSA")
    d = f.to_dict()
    assert d["attribute_type"] == "KSA"
    assert d["attribute_desc"]


def test_attribute_types_defined():
    assert set(requirements.ATTRIBUTE_TYPES) == {"KPP", "KSA", "APA"}


def test_dotmlpf_p_has_eight_domains():
    assert len(requirements.DOTMLPF_P) == 8


def test_alignment_to_dict():
    d = requirements.align_to_document("CPD").to_dict()
    assert d["doc_type"] == "CPD"
    assert "doc_info" in d
