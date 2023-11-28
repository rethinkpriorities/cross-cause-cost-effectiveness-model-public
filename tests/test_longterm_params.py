import pytest
import numpy as np
from squigglepy import M
import squigglepy as sq

import ccm.config as config
from ccm.base_parameters import FrozenDict
from ccm.contexts import using_parameters
from ccm.interventions.xrisk.impact.impact_method_params import ALL_IMPACT_METHODS, ImpactMethodParams
from ccm.interventions.xrisk.xrisk_interventions import XRiskIntervention
from ccm.parameters import Parameters
from ccm.utility.models import ConstantDistributionSpec, DistributionSpec
from ccm.world.eras import Era
from ccm.world.longterm_params import LongTermParams, DEFAULT_ERAS
from ccm.world.risk_types import get_risk_types, RiskTypeAI


SIMULATIONS = config.get_simulations()
ALL_RISK_TYPES = get_risk_types()

constant_speed = DistributionSpec.from_sq(sq.ConstantDistribution(0.001))


def params_with_risk_eras(risk_eras=DEFAULT_ERAS):
    return Parameters(
        longterm_params=LongTermParams(risk_eras=risk_eras, expansion_speed=(constant_speed)),
    )


def params_with_impact_and_risk_eras(impact_method, risk_eras=DEFAULT_ERAS):
    return Parameters(
        impact_method=ImpactMethodParams(impact_method=impact_method),
        longterm_params=LongTermParams(risk_eras=risk_eras, expansion_speed=(constant_speed)),
    )


@pytest.mark.parametrize("impact_method", ALL_IMPACT_METHODS.values())
@pytest.mark.parametrize("risk_type", ALL_RISK_TYPES)
@pytest.mark.parametrize("risk_multiplier", [10, 10 ** (-4)])
def test_impact_given_risk_reduction_is_sensitive_to_annual_risks(impact_method, risk_type, risk_multiplier):
    proportional_change_in_probability = np.array([0.1] * SIMULATIONS)
    years_changed = np.array([20] * SIMULATIONS)
    print(impact_method)
    with using_parameters(params_with_risk_eras()):
        base_impact_default_risk = impact_method.calc_base_impact(
            risk_type=risk_type,
            proportion_extinction_risk_changed=proportional_change_in_probability,
            proportion_catastrophe_risk_changed=proportional_change_in_probability,
            years_risk_changed=years_changed,
        )
        impact_given_risk_reduction_default_risk = impact_method.calc_impact_given_prop_risk_reduction(
            risk_type=risk_type,
            proportion_extinction_risk_changed=proportional_change_in_probability,
            proportion_catastrophe_risk_changed=proportional_change_in_probability,
            years_risk_changed=years_changed,
        )

    modified_risk_eras = []
    for era in DEFAULT_ERAS:
        modified_era = Era(
            length=era.length,
            annual_extinction_risk=era.annual_extinction_risk * risk_multiplier,
            proportional_risks_by_type=era.proportional_risks_by_type,
        )
        modified_risk_eras.append(modified_era)
    modified_risk_eras = tuple(modified_risk_eras)

    with using_parameters(params_with_risk_eras(modified_risk_eras)):
        base_impact_modified_risk = impact_method.calc_base_impact(
            risk_type=risk_type,
            proportion_extinction_risk_changed=proportional_change_in_probability,
            proportion_catastrophe_risk_changed=proportional_change_in_probability,
            years_risk_changed=years_changed,
        )
        impact_given_risk_reduction_modified_risk = impact_method.calc_impact_given_prop_risk_reduction(
            risk_type=risk_type,
            proportion_extinction_risk_changed=proportional_change_in_probability,
            proportion_catastrophe_risk_changed=proportional_change_in_probability,
            years_risk_changed=years_changed,
        )

    if risk_multiplier > 1:
        assert np.mean(base_impact_modified_risk) > np.mean(
            base_impact_default_risk
        ), "Under increased risks, an x-risk mitigation intervention should have a bigger impact, not smaller!"
        assert np.mean(impact_given_risk_reduction_modified_risk) > np.mean(
            impact_given_risk_reduction_default_risk,
        ), "Under increased risks, the same proportional x-risk mitigation should have a more impact, not less!"

    if risk_multiplier < 1:
        assert np.mean(base_impact_modified_risk) < np.mean(
            base_impact_default_risk,
        ), "Under reduced risks, an x-risk mitigation intervention should have a smaller impact, not bigger!"
        assert np.mean(impact_given_risk_reduction_modified_risk) < np.mean(
            impact_given_risk_reduction_default_risk,
        ), "Under reduced risks, the same proportional x-risk mitigation should have a less impact, not more!"


@pytest.mark.parametrize("risk_type", [RiskTypeAI.MISALIGNMENT])  # ALL_RISK_TYPES)
@pytest.mark.parametrize("impact_method", ALL_IMPACT_METHODS.keys())
def test_effectiveness_is_sensitive_to_annual_risks(risk_type, impact_method):
    effect_on_xrisk = ConstantDistributionSpec(type="constant", distribution="constant", value=0.05)
    effect_on_catastrophic_risk = ConstantDistributionSpec(type="constant", distribution="constant", value=0.05)
    cost = ConstantDistributionSpec(type="constant", distribution="constant", value=10 * M)
    persistence = ConstantDistributionSpec(type="constant", distribution="constant", value=20)
    annual_risk_high = 1 / 101
    annual_risk_low = 1 / 20000

    era_low_risk = Era(
        length=1_000_000_000,
        annual_extinction_risk=annual_risk_low,
        proportional_risks_by_type=FrozenDict({risk: 1 / len(ALL_RISK_TYPES) for risk in ALL_RISK_TYPES}),
    )
    era_high_risk = Era(
        length=1_000_000_000,
        annual_extinction_risk=annual_risk_high,
        proportional_risks_by_type=FrozenDict({risk: 1 / len(ALL_RISK_TYPES) for risk in ALL_RISK_TYPES}),
    )

    with using_parameters(params_with_impact_and_risk_eras(impact_method, (era_low_risk,))):
        intervention_under_low_risk = XRiskIntervention(
            risk_type=risk_type,
            cost=cost,
            prob_no_effect=0.0,
            prob_good=1.0,
            intensity_bad=0.0,
            effect_on_xrisk=effect_on_xrisk,
            effect_on_catastrophic_risk=effect_on_catastrophic_risk,
            persistence=persistence,
        )
        (
            healthy_years_saved_low_risk,
            explicit_zeros_low_risk,
        ) = intervention_under_low_risk.glt_dalys_per_1000_estimator()
        avg_years_saved_low_risk = np.sum(healthy_years_saved_low_risk) / (
            len(healthy_years_saved_low_risk) + explicit_zeros_low_risk
        )
        prop_zeros_low_risk = (explicit_zeros_low_risk + np.sum(healthy_years_saved_low_risk == 0)) / (
            len(healthy_years_saved_low_risk) + explicit_zeros_low_risk
        )

    with using_parameters(params_with_impact_and_risk_eras(impact_method, (era_high_risk,))):
        intervention_under_high_risk = XRiskIntervention(
            risk_type=risk_type,
            cost=cost,
            prob_no_effect=0.0,
            prob_good=1.0,
            intensity_bad=0.0,
            effect_on_xrisk=effect_on_xrisk,
            effect_on_catastrophic_risk=effect_on_catastrophic_risk,
            persistence=persistence,
        )
        (
            healthy_years_saved_high_risk,
            explicit_zeros_high_risk,
        ) = intervention_under_high_risk.glt_dalys_per_1000_estimator()
        avg_years_saved_high_risk = np.sum(healthy_years_saved_high_risk) / (
            len(healthy_years_saved_high_risk) + explicit_zeros_high_risk
        )
        prop_zeros_high_risk = (explicit_zeros_high_risk + np.sum(healthy_years_saved_high_risk == 0)) / (
            len(healthy_years_saved_high_risk) + explicit_zeros_high_risk
        )

    assert (
        avg_years_saved_high_risk > avg_years_saved_low_risk
    ), "Under increased risks, an x-risk mitigation intervention should save more DALYs, not less!"
    assert (
        prop_zeros_low_risk > prop_zeros_high_risk
    ), "Under increased risks, the effects of a x-risk mitigation intervention should be zero less often!"


@pytest.mark.parametrize("target_risk_type", ALL_RISK_TYPES)
@pytest.mark.parametrize("impact_method", ALL_IMPACT_METHODS.keys())
def test_effectiveness_is_sensitive_to_proportional_risks(target_risk_type, impact_method):
    proportional_risk_high = 0.8
    proportional_risk_low = 0.01
    effect_on_xrisk = ConstantDistributionSpec(type="constant", distribution="constant", value=0.05)
    effect_on_catastrophic_risk = ConstantDistributionSpec(type="constant", distribution="constant", value=0.05)
    persistence = ConstantDistributionSpec(type="constant", distribution="constant", value=20)
    cost = ConstantDistributionSpec(type="constant", distribution="constant", value=10 * M)

    era_low_prop_risk = Era(
        length=1_000_000_000,
        annual_extinction_risk=1 / 10_000,
        proportional_risks_by_type=FrozenDict(
            {
                risk: proportional_risk_low
                if risk == target_risk_type
                else (1 - proportional_risk_low) / (len(ALL_RISK_TYPES) - 1)
                for risk in ALL_RISK_TYPES
            }
        ),
    )
    era_high_prop_risk = Era(
        length=1_000_000_000,
        annual_extinction_risk=1 / 10_000,
        proportional_risks_by_type=FrozenDict(
            {
                risk: proportional_risk_high
                if risk == target_risk_type
                else (1 - proportional_risk_high) / (len(ALL_RISK_TYPES) - 1)
                for risk in ALL_RISK_TYPES
            }
        ),
    )

    with using_parameters(params_with_impact_and_risk_eras(impact_method, (era_low_prop_risk,))):
        intervention_under_low_risk = XRiskIntervention(
            risk_type=target_risk_type,
            cost=cost,
            prob_no_effect=0.0,
            prob_good=1.0,
            intensity_bad=0.0,
            effect_on_xrisk=effect_on_xrisk,
            effect_on_catastrophic_risk=effect_on_catastrophic_risk,
            persistence=persistence,
        )
        (
            healthy_years_saved_low_risk,
            explicit_zeros_low_risk,
        ) = intervention_under_low_risk.glt_dalys_per_1000_estimator()
        avg_years_saved_low_risk = np.sum(healthy_years_saved_low_risk) / (
            len(healthy_years_saved_low_risk) + explicit_zeros_low_risk
        )
        prop_zeros_low_risk = (explicit_zeros_low_risk + np.sum(healthy_years_saved_low_risk == 0)) / (
            len(healthy_years_saved_low_risk) + explicit_zeros_low_risk
        )

    with using_parameters(params_with_impact_and_risk_eras(impact_method, (era_high_prop_risk,))):
        intervention_under_high_risk = XRiskIntervention(
            risk_type=target_risk_type,
            cost=cost,
            prob_no_effect=0.0,
            prob_good=1.0,
            intensity_bad=0.0,
            effect_on_xrisk=ConstantDistributionSpec(type="constant", distribution="constant", value=0.05),
            effect_on_catastrophic_risk=ConstantDistributionSpec(type="constant", distribution="constant", value=0.05),
            persistence=persistence,
        )
        (
            healthy_years_saved_high_risk,
            explicit_zeros_high_risk,
        ) = intervention_under_high_risk.glt_dalys_per_1000_estimator()
        avg_years_saved_high_risk = np.sum(healthy_years_saved_high_risk) / (
            len(healthy_years_saved_high_risk) + explicit_zeros_high_risk
        )
        prop_zeros_high_risk = (explicit_zeros_high_risk + np.sum(healthy_years_saved_high_risk == 0)) / (
            len(healthy_years_saved_high_risk) + explicit_zeros_high_risk
        )

    assert (
        avg_years_saved_high_risk > avg_years_saved_low_risk
    ), "If a risk gets proportionally higher, an intervention targeting it should save more DALYs, not less!"
    assert (
        prop_zeros_low_risk > prop_zeros_high_risk
    ), "If a risk gets proportionally higher, should be zero less often!"
