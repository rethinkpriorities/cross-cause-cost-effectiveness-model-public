from collections.abc import Callable

from pydantic import BaseModel

from ccm.base_parameters import FrozenDict
import ccm.config as config
from ccm.world.risk_types import RiskType


CUR_YEAR = config.get_current_year()


class Era(BaseModel):
    """Instances of Era describe eras of risk"""

    length: int
    annual_extinction_risk: float | None = None
    absolute_risks_by_type: FrozenDict[RiskType, float] | None = None
    proportional_risks_by_type: FrozenDict[RiskType, float] | None = None
    __hash__: Callable[..., int] = object.__hash__

    def __init__(self, **kwargs):
        """
        Initialize with either: the absolute extinction probability for each type of risk; or the total extinction
        probability and the proportional probability from each type of risk.
        """
        super().__init__(**kwargs)
        assert self.annual_extinction_risk is not None or self.absolute_risks_by_type is not None

        if self.absolute_risks_by_type is None:
            assert self.proportional_risks_by_type is not None
            self.absolute_risks_by_type = self.get_absolute_risks()
        else:
            self.annual_extinction_risk = sum(self.absolute_risks_by_type.values())
            self.proportional_risks_by_type = self.get_proportional_risks()  # override given proportional_risks_by_type

    def get_length(self) -> int:
        return self.length

    def get_annual_extinction_probability(self) -> float:
        return self.annual_extinction_risk  # type: ignore  # already check it is not None

    def get_absolute_risks(self) -> FrozenDict[RiskType, float]:
        """Infers absolute risks by type from total and proportional risks."""
        if self.absolute_risks_by_type:
            return self.absolute_risks_by_type
        assert self.proportional_risks_by_type is not None
        assert self.annual_extinction_risk is not None
        absolute_dict = {}
        for key in self.proportional_risks_by_type:
            absolute_dict[key] = self.proportional_risks_by_type[key] * self.annual_extinction_risk
        return FrozenDict(absolute_dict)

    def get_proportional_risks(self) -> FrozenDict[RiskType, float]:
        """Infers proportional risks from absolute risks."""
        if self.proportional_risks_by_type is not None:
            return self.proportional_risks_by_type
        assert self.absolute_risks_by_type is not None
        proportional_dict = {}
        for key in self.absolute_risks_by_type:
            proportional_dict[key] = self.absolute_risks_by_type[key] / self.annual_extinction_risk  # type: ignore
        return FrozenDict(proportional_dict)
