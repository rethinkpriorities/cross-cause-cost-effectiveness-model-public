"""
Premises and calculations about various types of macro Risks, both existential and non-existential.
"""

from typing import Annotated, Literal

import numpy as np
from numpy.typing import NDArray
from pydantic import Field
from squigglepy import B, M
import squigglepy as sq

import ccm.data.xrisks_df_access as xrisks_df
from ccm.base_parameters import BaseParameters, FrozenDict
from ccm.utility.models import ConfidenceDistributionSpec, SomeDistribution, ConstantDistributionSpec
from ccm.world.eras import Era
from ccm.world.risk_types import RiskType, RiskTypeAI, RiskTypeGLT

# Space colonization params
DEFAULT_GALACTIC_DENSITY = ConstantDistributionSpec.from_sq(sq.ConstantDistribution(2.2 * 10 ** (-5)))
DEFAULT_SUPERCLUSTER_DENSITY = ConstantDistributionSpec.from_sq(
    sq.ConstantDistribution(2.9 * 10 ** (-9))
)  # density of stars in the Virgo Supercluster
DEFAULT_EXPANSION_SPEED = ConfidenceDistributionSpec.lognorm(
    10 ** (-5),
    10 ** (-2),
    lclip=10 ** (-5),
    rclip=0.1,
)

DEFAULT_STELLAR_POPULATION_CAPACITY = ConfidenceDistributionSpec.lognorm(
    lo=1 * B,
    hi=100 * B,
    lclip=10,
    credibility=90,
)

# Risk distribution params
DEFAULT_CATASTROPHE_EXTINCTION_RISK_RATIOS: FrozenDict[RiskType, int] = FrozenDict(
    {
        RiskTypeGLT.NUKES: 45,
        # bio risk: based on 0.0025 estimated yearly chance of Spanish Flu like virus and xrisks df bio numbers:
        #   A pandemic of an "intensity" (% of people died) equal to or greater than that of the Spanish flu,
        #   which resulted in 20 to 100 million deaths [32 million accreditted]
        #   the mean recurrence time of the same intensity today is 1/0.0025 = 400 y
        RiskTypeGLT.BIO: 50,
        RiskTypeGLT.NATURAL: 100,
        RiskTypeAI.MISALIGNMENT: 2,
        RiskTypeAI.MISUSE: 50,
        RiskTypeGLT.NANO: 50,
        RiskTypeGLT.UNKNOWN: 30,
    }
)
# parameters described here: https://docs.google.com/document/d/1ZwLGjmIAD1D5ldf-8m5MSlI90vY5kzGJ16GRo9fr8LE/edit
DEFAULT_CATASTROPHE_INTENSITIES: FrozenDict[RiskType, SomeDistribution] = FrozenDict(
    {
        RiskTypeGLT.NUKES: ConfidenceDistributionSpec.norm(lo=0.36, hi=0.96, lclip=10**-3, rclip=0.99),
        RiskTypeGLT.BIO: ConfidenceDistributionSpec.lognorm(
            lo=20 * M / (1.8 * B),
            hi=100 * M / (1.8 * B),
            lclip=10**-4,
            rclip=0.1,
        ),
        RiskTypeGLT.NATURAL: ConfidenceDistributionSpec.lognorm(
            lo=20 * M / (1.8 * B),
            hi=100 * M / (1.8 * B),
            lclip=10**-2,
            rclip=0.99,
        ),
        RiskTypeAI.MISALIGNMENT: ConfidenceDistributionSpec.norm(lo=0.36, hi=0.96, lclip=0.01, rclip=0.99),
        RiskTypeAI.MISUSE: ConfidenceDistributionSpec.norm(lo=0.05, hi=0.96, lclip=0.01, rclip=0.99),
        RiskTypeGLT.NANO: ConfidenceDistributionSpec.lognorm(
            lo=20 * M / (1.8 * B),
            hi=100 * M / (1.8 * B),
            lclip=10**-3,
            rclip=0.99,
        ),
        RiskTypeGLT.UNKNOWN: ConfidenceDistributionSpec.lognorm(
            lo=20 * M / (1.8 * B),
            hi=100 * M / (1.8 * B),
            lclip=10**-3,
            rclip=0.99,
        ),
    }
)

# NOTE: AI default risks split as 90% misalignment and 10% misuse in the absence of specific estimates
# TODO: add specific risk fractions for AI misuse and misalignment in xrisk_df.csv
DEFAULT_AI_MISUSE_TO_MISALIGNMENT_RISK_PROP = 1 / 9
DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK_PER_YEAR: FrozenDict[RiskType, NDArray[np.float64]] = FrozenDict(
    {
        RiskTypeAI.MISALIGNMENT: (
            xrisks_df.get_proportional_risks_by_type(RiskTypeAI.TOTAL)
            / (DEFAULT_AI_MISUSE_TO_MISALIGNMENT_RISK_PROP + 1)
        ),
        RiskTypeAI.MISUSE: (
            xrisks_df.get_proportional_risks_by_type(RiskTypeAI.TOTAL)
            * DEFAULT_AI_MISUSE_TO_MISALIGNMENT_RISK_PROP
            / (DEFAULT_AI_MISUSE_TO_MISALIGNMENT_RISK_PROP + 1)
        ),
        RiskTypeGLT.BIO: xrisks_df.get_proportional_risks_by_type(RiskTypeGLT.BIO),
        RiskTypeGLT.NUKES: xrisks_df.get_proportional_risks_by_type(RiskTypeGLT.NUKES),
        RiskTypeGLT.NANO: xrisks_df.get_proportional_risks_by_type(RiskTypeGLT.NANO),
        RiskTypeGLT.NATURAL: xrisks_df.get_proportional_risks_by_type(RiskTypeGLT.NATURAL),
        RiskTypeGLT.UNKNOWN: xrisks_df.get_proportional_risks_by_type(RiskTypeGLT.UNKNOWN),
    }
)
DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK: FrozenDict[RiskType, float] = FrozenDict(
    {
        RiskTypeAI.MISALIGNMENT: float(
            np.mean(DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK_PER_YEAR[RiskTypeAI.MISALIGNMENT])
        ),
        RiskTypeAI.MISUSE: float(np.mean(DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK_PER_YEAR[RiskTypeAI.MISUSE])),
        RiskTypeGLT.BIO: float(np.mean(DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK_PER_YEAR[RiskTypeGLT.BIO])),
        RiskTypeGLT.NANO: float(np.mean(DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK_PER_YEAR[RiskTypeGLT.NANO])),
        RiskTypeGLT.NATURAL: float(np.mean(DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK_PER_YEAR[RiskTypeGLT.NATURAL])),
        RiskTypeGLT.NUKES: float(np.mean(DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK_PER_YEAR[RiskTypeGLT.NUKES])),
        RiskTypeGLT.UNKNOWN: float(np.mean(DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK_PER_YEAR[RiskTypeGLT.UNKNOWN])),
    }
)

# Risk eras params
baseline_risks = xrisks_df.get_baseline_risks()
DEFAULT_ERAS = (
    Era(
        length=30,
        annual_extinction_risk=float(np.mean(baseline_risks[0:30])),
        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
    ),
    Era(
        length=100,
        annual_extinction_risk=float(np.mean(baseline_risks[30:130])),
        proportional_risks_by_type=DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK,
    ),
    Era(
        length=1000,
        annual_extinction_risk=np.mean(baseline_risks[-1]),
        proportional_risks_by_type={
            RiskTypeAI.MISALIGNMENT: 0.2,
            RiskTypeAI.MISUSE: 0.05,
            RiskTypeGLT.BIO: 0.05,
            RiskTypeGLT.NANO: 0.1,
            RiskTypeGLT.NATURAL: 0,
            RiskTypeGLT.NUKES: 0.005,
            RiskTypeGLT.UNKNOWN: 0.595,
        },
    ),
    Era(
        length=100_000_000,
        annual_extinction_risk=np.mean(baseline_risks[-1]),
        proportional_risks_by_type={
            RiskTypeAI.MISALIGNMENT: 0,
            RiskTypeAI.MISUSE: 0,
            RiskTypeGLT.BIO: 0,
            RiskTypeGLT.NANO: 0,
            RiskTypeGLT.NATURAL: 0,
            RiskTypeGLT.NUKES: 0,
            RiskTypeGLT.UNKNOWN: 1,
        },
    ),
)
DEFAULT_MAX_CREDITABLE_YEAR = 3_023


class LongTermParams(BaseParameters, frozen=True):
    """Parameters for the estimation of existential and non-existential risks."""

    type: Literal["Long Term Parameters"] = "Long Term Parameters"
    version: Literal["2"] = "2"
    risk_eras: Annotated[
        tuple[Era, ...],
        Field(
            title="Risk eras",
            description=(
                "Definition of each 'risk era', in terms of its length (in years), "
                + "the annual extinction risk for its duration, an how the risks are distributed "
                + "between various risk types."
            ),
        ),
    ] = DEFAULT_ERAS
    max_creditable_year: Annotated[
        int,
        Field(
            title="Maximum year",
            description="The maximum creditable year to take into account in the risk calculations.",
        ),
    ] = DEFAULT_MAX_CREDITABLE_YEAR
    galactic_density: Annotated[
        SomeDistribution,
        Field(
            title="Density of the galaxy",
            description="Density of stars in the galaxy, in stars per cubic light year.",
        ),
    ] = DEFAULT_GALACTIC_DENSITY
    supercluster_density: Annotated[
        SomeDistribution,
        Field(
            title="Density of a galaxy supercluster",
            description="Density of stars in a supercluster, in stars per cubic light year",
        ),
    ] = DEFAULT_SUPERCLUSTER_DENSITY
    stellar_population_capacity: Annotated[
        SomeDistribution,
        Field(
            title="Population per star",
            description="The average human population per star",
        ),
    ] = DEFAULT_STELLAR_POPULATION_CAPACITY
    expansion_speed: Annotated[
        SomeDistribution,
        Field(
            title="Space expansion speed",
            description="The median speed at which humanity will expand, in light years per year.",
        ),
    ] = DEFAULT_EXPANSION_SPEED
    catastrophe_extinction_risk_ratios: Annotated[
        FrozenDict[RiskType, int],
        Field(
            title="Catastrophic versus existential risks",
            description=(
                "How much more likely a disaster is to be a non-extinction catastrophe than an extinction level event."
            ),
        ),
    ] = DEFAULT_CATASTROPHE_EXTINCTION_RISK_RATIOS
    catastrophe_intensities: Annotated[
        FrozenDict[RiskType, SomeDistribution],
        Field(
            title="Catastrophe intensity",
            description="The proportion of the population that would die in a non-extinction catastrophe",
        ),
    ] = DEFAULT_CATASTROPHE_INTENSITIES
    fractions_of_near_term_total_risk: Annotated[
        FrozenDict[RiskType, float],
        Field(
            title="Risk per year",
            description="Fractions of total risk belonging to risk type by year",
        ),
    ] = DEFAULT_FRACTIONS_OF_NEAR_TERM_TOTAL_RISK
