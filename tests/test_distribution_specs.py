import pytest
from squigglepy import DiscreteDistribution

from ccm.utility.models import CategoricalDistributionSpec


def test_categorical_dist():
    x_spec = CategoricalDistributionSpec(
        type="categorical",
        distribution="categorical",
        items=[
            (0.5, 3),
            (0.5, 4),
        ],
    )
    x_dist = x_spec.to_sq()
    assert isinstance(x_dist, DiscreteDistribution)
    assert all(x in [3, 4] for x in x_dist @ 10)
    assert x_dist.items[0][0] == 0.5
    assert x_dist.items[1][0] == 0.5
    with pytest.raises(ValueError, match="must sum to 1"):
        CategoricalDistributionSpec(
            type="categorical",
            distribution="categorical",
            items=[
                (0.5, 3),
                (0.5, 4),
                (0.5, 5),
            ],
        )
    assert CategoricalDistributionSpec.from_distribution(x_dist).items == x_spec.items
