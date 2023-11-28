"""
Adapter for calling MoralWeightEstimator from CCM model. Also handles caching.
Shouldn't need this anymore after we add dependency injection.
"""

import numpy as np
import squigglepy as sq
from numpy.typing import NDArray

import ccm.config as config
import ccm.utility.squigglepy_wrapper as sqw
from ccm.contexts import inject_parameters
from ccm.interventions.animal.animal_intervention_params import INTERVENABLE_ANIMALS, AnimalInterventionParams
from ccm.world.animals import Animal

SIMULATIONS = config.SIMULATIONS

# Capacity Parameters from Bob Fischer
# Each key is the name of a approach to assessing relative moral weight
# Each value is a quantitative comparison according to that model, relative to human beings
# These values aim at relative amount of moral weight *assuming* sentience -- doubts about sentience are not covered
# Source: https://docs.google.com/spreadsheets/d/18rUZW4hlNduqj3Zv3fDg0ceOKhAUVWkmbOoZzZn0aPE/edit#gid=1489233206
CONDITIONAL_WELFARE_CAPACITY_ESTIMATIONS_BY_MODEL = {
    Animal.CHICKEN: {
        "Neuron Count": 0.002,
        "Quantitative": 0.641,
        "Qualitative": 0.511,
        "Cubic": 0.160,
        "Higher-confidence Proxies": 0.165,
        "Qualitative-minus-social": 0.552,
        "Pleasure-and-pain-centric": 0.439,
        "Higher / Lower Pleasures": 0.274,
        "Just Noticeable Differences": 0.154,
        "Grouped Proxies": 0.923,
        "Undiluted Experience": 0.906,
        "Equality": 0.953,
    },
    Animal.SHRIMP: {
        "Neuron Count": 0.000001,
        "Quantitative": 1.069556,
        "Qualitative": 0.138313,
        "Cubic": 0.002304,
        "Higher-confidence Proxies": 0.005508,
        "Qualitative-minus-social": 0.190899,
        "Pleasure-and-pain-centric": 0.172632,
        "Higher / Lower Pleasures": 0.026919,
        "Just Noticeable Differences": 0.105806,
        "Grouped Proxies": 0.924127,
        "Undiluted Experience": 0.969091,
        "Equality": 1.093333,
    },
    Animal.CARP: {
        "Neuron Count": 0.0002,
        "Quantitative": 0.8761,
        "Qualitative": 0.3117,
        "Cubic": 0.0308,
        "Higher-confidence Proxies": 0.0541,
        "Qualitative-minus-social": 0.3436,
        "Pleasure-and-pain-centric": 0.3613,
        "Higher / Lower Pleasures": 0.0960,
        "Just Noticeable Differences": 0.1022,
        "Grouped Proxies": 0.9994,
        "Undiluted Experience": 1.3500,
        "Equality": 1.0560,
    },
    Animal.BSF: {
        "Neuron Count": 0.000004,
        "Quantitative": 1.404314,
        "Qualitative": 0.073735,
        "Cubic": 0.000932,
        "Higher-confidence Proxies": 0.003880,
        "Qualitative-minus-social": 0.142857,
        "Pleasure-and-pain-centric": 0.118421,
        "Higher / Lower Pleasures": 0.014583,
        "Just Noticeable Differences": 0.096774,
        "Grouped Proxies": 0.851190,
        "Undiluted Experience": 0.433884,
        "Equality": 1.000000,
    },
}


@inject_parameters
def get_sentience_estimates(params: AnimalInterventionParams, animal: Animal) -> NDArray[np.float64]:
    try:
        sentience_distribution = params.moral_weight_params.sentience_ranges[animal].get_distribution()
    except KeyError as err:
        raise ValueError(f"Unsupported animal input for get_sentience_estimates: {animal}") from err

    sentience_values = sqw.sample(sentience_distribution, n=SIMULATIONS)
    random_numbers = sqw.sample(sq.uniform(0, 1), n=SIMULATIONS)
    species_is_sentient = sentience_values >= random_numbers
    return species_is_sentient.astype(np.float64)


@inject_parameters
def get_capacity_for_welfare_estimates(params: AnimalInterventionParams, animal: Animal) -> NDArray[np.float64]:
    """
    Returns the welfare capacity of the given species, as provided by a parameter override or calculated from
    weighting various modelling approaches.
    """
    if params.moral_weight_params.override_type == "Only welfare capacities":
        try:
            return sqw.sample(
                params.moral_weight_params.welfare_capacities_override[animal].get_distribution(),
                n=SIMULATIONS,
            )
        except KeyError as err:
            raise ValueError(f"Unsupported animal input for get_welfare_capacity: {animal}") from err

    try:
        welfare_capacities_by_model = CONDITIONAL_WELFARE_CAPACITY_ESTIMATIONS_BY_MODEL[animal]
    except KeyError as err:
        raise ValueError(f"Unsupported animal input for get_welfare_capacity: {animal}") from err

    # generate a distribution where the probability of any given welfare capacity value being sampled equals the
    # relative weight of the model that generated such estimate
    welfare_capacities_x_weight: dict[float, float] = {}
    for model in welfare_capacities_by_model:
        model_weight = params.moral_weight_params.weights_for_models[model]
        welfare_capacity_according_to_model = welfare_capacities_by_model[model]
        welfare_capacities_x_weight[welfare_capacity_according_to_model] = (
            welfare_capacities_x_weight.get(
                welfare_capacity_according_to_model,
                0,
            )
            + model_weight
        )
    welfare_capacities_distribution = sq.discrete(welfare_capacities_x_weight)

    return sqw.sample(welfare_capacities_distribution, n=SIMULATIONS)


@inject_parameters
def moral_weight_adjustor(params: AnimalInterventionParams, animal: Animal) -> NDArray[np.float64]:
    """Combines sampled capacity welfare conditional on sentience with estimated probabilities of sentience"""
    if params.moral_weight_params.override_type == "All moral weight calculations":
        try:
            return sqw.sample(
                params.moral_weight_params.moral_weights_override[animal].get_distribution(),
                n=SIMULATIONS,
            )
        except KeyError as err:
            raise ValueError(f"Unsupported animal input for moral_weight_adjustor: {animal}") from err

    sentience_estimates = get_sentience_estimates(animal)
    capacity_for_welfare_estimates = get_capacity_for_welfare_estimates(animal)
    return capacity_for_welfare_estimates * sentience_estimates


def get_relative_moral_weights() -> dict[Animal, dict]:
    moral_weights = {}
    for animal in INTERVENABLE_ANIMALS:
        moral_weights[animal] = moral_weight_adjustor(animal)

    relative_moral_weights = {}

    for idx, animal in enumerate(moral_weights.keys()):
        relative_moral_weights[animal] = {}
        other_animals = list(moral_weights.keys())[:idx] + list(moral_weights.keys())[idx + 1 :]
        for other_animal in other_animals:
            relative_moral_weights[animal][other_animal] = moral_weights[animal] / moral_weights[other_animal]

    return relative_moral_weights
