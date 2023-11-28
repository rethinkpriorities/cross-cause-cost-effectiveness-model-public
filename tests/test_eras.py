import math

import pytest

from ccm.base_parameters import FrozenDict
from ccm.world.eras import Era
from ccm.world.longterm_params import DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK
from ccm.world.risk_types import RiskTypeAI, RiskTypeGLT


def test_initialize_with_annual_risk():
    era = Era(length=5, annual_extinction_risk=0, proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK)
    assert era.get_annual_extinction_probability() == 0


def test_initialize_with_absolute_risk():
    absolute_risks = {
        RiskTypeAI.MISALIGNMENT: 0.02,
        RiskTypeGLT.BIO: 0.05,
        RiskTypeGLT.NANO: 0.04,
        RiskTypeGLT.NATURAL: 0.03,
        RiskTypeGLT.NUKES: 0.06,
        RiskTypeGLT.UNKNOWN: 0.01,
    }
    annual_risks = sum(absolute_risks.values())
    era = Era(length=5, absolute_risks_by_type=absolute_risks)
    assert math.isclose(era.get_annual_extinction_probability(), annual_risks)
    assert math.isclose(era.get_proportional_risks()[RiskTypeAI.MISALIGNMENT], 0.1, rel_tol=0.5)
    assert math.isclose(era.get_proportional_risks()[RiskTypeGLT.NANO], 0.2, rel_tol=0.5)

    increased_risks = FrozenDict({k: v * 2 for k, v in absolute_risks.items()})
    era_increased_risks = Era(length=era.length, absolute_risks_by_type=increased_risks)
    assert era_increased_risks.get_annual_extinction_probability() > era.get_annual_extinction_probability()
    assert math.isclose(
        era_increased_risks.get_annual_extinction_probability(),
        2 * era.get_annual_extinction_probability(),
        rel_tol=0.1,
    )
    for risk_type in absolute_risks:
        assert math.isclose(
            era.proportional_risks_by_type[risk_type],  # type: ignore  We know it is not none
            era_increased_risks.proportional_risks_by_type[risk_type],  # type: ignore  We know it is not none
            rel_tol=0.1,
        )


def test_initialize_with_proportional_risk():
    proportional_risks = FrozenDict(
        {  # type: ignore  # type checking doesn't understand frozendicts with enums as keys
            RiskTypeAI.MISALIGNMENT: 0.5,
            RiskTypeGLT.BIO: 0.1,
            RiskTypeGLT.NANO: 0.1,
            RiskTypeGLT.NATURAL: 0.1,
            RiskTypeGLT.NUKES: 0.08,
            RiskTypeGLT.UNKNOWN: 0.12,
        }
    )
    era = Era(
        length=5,
        annual_extinction_risk=0.42,
        proportional_risks_by_type=proportional_risks,
    )
    assert math.isclose(era.get_annual_extinction_probability(), 0.42)
    assert math.isclose(era.get_absolute_risks()[RiskTypeAI.MISALIGNMENT], 0.21)
    assert math.isclose(era.get_absolute_risks()[RiskTypeGLT.BIO], 0.042)

    modified_risks = FrozenDict(
        {  # type: ignore  # type checking doesn't understand frozendicts with enums as keys
            RiskTypeAI.MISALIGNMENT: 0.01,
            RiskTypeGLT.BIO: 0.2,
            RiskTypeGLT.NANO: 0.2,
            RiskTypeGLT.NATURAL: 0.2,
            RiskTypeGLT.NUKES: 0.2,
            RiskTypeGLT.UNKNOWN: 0.19,
        }
    )
    era_modified_risks = Era(
        length=era.length,
        annual_extinction_risk=era.annual_extinction_risk,
        proportional_risks_by_type=modified_risks,
    )
    assert math.isclose(
        era.get_annual_extinction_probability(),
        era_modified_risks.get_annual_extinction_probability(),
        rel_tol=0.1,
    )
    for risk_type in proportional_risks:
        expected_proportion = proportional_risks[risk_type] / modified_risks[risk_type]  # type: ignore  False-positive
        assert math.isclose(
            era.get_absolute_risks()[risk_type],  # type: ignore  False-positive
            expected_proportion * era_modified_risks.get_absolute_risks()[risk_type],  # type: ignore  False-positive
            rel_tol=0.1,
        )


def test_fails_if_no_risk_provided():
    with pytest.raises(AssertionError):
        Era(length=5, annual_extinction_risk=0.01)
