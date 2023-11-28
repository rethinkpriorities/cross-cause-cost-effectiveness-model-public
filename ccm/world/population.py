"""
Premises and calculations about World Population (of humans) over time.
"""

import numpy as np
from numpy.typing import NDArray
from squigglepy.numbers import B

import ccm.config as config
import ccm.utility.squigglepy_wrapper as sqw
import ccm.world.space as space
from ccm.contexts import inject_parameters
from ccm.world.longterm_params import LongTermParams
from ccm.world.space import GALACTIC_RADIUS, SUPERCLUSTER_RADIUS


CUR_YEAR = config.get_current_year()
WORLD_POPULATION_NOW = 8 * B
WORLD_POPULATION_2100 = 11.2 * B
AVERAGE_AGE_WORLDWIDE = 30  # our world in data
AVERAGE_LIFE_EXPECTANCY_WORLDWIDE = 72  # world bank


def get_total_life_years_until(end_period_array: NDArray[np.float64]) -> NDArray[np.float64]:
    # find samples in which some delay occurs.
    # Focus on these to ease computation time.
    non_zero_indices = (end_period_array > 0).nonzero()
    num_non_zero_samples = len(non_zero_indices)

    # Return early unless valid samples exist
    if num_non_zero_samples == 0:
        return np.zeros(len(end_period_array))

    non_zero_end_years = end_period_array[non_zero_indices]

    # count terrestrial and extraterrestrial life years separately
    terrestrial_life_years = _get_terrestrial_life_years_until(non_zero_end_years)
    extraterrestrial_life_years = _get_extraterrestrial_life_years_until(non_zero_end_years)
    overall_life_years = terrestrial_life_years + extraterrestrial_life_years

    life_years_until = np.zeros(len(end_period_array))
    life_years_until[non_zero_indices] = overall_life_years

    return life_years_until


def calculate_life_years_lost(samples: NDArray[np.float64]) -> NDArray[np.float64]:
    return samples * (AVERAGE_LIFE_EXPECTANCY_WORLDWIDE - AVERAGE_AGE_WORLDWIDE)


# ///////////////// Private ////////////////////


def _get_terrestrial_life_years_until(years_until_array: NDArray[np.float64]) -> NDArray[np.float64]:
    """Calculates the number of years lived until each of a given array of years."""

    # The array of years converted from relative to absolute, e.g.  2 => 2025
    end_year_array = years_until_array + CUR_YEAR

    # Calculate the number of life years before 2100
    # The fraction of the way between now and 2100
    fraction_until_2100 = np.where(end_year_array > 2100, 1, years_until_array / (2100 - CUR_YEAR))
    # Then nubmer of years until 2100
    years_until_2100 = fraction_until_2100 * (2100 - CUR_YEAR)
    value_to_2100 = (
        # simpliciation: assume constant population growth
        # Population = average of the population at the start and the population at the last year counted.
        WORLD_POPULATION_NOW
        + ((WORLD_POPULATION_2100 - WORLD_POPULATION_NOW) * fraction_until_2100 / 2)
    ) * years_until_2100

    # Calculate the number of life years between 2100 and 3000
    perpetual_population = _sample_populations_per_star(len(years_until_array))
    fraction_until_3000 = np.where(end_year_array > 3000, 1, np.maximum((end_year_array - 2100) / (3000 - 2100), 0))
    years_until_3000 = np.where(fraction_until_3000 > 0, fraction_until_3000 * (3000 - 2100), 0)

    value_to_3000 = (
        WORLD_POPULATION_2100 + ((perpetual_population - WORLD_POPULATION_2100) * fraction_until_3000) / 2
    ) * years_until_3000

    # The population that the Earth will eventually settle in to.
    value_thereafter = np.where(end_year_array > 3000, (end_year_array - 3000) * perpetual_population, 0)

    return value_to_2100 + value_to_3000 + value_thereafter


@inject_parameters
def _get_extraterrestrial_life_years_until(
    params: LongTermParams,
    end_year_array: NDArray[np.float64],
) -> NDArray[np.float64]:
    num_samples = len(end_year_array)
    if num_samples < 1:
        return np.array([])
    # Sample parameters and use the samples for galactic and intergalactic speeds
    expansion_speed_samples = space.sample_expansion_speeds(num_samples)
    population_per_star_samples = _sample_populations_per_star(num_samples)
    galactic_densities = sqw.sample(params.galactic_density.get_distribution(), n=num_samples)
    supercluster_densities = sqw.sample(params.supercluster_density.get_distribution(), n=num_samples)

    summed_inhabited_galactic_volume = space.compute_inhabited_volumes(
        end_year_array, expansion_speed_samples, GALACTIC_RADIUS
    )
    galactic_life_years = summed_inhabited_galactic_volume * population_per_star_samples * galactic_densities

    # Compute super cluster radius separately. Note that this is double-counting space, but the relative density
    # makes this a rounding error.
    summed_inhabited_supercluster_volume = space.compute_inhabited_volumes(
        end_year_array, expansion_speed_samples, SUPERCLUSTER_RADIUS
    )

    supercluster_life_years = (
        summed_inhabited_supercluster_volume * population_per_star_samples * supercluster_densities
    )

    return galactic_life_years + supercluster_life_years


@inject_parameters
def _sample_populations_per_star(
    params: LongTermParams,
    num_samples: int,
) -> NDArray[np.float64]:
    if num_samples < 1:
        return np.array([])
    return sqw.sample(
        params.stellar_population_capacity.get_distribution(),
        n=num_samples,
    )
