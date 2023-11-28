import numpy as np
import pytest
from pydantic import ValidationError
from squigglepy import K, M

from ccm.base_parameters import FrozenDict
from ccm.config import SIMULATIONS
from ccm.contexts import using_parameters
from ccm.interventions.animal.animal_intervention_params import AnimalInterventionParams
from ccm.interventions.animal.animal_interventions import AnimalIntervention
from ccm.parameters import Parameters
from ccm.utility.models import ConstantDistributionSpec
from ccm.world.animals import Animal
from ccm.world.moral_weight_params import MoralWeightsParams


def test_animal_dalys_per_1000_estimator_unsupported_animal():
    with pytest.raises(ValidationError, match="HUMAN"):
        AnimalIntervention(animal=Animal.HUMAN)


def test_more_affected_more_cost_effective():
    with using_parameters(Parameters()):
        intervention_low_prop_affected = AnimalIntervention(
            animal=Animal.SHRIMP,
            prop_affected=ConstantDistributionSpec(type="constant", distribution="constant", value=0.01),
        )
        intervention_high_prop_affected = AnimalIntervention(
            animal=Animal.SHRIMP,
            prop_affected=ConstantDistributionSpec(type="constant", distribution="constant", value=0.6),
        )

    assert np.mean(intervention_low_prop_affected.animal_dalys_per_1000_estimator()) < np.mean(
        intervention_high_prop_affected.animal_dalys_per_1000_estimator()
    ), "A higher `prop_affected` should make an intervention more cost-effective, not less!"


def test_more_persistence_more_cost_effective():
    with using_parameters(Parameters()):
        intervention_low_persistence = AnimalIntervention(
            animal=Animal.SHRIMP,
            persistence=ConstantDistributionSpec(type="constant", distribution="constant", value=1),
        )
        intervention_high_persistence = AnimalIntervention(
            animal=Animal.SHRIMP,
            persistence=ConstantDistributionSpec(type="constant", distribution="constant", value=5),
        )

    mean_low = np.mean(intervention_low_persistence.animal_dalys_per_1000_estimator())
    mean_high = np.mean(intervention_high_persistence.animal_dalys_per_1000_estimator())
    assert mean_low < mean_high, "A higher `persistence` should make an intervention more cost-effective, not less!"

    assert mean_low * 3.5 < mean_high, "5x persistence => 5x DALYs per 1000"

    assert mean_low * 10 > mean_high, "5x duration => 5x DALYs per 1000"


def test_more_life_suffering_more_cost_effective():
    with using_parameters(Parameters()):
        intervention_low_hours_spent_suffering = AnimalIntervention(
            animal=Animal.SHRIMP,
            hours_spent_suffering=ConstantDistributionSpec(type="constant", distribution="constant", value=0.01),
        )
        intervention_high_hours_spent_suffering = AnimalIntervention(
            animal=Animal.SHRIMP,
            hours_spent_suffering=ConstantDistributionSpec(type="constant", distribution="constant", value=0.6),
        )

    assert np.mean(intervention_low_hours_spent_suffering.animal_dalys_per_1000_estimator()) < np.mean(
        intervention_high_hours_spent_suffering.animal_dalys_per_1000_estimator()
    ), "A higher `hours_spent_suffering` should make an intervention more cost-effective, not less!"


def test_more_suffering_reduced_more_cost_effective():
    with using_parameters(Parameters()):
        intervention_low_prop_suffering_reduced = AnimalIntervention(
            animal=Animal.SHRIMP,
            prop_suffering_reduced=ConstantDistributionSpec(type="constant", distribution="constant", value=0.01),
        )
        intervention_high_prop_suffering_reduced = AnimalIntervention(
            animal=Animal.SHRIMP,
            prop_suffering_reduced=ConstantDistributionSpec(type="constant", distribution="constant", value=0.6),
        )

    assert np.mean(intervention_low_prop_suffering_reduced.animal_dalys_per_1000_estimator()) < np.mean(
        intervention_high_prop_suffering_reduced.animal_dalys_per_1000_estimator()
    ), "A higher `prop_suffering_reduced` should make an intervention more cost-effective, not less!"


def test_more_prob_success_more_cost_effective():
    with using_parameters(Parameters()):
        intervention_low_prob_success = AnimalIntervention(
            animal=Animal.SHRIMP,
            prob_success=ConstantDistributionSpec(type="constant", distribution="constant", value=0.01),
        )
        intervention_high_prob_success = AnimalIntervention(
            animal=Animal.SHRIMP,
            prob_success=ConstantDistributionSpec(type="constant", distribution="constant", value=0.6),
        )

    assert np.mean(intervention_low_prob_success.animal_dalys_per_1000_estimator()) < np.mean(
        intervention_high_prob_success.animal_dalys_per_1000_estimator()
    ), "A higher `prob_success` should make an intervention more cost-effective, not less!"


def test_lower_cost_more_cost_effective():
    with using_parameters(Parameters()):
        intervention_low_cost = AnimalIntervention(
            animal=Animal.SHRIMP,
            cost_of_intervention=ConstantDistributionSpec(type="constant", distribution="constant", value=10 * K),
        )
        intervention_high_cost = AnimalIntervention(
            animal=Animal.SHRIMP,
            cost_of_intervention=ConstantDistributionSpec(type="constant", distribution="constant", value=1 * M),
        )

    assert np.mean(intervention_low_cost.animal_dalys_per_1000_estimator()) > np.mean(
        intervention_high_cost.animal_dalys_per_1000_estimator()
    ), "A lower `cost` should make an intervention more cost-effective, not less!"


def test_cost_effectiveness_override():
    moral_weight = 0.05
    cost_effectiveness = 10.0
    cost_effectiveness_override = ConstantDistributionSpec(
        type="constant",
        distribution="constant",
        value=cost_effectiveness,
    )
    expected_dalys_per_1000 = np.array([cost_effectiveness * moral_weight] * SIMULATIONS)
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
                                value=moral_weight,
                            ),
                        },
                    ),
                )
            )
        )
    ):
        intervention_with_override = AnimalIntervention(
            animal=Animal.SHRIMP,
            suffering_years_per_dollar_override=cost_effectiveness_override,
            use_override=True,
        )
        np.testing.assert_array_equal(
            intervention_with_override.animal_dalys_per_1000_estimator(),
            expected_dalys_per_1000,
        )


def test_successes():
    prob_success = 0.5
    params = Parameters()

    with using_parameters(params):
        intervention = AnimalIntervention(
            animal=Animal.SHRIMP,
            prob_success=ConstantDistributionSpec(type="constant", distribution="constant", value=prob_success),
        )
        successes = intervention._successes.astype(float)
        assert np.mean(successes) > 0.98 * prob_success
        assert np.mean(successes) < 1.02 * prob_success
