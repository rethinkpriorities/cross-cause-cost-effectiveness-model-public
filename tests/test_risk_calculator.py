import math

import numpy as np
import pytest

import ccm.config as config
import ccm.utility.risk_calculator as risk_calculator
import ccm.utility.squigglepy_wrapper as sqw
from ccm.contexts import using_parameters
from ccm.parameters import Parameters
from ccm.world.eras import Era
from ccm.world.longterm_params import (
    DEFAULT_CATASTROPHE_EXTINCTION_RISK_RATIOS,
    DEFAULT_ERAS,
    DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
    LongTermParams,
)
from ccm.world.risk_types import RiskTypeAI, RiskTypeGLT


SIMULATIONS = config.get_simulations()
CURR_YEAR = config.get_current_year()


def test_get_distribution_of_years_to_extinction_includes_relevant_values() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(
                        length=5,
                        annual_extinction_risk=1 / 5,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                )
            )
        )
    ):
        dist = risk_calculator.get_distribution_of_years_to_extinction()
    samples = sqw.sample(dist, n=1000)
    assert len(np.unique(samples)) == 5


def test_get_distribution_of_years_to_extinction_samples_different_eras() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(
                        length=5,
                        annual_extinction_risk=1 / 5,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                    Era(
                        length=10,
                        annual_extinction_risk=1 / 10,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                )
            )
        )
    ):
        dist = risk_calculator.get_distribution_of_years_to_extinction()
    samples = sqw.sample(dist, n=1000)
    assert len(np.unique(samples)) == 15
    assert np.any(samples > 5)
    assert not np.any(samples > 15)


def test_get_distribution_of_years_to_extinction_samples_bases_era_probabilities_on_yearly_probabilities() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(
                        length=5,
                        annual_extinction_risk=1 / 5,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                    Era(
                        length=10,
                        annual_extinction_risk=1 / 10,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                    Era(
                        length=100,
                        annual_extinction_risk=1 / 10,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                )
            )
        )
    ):
        dist = risk_calculator.get_distribution_of_years_to_extinction()
    samples = sqw.sample(dist, n=1000)
    # 4/5^5 == 32, so samples less than 5 should be about x2 as likely as samples greater
    assert np.sum(samples <= 5) > np.sum(samples > 5)
    assert np.sum(samples <= 5) > np.sum(samples > 5) * 1.5
    assert np.sum(samples <= 5) < np.sum(samples > 5) * 3


@pytest.mark.parametrize("risk_multiplier", [10, 1 / 10])
def test_get_distribution_of_years_to_extinction_is_sensitive_to_risk(risk_multiplier):
    with using_parameters(Parameters(longterm_params=LongTermParams(risk_eras=DEFAULT_ERAS))):
        dist_default_risk = risk_calculator.get_distribution_of_years_to_extinction()
        years_to_extinction_under_default_risk = sqw.sample(dist_default_risk, n=10000)

    modified_risk_eras = []
    for era in DEFAULT_ERAS:
        modified_era = Era(
            length=era.length,
            annual_extinction_risk=era.annual_extinction_risk * risk_multiplier,
            proportional_risks_by_type=era.proportional_risks_by_type,
        )
        modified_risk_eras.append(modified_era)
    modified_risk_eras = tuple(modified_risk_eras)

    with using_parameters(Parameters(longterm_params=LongTermParams(risk_eras=modified_risk_eras))):
        dist_modified_risk = risk_calculator.get_distribution_of_years_to_extinction()
        years_to_extinction_under_modified_risk = sqw.sample(dist_modified_risk, n=1000)

    if risk_multiplier > 1:
        assert np.mean(years_to_extinction_under_modified_risk) < np.mean(
            years_to_extinction_under_default_risk
        ), "Under increased risks, it should take less years until extinction, not more!"
    if risk_multiplier < 1:
        assert np.mean(years_to_extinction_under_modified_risk) > np.mean(
            years_to_extinction_under_default_risk
        ), "Under reduced risks, it should take more years until extinction, not less!"


test_proportions = {
    RiskTypeAI.MISALIGNMENT: 0.5,
    RiskTypeGLT.BIO: 0.1,
    RiskTypeGLT.NANO: 0.1,
    RiskTypeGLT.NATURAL: 0.1,
    RiskTypeGLT.NUKES: 0.08,
    RiskTypeGLT.UNKNOWN: 0.12,
}


def test_get_cumulative_catastrophe_risk():
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(Era(length=5, annual_extinction_risk=0.2, proportional_risks_by_type=test_proportions),)
            )
        )
    ):
        cum_risk = risk_calculator.get_cumulative_catastrophe_risk(
            risk_type=RiskTypeAI.MISALIGNMENT,
            num_years=np.array(SIMULATIONS * [2]),
        )
    assert math.isclose(
        # Not exact because probabilities aren't direcly added
        np.mean(cum_risk),
        0.2
        * 2
        * test_proportions[RiskTypeAI.MISALIGNMENT]
        * DEFAULT_CATASTROPHE_EXTINCTION_RISK_RATIOS[RiskTypeAI.MISALIGNMENT],
        rel_tol=0.2,
    )


def test_approximate_geometric():
    pass


def test_gets_average_total_risk_over_eras() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(
                        length=5,
                        annual_extinction_risk=0.2,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                )
            )
        )
    ):
        average_total_risk = risk_calculator.get_average_total_risk_over_years(np.array(SIMULATIONS * [3]))
    assert math.isclose(np.mean(average_total_risk), 0.2)


def test_gets_average_total_risk_over_two_eras() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(
                        length=5,
                        annual_extinction_risk=0.2,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                    Era(
                        length=12,
                        annual_extinction_risk=0.001,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                )
            )
        )
    ):
        average_total_risk = risk_calculator.get_average_total_risk_over_years(np.array(SIMULATIONS * [7]))
    assert math.isclose(np.mean(average_total_risk), 0.2 * 5 / 7 + 0.001 * 2 / 7)


def test_gets_average_total_risk_over_three_eras() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(
                        length=5,
                        annual_extinction_risk=0.2,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                    Era(
                        length=12,
                        annual_extinction_risk=0,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                    Era(
                        length=4,
                        annual_extinction_risk=0.1,
                        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
                    ),
                )
            )
        )
    ):
        average_total_risk = risk_calculator.get_average_total_risk_over_years(np.array(SIMULATIONS * [20]))
    assert math.isclose(np.mean(average_total_risk), sum([0.2] * 5 + [0] * 12 + [0.1] * 3) / 20)


test_proportions = {
    RiskTypeAI.MISALIGNMENT: 0.5,
    RiskTypeGLT.BIO: 0.1,
    RiskTypeGLT.NANO: 0.1,
    RiskTypeGLT.NATURAL: 0.1,
    RiskTypeGLT.NUKES: 0.08,
    RiskTypeGLT.UNKNOWN: 0.12,
}


def test_gets_average_risk_over_eras_by_type() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(Era(length=5, annual_extinction_risk=0.2, proportional_risks_by_type=test_proportions),)
            )
        )
    ):
        average_risk = risk_calculator.get_average_risk_over_years_by_type(
            risk_type=RiskTypeAI.MISALIGNMENT,
            num_years=np.array(SIMULATIONS * [3]),
        )
    assert isinstance(average_risk, np.ndarray)
    assert len(average_risk) == SIMULATIONS
    np.testing.assert_allclose(average_risk, [0.1] * SIMULATIONS)


def test_gets_average_risk_over_two_eras_by_type() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(length=5, annual_extinction_risk=0.2, proportional_risks_by_type=test_proportions),
                    Era(length=12, annual_extinction_risk=0.001, proportional_risks_by_type=test_proportions),
                )
            )
        )
    ):
        average_risk = risk_calculator.get_average_risk_over_years_by_type(
            risk_type=RiskTypeAI.MISALIGNMENT,
            num_years=np.array(SIMULATIONS * [7]),
        )
    assert math.isclose(np.mean(average_risk), 0.1 * 5 / 7 + 0.0005 * 2 / 7)


def test_gets_average_risk_over_three_eras_by_type() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(length=5, annual_extinction_risk=0.2, proportional_risks_by_type=test_proportions),
                    Era(length=12, annual_extinction_risk=0.001, proportional_risks_by_type=test_proportions),
                    Era(length=4, annual_extinction_risk=0.1, proportional_risks_by_type=test_proportions),
                )
            )
        )
    ):
        average_risk = risk_calculator.get_average_risk_over_years_by_type(
            risk_type=RiskTypeAI.MISALIGNMENT,
            num_years=np.array(SIMULATIONS * [20]),
        )
    assert math.isclose(np.mean(average_risk), sum([0.1] * 5 + [0.0005] * 12 + [0.05] * 3) / 20)


def test_gets_cumulative_risk_over_years() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(length=5, annual_extinction_risk=0.2, proportional_risks_by_type=test_proportions),
                    Era(length=12, annual_extinction_risk=0.001, proportional_risks_by_type=test_proportions),
                )
            )
        )
    ):
        cum_risk = risk_calculator.get_cumulative_risk_over_years(np.array(SIMULATIONS * [7]))
    assert math.isclose(np.mean(cum_risk), 0.2 * 5 + 0.001 * 2)


def test_gets_cumulative_risk_over_years_by_type() -> None:
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=(
                    Era(length=5, annual_extinction_risk=0.2, proportional_risks_by_type=test_proportions),
                    Era(length=12, annual_extinction_risk=0.001, proportional_risks_by_type=test_proportions),
                )
            )
        )
    ):
        cum_risk = risk_calculator.get_cumulative_risk_over_years_by_type(
            RiskTypeAI.MISALIGNMENT,
            np.array(SIMULATIONS * [7]),
        )
    assert math.isclose(np.mean(cum_risk), 0.1 * 5 + 0.0005 * 2)
