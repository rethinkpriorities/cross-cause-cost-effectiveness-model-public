"""Repository/Factory for getting/constructing Intervention objects."""

from typing import Annotated, TypeAlias, Union

import numpy as np
import squigglepy as sq
from pydantic import Field

import ccm.config as config
import ccm.world.animals as animals
from ccm.interventions.animal.animal_interventions import DEFAULT_ANIMAL_PARAMS, AnimalIntervention
from ccm.interventions.ghd.ghd_interventions import GhdIntervention
from ccm.interventions.intervention import Intervention, ResultIntervention
from ccm.interventions.intervention_definitions.animal_welfare_interventions import ANIMAL_WELFARE_INTERVENTIONS
from ccm.interventions.intervention_definitions.default_interventions import DEFAULT_INTERVENTIONS
from ccm.interventions.intervention_definitions.hardcoded_interventions import HARDCODED_INTERVENTIONS
from ccm.interventions.intervention_definitions.scaled_interventions import SCALED_INTERVENTIONS
from ccm.interventions.intervention_definitions.xrisk_interventions import XRISK_INTERVENTIONS
from ccm.interventions.xrisk.xrisk_interventions import XRiskIntervention
from ccm.world.risk_types import RiskTypeAI, RiskTypeGLT

SIMULATIONS = config.get_simulations()

UNSCALED_INTERVENTIONS = DEFAULT_INTERVENTIONS.copy()
UNSCALED_INTERVENTIONS.extend(ANIMAL_WELFARE_INTERVENTIONS)
UNSCALED_INTERVENTIONS.extend(XRISK_INTERVENTIONS)
UNSCALED_INTERVENTIONS.extend(HARDCODED_INTERVENTIONS)
ALL_INTERVENTIONS = UNSCALED_INTERVENTIONS.copy()
ALL_INTERVENTIONS.extend(SCALED_INTERVENTIONS)

INTERVENTIONS_MAP = {interv.name: interv for interv in ALL_INTERVENTIONS}


# These are meant to facilitate working with FastAPI, as discriminated unions
# allow JS-based clients to infer the type of the object based on the contents of the object.
SomeIntervention: TypeAlias = Annotated[
    Union[ResultIntervention, AnimalIntervention, GhdIntervention, XRiskIntervention],
    Field(discriminator="type"),
]


def get_all_interventions() -> list[SomeIntervention]:
    return ALL_INTERVENTIONS


def get_unscaled_interventions() -> list[SomeIntervention]:
    return UNSCALED_INTERVENTIONS


def get_intervention(intervention_name: str) -> SomeIntervention:
    if intervention_name not in INTERVENTIONS_MAP:
        raise ValueError(f"Unknown Intervention name: {intervention_name}")

    return INTERVENTIONS_MAP[intervention_name]


def construct_cause_benchmark_intervention(
    cause: str, subcause: str, scaling_dist: sq.OperableDistribution | None = None
) -> Intervention:
    scale_display = ""
    if scaling_dist is not None:
        scale_display = f" scaled to ~{np.mean(sq.sample(scaling_dist, n=SIMULATIONS)) * 100:,.0f}%"
    if cause == "GHD":
        return GhdIntervention(
            name=f"{cause} - {subcause} Benchmark{scale_display}",
            _scale_dist=scaling_dist,
        )
    elif cause == "Animals":
        animal = animals.get_animal_by_name(subcause)
        return AnimalIntervention(
            animal=animal,
            name=f"{cause} - {subcause} Benchmark{scale_display}",
            _scale_dist=scaling_dist,
            **DEFAULT_ANIMAL_PARAMS[animal],
        )
    elif cause == "GLT":
        return XRiskIntervention(
            name=f"{cause} - {subcause} Benchmark{scale_display}",
            _scale_dist=scaling_dist,
            risk_type=RiskTypeGLT[subcause],
        )
    elif cause == "AIGS":
        return XRiskIntervention(
            name=f"{cause} - {subcause} Benchmark{scale_display}",
            _scale_dist=scaling_dist,
            risk_type=RiskTypeAI[subcause],
        )
    else:
        raise ValueError(f"No supported intervention for cause: [{cause}]")
