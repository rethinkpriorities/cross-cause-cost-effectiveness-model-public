import math

import numpy as np

import ccm.config as config
import ccm.interventions.intervention_definitions.all_interventions as interventions
from ccm.research_projects.funding_pools.specified_intervention_fp import (
    SpecifiedInterventionFundingPool,
)

SIMULATIONS = config.get_simulations()


def test_funding_pool_sample_shuffle_and_caching() -> None:
    # Using this intervention because we know ghd_interventions caches its results
    intervention = interventions.construct_cause_benchmark_intervention("GHD", "")
    funding_pool = SpecifiedInterventionFundingPool(intervention, "Test Funding Pool")

    original_samples, original_zeros = intervention.estimate_dalys_per_1000()
    funding_pool_samples_1 = funding_pool.convert_dollars_to_dalys(np.array([1000] * SIMULATIONS))
    funding_pool_samples_2 = funding_pool.convert_dollars_to_dalys(np.array([1000] * SIMULATIONS))

    # Check that samples are same but have been shuffled
    assert math.isclose(sum(original_samples), sum(funding_pool_samples_1.data), rel_tol=1e-10)
    assert not np.array_equal(original_samples, funding_pool_samples_1.data)

    # Check that funding_pool samples have been cached
    assert np.array_equal(funding_pool_samples_1.data, funding_pool_samples_2.data)
    assert funding_pool_samples_1.shape == funding_pool_samples_2.shape
