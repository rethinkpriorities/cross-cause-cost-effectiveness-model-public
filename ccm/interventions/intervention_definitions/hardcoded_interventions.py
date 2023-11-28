"""Repository/Factory for getting/constructing Intervention objects."""

import squigglepy as sq

from ccm.interventions.intervention import Intervention, ResultIntervention
from ccm.utility.models import DistributionSpec

# Note: If you change the name of an Intervention here, also change it in data/projects/projects.csv


def hardcoded_project(cost) -> Intervention:
    return ResultIntervention(
        type="result",
        area="utility",
        name=f"${cost} per DALY",
        description=f"""
        A generic intervention costing roughly ${cost} per DALY, added for convenience.

        A normal distribution is added to account for its uncertainty, with a 90% CI of +/- 20% of the cost per DALY.
        """,
        result_distribution=DistributionSpec.from_sq(sq.norm(1000 / cost * 0.8, 1000 / cost * 1.2)),
    )


HARDCODED_INTERVENTIONS = []
HARDCODED_INTERVENTIONS.extend(hardcoded_project(i) for i in range(1, 100))
HARDCODED_INTERVENTIONS.extend(hardcoded_project(i * 5 + 100) for i in range(11))
HARDCODED_INTERVENTIONS.extend(hardcoded_project(i * 100 + 100) for i in range(1, 5))
HARDCODED_INTERVENTIONS.extend([hardcoded_project(550)])
HARDCODED_INTERVENTIONS.extend(hardcoded_project(i * 100 + 100) for i in range(5, 15))
HARDCODED_INTERVENTIONS.extend([hardcoded_project(10000)])
HARDCODED_INTERVENTIONS.extend([hardcoded_project(20000)])


def get_hardcoded_interventions() -> list[Intervention]:
    return HARDCODED_INTERVENTIONS
