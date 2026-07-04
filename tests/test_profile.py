from acqnav.profile import ContractType, Maturity, TechProfile, Urgency


def test_defaults():
    p = TechProfile()
    assert p.trl == 1
    assert p.mrl == 0
    assert p.contract_type == ContractType.UNKNOWN
    assert p.urgency == Urgency.ROUTINE
    assert p.maturity == Maturity.DEVELOPMENTAL


def test_trl_clamped_high():
    assert TechProfile(trl=42).trl == 9


def test_trl_clamped_low():
    assert TechProfile(trl=-5).trl == 1


def test_mrl_clamped():
    assert TechProfile(mrl=99).mrl == 10
    assert TechProfile(mrl=-1).mrl == 0


def test_dollars_non_negative():
    assert TechProfile(dollars=-100).dollars == 0.0


def test_prior_transitions_non_negative():
    assert TechProfile(prior_transitions=-3).prior_transitions == 0


def test_enum_from_string():
    p = TechProfile(contract_type="other_transaction", urgency="urgent",
                    maturity="commercial")
    assert p.contract_type == ContractType.OTHER_TRANSACTION
    assert p.urgency == Urgency.URGENT
    assert p.maturity == Maturity.COMMERCIAL


def test_requirement_doc_normalized():
    assert TechProfile(requirement_doc="cdd").requirement_doc == "CDD"
    assert TechProfile(requirement_doc="gap").requirement_doc == "gap"


def test_requirement_doc_invalid():
    import pytest
    with pytest.raises(ValueError):
        TechProfile(requirement_doc="XYZ")


def test_roundtrip_dict():
    p = TechProfile(name="X", trl=5, contract_type=ContractType.OTA if hasattr(ContractType, "OTA") else ContractType.OTHER_TRANSACTION)
    d = p.to_dict()
    p2 = TechProfile.from_dict(d)
    assert p2.name == "X"
    assert p2.trl == 5


def test_from_dict_ignores_unknown_keys():
    p = TechProfile.from_dict({"name": "Y", "trl": 3, "bogus": 123})
    assert p.name == "Y"
    assert p.trl == 3


def test_to_dict_serializes_enums_to_strings():
    d = TechProfile(urgency=Urgency.URGENT).to_dict()
    assert d["urgency"] == "urgent"
    assert isinstance(d["contract_type"], str)
