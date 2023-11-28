"""Repository/Factory for getting/constructing Intervention objects."""

from typing import TYPE_CHECKING

from squigglepy.numbers import K, M
from ccm.interventions.animal.animal_interventions import DEFAULT_ANIMAL_PARAMS, AnimalIntervention
from ccm.utility.models import BetaDistributionSpec, ConfidenceDistributionSpec
from ccm.world.animals import Animal

if TYPE_CHECKING:
    from ccm.interventions.intervention_definitions.all_interventions import SomeIntervention


#  Shrimp Interventions

SHRIMP_DEFAULTS = {
    "use_override": False,
    "prop_affected": ConfidenceDistributionSpec.lognorm(5 * 10**-5, 10**-3, lclip=10**-6, rclip=5 * 10**-3),
    "prob_success": BetaDistributionSpec(type="beta", distribution="beta", alpha=3, beta=3),
    "cost_of_intervention": ConfidenceDistributionSpec.lognorm(150 * K, 1 * M, lclip=100 * K, rclip=1 * M),
    "prop_suffering_reduced": ConfidenceDistributionSpec.lognorm(0.5, 0.9, lclip=0.1, rclip=0.99),
}

shrimp_slaughter = AnimalIntervention(
    name="Shrimp Slaughter Intervention",
    description="An intervention aimed at reducing harm during slaughter for farmed shrimp.",
    animal=Animal.SHRIMP,
    **DEFAULT_ANIMAL_PARAMS[Animal.SHRIMP],
)

shrimp_water_quality = AnimalIntervention(
    name="Shrimp Water Pollution Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through better water quality.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.0063, 5.4, lclip=0),
)

shrimp_high_density = AnimalIntervention(
    name="Shrimp Crowding Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through reduced crowding.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.419, 113.4, lclip=0),
)

shrimp_ammonia = AnimalIntervention(
    name="Shrimp Ammonia Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through lower ammonia concentration.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.189, 78.2, lclip=0),
)

shrimp_lack_substrate = AnimalIntervention(
    name="Shrimp Substrate Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved substrates.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.09, 26.3, lclip=0),
)
shrimp_low_dissolved_oxygen = AnimalIntervention(
    name="Shrimp Dissolved Oxygen Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved oxygenation levels.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.049, 26.1, lclip=0),
)
shrimp_low_salinity = AnimalIntervention(
    name="Shrimp Salinity Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved salinity levels.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.066, 21.2, lclip=0),
)
shrimp_water_based_transit = AnimalIntervention(
    name="Shrimp Transit (Water-based) Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved transportation.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.093, 13.7, lclip=0),
)
shrimp_ph = AnimalIntervention(
    name="Shrimp PH Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved PH levels.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.33, 12.6, lclip=0),
)
shrimp_underfeeding = AnimalIntervention(
    name="Shrimp Underfeeding Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved feeding practices.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.016, 11.4, lclip=0),
)
shirmp_high_temp = AnimalIntervention(
    name="Shrimp Temperature (High) Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved temperature levels.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.017, 8.4, lclip=0),
)
shrimp_harvest = AnimalIntervention(
    name="Shrimp Harvest Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved harvest practices.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.043, 3.4, lclip=0),
)
shrimp_low_temp = AnimalIntervention(
    name="Shrimp Temperature (Low) Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved temperature levels.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.0028, 2.6, lclip=0),
)
shrimp_malnutrition = AnimalIntervention(
    name="Shrimp Malnutrition Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through improved nutrition.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.0012, 1.5, lclip=0),
)
shrimp_predators = AnimalIntervention(
    name="Shrimp Predators Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through predation reduction.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.00076, 0.64, lclip=0),
)
shrimp_waterless_transit = AnimalIntervention(
    name="Shrimp Transit (Waterless) Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through transportation improvements.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(0.0047, 0.23, lclip=0),
)
shrimp_eyestalk_ablation = AnimalIntervention(
    name="Shrimp Eyestock Ablation Intervention",
    description="An intervention aimed at improving farmed shrimp welfare through better ablation practices.",
    animal=Animal.SHRIMP,
    **SHRIMP_DEFAULTS,
    hours_spent_suffering=ConfidenceDistributionSpec.lognorm(10e-11, 2 * 10e-5, lclip=0),
)


SHRIMP_INTERVENTIONS: list["SomeIntervention"] = [
    shrimp_slaughter,
    shrimp_water_quality,
    shrimp_high_density,
    shrimp_ammonia,
    shrimp_lack_substrate,
    shrimp_low_dissolved_oxygen,
    shrimp_low_salinity,
    shrimp_water_based_transit,
    shrimp_ph,
    shrimp_underfeeding,
    shirmp_high_temp,
    shrimp_harvest,
    shrimp_low_temp,
    shrimp_malnutrition,
    shrimp_predators,
    shrimp_waterless_transit,
    shrimp_eyestalk_ablation,
]


def get_shrimp_interventions() -> list["SomeIntervention"]:
    return SHRIMP_INTERVENTIONS
