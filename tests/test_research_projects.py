import math

import numpy as np
import pytest
import squigglepy as sq
from scipy.sparse import coo_array
from squigglepy.numbers import K, M

import ccm.config as config
import ccm.interventions.intervention_definitions.all_interventions as interventions
from ccm.interventions.intervention import ResultIntervention
from ccm.research_projects.funding_pools.cause_benchmark_fp import CauseBenchmarkInterventionFundingPool
from ccm.research_projects.funding_pools.specified_intervention_fp import SpecifiedInterventionFundingPool
from ccm.research_projects.projects.research_project import FundingProfile, ResearchProject
from ccm.utility.models import DistributionSpec

SIMULATIONS = config.get_simulations()

project_1 = ResearchProject(
    short_name="Test Row 0",
    name="Test Row 0",
    description="Test Research Project.",
    cause="Animals",
    sub_cause="chicken",
    fte_years=sq.norm(0.25, 0.75, lclip=4 / 52),
    conclusions_require_updating=sq.norm(0.3, 0.7, lclip=0, rclip=1),
    target_updating=sq.norm(0.3, 0.7, lclip=0, rclip=1),
    money_in_area_millions=sq.norm(10, 90),
    percent_money_influenceable=sq.norm(0.3, 0.7, lclip=0, rclip=1),
    years_credit=sq.norm(1, 3, lclip=0),
    target_intervention=interventions.get_intervention("Cage-free Chicken Campaign"),
    funding_profile=FundingProfile(
        name="Mixed Funding Sources",
        research_funding_sources={
            SpecifiedInterventionFundingPool(interventions.get_intervention("Cage-free Chicken Campaign")): 0.5,
            SpecifiedInterventionFundingPool(interventions.get_intervention("RP Research Projects"), "RP Capital"): 0.5,
        },
        intervention_funding_sources={
            SpecifiedInterventionFundingPool(interventions.get_intervention("Cage-free Chicken Campaign")): 1.0
        },
    ),
)
project_2 = (
    ResearchProject(
        short_name="Test Row 1",
        name="Test Row 1",
        description="Test Research Project.",
        cause="Animals",
        sub_cause="chicken",
        fte_years=sq.norm(0.25, 0.75, lclip=4 / 52),
        conclusions_require_updating=sq.norm(0, 1, lclip=0, rclip=1),
        target_updating=sq.norm(0, 1, lclip=0, rclip=1),
        money_in_area_millions=sq.norm(10, 90),
        percent_money_influenceable=sq.norm(0, 1, lclip=0, rclip=1),
        years_credit=sq.norm(1, 3, lclip=0),
        target_intervention=interventions.get_intervention("Cage-free Chicken Campaign"),
        funding_profile=FundingProfile(
            name="Mixed Funding Sources",
            research_funding_sources={
                SpecifiedInterventionFundingPool(interventions.get_intervention("Cage-free Chicken Campaign")): 0.5,
                SpecifiedInterventionFundingPool(
                    interventions.get_intervention("RP Research Projects"), "RP Capital"
                ): 0.5,
            },
            intervention_funding_sources={
                SpecifiedInterventionFundingPool(interventions.get_intervention("Cage-free Chicken Campaign")): 1.0
            },
        ),
    ),
)


def test_val_impr_per_year():
    pass_test = True
    scenarios = [
        (10 * M, 0.5),
        (10 * M, 0),
        (10 * M, 1),
        (0, 1),
        (0, 0),
        (0, 0.5),
    ]

    for scenario in scenarios:
        money, change_money = scenario
        mon_infl_per_year = coo_array(
            (np.array(SIMULATIONS * [money]), (np.zeros(SIMULATIONS), np.arange(SIMULATIONS))),
            shape=(1, SIMULATIONS),
        )
        additional_dalys_per_dollar = coo_array(
            (np.array(SIMULATIONS * [change_money]), (np.zeros(SIMULATIONS), np.arange(SIMULATIONS))),
            shape=(1, SIMULATIONS),
        )
        prediction = money * change_money
        results = ResearchProject._calc_val_impr_per_year(mon_infl_per_year, additional_dalys_per_dollar)
        avg_result = np.sum(results.data) / np.multiply(*results.shape)
        if avg_result >= 0:
            if (0.99 * prediction) > avg_result or avg_result > (1.01 * prediction):
                print(f"Failed test: {scenario}")
                print(f"Predicted value improvement: {prediction}")
                print(f"Average of calculated value improvement: {avg_result}")
                pass_test = False
        else:
            if (0.99 * prediction) < avg_result or avg_result < (1.01 * prediction):
                print(f"Failed test: {scenario}")
                print(f"Predicted value improvement: {prediction}")
                print(f"Average of calculated value improvement: {results}")
                pass_test = False
    assert pass_test


def test_estimate_project_costs_project_1():
    mean_staff_costs = (140 * K + 190 * K) / 2
    mean_fte_years = 0.5
    mean_project_cost = mean_staff_costs * mean_fte_years
    est_mean_project_cost = np.mean(project_1._estimate_project_costs(np.ones(SIMULATIONS) * mean_fte_years))
    assert (0.95 * mean_project_cost) < est_mean_project_cost
    assert est_mean_project_cost < (1.05 * mean_project_cost)


def test_amount_money_influenced_per_year():
    scenarios = [
        (0, 0, 0, 0),
        (0, 0, 100 * M, 0),
        (0, 0, 100 * M, 1),
        (1, 0, 100 * M, 1),
        (0, 1, 100 * M, 1),
        (1, 1, 100 * M, 1),
        (0.5, 0.5, 100 * M, 0.5),
    ]
    for scenario in scenarios:
        need_update, prob_update, money, change_money = scenario

        prediction = need_update * prob_update * money * change_money
        results = ResearchProject._calc_amount_money_influenced_per_year(
            np.ones(SIMULATIONS) * need_update,
            np.ones(SIMULATIONS) * prob_update,
            np.ones(SIMULATIONS) * money,
            np.ones(SIMULATIONS) * change_money,
        )
        avg = np.mean(results)
        assert avg == 0 or (
            (0.97 * prediction) < avg and avg < (1.03 * prediction)
        ), f"Failed scenario: {scenario}. Predicted value improvement {prediction}, actual value improvement {avg}."


def test_net_project_impact_project_1():
    val_scenarios = [
        (10 * M, 0.5, 0.5),
        (10 * M, 0, 0),
        (10 * M, 1, 0),
        (10 * M, 0, 1),
        (0, 1, 1),
        (0, 0, 0),
        (0, 0.5, 0.5),
    ]

    mean_staff_costs = (140 * K + 190 * K) / 2

    for scenario in val_scenarios:
        money, prob_influence, change_money = scenario
        pos = money * prob_influence * change_money
        neg = money * (1 - prob_influence) * change_money
        value = pos - neg
        mean_fte_years = 0.5
        mean_project_cost = mean_staff_costs * mean_fte_years
        mean_years_credit = 2
        predicted_net_impact = value * mean_years_credit - mean_project_cost

        project_cost = project_1._estimate_project_costs(np.ones(SIMULATIONS) * mean_fte_years)
        years = project_1._estimate_counterfactual_credit_years()

        results = np.mean(years * value - project_cost)

        if results > 0:
            assert (0.95 * results) < predicted_net_impact
            assert predicted_net_impact < (1.05 * results)
        else:
            assert (0.95 * results) > predicted_net_impact
            assert predicted_net_impact > (1.05 * results)


def test_roi_for_equal_counterfactual():
    daly_efficiency = 100.0
    intervention = ResultIntervention(
        type="result",
        name="Test Intervention",
        result_distribution=DistributionSpec.from_sq(sq.discrete({daly_efficiency: 1.0})),
        area="utility",
    )
    funding_pool = SpecifiedInterventionFundingPool(intervention, "Test Intervention")
    rp = ResearchProject(
        short_name="Equivalence Test",
        name="Equivalence Test",
        description="Some description...",
        cause="GHD",
        sub_cause="",
        fte_years=sq.discrete({1.0: 1.0}),
        conclusions_require_updating=sq.discrete({1.0: 1.0}),
        target_updating=sq.discrete({1.0: 1.0}),
        money_in_area_millions=sq.discrete({1.0: 1.0}),
        percent_money_influenceable=sq.discrete({1.0: 1.0}),
        years_credit=sq.discrete({1.0: 1.0}),
        target_intervention=intervention,
        funding_profile=FundingProfile(
            name="Test Funding Profile",
            research_funding_sources={funding_pool: 1.0},
            intervention_funding_sources={funding_pool: 1.0},
        ),
        cost_per_staff_year=sq.discrete({100_000.0: 1.0}),
    )
    project_assessment = rp.assess_project()
    bottom_line = project_assessment.bottom_lines[funding_pool]

    # Gross DALYs per $1000 should hover around 0
    assert (-daly_efficiency * 0.20) < np.mean(bottom_line.gross_dalys_per_1000.todense()) < (daly_efficiency * 0.20)
    assert (-daly_efficiency * 0.20) < np.median(bottom_line.gross_dalys_per_1000.todense()) < (daly_efficiency * 0.20)

    # Average ROI should hover around -0.01, since we are on average having 0 gross DALYs impact,
    # then subtract $100,000 (equivalent to 1,000 DALYs converted by the source intervention) in FTE costs for net DALYs
    # impact, then divide by this same cost.
    assert math.isclose(bottom_line.average_roi, -1.0, rel_tol=0.15)
    assert math.isclose(np.median(bottom_line.roi.todense()), -1.0, rel_tol=0.15)


def test_exact_fixed_roi():
    target_daly_efficiency = 100.0
    current_daly_efficiency = 50.0
    target_intervention = ResultIntervention(
        type="result",
        name="Target",
        area="utility",
        result_distribution=DistributionSpec.from_sq(sq.discrete({target_daly_efficiency: 1.0})),
    )
    current_intervention = ResultIntervention(
        type="result",
        name="Current",
        area="utility",
        result_distribution=DistributionSpec.from_sq(sq.discrete({current_daly_efficiency: 1.0})),
    )
    funding_pool = SpecifiedInterventionFundingPool(current_intervention, "Current Intervention")
    rp = ResearchProject(
        short_name="Fixed Test",
        name="Fixed Test",
        description="Some description...",
        cause="GHD",
        sub_cause="",
        fte_years=sq.discrete({1.0: 1.0}),
        conclusions_require_updating=sq.discrete({1.0: 1.0}),
        target_updating=sq.discrete({1.0: 1.0}),
        money_in_area_millions=sq.discrete({10.0: 1.0}),
        percent_money_influenceable=sq.discrete({1.0: 1.0}),
        years_credit=sq.discrete({1.0: 1.0}),
        target_intervention=target_intervention,
        funding_profile=FundingProfile(
            name="Test Funding Profile",
            research_funding_sources={funding_pool: 1.0},
            intervention_funding_sources={funding_pool: 1.0},
        ),
        cost_per_staff_year=sq.discrete({100_000.0: 1.0}),
    )
    project_assessment = rp.assess_project()
    bottom_line = project_assessment.bottom_lines[funding_pool]

    # Additional DALYs = (100 - 50) * 10M * 1 = 500M
    # Cost = 1 staff-year * $100K/staff-year = $100K
    # Cost in DALYs = $100K * 50 DALYs/$ = 5M DALYs
    # Net DALYs = 500M - 5M = 495M
    # ROI = 495M / 5M = 99
    # Gross DALYs/$1000 = 500M / 100K = 5000
    assert bottom_line.average_roi == 99
    assert np.median(bottom_line.roi.todense()) == 99

    assert np.mean(bottom_line.gross_dalys_per_1000.todense()) == 5000
    assert np.median(bottom_line.gross_dalys_per_1000.todense()) == 5000


def test_dalys_per_1k_for_split_funding_profile():
    target_daly_efficiency = 100.0
    current_daly_efficiency = 50.0
    target_intervention = ResultIntervention(
        type="result",
        name="Target",
        area="utility",
        result_distribution=DistributionSpec.from_sq(sq.discrete({target_daly_efficiency: 1.0})),
    )
    current_intervention = ResultIntervention(
        type="result",
        name="Current",
        area="utility",
        result_distribution=DistributionSpec.from_sq(sq.discrete({current_daly_efficiency: 1.0})),
    )
    funding_pool_1 = SpecifiedInterventionFundingPool(current_intervention, "Current Intervention")
    funding_pool_2 = SpecifiedInterventionFundingPool(
        interventions.get_intervention("Non-Impactful Spending"), "Non-impactful"
    )
    rp = ResearchProject(
        short_name="Fixed Test",
        name="Fixed Test",
        description="Some description...",
        cause="GHD",
        sub_cause="",
        fte_years=sq.discrete({1.0: 1.0}),
        conclusions_require_updating=sq.discrete({1.0: 1.0}),
        target_updating=sq.discrete({1.0: 1.0}),
        money_in_area_millions=sq.discrete({10.0: 1.0}),
        percent_money_influenceable=sq.discrete({1.0: 1.0}),
        years_credit=sq.discrete({1.0: 1.0}),
        target_intervention=target_intervention,
        funding_profile=FundingProfile(
            name="Test Funding Profile",
            research_funding_sources={funding_pool_1: 0.5, funding_pool_2: 0.5},
            intervention_funding_sources={funding_pool_1: 1.0},
        ),
        cost_per_staff_year=sq.discrete({100_000.0: 1.0}),
    )
    project_assessment = rp.assess_project()

    # If two funding pools split the research costs 50/50, they should have the same
    #   Gross DALYs per $1000 (since this figure doesn't take into account counterfactual costs)
    bottom_line_1 = project_assessment.bottom_lines[funding_pool_1]
    bottom_line_2 = project_assessment.bottom_lines[funding_pool_2]

    assert np.mean(bottom_line_1.gross_dalys_per_1000.todense()) == 5000
    assert np.median(bottom_line_1.gross_dalys_per_1000.todense()) == 5000
    assert np.mean(bottom_line_2.gross_dalys_per_1000.todense()) == 5000
    assert np.median(bottom_line_2.gross_dalys_per_1000.todense()) == 5000


def test_funding_profile_validation():
    non_impactful_pool = SpecifiedInterventionFundingPool(
        interventions.get_intervention("Non-Impactful Spending"), "Non-impactful"
    )
    with pytest.raises(ValueError, match="Invalid research_funding_sources in"):
        FundingProfile(
            "Test Profile 1",
            {
                CauseBenchmarkInterventionFundingPool("Animals", "chicken"): 0.5,
                non_impactful_pool: 0.50001,
            },
            {non_impactful_pool: 1.0},
        )

    with pytest.raises(ValueError, match="Invalid intervention_funding_sources in"):
        FundingProfile(
            "Test Profile 2",
            {
                CauseBenchmarkInterventionFundingPool("Animals", "chicken"): 0.5,
                non_impactful_pool: 0.5,
            },
            {non_impactful_pool: 0.99},
        )
