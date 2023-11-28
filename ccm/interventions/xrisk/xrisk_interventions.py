"""
Simulations for XRisk Intervention estimates.
"""


from inspect import cleandoc
from functools import cached_property
from typing import Annotated, Literal, Optional

import numpy as np
import squigglepy as sq
from numpy.typing import NDArray
from pydantic import AfterValidator, Field
from squigglepy import B, M

import ccm.config as config
import ccm.interventions.xrisk.impact.utils.years_credit_calculator as years_credit_calculator
import ccm.utility.risk_calculator as risk_calculator
import ccm.utility.squigglepy_wrapper as sqw
import ccm.world.population as population
from ccm.contexts import inject_parameters
from ccm.interventions.intervention import EstimatorIntervention
from ccm.parameters import Parameters
from ccm.utility.models import ConfidenceDistributionSpec, SomeDistribution
from ccm.utility.squigglepy_wrapper import RNG
from ccm.world.longterm_params import LongTermParams
from ccm.world.risk_types import RiskType
from ccm.world.population import WORLD_POPULATION_NOW


SIMULATIONS = config.get_simulations()

DEFAULT_PERSISTENCE = ConfidenceDistributionSpec.lognorm(15, 25, lclip=0)
DEFAULT_PROB_GOOD: float = 0.7
DEFAULT_PROB_NO_EFFECT = 0.2
DEFAULT_INTENSITY_BAD: float = 0.3
DEFAULT_EFFECT_ON_XRISK = ConfidenceDistributionSpec.lognorm(
    lo=0.005,
    hi=0.05,
    lclip=0,
    rclip=0.2,
    credibility=90,
)
DEFAULT_EFFECT_ON_CATASTROPHIC_RISK = ConfidenceDistributionSpec.lognorm(
    lo=0.005,
    hi=0.05,
    lclip=0,
    rclip=0.2,
    credibility=90,
)


class XRiskIntervention(EstimatorIntervention, frozen=True):
    type: Literal["xrisk"] = "xrisk"
    version: Literal["1"] = "1"
    area: Literal["xrisk"] = "xrisk"
    risk_type: Annotated[
        RiskType,
        Field(
            title="Risk type",
            description="Which type of existential/catastrophic risk the intervention deals with.",
        ),
    ]
    description: Annotated[
        Optional[Annotated[str, AfterValidator(cleandoc)]],
        Field(title="Intervention description", description="A longer description for the x-risk intervention."),
    ] = None
    cost: Annotated[
        Optional[SomeDistribution],
        Field(
            title="Cost of the intervention",
            description=(
                "The cost of the intervention, as a range (in US dollars). If not provided, a reasonable default is "
                + r"estimated based in the impact magnitude, with a mean of USD ~12M for 0.5% relative risk reduced "
                + r"and ~6B for 20% of relative risk reduced."
            ),
        ),
    ] = None
    persistence: Annotated[
        SomeDistribution,
        Field(
            title="Persistence of the effects",
            description="How long the intervention's effects will last, in years.",
        ),
    ] = DEFAULT_PERSISTENCE
    prob_good: Annotated[
        float,
        Field(
            title="Probability of a good outcome",
            description="How probable it is that the intervention will lead to a net positive result.",
            ge=0.0,
            le=1.0,
        ),
    ] = DEFAULT_PROB_GOOD
    prob_no_effect: Annotated[
        float,
        Field(
            title="Probability of having no effect",
            description="How probable it is that the intervention has no effect at all.",
            ge=0.0,
            le=1.0,
        ),
    ] = DEFAULT_PROB_NO_EFFECT
    intensity_bad: Annotated[
        float,
        Field(
            title="Intensity of the possible harm from the intervention",
            description=(
                "Estimated net bad effect that can be caused by the intervention (e.g., through dual-use research), "
                + "expressed as a proportion of the intervention's intended effect."
            ),
            ge=0.0,
        ),
    ] = DEFAULT_INTENSITY_BAD
    effect_on_xrisk: Annotated[
        SomeDistribution,
        Field(
            title="Effect on existential risks",
            description="The proportional effect of the intervention on reducing existential risks.",
        ),
    ] = DEFAULT_EFFECT_ON_XRISK
    effect_on_catastrophic_risk: Annotated[
        SomeDistribution,
        Field(
            title="Effect on catastrophic risks",
            description="The proportional effect of the intervention on reducing catastrophic risks.",
        ),
    ] = DEFAULT_EFFECT_ON_CATASTROPHIC_RISK

    def __init__(self, **data):
        risk_type = data["risk_type"]
        name = data.pop("name", f"A generic {str(risk_type).title()} intervention")
        super().__init__(
            name=name,
            _estimator=self.glt_dalys_per_1000_estimator,
            **data,
        )

    def glt_dalys_per_1000_estimator(self) -> tuple[NDArray[np.float64], int]:
        healthy_life_yrs_saved, zeros = self.estimate_healthy_years_saved()

        if self.cost:
            megaproject_cost = sqw.sample(self.cost.get_distribution(), n=SIMULATIONS)
        else:
            megaproject_cost = self._project_cost_per_year_given_base_xrisk_impact_magnitude()
        glt_dalys_per_1000 = self._calc_megaproject_dalys_per_1000(healthy_life_yrs_saved, megaproject_cost)

        return glt_dalys_per_1000, zeros

    @inject_parameters
    def estimate_healthy_years_saved(self, params: LongTermParams) -> tuple[NDArray[np.float64], int]:
        # calculate xrisk event magnitudes, conditional on them happening while the intervention is effective
        dalys_conditional_on_xrisk_changed = self._estimate_conditional_impact_xrisk()

        # calculate the magnitude for the proportional number of non-extinction catastrophes
        prop_catastrophe_to_xrisk = params.catastrophe_extinction_risk_ratios[self.risk_type]
        num_catastrophe_events = len(dalys_conditional_on_xrisk_changed) * prop_catastrophe_to_xrisk
        dalys_conditional_on_catastrophe_changed = self._estimate_conditional_impact_catastrophe(
            num_events=num_catastrophe_events,
        )

        # adjust for some of them being caused, rather than prevented by the intervention
        adjusted_dalys_conditional_on_xrisk = self._adjust_results_for_backfiring(dalys_conditional_on_xrisk_changed)
        adjusted_dalys_conditional_on_catastrophe = self._adjust_results_for_backfiring(
            dalys_conditional_on_catastrophe_changed,
        )

        healthy_life_yrs_saved = np.concatenate(
            (
                adjusted_dalys_conditional_on_xrisk,
                adjusted_dalys_conditional_on_catastrophe,
            )
        )

        num_non_zero_results = len(healthy_life_yrs_saved)
        zeros = int(
            num_non_zero_results
            / (self._prop_simulations_xrisk_is_changed + self._prop_simulations_catastrophe_is_changed)
        )

        # fill with explicit zeros so that the result array has at least a number of elements == SIMULATIONS
        if len(healthy_life_yrs_saved) < SIMULATIONS:
            num_explicit_zeros = SIMULATIONS - len(healthy_life_yrs_saved)
            healthy_life_yrs_saved = np.concatenate((healthy_life_yrs_saved, np.zeros(num_explicit_zeros)))
            zeros -= num_explicit_zeros
        # resample and remove zeros if the result array has a number of elements > SIMULATIONS
        if len(healthy_life_yrs_saved) > SIMULATIONS:
            original_length = len(healthy_life_yrs_saved)
            healthy_life_yrs_saved = RNG.choice(healthy_life_yrs_saved, size=SIMULATIONS, replace=False)
            zeros = int(zeros * SIMULATIONS / original_length)

        return healthy_life_yrs_saved, zeros

    # ///////////////// Private Functions /////////////////

    def _default_name(self) -> str:
        return f"A generic {self.risk_type.value.title()} intervention"

    @cached_property
    def _years_risk_changed(self) -> NDArray[np.int64]:
        return sqw.sample(self.persistence.get_distribution(), n=SIMULATIONS).astype(int)

    @inject_parameters
    def _estimate_conditional_impact_xrisk(self, params: Parameters) -> NDArray[np.float64]:
        """Estimate the amount of DALYs averted in each sample, provided that a potential extinction event happens
        while the effects of the intervention persist, it is of the type targeted, and the intervention is effective in
        protecting against it."""
        impact_method = params.impact_method.get_impact_method()

        distribution_of_years_to_extinction = risk_calculator.get_distribution_of_years_to_extinction()
        years_extinction_delayed = years_credit_calculator.sample_years_credit(
            distribution_of_years_to_extinction,
            np.ones(SIMULATIONS),
            num_years_intervention_effective=self._years_risk_changed,
        )
        trimmed_years_extinction_delayed = impact_method.trim_to_max_year(years_extinction_delayed)
        total_life_years_lost = population.get_total_life_years_until(trimmed_years_extinction_delayed)

        return total_life_years_lost[total_life_years_lost != 0]

    @inject_parameters
    def _estimate_conditional_impact_catastrophe(
        self,
        params: LongTermParams,
        num_events: int = SIMULATIONS,
    ) -> NDArray[np.float64]:
        """Estimate the amount of DALYs averted in each sample, provided that a potential catastrophic event happens
        while the effects of the intervention persist, it is of the type targeted, and the intervention is effective in
        protecting against it."""
        proportion_dead = sqw.sample(
            params.catastrophe_intensities[self.risk_type].get_distribution(),
            n=num_events,
        )
        people_dead = WORLD_POPULATION_NOW * proportion_dead
        return population.calculate_life_years_lost(people_dead)

    @cached_property
    def _prop_simulations_xrisk_is_changed(self) -> float:
        """Estimates in which proportion of simulations the intervention should have an effect (either causing or
        preventing) a potential existential risk event."""
        # probability of an extinction event caused by this risk during the period when this intervention's effects
        # persist
        risk_type_extinction_risk = risk_calculator.get_cumulative_risk_over_years_by_type(
            self.risk_type,
            self._years_risk_changed,
        )

        # probability of the intervention preventing an extinction event, conditional on a potential extinction event of
        # this type happening while the effects of the intervention persist
        prob_effect_xrisk = (1 - self.prob_no_effect) * sqw.sample(
            self.effect_on_xrisk.get_distribution(),
            n=SIMULATIONS,
        )

        # probability of a potential extinction event of this type happening while the intervention persists AND it
        # being successful in preventing the risk
        prop_has_effect_xrisk = np.mean(risk_type_extinction_risk * prob_effect_xrisk)

        return prop_has_effect_xrisk

    @cached_property
    def _prop_simulations_catastrophe_is_changed(self) -> float:
        """Estimates in which proportion of simulations the intervention should have an effect (either causing or
        preventing) a potential catastrophic event."""
        # probability of a catastrophic event caused by this risk during the period when this intervention's effects
        # persist
        risk_type_catastrophe_risk = risk_calculator.get_cumulative_catastrophe_risk(
            risk_type=self.risk_type,
            num_years=self._years_risk_changed,
        )

        # probability of the intervention preventing a catastrophic event, conditional on a potential catastrophe of
        # this type happening while the effects of the intervention persist
        prob_effect_catastrophe = (1 - self.prob_no_effect) * sqw.sample(
            self.effect_on_catastrophic_risk.get_distribution(),
            n=SIMULATIONS,
        )

        # probability of a potential catastrophic event of this type happening while the intervention persists AND it
        # being successful in preventing the risk
        prop_has_effect_catastrophe = np.mean(risk_type_catastrophe_risk * prob_effect_catastrophe)

        return prop_has_effect_catastrophe

    def _adjust_results_for_backfiring(self, impact_results: NDArray[np.float64]) -> NDArray[np.float64]:
        prop_bad_results = (
            (1 - self.prob_good) * self.intensity_bad / (self.prob_good + ((1 - self.prob_good) * self.intensity_bad))
        )

        are_bad_results = sqw.sample(
            sq.discrete({0: 1 - prop_bad_results, 1: prop_bad_results}),
            n=len(impact_results),
        ).astype(bool)
        return np.where(are_bad_results, -impact_results, impact_results)

    @cached_property
    def _intensity_modifiers(self) -> NDArray[np.float64]:
        ## 50/50 as to whether a project is net good or bad, conditioning on having an impact at all
        bernoulli = sqw.sample(sq.discrete({1: self.prob_good, 0: 1 - self.prob_good}), n=SIMULATIONS)
        # set intensity to intensity_bad if bernoulli result is 0
        intensity_modifiers = np.where(bernoulli == 0, self.intensity_bad * -1, 1)

        return intensity_modifiers

    @cached_property
    def _base_xrisk_impact_magnitude(self) -> NDArray[np.float64]:
        return np.abs(
            self._intensity_modifiers
            * (1 - self.prob_no_effect)
            * sqw.sample(self.effect_on_xrisk.get_distribution(), n=SIMULATIONS),
        )

    def _project_cost_per_year_given_base_xrisk_impact_magnitude(self) -> NDArray[np.float64]:
        """We're basing cost off of a function of base_xrisk_impact_magnitude (as opposed to proportion_risk_reduced)
        in order to be able to model a cost curve without adding a spurious correlation between cost and OUTCOME_SHAPE
        later in the process. (Such a correlation could dominate all other factors, making results not useful; see
        https://github.com/rethinkpriorities/cross-cause-model/issues/28)
        """
        mu = (
            (self._base_xrisk_impact_magnitude / 0.005)
            * 10**13
            * np.exp(-13 * (1 - self._base_xrisk_impact_magnitude))
        )
        moe = mu / 3

        # This should produce something in the ballpark of
        # normal distribution with mean mu[i], sd=moe[i] / 2, clipped at 5M and 100B
        # means and std are very similar to sampling separately with each mean and std, but clipping is only approximate
        # We take a normal distribution and stretch it to different amounts
        # as if its mean were values in base_xrisk_impact array
        sampled_deviations_from_mean = sqw.sample(sq.norm(mean=0, sd=1), n=len(self._base_xrisk_impact_magnitude))
        rescaled_deviations = sampled_deviations_from_mean * moe
        # Apply rescaled deviations to rescaled means
        cost_per_year = rescaled_deviations + mu
        cost_per_year[cost_per_year < 5 * M] = 5 * M
        cost_per_year[cost_per_year > 100 * B] = 100 * B

        return cost_per_year

    @staticmethod
    def _calc_megaproject_dalys_per_1000(
        healthy_years_saved_per_project: NDArray[np.float64],
        cost_per_megaproject: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        megaproject_dalys_per_1000 = 1000 * healthy_years_saved_per_project / cost_per_megaproject

        return megaproject_dalys_per_1000
