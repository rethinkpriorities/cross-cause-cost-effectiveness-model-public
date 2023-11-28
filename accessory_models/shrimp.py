### The file that simulates the cost-effectiveness of shrimp corporate campaigns (vector)
### The cost-effectiveness estimates are adjusted for p(sentience) and welfare ranges

import numpy as np
import squigglepy as sq
from squigglepy.numbers import K, M, B

N = 10 * K

### GENERIC SHRIMP INTERVENTION

example_shrimp_project_dict = {
    "lifestages_affected": ["adult"],
    "harm_type": "slaughter",
    "low_suffering_reduced_proportion": 0.5,
    "high_suffering_reduced_proportion": 0.9,
    "low_p_success": 0.2,
    "high_p_success": 0.8,
    "low_p_shrimp_affected": 5 * 10**-5,
    "high_p_shrimp_affected": 5 * 10**-3,
    "low_cost": 150 * K,
    "high_cost": 1 * M,
}

harm_duration_dict = {
    "high_density": sq.lognorm(0.419, 133.4),
    "ammonia": sq.lognorm(0.189, 78.2),
    "lack_substrate": sq.lognorm(0.090, 26.3),
    "low_dissolved_oxygen": sq.lognorm(0.049, 26.1),
    "low_salinity": sq.lognorm(0.066, 21.2),
    "water_based_transit": sq.lognorm(0.093, 13.7),
    "ph": sq.lognorm(0.033, 12.6),
    "underfeeding": sq.lognorm(0.016, 11.4),
    "high_temp": sq.lognorm(0.017, 8.4),
    "water_pollution": sq.lognorm(0.0063, 5.4),
    "harvest": sq.lognorm(0.043, 3.4),
    "low_temp": sq.lognorm(0.0028, 2.6),
    "malnutrition": sq.lognorm(0.0012, 1.5),
    "predators": sq.lognorm(0.00076, 0.64),
    "slaughter": sq.lognorm(0.0072, 0.62),
    "waterless_transit": sq.lognorm(0.0047, 0.23),
    "eyestalk_ablation": sq.lognorm(10**-11, 2 * 10**-5),
}

lifestage_numbers = {
    "larval": 240 * B,
    "postlarval": 120 * B,
    "juvenile": 160 * B,
    "adult": 440 * B,
}


def generic_shrimp_sentience_conditioned_dalys_per_1000(intervention_dict, to_print=False):
    # number shrimp per year
    lifestages_affected = intervention_dict["lifestages_affected"]
    num_in_world = 0
    for stage in lifestages_affected:
        num_in_world += lifestage_numbers[stage]

    num_affected = num_in_world * sq.sample(
        sq.lognorm(
            intervention_dict["low_p_shrimp_affected"],
            intervention_dict["high_p_shrimp_affected"],
            lclip=0.1 * intervention_dict["low_p_shrimp_affected"],
            rclip=10 * intervention_dict["high_p_shrimp_affected"],
        ),
        N,
    )
    harm_type = intervention_dict["harm_type"]
    hrs_harm_duration = sq.sample(harm_duration_dict[harm_type], N)
    yrs_harm_duration = hrs_harm_duration / 24 / 365
    prop_harm_reduced = sq.sample(
        sq.lognorm(
            intervention_dict["low_suffering_reduced_proportion"],
            intervention_dict["high_suffering_reduced_proportion"],
            lclip=0.1 * intervention_dict["low_suffering_reduced_proportion"],
            rclip=1,
        ),
        N,
    )
    harm_reduced = yrs_harm_duration * prop_harm_reduced * num_affected

    prob_success = sq.sample(
        sq.lognorm(
            intervention_dict["low_p_success"],
            intervention_dict["high_p_success"],
            lclip=0.1 * intervention_dict["low_p_success"],
            rclip=1,
        ),
        N,
    )
    shrimp_dalys_averted = harm_reduced * prob_success

    cost_intervention = sq.sample(
        sq.lognorm(
            intervention_dict["low_cost"],
            intervention_dict["high_cost"],
            lclip=0.1 * intervention_dict["low_cost"],
            rclip=5 * intervention_dict["high_cost"],
        ),
        N,
    )

    shrimp_dalys_per_1000 = shrimp_dalys_averted / cost_intervention * 1000

    if to_print:
        print(f"Mean sentience-conditioned Shrimp-DALYs per $1000: {np.mean(shrimp_dalys_per_1000)}")
        print("Percentiles:")
        print(sq.get_percentiles(shrimp_dalys_per_1000))
    return shrimp_dalys_per_1000


def sample_is_shrimp_sentient():
    """
    Create a vector of binary variables representing whether a shrimp is sentient,
        based on our subjective 90% CI on the probability that shrimp are sentient.
    """
    p_sent_low = 0.2
    p_sent_high = 0.7
    p_sent_lclip = 0.01
    p_sent_rclip = 1

    p_sent = sq.sample(sq.lognorm(p_sent_low, p_sent_high, lclip=p_sent_lclip, rclip=p_sent_rclip), N)
    binaries_is_sent = np.zeros(N)

    for i in range(N):
        X = np.random.binomial(1, p_sent[i])
        binaries_is_sent[i] = X

    return binaries_is_sent


def shrimp_sentience_conditioned_welfare_range(to_print=False):
    """
    Create a vector of welfare ranges for shrimp, conditional on being sentient.
        Based on RP's moral weight project:
        https://docs.google.com/spreadsheets/d/1gJZlOTmrWwR6C7us5G0-aRM9miFeEcP11_6HEfpCPus/edit?usp=sharing
    """
    wr_shrimp_lower = 0.01
    wr_shrimp_upper = 2  # a bit less than the 95th percentile so the mean would match 0.439
    wr_shrimp_lclip = 0.000001  # neuron count for a shrimp
    wr_shrimp_rclip = 5  # a bit less than the 95th percentile for the undiluted experiences model

    wr_shrimp = sq.sample(sq.lognorm(wr_shrimp_lower, wr_shrimp_upper, lclip=wr_shrimp_lclip, rclip=wr_shrimp_rclip), N)

    if to_print:
        print(f"Mean welfare range for shrimp: {np.mean(wr_shrimp)}")
        print("Percentiles:")
        print(sq.get_percentiles(wr_shrimp))

    return wr_shrimp


def shrimp_campaign_human_dalys_per_1000(intervention_dict, to_print=False):
    sentience_conditioned_dalys_per_1000 = generic_shrimp_sentience_conditioned_dalys_per_1000(intervention_dict)
    is_sent = sample_is_shrimp_sentient()
    wr_shrimp = shrimp_sentience_conditioned_welfare_range()

    human_daly_equivalent_dalys_per_1000_shrimp_campaign = sentience_conditioned_dalys_per_1000 * is_sent * wr_shrimp

    if to_print:
        print(f"Mean sentience-conditioned shrimp-DALYs per $1000: {np.mean(sentience_conditioned_dalys_per_1000)}")
        print(f"Mean p(Sentience): {np.mean(is_sent)}")
        print(f"Mean sentience-conditioned welfare range for shrimp: {np.mean(wr_shrimp)}")
        print(f"Mean human-DALYs per 1000 shrimp: {np.mean(human_daly_equivalent_dalys_per_1000_shrimp_campaign)}")
        print("Percentiles:")
        print(sq.get_percentiles(human_daly_equivalent_dalys_per_1000_shrimp_campaign))

    return human_daly_equivalent_dalys_per_1000_shrimp_campaign


shrimp_campaign_human_dalys_per_1000(example_shrimp_project_dict, to_print=True)
