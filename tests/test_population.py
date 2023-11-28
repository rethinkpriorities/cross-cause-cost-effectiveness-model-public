import math
import numpy as np
import time

from squigglepy import B, M
import ccm.world.population as population
import ccm.world.space as space


def test_total_life_years_until():
    years = np.array([1, 7])
    life_years = population.get_total_life_years_until(years)
    assert life_years[0] < life_years[1]
    assert life_years[0] * 6 < life_years[1]
    assert life_years[0] * 10 > life_years[1]


def test_total_life_years_until_with_terrestrial_pops(monkeypatch):
    monkeypatch.setattr(space, "sample_expansion_speeds", lambda n,: np.zeros(n))
    perpetual_pop = 20 * B
    current_pop = 8 * B
    century_pop = 11 * B

    monkeypatch.setattr(population, "_sample_populations_per_star", lambda n: np.ones(n) * perpetual_pop)
    years = np.array([1, 5, 100, 120, 1000, 10_000])
    life_years = population.get_total_life_years_until(years)
    assert math.isclose(life_years[0], current_pop, rel_tol=0.1)
    assert math.isclose(life_years[1], current_pop * 5, rel_tol=0.2)
    assert math.isclose(life_years[2], ((current_pop + century_pop) / 2) * 100, rel_tol=0.1)
    assert math.isclose(life_years[3], (current_pop + century_pop) / 2 * 100 + century_pop * 20, rel_tol=0.1)
    assert math.isclose(life_years[4], (century_pop + perpetual_pop) / 2 * 1000, rel_tol=0.3)
    assert math.isclose(life_years[5], perpetual_pop * 10000, rel_tol=0.2)


def test_total_life_years_until_with_high_terrestrial_pops(monkeypatch):
    monkeypatch.setattr(space, "sample_expansion_speeds", lambda n,: np.zeros(n))
    perpetual_pop = 200 * B
    current_pop = 8 * B
    century_pop = 11 * B

    monkeypatch.setattr(population, "_sample_populations_per_star", lambda n: np.ones(n) * perpetual_pop)
    years = np.array([1, 5, 100, 120, 1000, 10_000])
    life_years = population.get_total_life_years_until(years)
    assert math.isclose(life_years[0], current_pop, rel_tol=0.1)
    assert math.isclose(life_years[1], current_pop * 5, rel_tol=0.2)
    assert math.isclose(life_years[2], ((current_pop + century_pop) / 2) * 100, rel_tol=0.1)
    assert math.isclose(life_years[3], (current_pop + century_pop) / 2 * 100 + century_pop * 20, rel_tol=0.2)
    assert math.isclose(life_years[4], (century_pop + perpetual_pop) / 2 * 1000, rel_tol=0.3)
    assert math.isclose(life_years[5], perpetual_pop * 10000, rel_tol=0.2)


def test_total_life_years_until_with_lower_terrestrial_pops(monkeypatch):
    monkeypatch.setattr(space, "sample_expansion_speeds", lambda n,: np.zeros(n))
    perpetual_pop = 50 * M
    current_pop = 8 * B
    century_pop = 11 * B

    monkeypatch.setattr(population, "_sample_populations_per_star", lambda n: np.ones(n) * perpetual_pop)
    years = np.array([1, 5, 100, 120, 1000, 1_000_000])
    life_years = population.get_total_life_years_until(years)
    assert math.isclose(life_years[0], current_pop, rel_tol=0.1)
    assert math.isclose(life_years[1], current_pop * 5, rel_tol=0.2)
    assert math.isclose(life_years[2], ((current_pop + century_pop) / 2) * 100, rel_tol=0.1)
    assert math.isclose(life_years[3], (current_pop + century_pop) / 2 * 100 + century_pop * 20, rel_tol=0.1)
    assert math.isclose(life_years[4], (century_pop + perpetual_pop) / 2 * 1000, rel_tol=0.3)
    assert math.isclose(life_years[5], perpetual_pop * 1_000_000, rel_tol=0.3)


def test_total_life_years_until_grows_non_linearly(monkeypatch):
    monkeypatch.setattr(space, "sample_expansion_speeds", lambda n,: np.ones(n) * 0.003)
    monkeypatch.setattr(population, "_sample_populations_per_star", lambda n: np.ones(n) * 10 * B)
    years = np.array([1, 10_000, 100_000, 10_000_000_000])
    life_years = population.get_total_life_years_until(years)
    assert math.isclose(life_years[0], life_years[1] / years[1], abs_tol=20 * B)
    assert not math.isclose(life_years[0], life_years[3] / years[3], rel_tol=0.25)


def test_total_life_years_handles_large_numbers():
    years = np.arange(50_000.0)

    start_time = time.time()

    population.get_total_life_years_until(years)

    end_time = time.time()
    execution_time = end_time - start_time

    assert execution_time < 0.2, f"Execution time was: {execution_time}s"


def test_population_helpers(monkeypatch):
    monkeypatch.setattr(space, "sample_expansion_speeds", lambda n: np.ones(n) * 0.003)
    monkeypatch.setattr(population, "_sample_populations_per_star", lambda n: np.ones(n) * 10 * B)
    years = np.array([1, 7, 10_000, 100_000])

    terrestrial_life_years = population._get_terrestrial_life_years_until(years)
    extraterrestrial_life_years = population._get_extraterrestrial_life_years_until(
        years,
    )

    assert terrestrial_life_years[0] > extraterrestrial_life_years[0]
    assert terrestrial_life_years[1] > extraterrestrial_life_years[1]
    assert terrestrial_life_years[3] < extraterrestrial_life_years[3]
