import numpy as np


def get_weighted_linear_utility(x, w):
    """
    Given a vector of "payoffs" from an empirical distribution,
        calculate the weighted linear utility (scalar).
    """
    wu_x = _get_weighted_utility_each_outcome(x, w)
    wlu = np.sum(wu_x)

    return wlu


def weight_function_aggressive(x):
    """
    Given a vector of "payoffs" from an empirical distribution,
        calculate the weight of each payoff.
    """
    w_x = []
    for x_i in x:
        w_i = np.log(1 - x_i) + 1 if x_i < 0 else 1 / (1 + x_i ** (1 / 4))
        w_x.append(w_i)
    w_x = np.array(w_x)
    return w_x


def weight_function_symmetric(x):
    """
    Given a vector of "payoffs" from an empirical distribution,
        calculate the weight of each payoff.
    """
    w_x = []
    for x_i in x:
        w_i = 2 - 1 / (1 + (-1 * x_i) ** (1 / 4)) if x_i < 0 else 1 / (1 + x_i ** (1 / 4))
        w_x.append(w_i)
    w_x = np.array(w_x)

    return w_x


def wlu_aggressive(x):
    return get_weighted_linear_utility(x, weight_function_aggressive)


def wlu_symmetric(x):
    return get_weighted_linear_utility(x, weight_function_symmetric)


# /////// private


def _get_probability(x):
    """
    Given a vector of "payoffs" from an empirical distribution,
        calculate the probability of each payoff.
    """
    n = len(x)
    p_x = np.array([1 / n] * n)

    return p_x


def _get_average_weight(x, w):
    """
    Given a vector of "payoffs" from an empirical distribution,
        calculate the average weight of the payoffs.
    """
    w_x = w(x)
    p_x = _get_probability(x)
    avg_w = np.sum(w_x * p_x)

    return avg_w


def _get_coefficients(x, w):
    """
    Given a vector of "payoffs" from an empirical distribution,
        calculate the coefficients of the linear utility function.
    """
    w_x = w(x)
    avg_w = _get_average_weight(x, w)

    c_x = w_x / avg_w

    return c_x


def _get_weighted_utility_each_outcome(x, w):
    """
    Given a vector of "payoffs" from an empirical distribution,
        calculate the weighted utility of each payoff (vector).
    """
    c_x = _get_coefficients(x, w)
    p_x = _get_probability(x)

    wu_x = c_x * p_x * x
    return wu_x
