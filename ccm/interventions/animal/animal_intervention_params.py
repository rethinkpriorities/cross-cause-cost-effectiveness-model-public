from typing import Annotated, Literal

from pydantic import Field
from squigglepy.numbers import B

from ccm.base_parameters import BaseParameters, FrozenDict
from ccm.utility.models import ConfidenceDistributionSpec, SomeDistribution
from ccm.world.animals import Animal
from ccm.world.moral_weight_params import MoralWeightsParams

# Animals for which there are interventions
INTERVENABLE_ANIMALS = [Animal.CHICKEN, Animal.SHRIMP, Animal.CARP, Animal.BSF]


DEFAULT_ANIMALS_BORN_PER_YEAR: FrozenDict[Animal, SomeDistribution] = FrozenDict(
    {
        # BSF natality consider the replenishment of the individuals farmed per year, globally, according to Rowe (2020)
        # SEE: https://perma.cc/FA58-KH7P
        Animal.BSF: ConfidenceDistributionSpec.norm(200 * B, 300 * B, lclip=20 * B, rclip=1000 * B),
        # Considers FAO 2021 estimates of aquaculture production worldwide - ~4.2 ton/year live weight
        # SEE: https://www.fao.org/fishery/statistics-query/en/aquaculture/aquaculture_quantity
        # and a 250-500g final weight for the 2-summer carp;
        # SEE: https://tinyurl.com/45y6nfpb (page 35)
        Animal.CARP: ConfidenceDistributionSpec.norm(8.34 * B, 16.7 * B, lclip=2 * B, rclip=50 * B),
        Animal.CHICKEN: ConfidenceDistributionSpec.norm(360 * B, 520 * B, lclip=100 * B, rclip=1000 * B),
        # distribution inferred from earlier calculations (see v0.7) based on
        # Daniela Waldhorn's Shrimp scoping report
        # SEE: https://docs.google.com/spreadsheets/d/1900FMSuohTS36ia3AMbJh0eLpk5lKI-6Kacos_acVxQ
        # SEE: https://www.getguesstimate.com/models/21583
        Animal.SHRIMP: ConfidenceDistributionSpec.lognorm(300 * B, 610 * B, lclip=50 * B, rclip=2000 * B),
    }
)


class AnimalInterventionParams(BaseParameters, frozen=True):
    """Parameters for animal welfare interventions"""

    type: Literal["Animal Intervention Parameters"] = "Animal Intervention Parameters"
    version: Literal["1"] = "1"
    moral_weight_params: Annotated[
        MoralWeightsParams,
        Field(
            title="Species moral weights",
            description="Moral weights for each species.",
        ),
    ] = MoralWeightsParams()
    num_animals_born_per_year: Annotated[
        FrozenDict[Animal, SomeDistribution],
        Field(
            title="Number of individuals born per year",
            description="A mapping expressing, for each species, how many new individuals are born each year.",
        ),
    ] = DEFAULT_ANIMALS_BORN_PER_YEAR
