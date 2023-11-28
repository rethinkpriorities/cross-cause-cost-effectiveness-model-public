from abc import ABC, abstractmethod
from collections.abc import Callable
from inspect import cleandoc
from typing import Annotated, Literal, Optional

import numpy as np
import squigglepy as sq
from numpy.typing import NDArray
from pydantic import AfterValidator, BaseModel, ConfigDict, Field

import ccm.config as config
import ccm.utility.squigglepy_wrapper as sqw
from ccm.utility.models import SomeDistribution

SIMULATIONS = config.get_simulations()


class Intervention(BaseModel, ABC, frozen=True):
    """
    Model defining some arbitrary intervention.

    The main entry point is `estimate_dalys_per_1000`,
    which returns the intervention effectiveness.

    All attributes of this class should be either serializable
    or excluded from serialization through Field(exclude=True).
    """

    type: str = Field(description="The type of the intervention (used as a discriminator).")
    name: str = Field(description="The name of the intervention. Acts as an ID.")
    area: Optional[Literal["ghd", "animal-welfare", "xrisk", "utility", "not-an-intervention"]] = Field(
        description="The cause area of the intervention."
    )
    description: Optional[Annotated[str, AfterValidator(cleandoc)]] = Field(
        description="A description of the intervention."
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)
    __hash__: Callable[..., int] = object.__hash__

    @abstractmethod
    def estimate_dalys_per_1000(self) -> tuple[NDArray[np.float64], int]:
        """Returns the DALY per $1000 effectiveness of the intervention as an array of samples."""
        ...


class ResultIntervention(Intervention, frozen=True):
    """
    An intervention defined directly by its result distribution.
    """

    type: Literal["result"]
    description: Optional[
        Annotated[str, AfterValidator(cleandoc)]
    ] = "A simple intervention defined by a result distribution"
    result_distribution: SomeDistribution

    def estimate_dalys_per_1000(self) -> tuple[NDArray[np.float64], int]:
        return sqw.sample(self.result_distribution.to_sq(), SIMULATIONS), 0


class EstimatorIntervention(Intervention, frozen=True):
    """
    An intervention with some arbitrary estimator (a function that
    returns samples) and an optional scale distribution.
    """

    type: Literal["animal-welfare", "ghd", "xrisk"]
    description: Optional[Annotated[str, AfterValidator(cleandoc)]] = "A generic intervention defined by an estimator"
    # Estimators and scale distributions can't be serialized,
    # so we exclude them from the output;
    # SEE https://docs.pydantic.dev/latest/usage/models/#private-model-attributes
    _estimator: Callable[[], NDArray[np.float64]]
    _scale_dist: sq.OperableDistribution | None = None

    def __init__(self, **data):
        estimator = data.get("_estimator")
        if estimator is None:
            raise AttributeError("Missing estimator; please provide a callable for `_estimator` argument")
        super().__init__(**data)
        self.__setattr__("_estimator", estimator)

    def estimate_dalys_per_1000(self) -> tuple[NDArray[np.float64], int]:
        results = self._estimator()
        if isinstance(results, tuple):
            samples, zeros = results
        else:
            samples = results
            zeros = 0
        if self._scale_dist is not None:
            return self._scale(samples), zeros
        return samples, zeros

    def _scale(self, samples: NDArray[np.float64]) -> NDArray[np.float64]:
        return samples * sqw.sample(self._scale_dist, n=SIMULATIONS)
