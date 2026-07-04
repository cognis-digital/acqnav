from acqnav import funding


def test_appropriations_defined():
    codes = {a.code for a in funding.all_appropriations()}
    assert {"3600", "3010", "3020", "3400", "3080"} <= codes


def test_get_appropriation():
    a = funding.get_appropriation("3600")
    assert "RDT&E" in a.name
    assert a.availability_years == 2


def test_om_is_one_year():
    assert funding.get_appropriation("3400").availability_years == 1


def test_procurement_is_three_year():
    assert funding.get_appropriation("3010").availability_years == 3


def test_guidance_development_is_rdte():
    g = funding.guidance_for("development")
    codes = [a.code for a in g.recommended]
    assert "3600" in codes


def test_guidance_production_is_procurement():
    g = funding.guidance_for("production")
    codes = [a.code for a in g.recommended]
    assert "3010" in codes or "3020" in codes


def test_guidance_sustainment_is_om():
    g = funding.guidance_for("sustainment")
    codes = [a.code for a in g.recommended]
    assert "3400" in codes


def test_mistake_rdte_for_production():
    g = funding.guidance_for("production", proposed_color="3600")
    assert any("MISTAKE" in w for w in g.warnings)


def test_mistake_om_for_development():
    g = funding.guidance_for("development", proposed_color="3400")
    assert any("MISTAKE" in w for w in g.warnings)


def test_sustainment_note_about_expiring():
    g = funding.guidance_for("sustainment")
    assert any("bona fide" in w.lower() or "1-year" in w.lower() for w in g.warnings)


def test_unknown_intent_warns():
    g = funding.guidance_for("teleportation")
    assert g.recommended == []
    assert any("Unknown intent" in w for w in g.warnings)


def test_proposed_color_mismatch_warns():
    g = funding.guidance_for("development", proposed_color="3010")
    assert any("not the typical fit" in w for w in g.warnings)


def test_software_intent():
    g = funding.guidance_for("software")
    codes = [a.code for a in g.recommended]
    assert "3080" in codes


def test_phasing_plan():
    plan = funding.phasing_plan({2026: "development", 2028: "production", 2030: "sustainment"})
    assert len(plan) == 3
    assert plan[0]["fy"] == 2026
    assert "3600" in plan[0]["colors"]
    assert "3400" in plan[2]["colors"]


def test_phasing_plan_sorted():
    plan = funding.phasing_plan({2030: "sustainment", 2026: "development"})
    fys = [row["fy"] for row in plan]
    assert fys == sorted(fys)


def test_appropriation_to_dict():
    d = funding.get_appropriation("3600").to_dict()
    assert set(d) >= {"code", "name", "availability_years", "can_buy", "cannot_buy"}


def test_guidance_to_dict():
    d = funding.guidance_for("development").to_dict()
    assert "recommended" in d and "warnings" in d
