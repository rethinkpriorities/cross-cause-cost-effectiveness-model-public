from abc import ABC, abstractmethod
from copy import deepcopy

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import coo_array

from ccm.interventions.intervention_definitions.all_interventions import SomeIntervention
from ccm.utility.squigglepy_wrapper import RNG


class FundingPool(ABC):
    """Counterfactual Funding Pool. A pool of money from which funds are withdrawn, distinguished by
    what that money would be spent on counterfactually if a Research Project did not successfully
    redirect those funds to something else. The less effective the counterfactual use of funds,
    the 'cheaper' that money is counterfactually in DALY terms.
    """

    def __init__(self) -> None:
        self._cached_DALY_efficiency: coo_array | None = None

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_counterfactual_intervention(self) -> SomeIntervention:
        pass

    def convert_dollars_to_dalys(self, cost: NDArray[np.float64] | float) -> coo_array:
        """Convert a single float or array of Dollar amounts into an array of equivalent DALY amounts, based on the
        effectiveness of an underlying Counterfactual Intervention.
        """
        if self._cached_DALY_efficiency is not None:
            daly_efficiency = self._cached_DALY_efficiency
        else:
            counterfactual = self.get_counterfactual_intervention()
            samples, zeros = counterfactual.estimate_dalys_per_1000()

            sample_length_with_zeros = len(samples) + zeros
            positions = RNG.choice(
                sample_length_with_zeros,
                size=len(samples),
                replace=False,
            )
            # Insert the samples at random positions in a sparse array of zeros
            sparse_samples = coo_array(
                (samples, (np.zeros(len(samples)), positions)),
                shape=(1, sample_length_with_zeros),
            )

            daly_efficiency = sparse_samples / 1000

            # Cache so that the sample order will remain the same between comparisons
            self._cached_DALY_efficiency = daly_efficiency

        cost_in_dalys = deepcopy(daly_efficiency)  # copy matrix shape and non-zero positions
        cost_in_dalys.data = cost * daly_efficiency.data  # type: ignore  false-positive (??)

        return cost_in_dalys
