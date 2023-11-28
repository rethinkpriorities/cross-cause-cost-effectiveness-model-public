"""
Premises and simulations about Animal Welfare Interventions.
"""
from inspect import cleandoc
from typing import Annotated, Literal

import numpy as np
import squigglepy as sq
from numpy.typing import NDArray
from pydantic import AfterValidator, Field
from squigglepy.numbers import K, M

import ccm.config as config
import ccm.utility.squigglepy_wrapper as sqw
from ccm.contexts import inject_parameters
from ccm.interventions.animal.animal_intervention_params import INTERVENABLE_ANIMALS, AnimalInterventionParams
from ccm.interventions.intervention import EstimatorIntervention
from ccm.utility.models import BetaDistributionSpec, ConfidenceDistributionSpec, SomeDistribution
from ccm.utility.moral_weight_adapter import moral_weight_adjustor
from ccm.world.animals import Animal

SIMULATIONS = config.get_simulations()
HOURS_PER_YEAR = 24 * 365.25


# Default interventions

DEFAULT_BSF_PARAMS = {
    "prop_affected": ConfidenceDistributionSpec.lognorm(5 * 10**-5, 10**-3, lclip=10**-6, rclip=5 * 10**-3),
    # 22-24 days spent in the larval stage, according to Tomberli, Sheppard & Joyce (2002);
    # assumes no suffering during the egg stage, and that larvaes are processed after that
    # SEE: https://doi.org/10.1603/0013-8746(2002)095[0379:SLHTOB]2.0.CO;2
    # assumes persisent suffering is as bad as 1/20 to 1/5 a DALY.
    "hours_spent_suffering": ConfidenceDistributionSpec.norm(24 * 22 / 20, 24 * 24 / 5, lclip=20, rclip=26),
    "prop_suffering_reduced": BetaDistributionSpec.create(9, 4),
    "prob_success": BetaDistributionSpec.create(3, 3),
    "cost_of_intervention": ConfidenceDistributionSpec.lognorm(150 * K, 1 * M, lclip=100 * K, rclip=1 * M),
    "persistence": ConfidenceDistributionSpec.lognorm(5, 20, lclip=1, credibility=90),
}

DEFAULT_CARP_PARAMS = {
    "prop_affected": ConfidenceDistributionSpec.lognorm(5 * 10**-5, 10**-3, lclip=10**-6, rclip=5 * 10**-3),
    # centered on a culture cycle of 383 days from hatching to final harvest
    # SEE: https://doi.org/10.1186/s12863-015-0256-2
    # assumes suffering relevant to the intervention occurs throughout this whole period (e.g., pound euthrophization)
    # assumes persisent suffering is as bad as 1/20 to 1/5 a DALY.
    "hours_spent_suffering": ConfidenceDistributionSpec.norm(24 * 345 / 20, 24 * 421 / 5, lclip=300, rclip=500),
    "prop_suffering_reduced": BetaDistributionSpec.create(1.6, 19),
    "prob_success": BetaDistributionSpec.create(3, 3),
    "cost_of_intervention": ConfidenceDistributionSpec.lognorm(150 * K, 1 * M, lclip=100 * K, rclip=1 * M),
    "persistence": ConfidenceDistributionSpec.lognorm(5, 20, lclip=1, credibility=90),
}

DEFAULT_CHICKEN_PARAMS = {
    "suffering_years_per_dollar_override": ConfidenceDistributionSpec.norm(
        lo=0.16 * K,
        hi=3.63 * K,
        lclip=(0.016 * K),
        rclip=(100 * K),
        credibility=90,
    ),
    "use_override": True,
}

DEFAULT_SHRIMP_PARAMS = {
    "prop_affected": ConfidenceDistributionSpec.lognorm(5 * 10**-5, 10**-3, lclip=10**-6, rclip=5 * 10**-3),
    # slaughter-related suffering. See shrimp accessory model (accessory_models/shrimp.py)
    "hours_spent_suffering": ConfidenceDistributionSpec.norm(0.0072, 0.62, lclip=0, rclip=0.95),
    # Significant reduction in hourly suffering.
    "prop_suffering_reduced": BetaDistributionSpec.create(9, 4),
    #  probability of intervention success, entirely fabricated
    "prob_success": BetaDistributionSpec.create(3, 3),
    "cost_of_intervention": ConfidenceDistributionSpec.lognorm(150 * K, 1 * M, lclip=100 * K, rclip=1 * M),
    "persistence": ConfidenceDistributionSpec.lognorm(5, 20, lclip=1, credibility=90),
}


# carp and bsf are currently equal to shrimp parameters.
# prop shrimp affected by intervention based on example of Aaron Boddy's example of 100M shrimp out of
#   400B being affected by recent Honduras producer success.
DEFAULT_ANIMAL_PARAMS = {
    Animal.BSF: DEFAULT_BSF_PARAMS,
    Animal.CARP: DEFAULT_CARP_PARAMS,
    Animal.CHICKEN: DEFAULT_CHICKEN_PARAMS,
    Animal.SHRIMP: DEFAULT_SHRIMP_PARAMS,
}

# Validators


def validate_animal(animal: Animal) -> Animal:
    assert animal in INTERVENABLE_ANIMALS
    return animal


# Set up animal intervention class


class AnimalIntervention(EstimatorIntervention, frozen=True):
    type: Literal["animal-welfare"] = "animal-welfare"
    version: Literal["1"] = "1"
    area: Literal["animal-welfare"] = "animal-welfare"
    animal: Annotated[
        Animal,
        Field(
            title="Target animal species",
            description="Which species the intervention is tailored for.",
        ),
        AfterValidator(validate_animal),
    ] = Animal.SHRIMP
    use_override: Annotated[
        bool,
        Field(
            title="Should override cost-effectiveness?",
            description="Directly specify a distribution of the years of suffering averted per $1000 rather than model "
            "that impact through other parameter choices.",
        ),
    ] = False
    prop_affected: Annotated[
        SomeDistribution,
        Field(
            title="Proportion affected",
            description="Proportion of animals affected by intervention",
        ),
    ] = ConfidenceDistributionSpec.lognorm(5 * 10**-5, 10**-3, lclip=10**-6, rclip=5 * 10**-3)
    hours_spent_suffering: Annotated[
        SomeDistribution,
        Field(
            title="Number of hours spent suffering",
            description=(
                "A confidence interval estimate for the absolute amount of hours an average individual of the target "
                "species will spend in pain during its lifetime. This should be restricted *only* to the type of "
                "suffering that is addressable through the intervention."
            ),
        ),
    ] = ConfidenceDistributionSpec.norm(0.0072 / 24 / 365, 0.62 / 24 / 365, lclip=0, rclip=0.95)
    prop_suffering_reduced: Annotated[
        SomeDistribution,
        Field(
            title="Proportion of suffering reduced",
            description="The proportion of an animal's suffering that is reduced by the intervention.",
        ),
    ] = ConfidenceDistributionSpec.lognorm(0.5, 0.9, lclip=0.1, rclip=0.99)
    prob_success: Annotated[
        SomeDistribution,
        Field(
            title="Probability of success",
            description="The probability that the animal welfare intervention succeeds.",
        ),
    ] = ConfidenceDistributionSpec.lognorm(0.2, 0.8, lclip=0.05, rclip=0.95)
    cost_of_intervention: Annotated[
        SomeDistribution,
        Field(
            title="Cost of intervention",
            description="How many US dollars does it cost to implement the intervention.",
        ),
    ] = ConfidenceDistributionSpec.lognorm(150 * K, 1 * M, lclip=100 * K, rclip=1 * M)
    persistence: Annotated[
        SomeDistribution,
        Field(
            title="Persistence",
            description="How long the intervention's effects will last, in years.",
        ),
    ] = ConfidenceDistributionSpec.lognorm(
        5,
        20,
        lclip=1,
        credibility=90,
    )

    # Laura Duffy estimtes for corp campaigns suffering years prevented per dollar from draft report on ballot
    # initiatives
    # Note: the actual distribution for this isn't normal, so could recreate this to get the real distribution
    suffering_years_per_dollar_override: Annotated[
        SomeDistribution,
        Field(
            title="Suffering-years per dollar override",
            description=(
                "If set, this value determines suffering-years averted per dollar, overriding other calculations."
            ),
        ),
    ] = ConfidenceDistributionSpec.norm(0.16 * K, 3.63 * K, lclip=(0.016 * K), credibility=90)

    def __init__(self, **data):
        target_species = Animal(data.get("animal", Animal.SHRIMP))
        name = data.pop("name", f"A generic {target_species.value.title()} welfare intervention")
        description = data.pop("description", None)
        if description:
            description = cleandoc(description)

        super().__init__(
            name=name,
            description=description,
            _estimator=self.animal_dalys_per_1000_estimator,
            **data,
        )

    def animal_dalys_per_1000_estimator(self) -> NDArray[np.float64]:
        if self.use_override:
            animal_yrs_per_1000 = sqw.sample(self.suffering_years_per_dollar_override.get_distribution(), n=SIMULATIONS)
        else:
            animal_yrs_per_1000 = self._expected_years_suffering_per_dollar() * 1000

        adjusted_welfare_range = moral_weight_adjustor(self.animal)

        # multiply the cost by the moral weight array to get an array of costs
        human_equivalent_dalys_per_1000 = animal_yrs_per_1000 * adjusted_welfare_range
        return human_equivalent_dalys_per_1000

    # ///////////////// Private Functions /////////////////

    @property
    def _successes(self) -> NDArray[np.bool_]:
        prob_success = sqw.sample(self.prob_success.get_distribution(), n=SIMULATIONS)
        random_results = sqw.sample(sq.uniform(0, 1), n=SIMULATIONS)
        successes = prob_success >= random_results
        return successes

    @inject_parameters
    def _expected_years_suffering_per_dollar(self, params: AnimalInterventionParams) -> NDArray[np.float64]:
        hours_spent_suffering = sqw.sample(self.hours_spent_suffering.get_distribution(), n=SIMULATIONS)
        prop_suffering_reduced = sqw.sample(self.prop_suffering_reduced.get_distribution(), n=SIMULATIONS)
        prop_affected = sqw.sample(self.prop_affected.get_distribution(), n=SIMULATIONS)
        intervention_effect_persistence = sqw.sample(self.persistence.get_distribution(), n=SIMULATIONS)
        cost_of_intervention = sqw.sample(self.cost_of_intervention.get_distribution(), n=SIMULATIONS)
        num_animals_born_per_year = sqw.sample(
            params.num_animals_born_per_year[self.animal].get_distribution(),
            n=SIMULATIONS,
        )

        # Years suffering averted, if the intervention is successful
        animal_yrs_suffering_averted_annually = (
            num_animals_born_per_year
            * prop_affected
            * (hours_spent_suffering / HOURS_PER_YEAR)
            * prop_suffering_reduced
        ) * self._successes.astype(float)

        # Expected years of suffering averted per dollar spent
        expected_years_suffering_per_dollar = (
            animal_yrs_suffering_averted_annually * intervention_effect_persistence / cost_of_intervention
        )

        return expected_years_suffering_per_dollar
