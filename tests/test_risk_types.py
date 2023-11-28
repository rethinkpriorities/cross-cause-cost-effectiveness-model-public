import ccm.world.risk_types as risk_types


def test_get_risk_types() -> None:
    types = [risk_type.value for risk_type in risk_types.get_risk_types()]
    assert len(types) == 7
    assert all(risk in types for risk in ("ai misalignment", "ai misuse", "nukes", "bio", "natural", "unknown", "nano"))
