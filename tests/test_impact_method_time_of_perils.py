import math

import numpy as np
from squigglepy import B

import ccm.config as config
import ccm.world.population as population
import ccm.world.space as space
from ccm.contexts import using_parameters
from ccm.interventions.xrisk.impact.time_of_perils_impact import TimeOfPerils
from ccm.parameters import Parameters
from ccm.world.longterm_params import LongTermParams
from ccm.world.risk_types import RiskTypeAI

SIMULATIONS = config.get_simulations()


def test_time_of_perils_delivers_plausible_values(monkeypatch) -> None:
    monkeypatch.setattr(space, "sample_expansion_speeds", lambda n: np.ones(n) * 0.003)
    monkeypatch.setattr(population, "_sample_populations_per_star", lambda n: np.ones(n) * 10 * B)
    half_off = np.ones(SIMULATIONS) * 0.5
    nothing = np.zeros(SIMULATIONS)

    with using_parameters(Parameters(longterm_params=LongTermParams(max_creditable_year=100000))):
        impact = TimeOfPerils().calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            nothing,
            np.array(SIMULATIONS * [10]),
        )
    assert np.median(impact) == 0
    assert np.mean(impact) > 0
    assert np.mean(impact) > 0


def test_time_of_perils_delivers_changes_based_on_intervention_length(monkeypatch):
    monkeypatch.setattr(space, "sample_expansion_speeds", lambda n: np.ones(n) * 0.003)
    monkeypatch.setattr(population, "_sample_populations_per_star", lambda n: np.ones(n) * 10 * B)
    half_off = np.ones(SIMULATIONS) * 0.5
    nothing = np.zeros(SIMULATIONS)
    model = TimeOfPerils()

    with using_parameters(Parameters(longterm_params=LongTermParams(max_creditable_year=100000))):
        impact_short = model.calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            nothing,
            np.array(SIMULATIONS * [1]),
        )
        impact_long = model.calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            nothing,
            np.array(SIMULATIONS * [100]),
        )
    avg_impact_short = np.median(impact_short)
    avg_impact_long = np.median(impact_long)

    assert avg_impact_short <= avg_impact_long
    assert math.isclose(avg_impact_short * 10, avg_impact_long, rel_tol=avg_impact_short)


def test_time_of_perils_delivers_changes_based_on_risk_amount(monkeypatch) -> None:
    monkeypatch.setattr(space, "sample_expansion_speeds", lambda n: np.ones(n) * 0.003)
    monkeypatch.setattr(population, "_sample_populations_per_star", lambda n: np.ones(n) * 10 * B)
    half_off = np.ones(SIMULATIONS) * 0.5
    tenth_off = np.ones(SIMULATIONS) * 0.1
    nothing = np.zeros(SIMULATIONS)

    with using_parameters(Parameters(longterm_params=LongTermParams(max_creditable_year=100000))):
        impact_small = TimeOfPerils().calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            tenth_off,
            nothing,
            np.array(SIMULATIONS * [10]),
        )
        impact_big = TimeOfPerils().calc_impact_given_prop_risk_reduction(
            RiskTypeAI.MISALIGNMENT,
            half_off,
            nothing,
            np.array(SIMULATIONS * [10]),
        )
    assert np.median(impact_small) <= np.median(impact_big)
