from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

import ccm.config as config
import ccm.interventions.xrisk.impact.utils.years_credit_calculator as years_credit_calculator
import ccm.utility.risk_calculator as risk_calculator
import ccm.utility.squigglepy_wrapper as sqw
import ccm.world.population as population
from ccm.contexts import inject_parameters
from ccm.world.longterm_params import LongTermParams
from ccm.world.population import WORLD_POPULATION_NOW
from ccm.world.risk_types import RiskType

CUR_YEAR = config.get_current_year()
SIMULATIONS = config.get_simulations()


class ImpactMethod(ABC):
    """Abstract class for strategies for counting impact in Healthy Life Years Saved (~DALYs averted) based on
    how much risk was reduced.
    """

    def __init__(self, name: str, description: str) -> None:
        self.__name = name
        self.__description = description

    @abstractmethod
    def calc_impact_given_prop_risk_reduction(
        self,
        risk_type: RiskType,
        proportion_extinction_risk_changed: NDArray[np.float64],
        proportion_catastrophe_risk_changed: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> NDArray[np.float64]:
        """
        Calculates DALY equivalents in extinction and catastrophe deaths averted,
        from a given proportion of risk reduced. Cut off after max_creditable_years.
        Defined in child classes.
        """

    def get_name(self) -> str:
        return self.__name

    def get_description(self) -> str:
        return self.__description

    # ///////////////// Private Methods /////////////////

    def calc_base_impact(
        self,
        risk_type: RiskType,
        proportion_extinction_risk_changed: NDArray[np.float64],
        proportion_catastrophe_risk_changed: NDArray[np.float64],
        years_risk_changed: NDArray[np.int64],
    ) -> NDArray[np.float64]:
        """Calculate impact in DALYs. Cut off after residual creditable. Used by classes inheriting from this absract
        class."""

        prob_good = len(np.where(proportion_extinction_risk_changed > 0)[0]) / np.count_nonzero(
            proportion_extinction_risk_changed
        )
        good_or_bad = np.where(np.random.random(len(proportion_extinction_risk_changed)) < prob_good, 1, -1)

        # Separately calculate the value of life lost due to extinction and to current living population
        # Calculate the value of life lost to extinction
        life_years_changed_xrisk = self._sample_life_years_changed_xrisk(
            risk_type,
            good_or_bad,
            years_risk_changed,
        )

        # Calculate the value of life lost to non-extinction level catastrophes
        # (long term population effects due to catastrophes are ignored)
        life_years_changed_catastrophe = self._sample_life_years_changed_catastrophe(
            risk_type,
            good_or_bad,
            years_risk_changed,
        )

        return life_years_changed_xrisk + life_years_changed_catastrophe

    # //////////// Private ////////////////

    def _sample_life_years_changed_catastrophe(
        self,
        risk_type: RiskType,
        proportion_catastrophe_risk_changed: NDArray[np.float64],
        years_risk_changed: NDArray[np.int64],
    ) -> NDArray[np.float64]:
        """Generates random sample of how many life years gained or lost from catastrophe risk changes"""
        # Probability a catastrophe will occur at some point during the period this intervention covers
        catastrophe_probability = risk_calculator.get_cumulative_catastrophe_risk(
            risk_type,
            years_risk_changed,
        )

        # Deaths if a catastrophe were to occur
        catastrophe_results = self._sample_catastrophe_deaths(
            risk_type=risk_type,
            world_pop=WORLD_POPULATION_NOW,
        )
        # Filter out those catastrophes that wouldn't be averted

        probability_changed_signs = np.where(proportion_catastrophe_risk_changed < 0, -1, 1)
        abs_proportion_catastrophe_risk_changed = np.abs(proportion_catastrophe_risk_changed)
        aversion_probability = abs_proportion_catastrophe_risk_changed * catastrophe_probability
        catastrophe_samples = np.where(
            sqw.sample_probabilities(SIMULATIONS) < aversion_probability,
            catastrophe_results,
            0,
        )
        # Some of these might cross over max_creditable_year for very short windows.
        # Go from number of people killed to number of life years lost
        return population.calculate_life_years_lost(catastrophe_samples) * probability_changed_signs

    def _sample_life_years_changed_xrisk(
        self,
        risk_type: RiskType,
        proportion_extinction_risk_changed: NDArray[np.float64],
        years_risk_changed: NDArray[np.int64],
    ) -> NDArray[np.float64]:
        """
        Given a list of eras, a proportion of a risk changed, and a number of years that risk is changed,
        randomly generates array of amounts of time an xrisk reduction delays exctinction.
        """

        risk_type_extinction_risk = risk_calculator.get_average_risk_over_years_by_type(risk_type, years_risk_changed)
        total_extinction_risk = risk_calculator.get_average_total_risk_over_years(years_risk_changed)
        fraction_total_extinction_risk = risk_type_extinction_risk / total_extinction_risk
        changes_in_extinction_probability = proportion_extinction_risk_changed * fraction_total_extinction_risk

        # Given absolute probability changes and future risks, calculate the expected time until an extinction event.
        years_extinction_delayed_samples = self._sample_intervention_delays_to_extinction(
            changes_in_extinction_probability=changes_in_extinction_probability,
            years_risk_changed=years_risk_changed,
        )

        # The years could be positive or negative. Store the sign for later use, and convert to absolute value.
        effect_signs = np.where(years_extinction_delayed_samples < 0, -1, 1)
        absolute_value_years = np.abs(years_extinction_delayed_samples)

        # Trim the num years exinction delayed to the max creditable year. We don't care beyond that.
        absolute_value_years = self.trim_to_max_year(absolute_value_years)
        life_years_changed_xrisk = population.get_total_life_years_until(absolute_value_years)

        return life_years_changed_xrisk * effect_signs

    def _sample_intervention_delays_to_extinction(
        self,
        changes_in_extinction_probability: NDArray[np.float64],
        years_risk_changed: NDArray[np.int64],
    ) -> NDArray[np.float64]:
        """Given a list of eras and a sampling of changes of absolute probability, call the years credit calculator to
        sample whether those probability changes makes a difference and how big of a difference they make."""
        dist = risk_calculator.get_distribution_of_years_to_extinction()
        years_extinction_delayed_samples = years_credit_calculator.sample_years_credit(
            dist,
            changes_in_extinction_probability,
            years_risk_changed,
        )

        return years_extinction_delayed_samples

    @staticmethod
    @inject_parameters
    def trim_to_max_year(
        params: LongTermParams,
        years_extinction_delayed_samples: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Trims years credit to a max year."""
        if params.max_creditable_year is None:
            return years_extinction_delayed_samples
        years_extinction_delayed_samples[years_extinction_delayed_samples > (params.max_creditable_year - CUR_YEAR)] = (
            params.max_creditable_year - CUR_YEAR
        )
        return years_extinction_delayed_samples

    @staticmethod
    @inject_parameters
    def _sample_catastrophe_deaths(
        params: LongTermParams,
        risk_type: RiskType,
        world_pop: int = WORLD_POPULATION_NOW,
    ) -> NDArray[np.float64]:
        proportion_dead = sqw.sample(
            params.catastrophe_intensities[risk_type].get_distribution(),
            n=SIMULATIONS,
        )
        return world_pop * proportion_dead
