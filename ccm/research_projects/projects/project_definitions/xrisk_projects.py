from functools import cache

import squigglepy as sq

import ccm.interventions.intervention_definitions.all_interventions as interventions
from ccm.research_projects.funding_pools.specified_intervention_fp import SpecifiedInterventionFundingPool
from ccm.research_projects.projects.research_project import FundingProfile, ResearchProject


@cache
def get_xrisk_projects() -> list[ResearchProject]:
    return [
        ResearchProject(
            short_name="A significant update to relatively ineffective AI misalignment project",
            name="A project to improve a modestly-funded ineffective AI misalignment project",
            description="""A project for about two people over roughly four weeks on optimizing a modestly-funded
            AI misalignment project that is ineffective relative to other, state of the art projects.""",
            cause="AIGS",
            sub_cause="ai misalignment",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(40, 30),
            target_updating=sq.beta(100, 30),
            # SEE: https://docs.google.com/spreadsheets/d/1onjuWEP-FRaVFbDGgDNHGDs_4QDenuMAeW19NWI5t-8/#gid=1030666228
            money_in_area_millions=sq.lognorm(209, 508, lclip=0),
            # set to the average contribution per donor
            percent_money_influenceable=sq.beta(3, 30),
            years_credit=sq.lognorm(5, 10, lclip=0, rclip=50),
            target_intervention=interventions.get_intervention("Small-scale AI Misalignment Project"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale AI Misalignment Project Scaled to ~86%")
                    ): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale AI Misalignment Project Scaled to ~86%")
                    ): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="A significant update to relatively ineffective AI misuse project",
            name="A project to improve a modestly-funded ineffective AI misuse project",
            description="""A project for about two people over roughly four weeks on optimizing a modestly-funded
            AI misuse project that is ineffective relative to other, state of the art projects.""",
            cause="AIGS",
            sub_cause="ai misuse",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(40, 30),
            target_updating=sq.beta(100, 30),
            # SEE: https://docs.google.com/spreadsheets/d/1onjuWEP-FRaVFbDGgDNHGDs_4QDenuMAeW19NWI5t-8/#gid=1030666228
            money_in_area_millions=sq.lognorm(11.5, 58, lclip=0),
            # set to the average contribution per donor
            percent_money_influenceable=sq.beta(3, 30),
            years_credit=sq.lognorm(5, 10, lclip=0, rclip=50),
            target_intervention=interventions.get_intervention("Small-scale AI Misuse Project"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale AI Misuse Project Scaled to ~86%")
                    ): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale AI Misuse Project Scaled to ~86%")
                    ): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="A significant update to relatively ineffective biological risk project",
            name="A project to improve a modestly-funded ineffective biological risk project",
            description="""A project for about two people over roughly four weeks on optimizing a modestly-funded
            biological risk project that is ineffective relative to other, state of the art projects.""",
            cause="GLT",
            sub_cause="bio",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(40, 30),
            target_updating=sq.beta(100, 30),
            # SEE: https://docs.google.com/spreadsheets/d/1onjuWEP-FRaVFbDGgDNHGDs_4QDenuMAeW19NWI5t-8/#gid=1030666228
            money_in_area_millions=sq.lognorm(771, 5_400, lclip=0),
            # set to the average contribution per donor
            percent_money_influenceable=sq.beta(2, 30),
            years_credit=sq.lognorm(5, 10, lclip=0, rclip=50),
            target_intervention=interventions.get_intervention("Small-scale Biorisk Project"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale Biorisk Project Scaled to ~86%")
                    ): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale Biorisk Project Scaled to ~86%")
                    ): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="A significant update to relatively ineffective nanotechnology risk project",
            name="A project to improve a modestly-funded ineffective nanotechnology risk project",
            description="""A project for about two people over roughly four weeks on optimizing a modestly-funded
            nanotechnology risk project that is ineffective relative to other, state of the art projects.""",
            cause="GLT",
            sub_cause="nano",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(40, 30),
            target_updating=sq.beta(100, 30),
            # SEE: https://docs.google.com/spreadsheets/d/1onjuWEP-FRaVFbDGgDNHGDs_4QDenuMAeW19NWI5t-8/#gid=1030666228
            money_in_area_millions=sq.lognorm(22, 550, lclip=0),
            # set to the average contribution per donor
            percent_money_influenceable=sq.beta(0.1, 1),
            years_credit=sq.lognorm(5, 10, lclip=0, rclip=50),
            target_intervention=interventions.get_intervention("Small-scale Nanotech Safety Project"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale Nanotech Safety Project Scaled to ~86%")
                    ): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale Nanotech Safety Project Scaled to ~86%")
                    ): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="A significant update to relatively ineffective natural risk project",
            name="A project to improve a modestly-funded ineffective natural risk project",
            description="""A project for about two people over roughly four weeks on optimizing a modestly-funded
            natural risk project that is ineffective relative to other, state of the art projects.""",
            cause="GLT",
            sub_cause="natural",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(40, 30),
            target_updating=sq.beta(100, 30),
            # SEE: https://docs.google.com/spreadsheets/d/1onjuWEP-FRaVFbDGgDNHGDs_4QDenuMAeW19NWI5t-8/#gid=1030666228
            money_in_area_millions=sq.lognorm(2_885, 57_703, lclip=0),
            # set to the average contribution per donor
            percent_money_influenceable=sq.beta(0.5, 50),
            years_credit=sq.lognorm(5, 10, lclip=0, rclip=50),
            target_intervention=interventions.get_intervention("Small-scale Natural Disaster Prevention Project"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale Natural Disaster Prevention Project Scaled to ~86%")
                    ): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale Natural Disaster Prevention Project Scaled to ~86%")
                    ): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="A significant update to relatively ineffective nuclear risk project",
            name="A project to improve a modestly-funded ineffective nuclear risk project",
            description="""A project for about two people over roughly four weeks on optimizing a modestly-funded
            nuclear risk project that is ineffective relative to other, state of the art projects.""",
            cause="GLT",
            sub_cause="nukes",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(40, 30),
            target_updating=sq.beta(100, 30),
            # SEE: https://docs.google.com/spreadsheets/d/1onjuWEP-FRaVFbDGgDNHGDs_4QDenuMAeW19NWI5t-8/#gid=1030666228
            money_in_area_millions=sq.lognorm(11, 1_706, lclip=0),
            # set to the average contribution per donor
            percent_money_influenceable=sq.beta(0.5, 35),
            years_credit=sq.lognorm(5, 10, lclip=0, rclip=50),
            target_intervention=interventions.get_intervention("Small-scale Nuclear Safety Project"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale Nuclear Safety Project Scaled to ~86%")
                    ): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Small-scale Nuclear Safety Project Scaled to ~86%")
                    ): 1.0
                },
            ),
        ),
        ResearchProject(
            short_name="A significant update to relatively ineffective unspecified risk project",
            name="A project to improve a modestly-funded ineffective unspecified risk project",
            description="""A project for about two people over roughly four weeks on optimizing a modestly-funded
            unspecified risk project that is ineffective relative to other, state of the art projects.""",
            cause="GLT",
            sub_cause="unknown",
            fte_years=sq.norm((1.5 * 2) / 52, (6.5 * 2) / 52, lclip=0.03),
            conclusions_require_updating=sq.beta(40, 30),
            target_updating=sq.beta(100, 30),
            # SEE: https://docs.google.com/spreadsheets/d/1onjuWEP-FRaVFbDGgDNHGDs_4QDenuMAeW19NWI5t-8/#gid=1030666228
            # set to "Other" category, since it includes genral longtermist projects
            # (forecasting, community building, broad cause exploration) that might help noticing new risks
            money_in_area_millions=sq.lognorm(41, 568, lclip=0),
            # set to the average contribution per donor
            percent_money_influenceable=sq.beta(0.5, 15),
            years_credit=sq.lognorm(5, 10, lclip=0, rclip=50),
            target_intervention=interventions.get_intervention("Exploratory Research into Unknown Risks"),
            funding_profile=FundingProfile(
                name="Funded by Client",
                research_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Exploratory Research into Unknown Risks Scaled to ~86%")
                    ): 1.0
                },
                intervention_funding_sources={
                    SpecifiedInterventionFundingPool(
                        interventions.get_intervention("Exploratory Research into Unknown Risks Scaled to ~86%")
                    ): 1.0
                },
            ),
        ),
    ]
