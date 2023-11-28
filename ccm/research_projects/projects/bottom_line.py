import numpy as np
from scipy.sparse import coo_array


class BottomLine:
    """Bottom-line output values for a ProjectAssessment, from the perspective of a single contributing Funding Pool.
    ROI: how many times more QALYs will be produced if money from a given Funding Pool is invested in the
        Research Project instead of the assumed counterfactual use of that money.
    Average ROI: calculated as a Ratio of Averages (rather than an Average of Ratios) from the same data the ROI
        samples were derived from.
    Gross DALYs-per-$1000: How many additional QALYs are produced for each $1000 invested in the Research Project.
        Ignores any counterfactual use of the Research funding money.
    """

    def __init__(
        self,
        roi: coo_array,
        average_roi: np.float64,
        gross_dalys_per_1000: coo_array,
    ) -> None:
        self.roi = roi
        # Average ROI calculated as a Ratio of Averages (rather than an Average of Ratios)
        self.average_roi = average_roi
        self.gross_dalys_per_1000 = gross_dalys_per_1000
