from functools import cache

import squigglepy as sq

import ccm.interventions.intervention_definitions.all_interventions as interventions
from ccm.research_projects.funding_pools.specified_intervention_fp import SpecifiedInterventionFundingPool
from ccm.research_projects.projects.research_project import FundingProfile, ResearchProject


@cache
def get_animal_projects() -> list[ResearchProject]:
    return [
        ResearchProject(
            short_name="Small update to a state-of-the-art animal welfare project",
            name="A project to modestly improve a well-funded animal welfare project",
            description="""A project for about one person over roughly three to six months on optimizing a well-financed
        animal welfare project that is particularly effective.""",
            cause="Animals",
            sub_cause="",
            fte_years=sq.norm((12 * 1.25) / 52, (26 * 1.25) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(5, 100),
            target_updating=sq.beta(100, 30),
            money_in_area_millions=sq.lognorm(5, 20),
            percent_money_influenceable=sq.beta(5, 15),
            years_credit=sq.lognorm(3, 5, lclip=0),
            target_intervention=interventions.get_intervention("$9 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$10 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$10 per DALY")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Speculative improvement a state-of-the-art animal welfare project",
            name="A speculative project to improve a state-of-the-art and well-funded animal project",
            description="""A project for about one person over roughly three to six mohnths searching for a
            speculative improvement to a well-financed animal welfare project that is already particlarly effective.""",
            cause="Animals",
            sub_cause="",
            conclusions_require_updating=sq.beta(4, 200),
            fte_years=sq.norm((12 * 1.25) / 52, (26 * 1.25) / 52, lclip=0.03),
            target_updating=sq.beta(100, 30),
            money_in_area_millions=sq.lognorm(5, 20),
            percent_money_influenceable=sq.beta(5, 15),
            years_credit=sq.lognorm(4, 12, lclip=0),
            target_intervention=interventions.get_intervention("$7 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$10 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$10 per DALY")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Large update to a small animal welfare project",
            name="A project to significantly improve a animal welfare project whose funding is unclear",
            description="""A project for about one person over roughly three to six months on optimizing a well-financed
        animal welfare project that has an unclear amount of funding.""",
            cause="Animals",
            sub_cause="",
            conclusions_require_updating=sq.beta(6, 30),
            fte_years=sq.norm((12 * 1.25) / 52, (26 * 1.25) / 52, lclip=0.03),
            target_updating=sq.beta(100, 30),
            money_in_area_millions=sq.norm(0, 4, lclip=0),
            percent_money_influenceable=sq.beta(50, 2),
            years_credit=sq.lognorm(3, 5, lclip=0),
            target_intervention=interventions.get_intervention("$10 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$20 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$20 per DALY")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Large update to relatively ineffective animal welfare project",
            name="A project to improve a modestly-funded ineffective animal project",
            description="""A project for about one person over roughly three to six months aimed at improving a
            well-financed animal welfare project that is not particularly effective.""",
            cause="Animals",
            sub_cause="Chickens",
            conclusions_require_updating=sq.beta(35, 25),
            fte_years=sq.norm((12 * 1.25) / 52, (26 * 1.25) / 52, lclip=0.03),
            target_updating=sq.beta(10, 60),
            money_in_area_millions=sq.lognorm(5, 10),
            percent_money_influenceable=sq.beta(300, 600),
            years_credit=sq.lognorm(5, 10, lclip=0),
            target_intervention=interventions.get_intervention("$70 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$80 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$80 per DALY")): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="Speculative update to ineffective animal welfare project",
            name="A longshot project to improve a modestly-funded ineffective animal welfare project",
            description="""A project for about one person over roughly three to six months on improving an
            animal welfare project that is not particularly effective.""",
            cause="GHD",
            sub_cause="",
            fte_years=sq.norm((12 * 1.25) / 52, (26 * 1.25) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(2, 60),
            target_updating=sq.beta(2, 60),
            money_in_area_millions=sq.lognorm(5, 10),
            percent_money_influenceable=sq.beta(25, 40),
            years_credit=sq.lognorm(5, 20, lclip=0),
            target_intervention=interventions.get_intervention("$60 per DALY"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$80 per DALY")): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(interventions.get_intervention("$80 per DALY")): 1.0
                },
            ),
        ),
    ]
