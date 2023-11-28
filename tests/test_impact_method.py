import math

import numpy as np
import pytest
from numpy.typing import NDArray
from squigglepy import B, M

import ccm.config as config
from ccm.base_parameters import FrozenDict
from ccm.contexts import using_parameters
from ccm.interventions.xrisk.impact.impact_method import ImpactMethod
from ccm.parameters import Parameters
from ccm.world.eras import Era
from ccm.world.longterm_params import (
    DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
    LongTermParams,
)
from ccm.world.risk_types import RiskType, RiskTypeAI, RiskTypeGLT

SIMULATIONS = config.get_simulations()

CUR_YEAR = config.get_current_year()


class BasicImpactMethod(ImpactMethod):
    """A simple ImpactMethod for testing purposes where `calc_impact_given_prop_risk_reduction`
    returns an empty array.
    """

    def calc_impact_given_prop_risk_reduction(
        self,
        risk_type: RiskType,
        proportion_extinction_risk_changed: NDArray[np.float64],
        proportion_catastrophe_risk_changed: NDArray[np.float64],
        years_risk_changed: NDArray[np.int64],
    ) -> NDArray[np.float64]:
        return np.array([])


def test_impact_method_calc_base_impact_with_max_creditable_year():
    test_eras = (
        Era(
            length=35,
            annual_extinction_risk=0.01,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=35,
            annual_extinction_risk=0.00001,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=100,
            annual_extinction_risk=0.007,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
    )
    half_off = np.ones(SIMULATIONS) * 0.5
    nothing = np.zeros(SIMULATIONS)
    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=test_eras,
                max_creditable_year=CUR_YEAR + 50,
                catastrophe_extinction_risk_ratios=FrozenDict({RiskTypeAI.MISALIGNMENT: 0}),
            )
        )
    ):
        model_short = BasicImpactMethod("", "")
        impact_short = model_short.calc_base_impact(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            nothing,
            np.array(SIMULATIONS * [30]),
        )

    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=test_eras,
                max_creditable_year=CUR_YEAR + 100,
                catastrophe_extinction_risk_ratios=FrozenDict({RiskTypeAI.MISALIGNMENT: 0}),
            )
        )
    ):
        model_long = BasicImpactMethod("", "")
        impact_long = model_long.calc_base_impact(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            nothing,
            np.array(SIMULATIONS * [30]),
        )

    median_impact_short = np.median(impact_short)
    median_impact_long = np.median(impact_long)

    assert median_impact_short == 0 or median_impact_short < median_impact_long
    assert median_impact_short == 0 or median_impact_short * 1.3 < median_impact_long
    assert median_impact_short == 0 or median_impact_short * 3 > median_impact_long


def test_impact_method_calc_base_impact_with_different_era():
    test_short_eras = (
        Era(
            length=30,
            annual_extinction_risk=0.05,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=1,
            annual_extinction_risk=0.00005,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=2,
            annual_extinction_risk=0.4,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
    )
    test_long_eras = (
        Era(
            length=30,
            annual_extinction_risk=0.05,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=30,
            annual_extinction_risk=0.00005,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=2,
            annual_extinction_risk=0.4,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
    )

    half_off = np.ones(SIMULATIONS) * 0.5
    nothing = np.zeros(SIMULATIONS)

    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=test_short_eras,
                max_creditable_year=1_000_000,
                catastrophe_extinction_risk_ratios=FrozenDict({RiskTypeAI.MISALIGNMENT: 0}),
            )
        )
    ):
        model_short = BasicImpactMethod("", "")
        impact_short = model_short.calc_base_impact(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            nothing,
            np.array(SIMULATIONS * [30]),
        )

    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=test_long_eras,
                max_creditable_year=1_000_000,
                catastrophe_extinction_risk_ratios=FrozenDict({RiskTypeAI.MISALIGNMENT: 0}),
            )
        )
    ):
        model_long = BasicImpactMethod("", "")
        impact_long = model_long.calc_base_impact(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            nothing,
            np.array(SIMULATIONS * [30]),
        )

    median_impact_short = np.median(impact_short)
    median_impact_long = np.median(impact_long)

    assert median_impact_short == 0 or median_impact_short < median_impact_long
    assert median_impact_short == 0 or median_impact_short * 1.2 < median_impact_long
    assert median_impact_short == 0 or median_impact_short * 4 > median_impact_long


def test_sample_life_years_changed_xrisk_produces_expected_results_with_high_risks():
    test_eras = (
        Era(
            length=30,
            annual_extinction_risk=0.1,
            proportional_risks_by_type=FrozenDict(
                {  # type: ignore  # type checking doesn't understand frozendicts with enums as keys
                    RiskTypeAI.MISALIGNMENT: 1,
                    RiskTypeAI.MISUSE: 0,
                    RiskTypeGLT.BIO: 0,
                    RiskTypeGLT.NANO: 0,
                    RiskTypeGLT.NATURAL: 0,
                    RiskTypeGLT.NUKES: 0,
                    RiskTypeGLT.UNKNOWN: 0,
                }
            ),
        ),
        Era(
            length=1,
            annual_extinction_risk=0.00005,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=20,
            annual_extinction_risk=0.4,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
    )

    smidge_off = np.ones(SIMULATIONS) * 0.03
    some_off = np.ones(SIMULATIONS) * 0.3

    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=test_eras,
                max_creditable_year=23000,
            )
        )
    ):
        model = BasicImpactMethod("", "")

        life_years_samples = model._sample_life_years_changed_xrisk(
            RiskTypeAI.MISALIGNMENT,
            smidge_off,
            np.array(SIMULATIONS * [30]),
        )
        non_zero_differences = life_years_samples[life_years_samples != 0]
        # Number where first xrisk is in range, where the absolute change is enough to make a difference
        expected_number = (1 - ((0.9) ** 30)) * (0.03) * SIMULATIONS
        actual_number = len(non_zero_differences)
        assert math.isclose(actual_number, expected_number, rel_tol=0.2)
        # Saves about 10 years
        assert np.mean(life_years_samples[life_years_samples > 0]) > 10 * B
        assert np.mean(life_years_samples[life_years_samples > 0]) < 20 * 8 * B

        life_years_samples = model._sample_life_years_changed_xrisk(
            RiskTypeAI.MISALIGNMENT,
            some_off,
            np.array(SIMULATIONS * [30]),
        )
        non_zero_differences = life_years_samples[life_years_samples != 0]
        expected_number = (1 - ((0.9) ** 30)) * (0.3) * SIMULATIONS
        actual_number = len(non_zero_differences)
        assert math.isclose(actual_number, expected_number, rel_tol=0.2)

        life_years_samples = model._sample_life_years_changed_xrisk(
            RiskTypeAI.MISALIGNMENT,
            some_off,
            np.array(SIMULATIONS * [5]),
        )
        non_zero_differences = life_years_samples[life_years_samples != 0]
        expected_number = (1 - ((0.9) ** 5)) * (0.3) * SIMULATIONS
        actual_number = len(non_zero_differences)
        assert math.isclose(actual_number, expected_number, rel_tol=0.2)

        life_years_samples = model._sample_life_years_changed_xrisk(
            RiskTypeAI.MISALIGNMENT,
            smidge_off,
            np.array(SIMULATIONS * [12]),
        )
        non_zero_differences = life_years_samples[life_years_samples != 0]
        expected_number = (1 - ((0.9) ** 12)) * (0.03) * SIMULATIONS
        actual_number = len(non_zero_differences)
        assert math.isclose(actual_number, expected_number, rel_tol=0.2)


def test_sample_life_years_changed_xrisk_produces_expected_results_with_low_risk():
    test_eras = (
        Era(
            length=30,
            annual_extinction_risk=0.01,
            proportional_risks_by_type=FrozenDict(
                {  # type: ignore  # type checking doesn't understand frozendicts with enums as keys
                    RiskTypeAI.MISALIGNMENT: 1,
                    RiskTypeAI.MISUSE: 0,
                    RiskTypeGLT.BIO: 0,
                    RiskTypeGLT.NANO: 0,
                    RiskTypeGLT.NATURAL: 0,
                    RiskTypeGLT.NUKES: 0,
                    RiskTypeGLT.UNKNOWN: 0,
                }
            ),
        ),
        Era(
            length=1,
            annual_extinction_risk=0.00005,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=20,
            annual_extinction_risk=0.4,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
    )

    some_off = np.ones(SIMULATIONS) * 0.3

    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=test_eras,
                max_creditable_year=23000,
            )
        )
    ):
        model = BasicImpactMethod("", "")

        life_years_samples = model._sample_life_years_changed_xrisk(
            RiskTypeAI.MISALIGNMENT,
            some_off,
            np.array(SIMULATIONS * [20]),
        )
    # First extinction event likely to be in first era. Second could be in first or third.
    assert np.mean(life_years_samples[life_years_samples > 0]) > 100 * B
    assert np.mean(life_years_samples[life_years_samples > 0]) < 50 * 8 * B


def test_sample_life_years_changed_xrisk_produces_positive_and_negative_results():
    test_eras = (
        Era(
            length=30,
            annual_extinction_risk=0.01,
            proportional_risks_by_type=FrozenDict(
                {  # type: ignore  # type checking doesn't understand frozendicts with enums as keys
                    RiskTypeAI.MISALIGNMENT: 1,
                    RiskTypeAI.MISUSE: 0,
                    RiskTypeGLT.BIO: 0,
                    RiskTypeGLT.NANO: 0,
                    RiskTypeGLT.NATURAL: 0,
                    RiskTypeGLT.NUKES: 0,
                    RiskTypeGLT.UNKNOWN: 0,
                }
            ),
        ),
        Era(
            length=1,
            annual_extinction_risk=0.00005,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=20,
            annual_extinction_risk=0.4,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
    )

    some_off = np.ones(SIMULATIONS) * 0.3
    some_off[0 : int(len(some_off) / 2)] = -0.3

    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=test_eras,
                max_creditable_year=23000,
            )
        )
    ):
        model = BasicImpactMethod("", "")

        life_years_samples = model._sample_life_years_changed_xrisk(
            RiskTypeAI.MISALIGNMENT,
            some_off,
            np.array(SIMULATIONS * [20]),
        )
    # First extinction event likely to be in first era. Second could be in first or third.
    assert np.sum(life_years_samples > 0) > 0
    assert np.sum(life_years_samples < 0) > 0


def test_sample_life_years_changed_catastrophe_produces_expected_results():
    test_eras = (
        Era(
            length=30,
            annual_extinction_risk=0.1,
            proportional_risks_by_type=FrozenDict(
                {  # type: ignore  # type checking doesn't understand frozendicts with enums as keys
                    RiskTypeAI.MISALIGNMENT: 1,
                    RiskTypeAI.MISUSE: 0,
                    RiskTypeGLT.BIO: 0,
                    RiskTypeGLT.NANO: 0,
                    RiskTypeGLT.NATURAL: 0,
                    RiskTypeGLT.NUKES: 0,
                    RiskTypeGLT.UNKNOWN: 0,
                }
            ),
        ),
        Era(
            length=1,
            annual_extinction_risk=0.00005,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
        Era(
            length=20,
            annual_extinction_risk=0.4,
            proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
        ),
    )

    smidge_off = np.ones(SIMULATIONS) * 0.03

    with using_parameters(
        Parameters(
            longterm_params=LongTermParams(
                risk_eras=test_eras,
                catastrophe_extinction_risk_ratios=FrozenDict(
                    {
                        # type: ignore  # type checking doesn't understand frozendicts with enums as keys
                        RiskTypeAI.MISALIGNMENT: 1,
                        RiskTypeAI.MISUSE: 0,
                        RiskTypeGLT.BIO: 0,
                        RiskTypeGLT.NANO: 0,
                        RiskTypeGLT.NATURAL: 0,
                        RiskTypeGLT.NUKES: 0,
                        RiskTypeGLT.UNKNOWN: 0,
                    }
                ),
            )
        )
    ):
        model = BasicImpactMethod("", "")

        life_years_samples = model._sample_life_years_changed_catastrophe(
            RiskTypeAI.MISALIGNMENT,
            smidge_off,
            np.array(SIMULATIONS * [30]),
        )
    non_zero_differences = life_years_samples[life_years_samples != 0]
    # Number where first xrisk is in range, where the absolute change is enough to make a difference
    expected_number = (1 - ((0.9) ** 30)) * (0.03) * SIMULATIONS
    actual_number = len(non_zero_differences)
    assert math.isclose(actual_number, expected_number, rel_tol=0.2)

    assert np.mean(life_years_samples[life_years_samples > 0]) > 100 * M


@pytest.mark.parametrize(
    argnames=("risk_type", "world_pop", "expected_avg_min", "expected_avg_max"),
    argvalues=[
        (RiskTypeGLT.BIO, 8 * B, 10 * M, 1 * B),
        (RiskTypeGLT.NATURAL, 8 * B, 1 * M, 1 * B),
        (RiskTypeGLT.NUKES, 8 * B, 100 * M, 8 * B),
        (RiskTypeAI.MISALIGNMENT, 8 * B, 10 * M, 8 * B),
    ],
)
def test_sample_catastrophe_deaths_bio(
    risk_type,
    world_pop,
    expected_avg_min,
    expected_avg_max,
):
    with using_parameters(Parameters(longterm_params=LongTermParams())):
        model = BasicImpactMethod("", "")
        deaths = model._sample_catastrophe_deaths(
            risk_type,
            world_pop,
        )
    average = np.mean(deaths)
    assert average > expected_avg_min
    assert average < expected_avg_max
