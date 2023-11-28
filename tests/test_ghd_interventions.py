import numpy as np
import squigglepy as sq

from ccm.contexts import using_parameters
from ccm.interventions.ghd.ghd_intervention_params import GhdInterventionParams
from ccm.interventions.ghd.ghd_interventions import GhdIntervention
from ccm.parameters import Parameters
from ccm.utility.models import ConfidenceDistributionSpec, DistributionSpec


def test_gw_dalys_per_1000():
    """Simple sanity check for get_gw_dalys_per_1000"""
    lo = 31
    hi = 81
    avg_cost_per_daly = (lo + hi) / 2
    expected_dalys_per_1000 = 1000 / avg_cost_per_daly

    with using_parameters(
        Parameters(
            ghd_intervention_params=GhdInterventionParams(
                adjust_for_xrisk=False,
            )
        )
    ):
        # note: the real distribution is clipped on the left side, but we don't clip in the test to keep it
        # symmetric so the mean is easier to calculate
        intervention = GhdIntervention(name="GiveWell", cost_per_daly=DistributionSpec.from_sq(sq.norm(lo, hi)))
        dalys_per_1000 = intervention.risk_adjusted_dalys_per_1000()

    assert np.median(dalys_per_1000) > 0.8 * expected_dalys_per_1000
    assert np.median(dalys_per_1000) < 1.2 * expected_dalys_per_1000


def test_gd_dalys_per_1000():
    """Simple sanity check for get_gd_dalys_per_1000"""
    lo = 460
    hi = 600
    avg_cost_per_daly = (lo + hi) / 2
    expected_dalys_per_1000 = 1000 / avg_cost_per_daly

    with using_parameters(Parameters(ghd_intervention_params=GhdInterventionParams(adjust_for_xrisk=False))):
        intervention = GhdIntervention(name="GiveDirectly", cost_per_daly=DistributionSpec.from_sq(sq.norm(lo, hi)))
        dalys_per_1000 = intervention.risk_adjusted_dalys_per_1000()

    assert np.median(dalys_per_1000) > 0.8 * expected_dalys_per_1000
    assert np.median(dalys_per_1000) < 1.2 * expected_dalys_per_1000


def test_low_cost_ghd_intervention_beats_high_cost():
    with using_parameters(Parameters(ghd_intervention_params=GhdInterventionParams(adjust_for_xrisk=False))):
        intervention_high_cost = GhdIntervention(
            name="High Cost",
            cost_per_daly=DistributionSpec.from_sq(sq.norm(1000, 1100)),
        )
        intervention_low_cost = GhdIntervention(
            name="Low Cost",
            cost_per_daly=DistributionSpec.from_sq(sq.norm(10, 11)),
        )
        assert np.mean(intervention_low_cost.risk_adjusted_dalys_per_1000()) > np.mean(
            intervention_high_cost.risk_adjusted_dalys_per_1000()
        ), "A low cost-per-DALY GHD intervention should be more cost-effective than a high cost-per-DALY intervention"


def test_high_p_survival_beats_low_p_survival():
    with using_parameters(Parameters(ghd_intervention_params=GhdInterventionParams(adjust_for_xrisk=False))):
        intervention_high_p_survival = GhdIntervention(
            name="test",
            cost_per_daly=DistributionSpec.from_distribution(sq.norm(100, 101)),
        )
        high_p_survival = intervention_high_p_survival.risk_adjusted_dalys_per_1000()

    with using_parameters(Parameters(ghd_intervention_params=GhdInterventionParams(adjust_for_xrisk=True))):
        intervention_low_p_survival = GhdIntervention(
            name="test",
            cost_per_daly=DistributionSpec.from_distribution(sq.norm(100, 101)),
        )
        low_p_survival = intervention_low_p_survival.risk_adjusted_dalys_per_1000()

    assert np.mean(high_p_survival) > np.mean(
        low_p_survival
    ), "A GHD intervention should be more cost-effective when P(survival) is higher"


def test_get_p_survival():
    "Test that decreasing P(survival) decreases the expected value of GHD interventions"

    with using_parameters(Parameters(ghd_intervention_params=GhdInterventionParams(adjust_for_xrisk=False))):
        intervention_unadjusted = GhdIntervention(
            name="test",
            years_until_intervention_has_effect=ConfidenceDistributionSpec.lognorm(1, 3),
        )
        p_survival_unadjusted = intervention_unadjusted._get_p_survival()

    with using_parameters(Parameters(ghd_intervention_params=GhdInterventionParams(adjust_for_xrisk=True))):
        intervention_short_wait = GhdIntervention(
            name="test",
            years_until_intervention_has_effect=ConfidenceDistributionSpec.lognorm(1, 3),
        )
        p_survival_short_wait = intervention_short_wait._get_p_survival()

    with using_parameters(Parameters(ghd_intervention_params=GhdInterventionParams(adjust_for_xrisk=True))):
        intervention_long_wait = GhdIntervention(
            name="test",
            years_until_intervention_has_effect=ConfidenceDistributionSpec.lognorm(20, 30),
        )
        p_survival_long_wait = intervention_long_wait._get_p_survival()

    assert np.min(p_survival_unadjusted) > np.max(
        p_survival_short_wait
    ), "P(survival) with no xrisk adjustment should always be higher than P(survival) with any xrisk adjustment"
    assert np.mean(p_survival_short_wait) > np.mean(
        p_survival_long_wait
    ), "P(survival) with a short wait should be higher on average than P(survival) with a long wait"
