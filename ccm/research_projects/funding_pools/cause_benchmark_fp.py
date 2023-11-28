import ccm.interventions.intervention_definitions.all_interventions as interventions
from ccm.interventions.intervention_definitions.all_interventions import Intervention
from ccm.research_projects.funding_pools.funding_pool import FundingPool


class CauseBenchmarkInterventionFundingPool(FundingPool):
    """Funding from a pool of money that counterfactually would have been invested in the best known
    Intervention in the given Cause Area.
    """

    def __init__(self, cause: str, sub_cause: str) -> None:
        self.intervention = interventions.construct_cause_benchmark_intervention(cause, sub_cause)
        super().__init__()

    def get_name(self) -> str:
        return "Cause Area Benchmark"

    def get_counterfactual_intervention(self) -> Intervention:
        return self.intervention
