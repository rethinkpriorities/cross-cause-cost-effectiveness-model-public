from ccm.research_projects.funding_pools.funding_pool import FundingPool


class FundingProfile:
    """Representation of where the funding for given Research Project and its Target Intervention is coming from."""

    def __init__(
        self,
        name: str,
        research_funding_sources: dict[FundingPool, float],
        intervention_funding_sources: dict[FundingPool, float],
    ) -> None:
        FundingProfile.validate_funding_sources(research_funding_sources, name, "research_funding_sources")
        FundingProfile.validate_funding_sources(intervention_funding_sources, name, "intervention_funding_sources")

        self.name = name
        self.research_funding_sources = research_funding_sources
        self.intervention_funding_sources = intervention_funding_sources

    @staticmethod
    def validate_funding_sources(
        funding_sources: dict[FundingPool, float], profile_name: str, source_type: str
    ) -> None:
        if sum(funding_sources.values()) != 1.0:
            raise ValueError(f"Invalid {source_type} in FundingProfile {profile_name}; proportions must add up to 1")
