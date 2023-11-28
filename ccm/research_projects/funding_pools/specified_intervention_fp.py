from ccm.interventions.intervention_definitions.all_interventions import Intervention
from ccm.research_projects.funding_pools.funding_pool import FundingPool


class SpecifiedInterventionFundingPool(FundingPool):
    """Funding from a pool of money that counterfactually would have been invested in a particular
    specified Intervention.
    """

    def __init__(self, intervention: Intervention, name: str = "Specified Intervention") -> None:
        self.intervention = intervention
        self._name = name
        super().__init__()

    def get_name(self) -> str:
        return self._name

    def get_counterfactual_intervention(self) -> Intervention:
        return self.intervention
