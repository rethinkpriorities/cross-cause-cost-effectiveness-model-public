"""
Loads projects from projects.csv file.
"""

import pandas as pd

import ccm.config as config
import ccm.interventions.intervention_definitions.all_interventions as interventions
import ccm.utility.utils as utils
from ccm.research_projects.funding_pools.specified_intervention_fp import SpecifiedInterventionFundingPool
from ccm.research_projects.projects.research_project import FundingProfile, ResearchProject


def read_projects() -> list[ResearchProject]:
    p = _get_projects_df()

    output = []
    for row in range(len(p.index)):
        target_intervention_name = p.iloc[row]["Target Intervention"]
        target_intervention = interventions.get_intervention(target_intervention_name)
        current_intervention_name = p.iloc[row]["Current Intervention"]
        current_intervention = interventions.get_intervention(current_intervention_name)
        funding_pool_name = f"Counterfactual - {current_intervention_name}"
        funding_pool = SpecifiedInterventionFundingPool(current_intervention, funding_pool_name)
        project = ResearchProject(
            short_name=p.iloc[row]["Short name"],
            name=p.iloc[row]["Project/Question"],
            description=p.iloc[row]["Description"],
            cause=p.iloc[row]["Cause"],
            sub_cause=p.iloc[row]["Sub-cause"],
            fte_years=utils.create_distribution(
                distribution_type=p.iloc[row]["years distribution"],
                range_low=p.iloc[row]["years FTE - low"],
                range_high=p.iloc[row]["years FTE - high"],
                lclip=p.iloc[row]["years FTE lclip"],
                rclip=p.iloc[row]["years FTE rclip"],
            ),
            conclusions_require_updating=utils.create_distribution(
                distribution_type=p.iloc[row]["concl updating distribution"],
                range_low=p.iloc[row]["conclusions that require updating - low"],
                range_high=p.iloc[row]["conclusions that require updating - high"],
                lclip=p.iloc[row]["conclusions lclip"],
                rclip=p.iloc[row]["conclusions rclip"],
            ),
            target_updating=utils.create_distribution(
                distribution_type=p.iloc[row]["target_updating distribution"],
                range_low=p.iloc[row]["target_updating - low"],
                range_high=p.iloc[row]["target_updating - high"],
                lclip=p.iloc[row]["target_updating lclip"],
                rclip=p.iloc[row]["target_updating rclip"],
            ),
            money_in_area_millions=utils.create_distribution(
                distribution_type=p.iloc[row]["influenceable distribution"],
                range_low=p.iloc[row]["$M influenceable per year low"],
                range_high=p.iloc[row]["$M influenceable per year high"],
                lclip=p.iloc[row]["influenceable lclip"],
                rclip=p.iloc[row]["influenceable rclip"],
            ),
            percent_money_influenceable=utils.create_distribution(
                distribution_type=p.iloc[row]["percent money influenceable - distribution"],
                range_low=p.iloc[row]["percent money influenceable - low"],
                range_high=p.iloc[row]["percent money influenceable - high"],
                lclip=p.iloc[row]["percent influenceable lclip"],
                rclip=p.iloc[row]["percent influenceable rclip"],
            ),
            years_credit=utils.create_distribution(
                distribution_type=p.iloc[row]["years counterfactual credit - distribution"],
                range_low=p.iloc[row]["years counterfactual credit - low"],
                range_high=p.iloc[row]["years counterfactual credit - high"],
                lclip=p.iloc[row]["counterfactual lclip"],
                rclip=p.iloc[row]["counterfactual rclip"],
            ),
            target_intervention=target_intervention,
            funding_profile=FundingProfile("Funded by Client", {funding_pool: 1.0}, {funding_pool: 1.0}),
        )
        output.append(project)

    return output


# ///////////////// Private Functions /////////////////


def _get_projects_df() -> pd.DataFrame:
    projects_data = pd.read_csv(config.PROJECTS_DATA_DIR / "projects.csv")
    return projects_data
