from dataclasses import dataclass

from numpy import ndarray

from ccm.interventions.animal.animal_interventions import Animal
from ccm.interventions.xrisk.impact.impact_method import ImpactMethod


@dataclass
class EffectivenessEstimates:
    """
    Cost-effectiveness estimates for all interventions.
    All estimates are in DALYs per $1000 spent on direct work.
    """

    ghd: dict[str, ndarray]
    animal: dict[Animal, ndarray]
    glt: dict[ImpactMethod, dict[str, ndarray]]
    ai: dict[ImpactMethod, ndarray]
    summary: dict[ImpactMethod, dict[str | Animal, ndarray]]
