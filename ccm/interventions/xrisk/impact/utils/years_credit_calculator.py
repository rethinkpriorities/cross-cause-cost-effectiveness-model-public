import numpy as np
from numpy.typing import NDArray
import squigglepy as sq
import ccm.config as config
import ccm.utility.squigglepy_wrapper as sqw

SIMULATIONS = config.get_simulations()


def sample_years_credit(
    year_of_extinction_distribution: sq.OperableDistribution,
    change_in_probability_by_sample: NDArray[np.float64],
    num_years_intervention_effective: NDArray[np.int64],
    # Note, there must be possible extinction dates beyond the span when the intervention is effective.
    # It can't be that the intervention could prevent extinction in the last possible year we could go extinct.
) -> NDArray[np.float64]:
    # Take two samples,  one an expected time to a close call with extinction, the second the subsequent extinction.
    # Our intervention has a chance of making a difference if the first close call falls within the period of
    # intervention effect.
    sampled_time_of_first_risk = sqw.sample(year_of_extinction_distribution, n=SIMULATIONS)
    sampled_time_of_second_risk = _get_higher_samples(
        year_of_extinction_distribution,
        sampled_time_of_first_risk,
        num_years_intervention_effective,
    )

    # Examine indices where first risk occurs in time of intervention. If random sample < probability the intervention
    # makes a positive or negative difference, then the index makes a difference
    indices_where_makes_a_difference = _get_indices_where_intervention_makes_a_difference(
        sampled_time_of_first_risk,
        change_in_probability_by_sample,
        num_years_intervention_effective,
    )

    # Calculate the difference made. If the intervention was positive, subtract the first from the second (disaster
    # averted) otherwise vice versa (disaster caused)
    differences_made = np.multiply(
        (sampled_time_of_second_risk - sampled_time_of_first_risk),
        np.sign(change_in_probability_by_sample),
    )

    year_difference_made = np.where(indices_where_makes_a_difference, differences_made, 0)
    return year_difference_made


def _get_indices_where_intervention_makes_a_difference(
    sampled_time_of_first_risk: NDArray[np.float64],
    reduction_in_probability_by_sample: NDArray[np.float64],
    num_years_intervention_effective: NDArray[np.int64],
) -> NDArray[np.bool_]:
    """Get indices of values in sampled_time_of_first_risk where it is in the intervention period and a random sample
    is less than the reduction in probability the intervention causes"""
    probability_samples = np.random.random(SIMULATIONS)

    return np.logical_and(
        sampled_time_of_first_risk <= num_years_intervention_effective,
        probability_samples < abs(reduction_in_probability_by_sample),
    )


def _get_higher_samples(
    dist: sq.OperableDistribution,
    lower_samples: NDArray[np.float64],
    max_value: NDArray[np.int64],
):
    """From a distribution and a list of samples, select samples from the distribution that are > first samples if
    those samples have a value less than or equal to max_value"""
    # Including a max_value lets us only focus on the values that need resampling.
    higher_samples = sqw.sample(dist, n=len(lower_samples))
    in_range = lower_samples <= max_value
    while True:
        # Get indices where second risk falls before the first risk, looking at only those that might be relevant
        indices_to_resample = np.logical_and(
            higher_samples <= lower_samples,
            in_range,
        ).nonzero()[0]
        # Repeat until no relevant indices found
        # Instead of defining indices to resample twice in the code, just define once and break as appropriate
        if not np.any(indices_to_resample):
            break
        new_values = sqw.sample(dist, n=len(indices_to_resample))
        higher_samples[indices_to_resample] = new_values
    return higher_samples
