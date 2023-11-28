import numpy as np

import ccm.utility.utils as utils


def test_one_basis_point():
    assert 100 * utils.ONE_BASIS_POINT == 0.01


def test_enforce_min_absolute_value():
    input = np.array([1.0, 0.1, 0.09, 0, -0.09, -0.1, -1.0])
    result = utils.enforce_min_absolute_value(input, 0.1)
    expected = np.array([1, 0.1, 0.1, 0.1, -0.1, -0.1, -1.0])
    assert np.array_equal(result, expected)
