import numpy as np
from numpy.typing import NDArray

import ccm.config as config
from ccm.interventions.xrisk.impact.impact_method import ImpactMethod
from ccm.world.risk_types import RiskType

CUR_YEAR = config.get_current_year()
THOUSAND_YEARS = 1000


class ThousandYearImpact(ImpactMethod):
    """Calculate Impact similarly to Expected Years Saved, but as if the world were going to end in 1000
    years either way.

    This can be useful for comparing Interventions without introducing a bunch of variables we don't have good
    >1000 year projections for (e.g. population growth, annual risk amounts). However, keep in mind that it is, by
    definition, completely discarding any value which would have been accrued past 1000 years, which could be quite
    substantial."""

    def __init__(self) -> None:
        super().__init__(
            "thousand year impact",
            (
                "Estimating the expected years saved assuming extinction in 1000 years, and calculating impact for "
                "population over that period"
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
