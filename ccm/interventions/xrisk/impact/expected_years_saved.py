import numpy as np
from numpy.typing import NDArray

from ccm.interventions.xrisk.impact.impact_method import ImpactMethod
from ccm.world.risk_types import RiskType


class ExpectedYearsSaved(ImpactMethod):
    """Baseline CCM impact calculation method; calculates EV of years survived with and without the intervention
    (with no upper limit to years survived) to determine years_credit, then calculates how many healthy-human-years
    are projected to occur during the span of years_credit.
    """

    def __init__(self) -> None:
        super().__init__(
            "expected years saved",
            "Estimating the expected years saved and calculating impact for population over that period",
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
