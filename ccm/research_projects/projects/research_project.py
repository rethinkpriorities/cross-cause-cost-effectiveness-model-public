from copy import deepcopy

import numpy as np
import squigglepy as sq
from numpy.typing import NDArray
from scipy.sparse import coo_array
from squigglepy.numbers import K, M

import ccm.config as config
import ccm.utility.squigglepy_wrapper as sqw
from ccm.interventions.intervention_definitions.all_interventions import SomeIntervention
from ccm.research_projects.funding_pools.funding_pool import FundingPool
from ccm.research_projects.projects.bottom_line import BottomLine
from ccm.research_projects.projects.funding_profile import FundingProfile
from ccm.research_projects.projects.project_assessment import ProjectAssessment
from ccm.utility.squigglepy_wrapper import RNG
from ccm.utility.utils import enforce_min_absolute_value, match_coo_axis_lengths

SIMULATIONS = config.get_simulations()
DOLLAR_TO_1000_D_CONVERSION = 1_000
DALY_EFFICIENCY_MIN_ABSOLUTE_VALUE = 1e-20


class ResearchProject:
    """A Rethink Priorities Research Project, with logic for assessing costs, ROI, and impact of the project from the
    perspective of various funders.
    """

    # Hardcoded salary costs
    DEFAULT_SALARY_DISTRIBUTION = sq.norm(140 * K, 190 * K, lclip=100 * K, rclip=220 * K)

    def __init__(
        self,
        short_name: str,
        name: str,
        description: str,
        cause: str,
        sub_cause: str,
        fte_years: sq.OperableDistribution,
        # Probability that the target intervention is viable and discoverable
        conclusions_require_updating: sq.OperableDistribution,
        # Probability that the funder will alter their views in light of the research project
        target_updating: sq.OperableDistribution,
        money_in_area_millions: sq.OperableDistribution,
        # Percentage of money that the research project would move to the target, conditional on viability
        percent_money_influenceable: sq.OperableDistribution,
        # Years of affect of the discovery. After this, it is assumed that the intervention would be found regardless
        years_credit: sq.OperableDistribution,
        # The hypothetical new intervention that might be discovered
        target_intervention: SomeIntervention,
        # Where money comes from to fund research and support <-- this includes both the support for existing
        # interventions and research
        funding_profile: FundingProfile,
        cost_per_staff_year: sq.OperableDistribution = DEFAULT_SALARY_DISTRIBUTION,
    ) -> None:
        self.short_name = short_name
        self.name = name
        self.description = description
        self.cause = cause
        self.sub_cause = sub_cause
        self.target_intervention = target_intervention
        self.fte_years = fte_years
        self.conclusions_require_updating = conclusions_require_updating
        self.target_updating = target_updating
        self.money_in_area_millions = money_in_area_millions
        self.percent_money_influenceable = percent_money_influenceable
        self.years_credit = years_credit
        self.funding_profile = funding_profile
        self.cost_per_staff_year = cost_per_staff_year

    def assess_project(self) -> ProjectAssessment:
        """Assess the gain in DALYs of pursuing this research project
        and wraps return data in ProjectAssessment object"""
        # Research Project gains come from shifting money from an existing 'current' intervention to a new
        # 'target' intervention. Impact depends on the probability and amount of money shift.
        # Cost is weighed in terms of lost good done by
        #   * shifting away from an existing intervention (support cost)
        #   * project costs + staff time (funding cost)
        # Project funding costs themselves come from the counterfactual use that funding would have
        # if not spent on research.

        fte_years_for_project = self._estimate_fte_years()
        # Funding costs, which affect the positive return, are assessed in terms of staff time.
        # Project efficiency to RP is also assessed in terms of staff time.
        total_project_costs = self._estimate_project_costs(fte_years_for_project)

        # Research speeds up discovery by 'credit' number of years. After that many years,
        # assume relevant discoveries would be made by others (without any further cost).
        years_credit = self._estimate_counterfactual_credit_years()

        # Estimate the DALYs produced if support were not redirected from
        # existing interventions to the intevention uncovered by this research project.
        counterfactual_int_dalys_per_dollar = ResearchProject._estimate_weighted_dalys_per_dollar(
            self.funding_profile.intervention_funding_sources
        )

        # Estimate DALYs producted if support were redirected from existing interventions to this research project.
        samples, zeros = self.target_intervention.estimate_dalys_per_1000()

        sample_length_with_zeros = len(samples) + zeros
        positions = RNG.choice(sample_length_with_zeros, size=len(samples), replace=False)
        sparse_samples = coo_array(
            (samples, (np.zeros(len(samples)), positions)),
            shape=(1, sample_length_with_zeros),
        )

        target_int_dalys_per_dollar = sparse_samples / DOLLAR_TO_1000_D_CONVERSION

        # the source and the target in interventions may have different total lengths, because the lower the probability
        # of an intervention being effective, the more zeros will have be added when calling its
        # `.estimate_dalys_per_1000()` method. Therefore, before any comparison is made between the two, we need to
        # resize one of them so that they have the same lengths, while keeping the right proportion of zeros
        resized_target_int_dalys_per_dollar, resized_counterfactual_int_dalys_per_dollar = match_coo_axis_lengths(
            target_int_dalys_per_dollar,
            counterfactual_int_dalys_per_dollar,
            axis=1,
        )

        # The difference is the net gain in DALYs, per dollar.
        additional_dalys_per_dollar = deepcopy(resized_target_int_dalys_per_dollar)
        additional_dalys_per_dollar.data = (  # type: ignore  # scipy-related error
            resized_target_int_dalys_per_dollar.data - resized_counterfactual_int_dalys_per_dollar.data
        )

        # Impact only lasts as long as years of advance RP offers to interventions inevitable discovery.
        # Adjust DALY gain by years of discovery advance AND by percentage of support to be shifted.
        gross_impact_in_dalys = self._estimate_gross_impact_in_dalys(years_credit, additional_dalys_per_dollar)

        cost_segments_dollars = self._segment_costs_by_funding_pool(total_project_costs)
        cost_segments_dalys = self._convert_cost_segments_to_dalys(cost_segments_dollars)

        # Take difference between positive impact and project's funding costs in DALYs.
        net_impact_in_dalys = ResearchProject._calc_net_impact(gross_impact_in_dalys, cost_segments_dalys)

        # Calcuate impact as ratio of staff time.
        fte_years_for_project_resized = RNG.choice(fte_years_for_project, size=net_impact_in_dalys.nnz, replace=False)
        net_dalys_per_staff_year = deepcopy(net_impact_in_dalys)
        net_dalys_per_staff_year.data = net_impact_in_dalys.data / fte_years_for_project_resized

        bottom_lines = ResearchProject._calc_bottom_lines_for_each_funding_pool(
            gross_impact_in_dalys,
            net_impact_in_dalys,
            total_project_costs,
            cost_segments_dollars,
            cost_segments_dalys,
        )

        return ProjectAssessment(
            short_name=self.short_name,
            cost=total_project_costs,
            years_credit=years_credit,
            gross_impact_dalys=gross_impact_in_dalys,
            net_impact_dalys=net_impact_in_dalys,
            net_dalys_per_staff_year=net_dalys_per_staff_year,
            bottom_lines=bottom_lines,
        )

    # ///////////////// Private Instance Methods /////////////////

    def _estimate_fte_years(self) -> NDArray[np.float64]:
        fte_years_for_project = sqw.sample(self.fte_years, n=SIMULATIONS)
        return fte_years_for_project

    def _estimate_counterfactual_credit_years(self) -> NDArray[np.float64]:
        """Estimate how many years of counterfactual credit RP gets for the project. In other words, in how many years
        would the Target Intervention or better have been discovered by the funder without the Research Project?
        """
        credit_years = sqw.sample(self.years_credit, n=SIMULATIONS)
        return credit_years

    def _estimate_gross_impact_in_dalys(
        self,
        num_years_credit: NDArray[np.float64],
        additional_dalys_per_dollar: coo_array,
    ) -> coo_array:
        """Estimate gross amount of DALYs produced by the Research Project, based on how much of the relevant cause
        area money we expect to influence, how many additional DALYs per dollar we are expecting from the Target
        Intervention as compared to the counterfactual, and how many years of counterfactual impact we can take credit
        for.
        """

        non_zero_samples = additional_dalys_per_dollar.nnz
        prob_conclusions_need_updating = sqw.sample(self.conclusions_require_updating, n=non_zero_samples)
        prob_target_updating = sqw.sample(self.target_updating, n=non_zero_samples)
        money_in_area_per_year = sqw.sample(self.money_in_area_millions, n=non_zero_samples) * M
        percent_money_influenced_per_year = sqw.sample(self.percent_money_influenceable, n=non_zero_samples)

        influenced_money_per_year = ResearchProject._calc_amount_money_influenced_per_year(
            prob_conclusions_need_updating,
            prob_target_updating,
            money_in_area_per_year,
            percent_money_influenced_per_year,
        )

        influenced_money_per_year_sparse = deepcopy(additional_dalys_per_dollar)  # copy shape and non-zero positions
        influenced_money_per_year_sparse.data = influenced_money_per_year

        impr_per_year = ResearchProject._calc_val_impr_per_year(
            influenced_money_per_year_sparse,
            additional_dalys_per_dollar,
        )

        est_impact = deepcopy(impr_per_year)  # copy matrix shape and non-zero positions
        est_impact.data = impr_per_year.data * num_years_credit  # type: ignore  # scipy-related typing error

        return est_impact

    def _estimate_project_costs(self, fte_years_for_project: NDArray[np.float64]) -> NDArray[np.float64]:
        staff_cost_per_fte_year = sqw.sample(self.cost_per_staff_year, n=SIMULATIONS)
        project_cost = staff_cost_per_fte_year * fte_years_for_project

        return project_cost

    def _segment_costs_by_funding_pool(
        self, total_project_costs: NDArray[np.float64]
    ) -> dict[FundingPool, NDArray[np.float64]]:
        """Split the total_project_costs into cost segments for each Funding Pool, based on each Funding Pool's weight
        in the Funding Profile.
        """
        cost_pools_dollars = {}
        for pool, weight in self.funding_profile.research_funding_sources.items():
            cost_pools_dollars[pool] = weight * total_project_costs
        return cost_pools_dollars

    def _convert_cost_segments_to_dalys(
        self, cost_segments_dollars: dict[FundingPool, NDArray[np.float64]]
    ) -> dict[FundingPool, coo_array]:
        """Using each Funding Pools counterfactual conversion rate, convert each Cost Segment from Dollars to DALYs."""
        cost_segments_dalys = {}
        for pool, segment_dollar_cost in cost_segments_dollars.items():
            cost_segments_dalys[pool] = pool.convert_dollars_to_dalys(segment_dollar_cost)
        return cost_segments_dalys

    # ///////////////// Private Static Methods /////////////////

    @staticmethod
    def _estimate_weighted_dalys_per_dollar(weighted_funding_pools: dict[FundingPool, float]) -> coo_array:
        """Estimate a weighted average DALYs/dollar conversion rate based on the given Funding Pools."""
        dalys_per_dollar: coo_array | None = None
        for pool, weight in weighted_funding_pools.items():
            weighted_dalys_per_dollar = pool.convert_dollars_to_dalys(np.ones(SIMULATIONS)) * weight
            if dalys_per_dollar is None:
                dalys_per_dollar = weighted_dalys_per_dollar
            else:
                dalys_per_dollar, weighted_dalys_per_dollar = match_coo_axis_lengths(
                    dalys_per_dollar,
                    weighted_dalys_per_dollar,
                    axis=1,
                )
                dalys_per_dollar.data += weighted_dalys_per_dollar.data  # type: ignore  # scipy-related typing error

        assert dalys_per_dollar is not None, "Empty funding pool"
        return dalys_per_dollar

    @staticmethod
    def _calc_amount_money_influenced_per_year(
        prob_conclusions_need_updating: NDArray[np.float64],
        prob_target_updating: NDArray[np.float64],
        money_in_area_per_year: NDArray[np.float64],
        percent_money_influenced_per_year: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        rand_1 = sqw.sample_probabilities(len(prob_conclusions_need_updating))
        rand_2 = sqw.sample_probabilities(len(prob_target_updating))
        is_successful = np.logical_and(rand_1 < prob_conclusions_need_updating, rand_2 < prob_target_updating)

        return is_successful * money_in_area_per_year * percent_money_influenced_per_year

    @staticmethod
    def _calc_net_impact(
        gross_impact_in_dalys: coo_array,
        cost_segments_dalys: dict[FundingPool, coo_array],
    ) -> coo_array:
        """Net-Impact-in-DALYs is defined as (gross impact in DALYS - total cost in DALYs). Note that the Gross Impact
        and Costs must both be in the same unit.
        """
        net_impact_in_dalys = deepcopy(gross_impact_in_dalys)  # copy matrix shape and non-zero positions
        for cost_segment_dalys in cost_segments_dalys.values():
            net_impact_in_dalys.data = gross_impact_in_dalys.data - cost_segment_dalys.data  # type: ignore
        return net_impact_in_dalys

    @staticmethod
    def _calc_val_impr_per_year(
        mon_infl_per_year: coo_array,
        additional_dalys_per_dollar: coo_array,
    ) -> coo_array:
        """Calculate amount of gross DALYs obtained by the Research Project."""

        impr_per_year = deepcopy(mon_infl_per_year)  # copy matrix shape and non-zero positions
        impr_per_year.data = mon_infl_per_year.data * additional_dalys_per_dollar.data  # type: ignore  # scipy's fault
        return impr_per_year

    @staticmethod
    def _calc_bottom_lines_for_each_funding_pool(
        gross_impact_in_dalys: coo_array,
        net_impact_in_dalys: coo_array,
        total_project_costs: NDArray[np.float64],
        cost_segments_dollars: dict[FundingPool, NDArray[np.float64]],
        cost_segments_dalys: dict[FundingPool, coo_array],
    ) -> dict[FundingPool, BottomLine]:
        """Calculates the bottom-line figures per Funding Pool."""
        bottom_lines = {}
        for pool, segment_dollar_cost in cost_segments_dollars.items():
            bottom_lines[pool] = ResearchProject._calc_bottom_line_for_funding_pool(
                gross_impact_in_dalys,
                net_impact_in_dalys,
                total_project_costs,
                segment_dollar_cost,
                cost_segments_dalys[pool],
            )
        return bottom_lines

    @staticmethod
    def _calc_bottom_line_for_funding_pool(
        gross_impact_in_dalys: coo_array,
        net_impact_in_dalys: coo_array,
        total_cost_dollars: NDArray[np.float64],
        segment_cost_dollars: NDArray[np.float64],
        segment_cost_in_dalys: coo_array,
    ) -> BottomLine:
        """Calculates the bottom-line figures for a given Funding Pool. In order to prevent double-counting of impact,
        we assign a proportion_of_credit weighted by how much of the total cost in dollars was covered by the given
        Funding Pool.
        """
        # Note: Enforcing a minimum absolute value for current_DALYs_per_dollar,
        # to prevent division overflows and inf ratios
        segment_cost_in_dalys.data = enforce_min_absolute_value(
            segment_cost_in_dalys.data,  # type: ignore  # scipy's fault
            DALY_EFFICIENCY_MIN_ABSOLUTE_VALUE,
        )

        proportion_credit = segment_cost_dollars / total_cost_dollars
        segment_net_impact_in_dalys_non_zeros = net_impact_in_dalys.data * proportion_credit  # type: ignore
        roi_non_zeros = segment_net_impact_in_dalys_non_zeros.data / segment_cost_in_dalys.data

        roi = deepcopy(segment_cost_in_dalys)  # copy matrix shape and non-zero positions
        roi.data = roi_non_zeros

        ave_segment_net_impact_in_dalys = np.sum(segment_net_impact_in_dalys_non_zeros) / np.multiply(
            *segment_cost_in_dalys.shape,
        )
        ave_segment_cost_dollars = np.sum(segment_cost_in_dalys.data) / np.multiply(*segment_cost_in_dalys.shape)
        average_roi = ave_segment_net_impact_in_dalys / ave_segment_cost_dollars

        segment_gross_impact_in_dalys_non_zeros = gross_impact_in_dalys.data * proportion_credit  # type: ignore
        gross_dalys_per_1000_non_zeros = DOLLAR_TO_1000_D_CONVERSION * (
            segment_gross_impact_in_dalys_non_zeros / segment_cost_dollars.data
        )

        gross_dalys_per_1000 = deepcopy(gross_impact_in_dalys)  # copy matrix shape and non-zero positions
        gross_dalys_per_1000.data = gross_dalys_per_1000_non_zeros

        return BottomLine(roi, average_roi, gross_dalys_per_1000)
