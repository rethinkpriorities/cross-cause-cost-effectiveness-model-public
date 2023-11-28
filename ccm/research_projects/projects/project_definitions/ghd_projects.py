from functools import cache

import squigglepy as sq

import ccm.interventions.intervention_definitions.all_interventions as interventions
from ccm.research_projects.funding_pools.specified_intervention_fp import SpecifiedInterventionFundingPool
from ccm.research_projects.projects.research_project import FundingProfile, ResearchProject


@cache
def get_ghd_projects() -> list[ResearchProject]:
    return [
        ResearchProject(
            short_name="Generic GHD project",
            name="A generic GHD project",
            description="""A generic GHD project""",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(0.1, 0.1),
            target_updating=sq.beta(0.1, 0.1),
            money_in_area_millions=sq.lognorm(1, 100000),
            percent_money_influenceable=sq.beta(0.1, 0.1),
            years_credit=sq.lognorm(1, 10, lclip=0),
            target_intervention=interventions.get_intervention("$100 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$120 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$120 per DALY")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Modest update to a state-of-the-art GHD project",
            name="A project to modestly improve a well-funded effective GHD project.",
            description="""A project for about two people over roughly four weeks on optimizing a well-financed
        GHD project that is already unusually effective.""",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(5, 100),
            target_updating=sq.beta(100, 30),
            money_in_area_millions=sq.lognorm(50, 100),
            percent_money_influenceable=sq.beta(5, 15),
            years_credit=sq.lognorm(0.25, 2, lclip=0),
            target_intervention=interventions.get_intervention("$48 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$50 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$50 per DALY")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Speculative update for a state-of-the-art GHD project",
            name="A speculative project to improve of a well-funded effective GHD project",
            description="""A project for about two people over roughly twelve weeks searching for
            a speculative (and unlikely to be found) improvement to a well-financed GHD project that is already
            unusually effective.""",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((6 * 2) / 52, (18 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(4, 200),
            target_updating=sq.beta(100, 30),
            money_in_area_millions=sq.lognorm(50, 100),
            percent_money_influenceable=sq.beta(5, 15),
            years_credit=sq.lognorm(4, 12, lclip=0),
            target_intervention=interventions.get_intervention("$48 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$50 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$50 per DALY")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Large improvement to a small-scale GHD project",
            name="A longshot project to significantly improve a GHD project with unclear funding",
            description="""A project for about two people over roughly four weeks aimed at finding a significant
            improvement to a GHD project whose funding potential is unclear.""",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(6, 30),
            target_updating=sq.beta(100, 30),
            money_in_area_millions=sq.norm(0, 20, lclip=0),
            percent_money_influenceable=sq.beta(50, 2),
            years_credit=sq.lognorm(1, 5, lclip=0),
            target_intervention=interventions.get_intervention("$45 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$55 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$55 per DALY")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Large update to ineffective GHD project",
            name="A project to improve a modestly-funded ineffective GHD project",
            description="""A project for about two people over roughly four weeks aimed at improving a modestly-funded
        GHD project that isn't particularly effective.""",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(35, 25),
            target_updating=sq.beta(10, 60),
            money_in_area_millions=sq.lognorm(5, 10),
            percent_money_influenceable=sq.beta(300, 600),
            years_credit=sq.lognorm(5, 10, lclip=0),
            target_intervention=interventions.get_intervention("$125 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$150 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$150 per DALY")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Speculative update to ineffective GHD project",
            name="A longshot project to improve a modestly-funded ineffective GHD project",
            description="""A project for about two people over roughly four weeks aimed at significantly improving
            a modestly-funded GHD project that isn't particularly effective.""",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(0.1, 30),
            target_updating=sq.beta(2, 60),
            money_in_area_millions=sq.lognorm(5, 20),
            percent_money_influenceable=sq.beta(25, 40),
            years_credit=sq.lognorm(5, 20, lclip=0),
            target_intervention=interventions.get_intervention("$80 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$125 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$125 per DALY")): 1.0
                },
            ),
        ),
    ]
