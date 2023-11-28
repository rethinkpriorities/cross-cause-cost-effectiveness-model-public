from typing import Literal

import numpy as np
import squigglepy as sq
from numpy.typing import NDArray

import ccm.config as config
import ccm.world.risk_types as risk_types
from ccm.contexts import inject_parameters
from ccm.utility.utils import ONE_BASIS_POINT, replace_zero_float_with_tiny
from ccm.world.longterm_params import LongTermParams
from ccm.world.risk_types import RiskType, RiskTypeAI


SIMULATIONS = config.get_simulations()
CUR_YEAR = config.get_current_year()


@inject_parameters
def get_distribution_of_years_to_extinction(params: LongTermParams) -> sq.OperableDistribution:
    """
    Given a list of eras,
    returns a distribution of time until extinction based on each era's annual risk probability
    """
    distributions: list[sq.OperableDistribution] = []
    probabilities: list[float] = []
    start: int = 0
    for era in params.risk_eras:
        era_length = era.get_length()
        era_risk = era.get_annual_extinction_probability()
        end = start + era_length - 1
        next_dist = _approximate_geometric(start, end, era_risk)
        if era == params.risk_eras[-1]:
            next_prob = 1 - sum(probabilities)
        else:
            next_prob = (1 - sum(probabilities)) * (1 - (1 - era_risk) ** era_length)
        distributions.append(next_dist)
        probabilities.append(next_prob)
        start = end + 1

    mix = sq.mixture(distributions, probabilities)
    return mix


@inject_parameters
def get_cumulative_catastrophe_risk(
    params: LongTermParams,
    risk_type: RiskType,
    num_years: NDArray[np.int64],
) -> NDArray[np.float64]:
    # To get cumulative catastrophe ratios, compare probability ratio of catastrophe to extinction risk with
    # probability of extinction risk
    yearly_risk = params.catastrophe_extinction_risk_ratios[risk_type] * get_average_risk_over_years_by_type(
        risk_type,
        num_years,
    )

    cumulative = 1 - ((1 - yearly_risk) ** num_years)
    return cumulative


def one_basis_point_percent_of_each_xrisk_by_type(
    num_years: NDArray[np.int64],
) -> dict[RiskType | Literal["total"] | Literal["non-ai"], NDArray[np.float64]]:
    basis_pt_dict = {}
    for risk_type in risk_types.get_risk_types():
        risk = get_cumulative_risk_over_years_by_type(risk_type, num_years)
        basis_pt_dict[risk_type] = ONE_BASIS_POINT / np.vectorize(replace_zero_float_with_tiny)(risk)
    basis_pt_dict["total"] = ONE_BASIS_POINT / get_cumulative_risk_over_years(num_years)
    basis_pt_dict["non-ai"] = ONE_BASIS_POINT / np.vectorize(replace_zero_float_with_tiny)(
        get_cumulative_risk_over_years(num_years)
        - get_cumulative_risk_over_years_by_type(RiskTypeAI.MISALIGNMENT, num_years)
        - get_cumulative_risk_over_years_by_type(RiskTypeAI.MISUSE, num_years)
    )

    return basis_pt_dict


@inject_parameters
def get_average_total_risk_over_years(params: LongTermParams, num_years: NDArray[np.int64]) -> NDArray[np.float64]:
    """Returns the mean yearly risk across multiple eras, staring with the first era and going for num_years"""
    max_year_sampled = max(num_years)
    risks_by_year = np.zeros(max_year_sampled)
    idx = 0
    for era in params.risk_eras:
        risks_by_year[idx : min(idx + era.get_length(), max_year_sampled)] = era.get_annual_extinction_probability()
        idx += era.get_length()
        if idx > max_year_sampled:
            break

    all_years = np.unique(num_years)
    year_x_avg_risk = {year: np.mean(risks_by_year[:year]) for year in all_years}

    u, inv = np.unique(num_years, return_inverse=True)
    avg_risks = np.array([year_x_avg_risk[year] for year in u])
    return avg_risks[inv]


@inject_parameters
def get_average_risk_over_years_by_type(
    params: LongTermParams,
    risk_type: RiskType,
    num_years: NDArray[np.int64],
) -> NDArray[np.float64]:
    """Returns the mean yearly risk across multiple eras by type, staring with the first era and going for num_years"""
    max_year_sampled = max(num_years)
    risks_by_year = np.zeros(max_year_sampled)
    idx = 0
    for era in params.risk_eras:
        risks_by_year[idx : min(idx + era.get_length(), max_year_sampled)] = era.get_absolute_risks()[risk_type]
        idx += era.get_length()
        if idx > max_year_sampled:
            break

    all_years = np.unique(num_years)
    year_x_avg_risk = {year: np.mean(risks_by_year[:year]) for year in all_years}

    u, inv = np.unique(num_years, return_inverse=True)
    avg_risks = np.array([year_x_avg_risk[year] for year in u])
    return avg_risks[inv]


@inject_parameters
def get_average_catastrophe_risk_over_years_by_type(
    params: LongTermParams,
    risk_type: RiskType,
    num_years: NDArray[np.int64],
) -> NDArray[np.float64]:
    # To get cumulative catastrophe ratios, compare probability ratio of catastrophe to extinction risk with
    # probability of extinction risk
    yearly_risk = params.catastrophe_extinction_risk_ratios[risk_type] * get_average_risk_over_years_by_type(
        risk_type,
        num_years,
    )

    return yearly_risk


def get_cumulative_risk_over_years(num_years: NDArray[np.int64]) -> NDArray[np.float64]:
    """given eras and a number of years, returns the average risk across those eras over the next num_years"""
    return get_average_total_risk_over_years(num_years) * num_years


def get_cumulative_risk_over_years_by_type(risk_type: RiskType, num_years: NDArray[np.int64]) -> NDArray[np.float64]:
    """
    Given eras, a irsk type, and a number of years, returns the average risk across those eras over the next num_years
    """
    return get_average_risk_over_years_by_type(risk_type, num_years) * num_years


def get_by_type_year(params: LongTermParams, risk_type: RiskType, target_year: int) -> float:
    """given eras, a risk type, and a ayear, returns the total xrisk by that year"""
    idx_year = CUR_YEAR
    for era in params.risk_eras:
        idx_year += era.get_length()
        if idx_year > target_year:
            return era.get_absolute_risks()[risk_type]

    return 0.0


# ///////////////// Private Functions /////////////////


# This should really be a geometric distribution, but it approximates it ok.
def _approximate_geometric(bottom: int, top: int, iteration_probability: float) -> sq.OperableDistribution:
    def floor_and_add_bottom(val):
        return np.floor(val + bottom)

    exponential_distribution = sq.exponential(1 / iteration_probability, lclip=0, rclip=(top - bottom))
    dist = sq.dist_fn(exponential_distribution, floor_and_add_bottom)
    assert isinstance(dist, sq.OperableDistribution)
    return dist
