import numpy as np
from numpy.typing import NDArray
from scipy.sparse import coo_array

from ccm.research_projects.funding_pools.funding_pool import FundingPool
from ccm.research_projects.projects.bottom_line import BottomLine


class ProjectAssessment:
    """Data Transfer Object for output of Project Assessments (ROI calculations, etc)."""

    def __init__(
        self,
        short_name: str,
        cost: NDArray[np.float64],
        years_credit: NDArray[np.float64],
        gross_impact_dalys: coo_array,
        net_impact_dalys: coo_array,
        net_dalys_per_staff_year: coo_array,
        bottom_lines: dict[FundingPool, BottomLine],
    ) -> None:
        self.short_name = short_name
        self.cost = cost
        self.years_credit = years_credit
        self.gross_impact_DALYs = gross_impact_dalys
        self.net_impact_DALYs = net_impact_dalys
        self.net_DALYs_per_staff_year = net_dalys_per_staff_year
        self.bottom_lines = bottom_lines
