"""
Premises about specific Rethink Priorities Research Projects.
"""

from functools import cache

import squigglepy as sq

import ccm.interventions.intervention_definitions.all_interventions as interventions
import ccm.research_projects.projects.projects_loader as projects_loader
from ccm.research_projects.funding_pools.specified_intervention_fp import SpecifiedInterventionFundingPool
from ccm.research_projects.projects.research_project import FundingProfile, ResearchProject


@cache
def get_legacy_projects(equal_money_for_causes: bool) -> list[ResearchProject]:
    # Amounts of money that are influenceable by RP's research, in millions.
    if equal_money_for_causes:
        # (lower_bound, upper_bound)  # noqa: ERA001
        ghd_money = (500, 1000)
        non_op_ghd_money = (500, 1000)
        chicken_money = (500, 1000)
        carp_money = (500, 1000)
        shrimp_money = (500, 1000)
    else:
        ghd_money = (15, 90)
        non_op_ghd_money = (15, 90)
        chicken_money = (2, 50)
        carp_money = (2, 50)
        shrimp_money = (2, 50)

    project_definitions = [
        ResearchProject(
            short_name="GHD project (large)",
            name="Generic GHD project for large state of the art intervention",
            description="""A project for about two people over roughly four weeks on optimizing a well-financed
            GHD project that is close to the state of the art.""",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.lognorm(0.06, 0.20, lclip=0, rclip=1),
            target_updating=sq.norm(0.9, 0.99, lclip=0, rclip=1),
            money_in_area_millions=sq.lognorm(ghd_money[0], ghd_money[1]),
            percent_money_influenceable=sq.norm(0.95, 0.99, lclip=0, rclip=1),
            years_credit=sq.lognorm(0.25, 2, lclip=0),
            target_intervention=interventions.get_intervention("GiveWell Bar"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("GiveWell Bar Scaled to ~88%")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("GiveWell Bar Scaled to ~88%")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="GHD project (small)",
            name="Generic GHD project optimizing moderately-well financed intervention",
            description="""A project for about two people over roughly four weeks on optimizing a moderately well
            financed GHD intervention that is close to the state of the art.""",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.lognorm(0.02, 0.20, lclip=0, rclip=1),
            target_updating=sq.norm(0.9, 0.99, lclip=0, rclip=1),
            money_in_area_millions=sq.lognorm(non_op_ghd_money[0], non_op_ghd_money[1]),
            percent_money_influenceable=sq.norm(0.95, 0.99, lclip=0, rclip=1),
            years_credit=sq.lognorm(0.25, 2, lclip=0),
            target_intervention=interventions.get_intervention("GiveWell Bar"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("GiveWell Bar Scaled to ~88%")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("GiveWell Bar Scaled to ~88%")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Chicken project",
            name="Generic chicken welfare project",
            description="""A project for about half a year FTE on optimizing an intervention nearly as effective as a
            cage-free campaign.""",
            cause="Animals",
            sub_cause="Chicken",
            fte_years=sq.norm((52 * 0.25) / 52, (52 * 0.75) / 52, lclip=4 / 52),
            conclusions_require_updating=sq.norm(0.5, 0.9, lclip=0, rclip=1),
            target_updating=sq.norm(0.9, 0.99, lclip=0, rclip=1),
            money_in_area_millions=sq.lognorm(chicken_money[0], chicken_money[1]),
            percent_money_influenceable=sq.norm(0.95, 0.99, lclip=0, rclip=1),
            years_credit=sq.lognorm(0.5, 4, lclip=0),
            target_intervention=interventions.get_intervention("Cage-free Chicken Campaign"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Cage-free Chicken Campaign Scaled to ~86%")
                    ): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Cage-free Chicken Campaign Scaled to ~86%")
                    ): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Carp project",
            name="Generic carp welfare project",
            description="""A project for about half a year FTE on optimizing an effective carp welfare intervention.""",
            cause="Animals",
            sub_cause="carp",
            fte_years=sq.norm((52 * 0.25) / 52, (52 * 0.75) / 52, lclip=4 / 52),
            conclusions_require_updating=sq.norm(0.5, 0.9, lclip=0, rclip=1),
            target_updating=sq.norm(0.9, 0.99, lclip=0, rclip=1),
            money_in_area_millions=sq.lognorm(carp_money[0], carp_money[1]),
            percent_money_influenceable=sq.norm(0.95, 0.99, lclip=0, rclip=1),
            years_credit=sq.lognorm(0.5, 4, lclip=0),
            target_intervention=interventions.get_intervention("Generic Carp Intervention"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("Generic Carp Intervention")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("Generic Carp Intervention")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Shrimp project",
            name="Generic shrimp welfare project",
            description="""A project for about half a year FTE on optimizing an effective shrimp welfare intervention.
            """,
            cause="Animals",
            sub_cause="shrimp",
            fte_years=sq.norm((52 * 0.25) / 52, (52 * 0.75) / 52, lclip=4 / 52),
            conclusions_require_updating=sq.norm(0.5, 0.9, lclip=0, rclip=1),
            target_updating=sq.norm(0.9, 0.99, lclip=0, rclip=1),
            money_in_area_millions=sq.lognorm(shrimp_money[0], shrimp_money[1]),
            percent_money_influenceable=sq.norm(0.95, 0.99, lclip=0, rclip=1),
            years_credit=sq.lognorm(0.5, 4, lclip=0),
            target_intervention=interventions.get_intervention("Shrimp Slaughter Intervention"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Generic Shrimp Intervention Scaled to ~86%")
                    ): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Generic Shrimp Intervention Scaled to ~86%")
                    ): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Equivalence Test",
            name="Equivalence Test",
            description="Fake Research Project to test Mixed Funding Sources.",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.lognorm(0.06, 0.20, lclip=0, rclip=1),
            target_updating=sq.norm(0.9, 0.99, lclip=0, rclip=1),
            money_in_area_millions=sq.lognorm(ghd_money[0], ghd_money[1]),
            percent_money_influenceable=sq.norm(0.95, 0.99, lclip=0, rclip=1),
            years_credit=sq.lognorm(0.25, 2, lclip=0),
            target_intervention=interventions.get_intervention("GiveWell Bar"),
            funding_profile=FundingProfile(
                name="Mixed Funding Sources",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("GiveWell Bar")): 0.5,
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("RP Research Projects"), "RP Capital"
                    ): 0.5,
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("GiveWell Bar")): 1.0
                },
            ),
        ),
    ]

    research_projects = project_definitions

    # Yet another way to load project definitions
    research_projects.extend(projects_loader.read_projects())

    return research_projects
