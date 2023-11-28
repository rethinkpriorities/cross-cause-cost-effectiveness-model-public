import numpy as np

from ccm.base_parameters import FrozenDict
from ccm.contexts import using_parameters
from ccm.interventions.animal.animal_intervention_params import AnimalInterventionParams
from ccm.interventions.animal.animal_interventions import DEFAULT_SHRIMP_PARAMS, AnimalIntervention
from ccm.parameters import Parameters
from ccm.utility.models import ConstantDistributionSpec
from ccm.world.animals import Animal
from ccm.world.moral_weight_params import MoralWeightsParams


def test_more_animal_years_more_cost_effective():
    with using_parameters(
        Parameters(
            animal_intervention_params=AnimalInterventionParams(
                num_animals_born_per_year=FrozenDict(
                    {
                        Animal.SHRIMP: ConstantDistributionSpec(
                            type="constant", distribution="constant", value=10**9
                        ),
                    }
                )
            ),
        )
    ):
        intervention_small_population = AnimalIntervention(
            animal=Animal.SHRIMP,
            **DEFAULT_SHRIMP_PARAMS,
        )
        cost_effectiveness_small_population = np.mean(intervention_small_population.animal_dalys_per_1000_estimator())
    with using_parameters(
        Parameters(
            animal_intervention_params=AnimalInterventionParams(
                num_animals_born_per_year=FrozenDict(
                    {
                        Animal.SHRIMP: ConstantDistributionSpec(
                            type="constant", distribution="constant", value=10**12
                        ),
                    }
                ),
            ),
        )
    ):
        intervention_big_population = AnimalIntervention(
            animal=Animal.SHRIMP,
            **DEFAULT_SHRIMP_PARAMS,
        )
        cost_effectiveness_big_population = np.mean(intervention_big_population.animal_dalys_per_1000_estimator())

    assert cost_effectiveness_big_population > cost_effectiveness_small_population, (
        "An intervention that mitigates suffering supposing a big population should be more cost-effective than one "
        "the same intervention if you suppose a small population"
    )


def test_higher_mw_more_cost_effective():
    with using_parameters(
        Parameters(
            animal_intervention_params=AnimalInterventionParams(
                moral_weight_params=MoralWeightsParams(
                    override_type="All moral weight calculations",
                    moral_weights_override=FrozenDict(
                        {
                            Animal.SHRIMP: ConstantDistributionSpec(
                                type="constant",
                                distribution="constant",
                                value=0.01,
                            ),
                        },
                    ),
                )
            )
        )
    ):
        intervention_low_mw = AnimalIntervention(
            animal=Animal.SHRIMP,
            **DEFAULT_SHRIMP_PARAMS,
        )
        cost_effectiveness_low_mw = np.mean(intervention_low_mw.animal_dalys_per_1000_estimator())
    with using_parameters(
        Parameters(
            animal_intervention_params=AnimalInterventionParams(
                moral_weight_params=MoralWeightsParams(
                    override_type="All moral weight calculations",
                    moral_weights_override=FrozenDict(
                        {
                            Animal.SHRIMP: ConstantDistributionSpec(
                                type="constant",
                                distribution="constant",
                                value=0.5,
                            ),
                        },
                    ),
                )
            )
        )
    ):
        intervention_high_mw = AnimalIntervention(
            animal=Animal.SHRIMP,
            **DEFAULT_SHRIMP_PARAMS,
        )
        cost_effectiveness_high_mw = np.mean(intervention_high_mw.animal_dalys_per_1000_estimator())

    assert cost_effectiveness_high_mw > cost_effectiveness_low_mw, (
        "An intervention that mitigates suffering supposing a high moral value should be more cost-effective than one "
        "the same intervention if you suppose a low moral value"
    )
