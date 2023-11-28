"""Repository/Factory for getting/constructing Intervention objects."""

from typing import TYPE_CHECKING

import ccm.config as config
from ccm.interventions.animal.animal_interventions import DEFAULT_ANIMAL_PARAMS, AnimalIntervention
from ccm.world.animals import Animal
from ccm.interventions.intervention_definitions.shrimp_interventions import shrimp_ammonia, shrimp_slaughter

if TYPE_CHECKING:
    from ccm.interventions.intervention_definitions.all_interventions import SomeIntervention

SIMULATIONS = config.get_simulations()


#  Generic Interventions

generic_chicken = AnimalIntervention(
    name="Generic Chicken Campaign",
    description="""An intervention aimed at improving the welfare of egg-laying
hens or broiler chickens through corporate advocacy.""",
    animal=Animal.CHICKEN,
    **DEFAULT_ANIMAL_PARAMS[Animal.CHICKEN],
)

generic_shrimp = AnimalIntervention(
    name="Generic Shrimp Intervention",
    description="""An intervention aimed at improving the welfare of farmed shrimp
through corporate advocacy.""",
    animal=Animal.SHRIMP,
    **DEFAULT_ANIMAL_PARAMS[Animal.SHRIMP],
)

generic_carp = AnimalIntervention(
    name="Generic Carp Intervention",
    description="""An intervention aimed at improving the welfare of farmed carp
through corporate advocacy.""",
    animal=Animal.CARP,
    **DEFAULT_ANIMAL_PARAMS[Animal.CARP],
)

generic_bsf = AnimalIntervention(
    name="Generic Black Soldier Fly Intervention",
    description="""An intervention aimed at improving the welfare of farmed black soldier flies
through corporate advocacy.""",
    animal=Animal.BSF,
    **DEFAULT_ANIMAL_PARAMS[Animal.BSF],
)

#  Chicken Interventions

chicken_cage_free = AnimalIntervention(
    name="Cage-free Chicken Campaign",
    description="""An intervention aimed at improving the welfare of egg-laying hens
through corporate advocacy.""",
    animal=Animal.CHICKEN,
    **DEFAULT_ANIMAL_PARAMS[Animal.CHICKEN],
)


#  Shrimp Interventions


ANIMAL_WELFARE_INTERVENTIONS: list["SomeIntervention"] = [
    generic_bsf,
    generic_chicken,
    generic_shrimp,
    generic_carp,
    chicken_cage_free,
    #  chicken_cage_free_2018,
    #  chicken_broiler,
    shrimp_slaughter,
    shrimp_ammonia,
]


def get_hardcoded_interventions() -> list["SomeIntervention"]:
    return ANIMAL_WELFARE_INTERVENTIONS
