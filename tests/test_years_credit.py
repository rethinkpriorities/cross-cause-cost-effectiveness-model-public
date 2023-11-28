import numpy as np
import math
import random
import squigglepy as sq

import ccm.config as config
import ccm.interventions.xrisk.impact.utils.years_credit_calculator as years_credit

SIMULATIONS = config.get_simulations()


def test_sample_years_credit() -> None:
    dist = sq.discrete([1, 2])
    reduction_in_probability_by_sample = np.ones(SIMULATIONS) * 0.5
    credit = years_credit.sample_years_credit(
        year_of_extinction_distribution=dist,
        change_in_probability_by_sample=reduction_in_probability_by_sample,
        num_years_intervention_effective=np.array(SIMULATIONS * [1]),
    )
    # At most one years credit
    assert len(credit[np.logical_or(credit == 0, credit == 1)]) == len(credit)


def test_sample_years_credit_with_bigger_values() -> None:
    dist = sq.discrete([1, 20])
    reduction_in_probability_by_sample = np.ones(SIMULATIONS) * 0.5
    credit = years_credit.sample_years_credit(
        year_of_extinction_distribution=dist,
        change_in_probability_by_sample=reduction_in_probability_by_sample,
        num_years_intervention_effective=np.array(SIMULATIONS * [1]),
    )
    # credit based on time between years
    assert len(credit[np.logical_or(credit == 0, credit == 19)]) == len(credit)


def test_sample_years_credit_against_simple_model() -> None:
    def prob_survival_until_then_death_at(array):
        survival_until = np.cumprod(1 - array[0:-1])
        survival_until = np.insert(survival_until, 0, 1)
        death_at = array
        return survival_until * death_at

    i = random.randint(1, 10)
    print(f"testing with: {i}")
    #  Build simple model of time until extinction with unadjusted and adjusted probabilities.
    list_of_years = np.cumsum(np.ones(50))
    default_conditional_probs = np.ones(50) * 0.33
    # Given that we only apply the reduction in probability to the first extinction event in years credit,
    # this is more accurate if the early probabilities are small.
    default_conditional_probs[0:10] = 0.05
    adjusted_conditional_probs = default_conditional_probs.copy()
    adjusted_conditional_probs[0:i] = adjusted_conditional_probs[0:i] * 0.5
    probability_of_extinction_by_year = prob_survival_until_then_death_at(default_conditional_probs)
    adjusted_probability_of_extinction_by_year = prob_survival_until_then_death_at(adjusted_conditional_probs)
    dist_default = sq.discrete(dict(zip(list_of_years.tolist(), probability_of_extinction_by_year.tolist())))
    dist_adjusted = sq.discrete(dict(zip(list_of_years.tolist(), adjusted_probability_of_extinction_by_year.tolist())))

    reduction_in_probability_by_sample = np.ones(SIMULATIONS) * 0.5
    credit = years_credit.sample_years_credit(
        year_of_extinction_distribution=dist_default,
        change_in_probability_by_sample=reduction_in_probability_by_sample,
        num_years_intervention_effective=np.array(SIMULATIONS * [i]),
    )

    # The results should be approximately the same.
    # They aren't exactly the same because we only apply the reduction in probability to the first extinction event.
    # The second event is sampled from the unadjusted distribution in years_credit, but not the simple model above.
    differences = sq.sample(dist_adjusted, n=150000) - sq.sample(dist_default, n=150000)
    expected_value = np.mean(differences)
    actual_value = np.mean(credit)
    assert math.isclose(actual_value, expected_value, rel_tol=0.2)
