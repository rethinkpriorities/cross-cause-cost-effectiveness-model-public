import numpy as np
import pytest

import ccm.config as config
import ccm.utility.moral_weight_adapter as mw
from ccm.base_parameters import FrozenDict
from ccm.contexts import using_parameters
from ccm.interventions.animal.animal_intervention_params import AnimalInterventionParams
from ccm.parameters import Parameters
from ccm.utility.models import ConstantDistributionSpec
from ccm.world.animals import Animal, get_animal_by_name
from ccm.world.moral_weight_params import MoralWeightsParams

SIMULATIONS = config.SIMULATIONS


def test_sentience_estimates():
    input_sentience = 0.1
    with using_parameters(
        Parameters(
            animal_intervention_params=AnimalInterventionParams(
                moral_weight_params=MoralWeightsParams(
                    sentience_ranges=FrozenDict(
                        {
                            Animal.SHRIMP: ConstantDistributionSpec(
                                type="constant",
                                distribution="constant",
                                value=input_sentience,
                            ),
                        },
                    )
                ),
            )
        )
    ):
        returned_sentience_estimates = mw.get_sentience_estimates(Animal.SHRIMP)
        assert isinstance(returned_sentience_estimates, np.ndarray), "Returned object is not a numpy array"
        assert len(returned_sentience_estimates) == SIMULATIONS, "Returned object has the wrong length"
        np.testing.assert_approx_equal(
            actual=np.mean(returned_sentience_estimates),
            desired=input_sentience,
            significant=1,
            err_msg="Returned object includes unexpected values",
        )


def test_get_capacity_for_welfare_estimates():
    input_model_weights = FrozenDict(
        {
            "Neuron Count": 1.0,
            "Quantitative": 0.0,
            "Qualitative": 0.0,
            "Cubic": 0.0,
            "Higher-confidence Proxies": 0.0,
            "Qualitative-minus-social": 0.0,
            "Pleasure-and-pain-centric": 0.0,
            "Higher / Lower Pleasures": 0.0,
            "Just Noticeable Differences": 0.0,
            "Grouped Proxies": 0.0,
            "Undiluted Experience": 0.0,
            "Equality": 0.0,
        }
    )
    expected_welfare_capacity = mw.CONDITIONAL_WELFARE_CAPACITY_ESTIMATIONS_BY_MODEL[Animal.SHRIMP]["Neuron Count"]
    with using_parameters(
        Parameters(
            animal_intervention_params=AnimalInterventionParams(
                moral_weight_params=MoralWeightsParams(
                    override_type="No override", weights_for_models=input_model_weights
                ),
            )
        )
    ):
        returned_walfare_capacity = mw.get_capacity_for_welfare_estimates(Animal.SHRIMP)
        assert isinstance(returned_walfare_capacity, np.ndarray), "Returned object is not a numpy array"
        assert len(returned_walfare_capacity) == SIMULATIONS, "Returned object has the wrong length"
        assert np.all(
            returned_walfare_capacity == expected_welfare_capacity,
        ), "Returned object includes unexpected values"


def test_get_capacity_for_welfare_estimates_override():
    input_welfare_capacity = 0.1
    with using_parameters(
        Parameters(
            animal_intervention_params=AnimalInterventionParams(
                moral_weight_params=MoralWeightsParams(
                    override_type="Only welfare capacities",
                    welfare_capacities_override=FrozenDict(
                        {
                            Animal.SHRIMP: ConstantDistributionSpec(
                                type="constant",
                                distribution="constant",
                                value=input_welfare_capacity,
                            ),
                        },
                    ),
                ),
            ),
        )
    ):
        returned_walfare_capacity = mw.get_capacity_for_welfare_estimates(Animal.SHRIMP)
        assert isinstance(returned_walfare_capacity, np.ndarray), "Returned object is not a numpy array"
        assert len(returned_walfare_capacity) == SIMULATIONS, "Returned object has the wrong length"
        assert np.all(
            returned_walfare_capacity == input_welfare_capacity,
        ), "Returned object includes unexpected values"


def test_moral_weight_adjustor():
    input_sentience = 0.1
    input_model_weights = FrozenDict(
        {
            "Neuron Count": 1.0,
            "Quantitative": 0.0,
            "Qualitative": 0.0,
            "Cubic": 0.0,
            "Higher-confidence Proxies": 0.0,
            "Qualitative-minus-social": 0.0,
            "Pleasure-and-pain-centric": 0.0,
            "Higher / Lower Pleasures": 0.0,
            "Just Noticeable Differences": 0.0,
            "Grouped Proxies": 0.0,
            "Undiluted Experience": 0.0,
            "Equality": 0.0,
        }
    )
    expected_moral_weight = (
        input_sentience * mw.CONDITIONAL_WELFARE_CAPACITY_ESTIMATIONS_BY_MODEL[Animal.SHRIMP]["Neuron Count"]
    )
    with using_parameters(
        Parameters(
            animal_intervention_params=AnimalInterventionParams(
                moral_weight_params=MoralWeightsParams(
                    sentience_ranges=FrozenDict(
                        {
                            Animal.SHRIMP: ConstantDistributionSpec(
                                type="constant",
                                distribution="constant",
                                value=input_sentience,
                            ),
                        },
                    ),
                    override_type="No override",
                    weights_for_models=input_model_weights,
                ),
            ),
        )
    ):
        returned_moral_weight = mw.moral_weight_adjustor(Animal.SHRIMP)
        assert isinstance(returned_moral_weight, np.ndarray), "Returned object is not a numpy array"
        assert len(returned_moral_weight) == SIMULATIONS, "Returned object has the wrong length"
        np.testing.assert_approx_equal(
            actual=np.mean(returned_moral_weight),
            desired=expected_moral_weight,
            significant=1,
            err_msg="Returned object includes unexpected values",
        )


def test_moral_weight_adjustor_override():
    input_moral_weight = 0.01
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
                                value=input_moral_weight,
                            ),
                        },
                    ),
                ),
            ),
        )
    ):
        returned_moral_weight = mw.moral_weight_adjustor(Animal.SHRIMP)
        assert isinstance(returned_moral_weight, np.ndarray), "Returned object is not a numpy array"
        assert len(returned_moral_weight) == SIMULATIONS, "Returned object has the wrong length"
        assert np.all(returned_moral_weight == input_moral_weight), "Returned object includes unexpected values"


@pytest.mark.parametrize(
    argnames="func",
    argvalues=[mw.get_sentience_estimates, mw.get_capacity_for_welfare_estimates, mw.moral_weight_adjustor],
)
def test_invalid_animal(func):
    with using_parameters(Parameters()), pytest.raises(ValueError, match="Unsupported animal input"):
        func(Animal.HUMAN)


def test_get_relative_moral_weights(monkeypatch):
    chicken = get_animal_by_name("chicken")
    get_animal_by_name("human")
    bsf = get_animal_by_name("bsf")
    shrimp = get_animal_by_name("shrimp")
    carp = get_animal_by_name("carp")

    def mock_moral_weight_adjustor(arg):
        if arg == chicken:
            return np.array([10, 1])
        elif arg == carp:
            return np.array([8, 1])
        elif arg == shrimp:
            return np.array([4, 1])
        elif arg == bsf:
            return np.array([2, 1])

    monkeypatch.setattr(mw, "moral_weight_adjustor", mock_moral_weight_adjustor)

    result = mw.get_relative_moral_weights()
    assert result[chicken][shrimp][0] == 10 / 4
    assert result[chicken][carp][0] == 10 / 8
    assert result[chicken][bsf][0] == 10 / 2
    assert result[bsf][chicken][0] == 2 / 10
    assert result[carp][shrimp][0] == 8 / 4
    assert result[shrimp][bsf][0] == 4 / 2

    assert result[chicken][shrimp][1] == 1
    assert result[chicken][carp][1] == 1
    assert result[chicken][bsf][1] == 1
    assert result[chicken][bsf][1] == 1
