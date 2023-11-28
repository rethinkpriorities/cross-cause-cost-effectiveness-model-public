import numpy as np
from numpy.typing import NDArray

import ccm.config as config
from ccm.interventions.xrisk.impact.impact_method import ImpactMethod
from ccm.world.eras import Era
from ccm.world.longterm_params import DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK, DEFAULT_MAX_CREDITABLE_YEAR
from ccm.world.risk_types import RiskType

SIMULATIONS = config.get_simulations()
CUR_YEAR = config.get_current_year()

TIME_OF_PERILS_ERAS = (
    Era(length=30, annual_extinction_risk=0.05, proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK),
    Era(length=100, annual_extinction_risk=0.001, proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK),
    Era(
        length=1000,
        annual_extinction_risk=0.000001,
        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
    ),
    Era(
        length=DEFAULT_MAX_CREDITABLE_YEAR,
        annual_extinction_risk=1e-8,
        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
    ),
)


class TimeOfPerils(ImpactMethod):
    """Calculate Impact similarly to Expected Years Saved up until the projected end of the Time of Perils,
    then assume in all universes where humanity survived that far, they embark on cubic population expansion
    throughout the lightcone.

    This will output very large numbers. Keep in mind that these outputs are contingent on a lot of conjuctive
    assumptions which we are not accounting for the reduced probability mass of. It's best to treat the output
    as a rough ceiling on the amount of Impact hypothetically possible without resorting to Digital Minds or
    major changes to our understanding of physics and/or metaphysics.

    See notes in ccm.world.time_of_perils.py for more detailed information about the Time of Perils model."""

    def __init__(self) -> None:
        super().__init__(
            "time of perils",
            (
                "Estimating the expected years saved and calculating impact for population over that period, assuming "
                "the Time of Perils ends in 2100, at which time x-risk is substantially reduced and population spreads "
                "throughout the stars"
            ),
        )

    def calc_impact_given_prop_risk_reduction(
        self,
        risk_type: RiskType,
        proportion_extinction_risk_changed: NDArray[np.float64],
        proportion_catastrophe_risk_changed: NDArray[np.float64],
        years_risk_changed: NDArray[np.int64],
        *args,
        **kwargs,
    ) -> NDArray[np.float64]:
        total_healthy_life_years_saved = self.calc_base_impact(
            risk_type,
            proportion_extinction_risk_changed,
            proportion_catastrophe_risk_changed,
            years_risk_changed,
            *args,
            **kwargs,
        )

        return total_healthy_life_years_saved
