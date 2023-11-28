from typing import cast, Literal
from copy import deepcopy

import numpy as np
import squigglepy as sq
from numpy import floating, ndarray
from numpy.typing import NDArray
from scipy.sparse import coo_array

import ccm.config as config
import ccm.utility.squigglepy_wrapper as sqw
from ccm.utility.squigglepy_wrapper import RNG

ONE_BASIS_POINT = 0.0001
STANDARD_PERCENTILES = [1, 5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 99]
SIMULATIONS = config.get_simulations()


def create_distribution(
    distribution_type: str,
    range_low: float,
    range_high: float,
    lclip: float | None = None,
    rclip: float | None = None,
    credibility: int = 90,
) -> sq.OperableDistribution:
    if distribution_type == "lognormal":
        dist = sq.lognorm
    elif distribution_type == "normal":
        dist = sq.norm
    else:
        raise ValueError(f"Unknown distribution_type input: {distribution_type}")
    if lclip == "":
        lclip = None
    if rclip == "":
        rclip = None

    return dist(range_low, range_high, lclip=lclip, rclip=rclip, credibility=credibility)


def sample_distribution(
    distribution_type: str,
    range_low: float,
    range_high: float,
    lclip: float | None = None,
    rclip: float | None = None,
    credibility: int = 90,
) -> NDArray[np.float64]:
    distribution = create_distribution(
        distribution_type,
        range_low,
        range_high,
        lclip=lclip,
        rclip=rclip,
        credibility=credibility,
    )

    return sqw.sample(distribution, n=SIMULATIONS)


def replace_zeros_with_tiny(arr: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    Replaces all zeroes in an array with tiniest positive float.
    """
    arr[arr == 0] = np.finfo(float).tiny
    return arr


def replace_zero_float_with_tiny(num: floating | float) -> floating:
    """
    Replaces a single zero float with tiniest positive float.
    """
    if num == 0:
        return np.finfo(float).tiny

    return np.float64(num)


def enforce_min_absolute_value(
    arr: NDArray[np.float64],
    min_abs_value: float,
) -> NDArray[np.float64]:
    arr[(arr < min_abs_value) & (arr > -min_abs_value) & (arr < 0)] = -min_abs_value
    arr[(arr < min_abs_value) & (arr > -min_abs_value) & (arr >= 0)] = min_abs_value
    arr[(arr < min_abs_value) & (arr > -min_abs_value) & (arr < 0)] = -min_abs_value
    return arr


def round_dictionary_vals(dict: dict, decimal_places: int = 0) -> dict:
    return {k: np.around(val, decimal_places) for k, val in dict.items()}


def get_percentiles(items: ndarray, pctls: list = STANDARD_PERCENTILES) -> dict:
    percentiles = sq.get_percentiles(items, percentiles=pctls)
    # TODO: Fix type instability upstream in squigglepy
    percentiles = cast(dict, percentiles)
    return percentiles


def stable_downsample_by_percentiles(samples: NDArray[np.float64], output_size: int) -> NDArray[np.float64]:
    """Output a smaller list of samples that is representative of the distribution implied in the larger
    input list of samples.
    """
    if len(samples) == output_size:
        return samples

    percentile_increment = 100 / (output_size + 1)
    percentiles = [n * percentile_increment for n in range(1, output_size + 1)]
    percentiles_dict = get_percentiles(samples, pctls=percentiles)
    return np.array(list(percentiles_dict.values()))


def debug_print_distribution(name: str, values: NDArray[np.float64]) -> None:
    print(f"{name}, min: {min(values)}, max: {max(values)}, mean: {np.mean(values)}, median:{np.median(values)}")


def cut_x_percent(array, x: float):
    """Cut the top and bottom x% of values from an array."""
    lower_cut = np.percentile(array, x)
    upper_cut = np.percentile(array, 100 - x)
    cut_scenarios_lower = [max(x, lower_cut) for x in array]
    cut_scenarios_higher = [min(x, upper_cut) for x in cut_scenarios_lower]

    return np.array(cut_scenarios_higher)


def match_coo_axis_lengths(
    array_1: coo_array,
    array_2: coo_array,
    axis: Literal[0, 1] = 1,
) -> tuple[coo_array, coo_array]:
    assert array_1.nnz == array_2.nnz, "Both arrays should start with the same number of stored elements!"

    if array_1.shape[axis] > array_2.shape[axis]:
        array_bigger = array_1
        array_smaller = array_2
    elif array_1.shape[axis] < array_2.shape[axis]:
        array_bigger = array_2
        array_smaller = array_1
    else:
        return array_1, array_2

    # randomly select a subsample of the values in the biggest array, so that its full length matches the length
    # of the smallest array, without changing the proportion of zeros
    array_bigger_prop_non_zeros = array_bigger.getnnz(axis) / array_bigger.shape[axis]
    num_samples_to_keep = int(array_bigger_prop_non_zeros * array_smaller.shape[axis])
    which_samples_to_keep = RNG.choice(array_bigger.data, size=num_samples_to_keep, replace=False)

    # add explicit zeros until the number of stored values is the same for both arrays
    num_explicit_zeros = array_smaller.getnnz(axis) - num_samples_to_keep
    which_samples_to_keep = np.concatenate((which_samples_to_keep, np.zeros(num_explicit_zeros)))

    # copy shape and non-zero positions from the smallest array; then replace the stored values by the (subsampled)
    # values of the biggest array
    resized_array = deepcopy(array_smaller)
    resized_array.data = which_samples_to_keep

    # return the two arrays in the order they were provided
    if array_1.shape[axis] > array_2.shape[axis]:
        return resized_array, array_smaller
    return array_smaller, resized_array
