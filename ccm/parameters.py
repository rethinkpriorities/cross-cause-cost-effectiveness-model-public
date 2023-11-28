from ccm.base_parameters import BaseParameters
from ccm.interventions.animal.animal_intervention_params import AnimalInterventionParams
from ccm.interventions.ghd.ghd_intervention_params import GhdInterventionParams
from ccm.interventions.xrisk.impact.impact_method_params import ImpactMethodParams
from ccm.world.longterm_params import LongTermParams


class Parameters(BaseParameters, frozen=True):
    """
    Main class for all parameters in the model.
    """

    ghd_intervention_params: GhdInterventionParams = GhdInterventionParams()
    animal_intervention_params: AnimalInterventionParams = AnimalInterventionParams()
    longterm_params: LongTermParams = LongTermParams()
    impact_method: ImpactMethodParams = ImpactMethodParams()

    @classmethod
    def is_top_params_obj(cls) -> bool:
        """Read-only property that informs whether the object is a top-level Parameters object"""
        return True
