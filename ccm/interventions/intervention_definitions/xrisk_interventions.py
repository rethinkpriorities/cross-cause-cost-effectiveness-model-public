"""Repository/Factory for getting/constructing Intervention objects."""

from typing import TYPE_CHECKING

from squigglepy.numbers import K, M, B

import ccm.config as config
from ccm.interventions.xrisk.xrisk_interventions import XRiskIntervention
from ccm.utility.models import ConfidenceDistributionSpec
from ccm.world.risk_types import RiskTypeAI, RiskTypeGLT

if TYPE_CHECKING:
    from ccm.interventions.intervention_definitions.all_interventions import SomeIntervention

SIMULATIONS = config.get_simulations()


major_ai_misalignment = XRiskIntervention(
    # broadly inspirated by OpenAI's Superalignment Team
    # SEE: https://openai.com/blog/introducing-superalignment
    area="xrisk",
    name="AI Misalignment Megaproject",
    description="""A very large project aimed at reducing existential risk from AI misalignment
either through technical research or policy advocacy.""",
    risk_type=RiskTypeAI.MISALIGNMENT,
    # centered on 20% of OpenAI's operational costs in 2022 (USD ~550mn according to Fortune), multiplied by 4 years
    cost=ConfidenceDistributionSpec.lognorm(8 * B, 28 * B, lclip=1 * B, rclip=500 * B),
    # Metaculus question on: "Will OpenAI announce that it has solved the core technical challenges of
    # superintelligence alignment by June 30, 2027?" - 10% chance of success, as of Sep 29th, 2023
    # SEE: https://www.metaculus.com/questions/17728/openai-solves-alignment-before-june-30-2027/
    # we consider there is a chance of only ~36% of they
    # being right, conditional on the announcement
    prob_no_effect=0.973,
    # "solve the core technical challenges of superintelligence alignment" - solve 50-80% of the problem
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(0.5, 0.8, lclip=0, rclip=1),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(0.5, 0.8, lclip=0, rclip=1),
)


best_ai_misalignment = XRiskIntervention(
    area="xrisk",
    name="Small-scale AI Misalignment Project",
    description="""A small project aimed at reducing existential risk from AI misalignment
either through technical research or policy advocacy.""",
    risk_type=RiskTypeAI.MISALIGNMENT,
    cost=ConfidenceDistributionSpec.lognorm(200 * K, 1 * M, lclip=50 * K, rclip=4 * M),
    # Same prob_no_effect as OAI Superalignment Team's,
    # and effect_on_xrisk/catastrophe lo/hi linearly extrapolated from their
    # effects and average costs
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
)


best_ai_misuse = XRiskIntervention(
    area="xrisk",
    name="Small-scale AI Misuse Project",
    description="""A small project aimed at reducing existential risk
from accidental misuse or intentional harmful use of AI.""",
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
)

major_bio = XRiskIntervention(
    area="xrisk",
    name="Portfolio of Biorisk Projects",
    description="""A collection of small and midsized projects
aimed at reducing the threat of engineered pandemics.""",
    risk_type=RiskTypeGLT.BIO,
    # 90% CI cost of a bio risk intervention;
    # SEE: https://docs.google.com/spreadsheets/d/1onjuWEP-FRaVFbDGgDNHGDs_4QDenuMAeW19NWI5t-8/#gid=1030666228
    prob_no_effect=0.6,
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-4) * 10,
        hi=5 * 10 ** (-3) * 10,
        lclip=0,
        rclip=1,
    ),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3) * 10,
        hi=5 * 10 ** (-3) * 10,
        lclip=0,
        rclip=1,
    ),
    cost=ConfidenceDistributionSpec.lognorm(500 * K * 30, 10 * M * 3, lclip=4 * 2 * K, rclip=4 * 200 * M),
)

best_bio = XRiskIntervention(
    area="xrisk",
    name="Small-scale Biorisk Project",
    description="A single small project aimed at reducing the threat of engineered pandemics.",
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
)

major_nano = XRiskIntervention(
    area="xrisk",
    name="Nanotech Safety Megaproject",
    description="A very large project aimed at reducing the threat of nanotechnology.",
    risk_type=RiskTypeGLT.NANO,
    # 90% CI cost of a nano risk intervention;
    # SEE: https://docs.google.com/spreadsheets/d/1onjuWEP-FRaVFbDGgDNHGDs_4QDenuMAeW19NWI5t-8/#gid=1030666228
    cost=ConfidenceDistributionSpec.lognorm(10 * M, 30 * M, lclip=4 * 2 * K, rclip=4 * 100 * M),
    prob_no_effect=0.9,
    effect_on_xrisk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3) * 8,
        hi=5 * 10 ** (-2) * 8,
        lclip=0,
        rclip=1,
    ),
    effect_on_catastrophic_risk=ConfidenceDistributionSpec.lognorm(
        lo=1 * 10 ** (-3) * 8,
        hi=5 * 10 ** (-3) * 8,
        lclip=0,
        rclip=1,
    ),
)

best_nano = XRiskIntervention(
    area="xrisk",
    name="Small-scale Nanotech Safety Project",
    description="A single small project aimed at reducing the threat of nanotechnology.",
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
)


best_natural = XRiskIntervention(
    area="xrisk",
    name="Small-scale Natural Disaster Prevention Project",
    description="""A small project aimed at reducing the probability that a natural disaster
will cause human extinction.""",
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
)


best_nukes = XRiskIntervention(
    area="xrisk",
    name="Small-scale Nuclear Safety Project",
    description="A small project aimed at reducing the threat or severity of a nuclear war.",
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
)


best_unknown = XRiskIntervention(
    area="xrisk",
    name="Exploratory Research into Unknown Risks",
    description="A small project aimed at better understanding potential novel existential risks.",
    risk_type=RiskTypeGLT.UNKNOWN,
    cost=ConfidenceDistributionSpec.lognorm(500 * K, 5 * M, lclip=4 * 2 * K, rclip=4 * 100 * M),
    prob_no_effect=0.999,
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
)


all_glt_interventions: list[XRiskIntervention] = [
    major_bio,
    best_bio,
    major_nano,
    best_nano,
    best_natural,
    best_nukes,
    best_unknown,
]


all_aigs_interventions: list[XRiskIntervention] = [
    major_ai_misalignment,
    best_ai_misalignment,
    best_ai_misuse,
]


all_xrisk_interventions: list[XRiskIntervention] = [*all_glt_interventions, *all_aigs_interventions]


XRISK_INTERVENTIONS: list["SomeIntervention"] = [
    *all_glt_interventions,
    *all_aigs_interventions,
]


def get_xrisk_interventions() -> list["SomeIntervention"]:
    return XRISK_INTERVENTIONS
