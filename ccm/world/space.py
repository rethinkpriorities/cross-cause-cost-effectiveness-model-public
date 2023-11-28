import math

import numpy as np
from squigglepy import T
from numpy.typing import NDArray

import ccm.utility.squigglepy_wrapper as sqw
from ccm.contexts import inject_parameters
from ccm.world.longterm_params import LongTermParams

# radius of MilkyWay galaxy, in light years
GALACTIC_RADIUS = 5 * 10**4
SUPERCLUSTER_RADIUS = 5 * 10**8
TIME_WHEN_STARS_BURN_OUT = 100 * T

PI = math.pi


def compute_inhabited_volumes(
    end_year_samples: NDArray[np.float64], speed: NDArray[np.float64], radius: int
) -> NDArray[np.float64]:
    """
    Compute amount of volume from sphere with given radius humanity will populate, starting from 0 with speed.
    Stops expanding upon hitting size determined by radius.
    Note, this is a 4-dimensional measure, since it is the total history of volume, not the volume at any single time.
    """
    time_expansion_finished = np.where(speed > 0, np.divide(radius, speed, where=speed > 0), TIME_WHEN_STARS_BURN_OUT)
    time_during_expansion = np.where(
        end_year_samples > time_expansion_finished, time_expansion_finished, end_year_samples
    )
    time_after_expansion = end_year_samples - time_during_expansion
    time_after_expansion[time_after_expansion < 0] = 0
    expansion_period_volume = (time_during_expansion**4 * PI * speed**3) / 3
    post_expansion_period_volume = time_after_expansion * 4 / 3 * PI * (radius**3)
    return expansion_period_volume + post_expansion_period_volume


@inject_parameters
def sample_expansion_speeds(params: LongTermParams, num_samples: int):
    return sqw.sample(
        params.expansion_speed.get_distribution(),
        n=num_samples,
    )
