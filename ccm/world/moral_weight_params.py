from typing import Annotated, Literal

import numpy as np
from pydantic import AfterValidator, Field

from ccm.base_parameters import BaseParameters, FrozenDict
from ccm.utility.models import BetaDistributionSpec, ConfidenceDistributionSpec, SomeDistribution
from ccm.world.animals import Animal

# Model Weights -- e.g. probability assignments of model correctness -- from 12 models from Bob Fischer
# Source: https://docs.google.com/spreadsheets/d/18rUZW4hlNduqj3Zv3fDg0ceOKhAUVWkmbOoZzZn0aPE/edit#gid=1489233206
DEFAULT_MODEL_WEIGHTS: FrozenDict[str, float] = FrozenDict(
    {
        "Neuron Count": 0.01,
        "Quantitative": 0.05,
        "Qualitative": 0.05,
        "Cubic": 0.01,
        "Higher-confidence Proxies": 0.2,
        "Qualitative-minus-social": 0.05,
        "Pleasure-and-pain-centric": 0.2,
        "Higher / Lower Pleasures": 0.03,
        "Just Noticeable Differences": 0.2,
        "Grouped Proxies": 0.1,
        "Undiluted Experience": 0.05,
        "Equality": 0.05,
    }
)


# Based on the Probabilities of Sentience by RP's Moral Weights Project (High Value Proxies)
# SEE: https://docs.google.com/spreadsheets/d/1XxpVrFsfWajqjGyT0YoZjGBWKDciPCDEUhn2CtcTgbI/#gid=921940071&range=A1:E20
# These ranges determine the distribution we sample to generate sentienece estimates
# Sentience is assumed as a prerequisite for moral worth
# These are probabilities of any sentience, not estimates of degrees of sentience.
# Distribution types here are approximations based on how skewed are the mean and the median relative to the 5th and
# 95th percentiles
DEFAULT_SENTIENCE_RANGES: FrozenDict[Animal, SomeDistribution] = FrozenDict(
    {
        Animal.BSF: BetaDistributionSpec.create(3, 6),
        Animal.CARP: BetaDistributionSpec.create(17, 7),
        Animal.CHICKEN: BetaDistributionSpec.create(28, 5),
        # used data for Crabs, since the MWP did not provide this estimate for shrimps
        Animal.SHRIMP: BetaDistributionSpec.create(5, 6),
    }
)

# Based on publishd results: https://forum.effectivealtruism.org/s/y5n47MfgrKvTLE3pw/p/Qk3hd6PrFManj8K6o
# Lower bounds are tweaked from 0 to capture midpoints.
# Distribution types here are approximations based on how skewed are the mean and the median relative to the 5th and
# 95th percentiles
DEFAULT_WELFARE_CAPACITIES: FrozenDict[Animal, SomeDistribution] = FrozenDict(
    {
        Animal.BSF: ConfidenceDistributionSpec.lognorm(0.001, 0.196, lclip=0),
        Animal.CARP: ConfidenceDistributionSpec.lognorm(0.013, 0.568, lclip=0),
        Animal.CHICKEN: ConfidenceDistributionSpec.norm(0.002, 0.869, lclip=0),
        Animal.SHRIMP: ConfidenceDistributionSpec.lognorm(0.0008, 1.149, lclip=0),
    }
)

# Based on the Sentience-Adjusted Welfare Ranges by RP's Moral Weights Project (Mixture model w/ Neuron Counts)
# SEE: https://docs.google.com/spreadsheets/d/1SpbrcfmBoC50PTxlizF5HzBIq4p-17m3JduYXZCH2Og/#gid=83030782&range=A2:E13
# Distribution types here are approximations based on how skewed are the mean and the median relative to the 5th and
# 95th percentiles
DEFAULT_MORAL_WEIGHTS: FrozenDict[Animal, SomeDistribution] = FrozenDict(
    {
        Animal.BSF: ConfidenceDistributionSpec.norm(0.01, 0.215, lclip=0),
        Animal.CARP: ConfidenceDistributionSpec.norm(0.05, 0.59, lclip=0),
        Animal.CHICKEN: ConfidenceDistributionSpec.norm(0.002, 0.856, lclip=0),
        Animal.SHRIMP: ConfidenceDistributionSpec.norm(0.01, 1.095, lclip=0),
    }
)


# Validators
def validate_model_weights(model_weights: FrozenDict[str, float]) -> FrozenDict[str, float]:
    np.testing.assert_approx_equal(sum(model_weights.values()), 1.0, significant=2)
    return model_weights


class MoralWeightsParams(BaseParameters, frozen=True):
    type: Annotated[
        Literal["Moral Weight Parameters"],
        Field(
            title="Type",
            description="A string representation of the parameter type",
        ),
    ] = "Moral Weight Parameters"
    version: Annotated[
        Literal["1"],
        Field(
            title="Version",
            description="The version of parameter class",
        ),
    ] = "1"
    override_type: Annotated[
        Literal["No override", "Only welfare capacities", "All moral weight calculations"],
        Field(
            title="Override moral weights calculations",
            description=(
                "Whether to override part or all of the moral weights calculations. If set to `'No override'`, "
                "all the calculations are performed considering the `weights_for_models` parameter, the "
                "`sentience_ranges` parameter and the welfare capacities for each model found by Rethink Priorities' "
                "Moral Weights  Project (*default*). If set to `'Only welfare capacities'`, the `weights_for_models` "
                "parameter is ignored, and the `welfare_capacities_override` is used instead to calculate moral "
                "weights by combining them with the `sentience_ranges` parameter. If set to "
                "`'All moral weight calculations'`, none of these are used, and instead the "
                "`moral_weights_override` parameter is used to set moral weights directly."
            ),
        ),
    ] = "Only welfare capacities"
    weights_for_models: Annotated[
        FrozenDict[str, float],
        Field(
            title="Welfare Model Weights",
            description="Weights for distinct welfare capacity modelling approaches. Must add up to 1.",
        ),
        AfterValidator(validate_model_weights),
    ] = DEFAULT_MODEL_WEIGHTS
    sentience_ranges: Annotated[
        FrozenDict[Animal, SomeDistribution],
        Field(
            title="Sentience Ranges",
            description="Sentience range distributions",
        ),
    ] = DEFAULT_SENTIENCE_RANGES
    welfare_capacities_override: Annotated[
        FrozenDict[Animal, SomeDistribution],
        Field(
            title="Welfare Capacities",
            description=(
                "Direct input of capacity welfare capacities for various species, "
                "*conditional on them being sentient*."
            ),
        ),
    ] = DEFAULT_WELFARE_CAPACITIES
    moral_weights_override: Annotated[
        FrozenDict[Animal, SomeDistribution],
        Field(
            title="Moral Weights",
            description="Direct input of moral weights for various species.",
        ),
    ] = DEFAULT_MORAL_WEIGHTS
