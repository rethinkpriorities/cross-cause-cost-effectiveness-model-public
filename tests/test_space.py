import math
import squigglepy as sq
import numpy as np
from ccm.contexts import using_parameters
from ccm.utility.models import DistributionSpec
from ccm.parameters import Parameters
from ccm.world.longterm_params import LongTermParams
import ccm.world.space as space

PI = math.pi


def test_compute_inhabited_volumes() -> None:
    sample_years = np.arange(1.0, 1000.0)
    speeds = np.ones(999)
    volumes = space.compute_inhabited_volumes(sample_years, speeds, 100)
    assert np.all(volumes[:-1] <= volumes[1:])
    assert volumes[0] < (4 / 3 * PI)
    assert volumes[1] > (4 / 3 * PI)
    # Volumes of spheres up to 999 radius
    discrete_volumes = (np.arange(999.0)) ** 3 * 4 / 3 * PI

    # The integral increase to the next volume is more than 1/3 the value of the next discrete volume
    lower_boundary = volumes[:-1] + discrete_volumes[1:] / 3
    # The intergal increase to the next volume is less than the value of the next discrete volume
    upper_boundary = volumes[:-1] + discrete_volumes[1:]
    assert np.all(volumes[1:100] > lower_boundary[:99])
    assert np.all(volumes[1:100] < upper_boundary[1:100])
    # After the boundary, we stop expanding
    assert not np.all(volumes[1:150] > lower_boundary[1:150])


def test_compute_inhabited_volumes_big_boundary() -> None:
    sample_years = np.arange(1.0, 1000.0)
    speeds = np.ones(999)
    volumes = space.compute_inhabited_volumes(sample_years, speeds, 500)
    # Volumes of spheres up to 999 radius
    discrete_volumes = (np.arange(999.0)) ** 3 * 4 / 3 * PI

    # The integral increase to the next volume is more than 1/3 the value of the next discrete volume
    lower_boundary = volumes[:-1] + discrete_volumes[1:] / 3
    # The intergal increase to the next volume is less than the value of the next discrete volume
    upper_boundary = volumes[:-1] + discrete_volumes[1:]
    assert np.all(volumes[1:500] > lower_boundary[:499])
    assert np.all(volumes[1:500] < upper_boundary[1:500])
    # After the boundary, we stop expanding
    assert not np.all(volumes[1:550] > lower_boundary[1:550])
    # Then increase by constant volume equal to boundary sphere
    assert np.all(volumes[500:] < volumes[499:-1] + 1.01 * discrete_volumes[499])
    assert not np.all(volumes[500:] < volumes[499:-1] + 1.01 * discrete_volumes[498])


def test_sample_expansion_speed() -> None:
    slow = sq.norm(0.0001, 0.001)
    with using_parameters(Parameters(longterm_params=LongTermParams(expansion_speed=DistributionSpec.from_sq(slow)))):
        samples = space.sample_expansion_speeds(100000)
        assert math.isclose(np.median(samples), np.median(sq.sample(slow, n=10000)), rel_tol=0.3)
        assert math.isclose(np.mean(samples), np.mean(sq.sample(slow, n=100000)), rel_tol=0.8)
    fast = sq.norm(0.009, 0.09)
    with using_parameters(Parameters(longterm_params=LongTermParams(expansion_speed=DistributionSpec.from_sq(fast)))):
        samples = space.sample_expansion_speeds(100000)
        assert math.isclose(np.median(samples), np.median(sq.sample(fast, n=10000)), rel_tol=0.3)
        assert math.isclose(np.mean(samples), np.mean(sq.sample(fast, n=100000)), rel_tol=0.8)
