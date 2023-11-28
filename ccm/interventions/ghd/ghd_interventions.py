"""
Premises and simulations about Global Health and Development Interventions.
The estimates for GW, GD, and OP are derived from info here:
https://www.openphilanthropy.org/research/technical-updates-to-our-global-health-and-wellbeing-cause-prioritization-framework/

Newer estimations detailed in comments here: https://github.com/rethinkpriorities/cross-cause-model/pull/38
"""


from functools import lru_cache
from inspect import cleandoc
from typing import Annotated, Literal, Optional

import numpy as np
from numpy.typing import NDArray
from pydantic import AfterValidator, Field

import ccm.config as config
import ccm.utility.risk_calculator as risk_calculator
import ccm.utility.squigglepy_wrapper as sqw
from ccm.contexts import inject_parameters
from ccm.interventions.ghd.ghd_intervention_params import GhdInterventionParams
from ccm.interventions.intervention import EstimatorIntervention
from ccm.utility.models import ConfidenceDistributionSpec, SomeDistribution

SIMULATIONS = config.get_simulations()
CUR_YEAR = config.get_current_year()

DEFAULT_YEARS_UNTIL_INTERVENTION_HAS_EFFECT = ConfidenceDistributionSpec.lognorm(2, 20)

OP_COST_EFFECTIVENESS = ConfidenceDistributionSpec.norm(
    40, 60, lclip=1, credibility=80
)  # 2,000x bar; SEE: https://bit.ly/3tLbaAg
GW_COST_EFFECTIVENESS = ConfidenceDistributionSpec.norm(31, 81, lclip=10, credibility=80)
GD_COST_EFFECTIVENESS = ConfidenceDistributionSpec.norm(460, 836, lclip=1, credibility=80)


class GhdIntervention(EstimatorIntervention, frozen=True):
    type: Literal["ghd"] = "ghd"
    version: Literal["1"] = "1"
    area: Literal["ghd"] = "ghd"
    name: Annotated[
        str,
        Field(
            title="Intervention name",
            description="The name of the intervention. Acts as an ID.",
        ),
    ]
    description: Annotated[
        Optional[Annotated[str, AfterValidator(cleandoc)]],
        Field(
            title="Intervention description",
            description="A longer description for the Global Health and Development intervention.",
        ),
    ] = "An intervention that promotes Global Health and Development."
    cost_per_daly: Annotated[
        SomeDistribution,
        Field(
            title="Custom cost per DALY",
            description=(
                "A distribution to be used as the cost-effectiveness bar instead of "
                + "the preset ones (GiveDirectly, GiveWell, OpenPhilantropy)."
            ),
        ),
    ] = ConfidenceDistributionSpec.norm(31, 81, lclip=10)
    years_until_intervention_has_effect: Annotated[
        SomeDistribution,
        Field(
            title="Years until intervention has an effect",
            description=(
                "Adjusts the cost-effectiveness of this intervention downward, "
                "based on the cumulative x-risk over this many years."
            ),
        ),
    ] = DEFAULT_YEARS_UNTIL_INTERVENTION_HAS_EFFECT

    def __init__(self, **data):
        super().__init__(_estimator=lru_cache(maxsize=1)(self.risk_adjusted_dalys_per_1000), **data)

    def risk_adjusted_dalys_per_1000(self) -> NDArray[np.float64]:
        """Input params define normal distribution of dollars-per-DALY, output is in DALYs/$1000 discounted by the
        possibility that x-risk event precludes benefits.
        """
        p_survival = self._get_p_survival()
        dalys_per_1000 = 1000 / (sqw.sample(self.cost_per_daly.get_distribution(), n=SIMULATIONS) / p_survival)

        return dalys_per_1000

    # ///////////////// Private Functions /////////////////

    @inject_parameters
    def _get_p_survival(self, params: GhdInterventionParams) -> NDArray[np.float64]:
        """Creates distribution of guesses when the intervention takes effect
        and gets an array probabilities that we survive until then.
        Parameters:
        adjust_for_xrisk (bool): Whether to use the xrisk adjustment, or skip it (force p_survival=1.0); setting this to
            True will result in higher DALY efficiency values being output for all GHD Interventions.
        """
        if not params.adjust_for_xrisk:
            return np.ones(SIMULATIONS)

        # Years until intervention effects are counted. If everyone dies before this, no effect is credited.
        forward_years = (
            sqw.sample(
                self.years_until_intervention_has_effect.get_distribution(),
                n=SIMULATIONS,
            )
            .round()
            .astype(int)
        )
        years = np.array([CUR_YEAR] * SIMULATIONS) + forward_years

        total_x_risk = risk_calculator.get_cumulative_risk_over_years(years)
        p_survival = np.ones(SIMULATIONS) - total_x_risk

        return p_survival
