import numpy as np
from numpy.typing import NDArray
from ccm.config import get_risk_weighter

import ccm.utility.risk_weighting_functions.WLU as WLU


FUNCS = {
    "EU": np.mean,
    "MIN": np.min,
    "MAX": np.max,
    "WLU - aggressive": WLU.wlu_aggressive,
    "WLU - symmetric": WLU.wlu_symmetric,
}


def risk_weighted_mean(array: NDArray):
    risk_weighting_func = FUNCS[get_risk_weighter()]
    return risk_weighting_func(array)
