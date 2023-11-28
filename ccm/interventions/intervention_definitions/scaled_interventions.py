"""Repository/Factory for getting/constructing Intervention objects."""

from typing import TYPE_CHECKING

import squigglepy as sq
from squigglepy.numbers import K, M

import ccm.config as config
from ccm.interventions.animal.animal_interventions import DEFAULT_ANIMAL_PARAMS, AnimalIntervention
from ccm.interventions.ghd.ghd_interventions import GW_COST_EFFECTIVENESS, GhdIntervention
from ccm.interventions.xrisk.xrisk_interventions import XRiskIntervention
from ccm.utility.models import ConfidenceDistributionSpec
from ccm.world.animals import Animal
from ccm.world.risk_types import RiskTypeAI, RiskTypeGLT

if TYPE_CHECKING:
    from ccm.interventions.intervention_definitions.all_interventions import SomeIntervention

SIMULATIONS = config.get_simulations()

standard_ghd = GhdIntervention(
    area="ghd",
    name="GiveWell Bar Scaled to ~88%",
    cost_per_daly=GW_COST_EFFECTIVENESS,
    _scale_dist=1 - sq.lognorm(0.05, 0.25, lclip=0, rclip=1),
)


standard_ai_misalignment = XRiskIntervention(
    area="xrisk",
    name="Small-scale AI Misalignment Project Scaled to ~86%",
    risk_type=RiskTypeAI.MISALIGNMENT,
    cost=ConfidenceDistributionSpec.lognorm(200 * K, 1 * M, lclip=50 * K, rclip=4 * M),
    prob_no_effect=0.964,
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(
        lo=10 ** (-6),
        hi=5.5 * 10 ** (-5),
        lclip=0,
        rclip=1,
    ),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(
        lo=10 ** (-6),
        hi=5.5 * 10 ** (-5),
        lclip=0,
        rclip=1,
    ),
    # scale down the cost effectiveness
    _scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
)

standard_ai_misuse = XRiskIntervention(
    area="xrisk",
    name="Small-scale AI Misuse Project Scaled to ~86%",
    risk_type=RiskTypeAI.MISUSE,
    prob_no_effect=0.95,
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-4),
        hi=5 * 10 ** (-3),
        lclip=0,
        rclip=1,
    ),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-2),
        hi=5 * 10 ** (-2),
        lclip=0,
        rclip=1,
    ),
    cost=ConfidenceDistributionSpec.lognorm(200 * K, 20 * M, lclip=4 * 2 * K, rclip=4 * 100 * M),
    # scale down the cost effectiveness
    _scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
)


standard_bio = XRiskIntervention(
    area="xrisk",
    name="Small-scale Biorisk Project Scaled to ~86%",
    risk_type=RiskTypeGLT.BIO,
    prob_no_effect=0.6,
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-4),
        hi=5 * 10 ** (-3),
        lclip=0,
        rclip=1,
    ),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3),
        hi=5 * 10 ** (-3),
        lclip=0,
        rclip=1,
    ),
    cost=ConfidenceDistributionSpec.lognorm(500 * K, 10 * M, lclip=4 * 2 * K, rclip=4 * 200 * M),
    # scale down the cost effectiveness
    _scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
)

standard_nano = XRiskIntervention(
    area="xrisk",
    name="Small-scale Nanotech Safety Project Scaled to ~86%",
    risk_type=RiskTypeGLT.NANO,
    cost=ConfidenceDistributionSpec.lognorm(200 * K, 2 * M, lclip=4 * 2 * K, rclip=4 * 100 * M),
    prob_no_effect=0.9,
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3),
        hi=5 * 10 ** (-2),
        lclip=0,
        rclip=1,
    ),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3),
        hi=5 * 10 ** (-3),
        lclip=0,
        rclip=1,
    ),
    # scale down the cost effectiveness
    _scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
)


standard_natural = XRiskIntervention(
    area="xrisk",
    name="Small-scale Natural Disaster Prevention Project Scaled to ~86%",
    risk_type=RiskTypeGLT.NATURAL,
    prob_no_effect=0.5,
    cost=ConfidenceDistributionSpec.lognorm(1 * M, 20 * M, lclip=4 * 2 * K, rclip=4 * 200 * M),
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3),
        hi=5 * 10 ** (-2),
        lclip=0,
        rclip=1,
    ),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3),
        hi=5 * 10 ** (-3),
        lclip=0,
        rclip=1,
    ),
    # scale down the cost effectiveness
    _scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
)


standard_nukes = XRiskIntervention(
    area="xrisk",
    name="Small-scale Nuclear Safety Project Scaled to ~86%",
    risk_type=RiskTypeGLT.NUKES,
    cost=ConfidenceDistributionSpec.lognorm(5 * M, 20 * M, lclip=4 * 2 * K, rclip=4 * 200 * M),
    prob_no_effect=0.8,
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3),
        hi=5 * 10 ** (-2),
        lclip=0,
        rclip=1,
    ),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-2),
        hi=5 * 10 ** (-2),
        lclip=0,
        rclip=1,
    ),
    # scale down the cost effectiveness
    _scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
)


standard_unknown = XRiskIntervention(
    area="xrisk",
    name="Exploratory Research into Unknown Risks Scaled to ~86%",
    risk_type=RiskTypeGLT.UNKNOWN,
    cost=ConfidenceDistributionSpec.lognorm(50 * K, 5 * M, lclip=4 * 2 * K, rclip=4 * 100 * M),
    prob_no_effect=0.5,
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3),
        hi=5 * 10 ** (-2),
        lclip=0,
        rclip=1,
    ),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-2),
        hi=5 * 10 ** (-2),
        lclip=0,
        rclip=1,
    ),
    # scale down the cost effectiveness
    _scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
)


standard_chicken = AnimalIntervention(
    animal=Animal.CHICKEN,
    name="Cage-free Chicken Campaign Scaled to ~86%",
    scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
    **DEFAULT_ANIMAL_PARAMS[Animal.CHICKEN],
)

standard_shrimp = AnimalIntervention(
    animal=Animal.SHRIMP,
    name="Generic Shrimp Intervention Scaled to ~86%",
    scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
    **DEFAULT_ANIMAL_PARAMS[Animal.SHRIMP],
)

standard_carp = AnimalIntervention(
    animal=Animal.CARP,
    name="Generic Carp Intervention Scaled to ~86%",
    scale_dist=1 - sq.lognorm(0.05, 0.3, lclip=0, rclip=1),
    **DEFAULT_ANIMAL_PARAMS[Animal.CARP],
)


SCALED_INTERVENTIONS: list["SomeIntervention"] = [
    standard_ghd,
    standard_nano,
    standard_bio,
    standard_natural,
    standard_nukes,
    standard_unknown,
    standard_ai_misalignment,
    standard_ai_misuse,
    standard_chicken,
    standard_shrimp,
    standard_carp,
]
