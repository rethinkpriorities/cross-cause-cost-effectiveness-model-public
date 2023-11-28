import numpy as np
import pytest
import squigglepy as sq

import ccm.config as config
import ccm.world.risk_types as risk_types
from ccm.contexts import using_parameters
from ccm.interventions.xrisk.impact.impact_method_params import ALL_IMPACT_METHODS, ImpactMethodParams
from ccm.interventions.xrisk.xrisk_interventions import XRiskIntervention
from ccm.parameters import Parameters
from ccm.utility.models import ConstantDistributionSpec
from ccm.world.risk_types import RiskTypeAI, RiskTypeGLT

ALL_RISK_TYPES = risk_types.get_risk_types()
SIMULATIONS = config.get_simulations()


rng = sq.rng.set_seed(42)


@pytest.mark.parametrize("impact_method", list(ALL_IMPACT_METHODS.keys()))
@pytest.mark.parametrize("risk_type", ALL_RISK_TYPES)
def test_glt_daly_estimator(impact_method, risk_type) -> None:
    with using_parameters(Parameters(impact_method=ImpactMethodParams(impact_method=impact_method))):
        intervention = XRiskIntervention(risk_type=risk_type)
        estimate_dalys_per_1000, zeros = intervention.glt_dalys_per_1000_estimator()

    assert isinstance(estimate_dalys_per_1000, np.ndarray), "Result does not include a `numpy.NDArray` object"
    assert isinstance(zeros, int), "Result does not include an integer with the number of zeros"
    assert len(estimate_dalys_per_1000) == SIMULATIONS, "Function returned an incorrect number of elements"
    assert np.all(np.isreal(estimate_dalys_per_1000)), "Function returned at least one value that is not a float"
    assert not np.all(estimate_dalys_per_1000 == 0), (
        f"All samples are zeroes when effectiveness is estimated using the `{impact_method}` method and "
        + f"`risk_type` is set to `'{risk_type.value}'`."
    )

    # smoke tests - is the average returned value reasonable?
    avg_dalys_per_1000 = np.sum(estimate_dalys_per_1000) / (len(estimate_dalys_per_1000) + zeros)
    assert avg_dalys_per_1000 < 10**24, "Average of returned DALYs/$1000 values is too high"
    assert avg_dalys_per_1000 > -(10**20), "Average of returned DALYs/$1000 values is too low"


@pytest.mark.parametrize("impact_method", list(ALL_IMPACT_METHODS.keys()))
@pytest.mark.parametrize("risk_type", ALL_RISK_TYPES)
def test_risk_reduced_per_project(impact_method, risk_type) -> None:
    with using_parameters(Parameters(impact_method=ImpactMethodParams(impact_method=impact_method))):
        intervention = XRiskIntervention(risk_type=risk_type)
        base_xrisk_impact_magnitude = intervention._base_xrisk_impact_magnitude

    max_prop_xrisk_reduction = max(base_xrisk_impact_magnitude)
    max_prop_non_xrisk_reduction = max(base_xrisk_impact_magnitude)

    assert max_prop_xrisk_reduction <= 0.2, "X risk relative risk reduction exceeds 0.2"
    assert max_prop_non_xrisk_reduction <= 0.2, "Non-X risk relative risk reduction exceeds 0.2"


@pytest.mark.parametrize("impact_method", list(ALL_IMPACT_METHODS.keys()))
@pytest.mark.parametrize("risk_type", ALL_RISK_TYPES)
def test_estimate_impact(impact_method, risk_type):
    with using_parameters(Parameters(impact_method=ImpactMethodParams(impact_method=impact_method))):
        intervention = XRiskIntervention(risk_type=risk_type)
        healthy_life_yrs_saved, zeros = intervention.estimate_healthy_years_saved()

    assert isinstance(
        healthy_life_yrs_saved,
        np.ndarray,
    ), "Resulting `healthy_life_yrs_saved` is not a `numpy.NDArray` object"
    assert isinstance(zeros, int), "Resulting `zeros` is not an `int`"
    assert (
        len(healthy_life_yrs_saved) == SIMULATIONS
    ), "Function returned an incorrect number of `healthy_life_yrs_saved` elements"
    assert np.all(
        np.isreal(healthy_life_yrs_saved),
    ), "Function returned at least one `healthy_life_yrs_saved` value that is not a float"
    assert not np.all(healthy_life_yrs_saved == 0), "All values for `healthy_life_yrs_saved` are zeros."


@pytest.mark.parametrize("risk_type", ALL_RISK_TYPES)
def test_estimate_intensity_modifiers(risk_type):
    intervention = XRiskIntervention(risk_type=risk_type)
    intensity_modifiers = intervention._intensity_modifiers
    assert isinstance(intensity_modifiers, np.ndarray), "Result is not a `numpy.NDArray` object"
    assert len(intensity_modifiers) == SIMULATIONS, "Function returned an incorrect number of elements"
    assert np.all(np.isreal(intensity_modifiers)), "Function returned at least one value that is not a float"
    assert np.min(intensity_modifiers) >= -1.0, "Function return an intensity modifier below -1.0"
    assert np.max(intensity_modifiers) <= 1.0, "Function return an intensity modifier above 1.0"


@pytest.mark.parametrize(
    argnames=(
        "risk_type",
        "prob_good",
        "prob_no_effect",
        "intensity_bad",
        "effect_on_xrisk",
    ),
    argvalues=[
        (RiskTypeAI.MISALIGNMENT, 0.7, 0.2, 0.3, 0.05),
        (RiskTypeGLT.NUKES, 0.7, 0.2, 0.3, 0.05),
    ],
)
def test_get_base_impact_magnitude_from_proportion_risk_reduced(
    risk_type,
    prob_good,
    prob_no_effect,
    intensity_bad,
    effect_on_xrisk,
):
    expected_good_results_magnitude = (1 - prob_no_effect) * effect_on_xrisk
    expected_bad_results_magnitude = expected_good_results_magnitude * abs(intensity_bad)
    expected_magnitude = expected_good_results_magnitude * prob_good + expected_bad_results_magnitude * (1 - prob_good)
    intervention = XRiskIntervention(
        risk_type=risk_type,
        prob_good=prob_good,
        prob_no_effect=prob_no_effect,
        intensity_bad=intensity_bad,
        effect_on_xrisk=ConstantDistributionSpec(type="constant", distribution="constant", value=effect_on_xrisk),
    )

    base_impact_magnitude = intervention._base_xrisk_impact_magnitude

    assert isinstance(base_impact_magnitude, np.ndarray), "Result is not a `numpy.NDArray` object"
    assert len(base_impact_magnitude) == SIMULATIONS, "Function returned an incorrect number of elements"
    np.testing.assert_approx_equal(
        actual=np.mean(base_impact_magnitude),
        desired=expected_magnitude,
        significant=1,
        err_msg="Returned array deviated from expected mean!",
    )


def test_higher_impact_magnitude_more_costly():
    with using_parameters(Parameters()):
        intervention_small_effect = XRiskIntervention(
            risk_type=RiskTypeGLT.BIO,
            effect_on_xrisk=ConstantDistributionSpec(type="constant", distribution="constant", value=0.001),
            effect_on_catastrophic_risk=ConstantDistributionSpec(type="constant", distribution="constant", value=0.001),
            prob_good=0.99,
            intensity_bad=0.0,
        )

        intervention_big_effect = XRiskIntervention(
            risk_type=RiskTypeGLT.BIO,
            effect_on_xrisk=ConstantDistributionSpec(type="constant", distribution="constant", value=0.5),
            effect_on_catastrophic_risk=ConstantDistributionSpec(type="constant", distribution="constant", value=0.5),
            prob_good=0.99,
            intensity_bad=0.0,
        )

        intervention_small_effect_cost = (
            intervention_small_effect._project_cost_per_year_given_base_xrisk_impact_magnitude()
        )
        intervention_big_effect_cost = (
            intervention_big_effect._project_cost_per_year_given_base_xrisk_impact_magnitude()
        )

    assert isinstance(intervention_small_effect_cost, np.ndarray), "Result is not a `numpy.NDArray` object"
    assert isinstance(intervention_big_effect_cost, np.ndarray), "Result is not a `numpy.NDArray` object"

    assert len(intervention_small_effect_cost) == SIMULATIONS, "Function returned an incorrect number of elements"
    assert len(intervention_big_effect_cost) == SIMULATIONS, "Function returned an incorrect number of elements"

    assert np.mean(intervention_small_effect_cost) < np.mean(intervention_big_effect_cost), (
        "When not directly provided by the user, the average cost for interventions with small effects should be lower "
        + "than for interventions with bigger effects."
    )


@pytest.mark.parametrize(
    argnames=(
        "healthy_years_saved_per_project",
        "cost_per_megaproject",
        "expected_results",
    ),
    argvalues=[
        (
            np.array([0.0, 100.0, 1.0 * 10**6]),
            np.array([100.0, 1000.0, 1.0 * 10**5]),
            np.array([0.0, 100.0, 10000.0]),
        )
    ],
)
def test_calc_megaproject_dalys_per_1000(
    healthy_years_saved_per_project,
    cost_per_megaproject,
    expected_results,
):
    intervention = XRiskIntervention(risk_type=RiskTypeGLT.BIO)
    megaproject_dalys_per_1000 = intervention._calc_megaproject_dalys_per_1000(
        healthy_years_saved_per_project=healthy_years_saved_per_project,
        cost_per_megaproject=cost_per_megaproject,
    )
    assert isinstance(megaproject_dalys_per_1000, np.ndarray), "Result is not a `numpy.NDArray` object"
    assert len(megaproject_dalys_per_1000) == len(expected_results), "Function returned an incorrect number of elements"
    np.testing.assert_array_equal(
        megaproject_dalys_per_1000,
        expected_results,
        err_msg="Function returned an unexpected value!",
        strict=True,
    )
