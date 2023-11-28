import math

import numpy as np

import ccm.config as config
from ccm.contexts import using_parameters
from ccm.interventions.xrisk.impact.expected_years_saved import ExpectedYearsSaved
from ccm.parameters import Parameters
from ccm.world.longterm_params import (
    LongTermParams,
)
from ccm.world.risk_types import RiskTypeAI

SIMULATIONS = config.get_simulations()


def test_thousand_years_delivers_plausible_values() -> None:
    half_off = np.ones(SIMULATIONS) * 0.5

    with using_parameters(Parameters(longterm_params=LongTermParams())):
        impact = ExpectedYearsSaved().calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            half_off,
            np.array(SIMULATIONS * [10]),
        )
    assert np.median(impact) == 0
    assert np.mean(impact) > 0
    assert np.mean(impact) > 0


def test_thousand_years_delivers_changes_based_on_intervention_length():
    half_off = np.ones(SIMULATIONS) * 0.5
    model = ExpectedYearsSaved()

    with using_parameters(Parameters(longterm_params=LongTermParams())):
        impact_short = model.calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            half_off,
            np.array(SIMULATIONS * [10]),
        )
        impact_long = model.calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            half_off,
            np.array(SIMULATIONS * [100]),
        )

    median_impact_short = np.median(impact_short)
    median_impact_long = np.median(impact_long)

    assert median_impact_short == 0 or median_impact_short < median_impact_long
    assert math.isclose(median_impact_short * 10, median_impact_long, rel_tol=median_impact_short)


def test_thousand_years_delivers_changes_based_on_risk_amount() -> None:
    half_off = np.ones(SIMULATIONS) * 0.5
    fraction_off = np.ones(SIMULATIONS) * 0.025

    with using_parameters(Parameters(longterm_params=LongTermParams())):
        impact_small = ExpectedYearsSaved().calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            fraction_off,
            half_off,
            np.array(SIMULATIONS * [10]),
        )
        impact_big = ExpectedYearsSaved().calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            half_off,
            np.array(SIMULATIONS * [100]),
        )
    assert np.median(impact_small) == 0 or np.median(impact_small) < np.median(impact_big)
