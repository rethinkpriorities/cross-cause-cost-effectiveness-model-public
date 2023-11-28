from typing import TYPE_CHECKING, TypeAlias

from pydantic import BaseModel, Field
from scipy.sparse import coo_array

from ccm.interventions.intervention_definitions.all_interventions import ALL_INTERVENTIONS, SomeIntervention
from ccm.research_projects.funding_pools.specified_intervention_fp import SpecifiedInterventionFundingPool
from ccm.research_projects.projects.funding_profile import FundingProfile
from ccm.research_projects.projects.project_assessment import ProjectAssessment
from ccm.research_projects.projects.research_project import ResearchProject
from ccm.utility.models import DistributionSpec, SomeDistribution

if TYPE_CHECKING:
    from ccm.research_projects.funding_pools.funding_pool import FundingPool


class AttributeModel(BaseModel):
    title: str
    description: str


class ResearchProjectAttributesModel(BaseModel):
    fte_years: SomeDistribution = Field(
        title="Full-time-equivalent Years",
        description="The number of full-time-equivalent years of work required to complete the research project.",
    )
    cost_per_staff_year: SomeDistribution = Field(
        title="Cost per Staff Year",
        description="The cost of one full-time-equivalent year of work on the research project.",
    )
    conclusions_require_updating: SomeDistribution = Field(
        title="Probability of finding the new intervention",
        description=(
            "The probability that the research projects find a new intervention (the target intervention). "
            "It can also be seen as the probability that the project's conclusions cause an update "
            "regarding the best available intervention."
        ),
    )
    target_updating: SomeDistribution = Field(
        title="Probability of updating to target",
        description=(
            "The probability that the funder will alter their views in light of the research project, "
            "moving money to the target intervention."
        ),
    )
    money_in_area_millions: SomeDistribution = Field(
        title="Money in the cause area",
        description="The amount of money in the area relevant to the research project, in millions of US dollars.",
    )
    percent_money_influenceable: SomeDistribution = Field(
        title="Percent of money influenceable",
        description="The percentage of money in the area relevant to the research project that is influenceable.",
    )
    years_credit: SomeDistribution = Field(
        title="Years of credit",
        description=(
            "The number of years until the discovery would have been made counterfactually,"
            " if not for the research project."
        ),
    )

    @classmethod
    def from_project(cls, project: ResearchProject):
        return cls(
            fte_years=DistributionSpec.from_distribution(project.fte_years),
            cost_per_staff_year=DistributionSpec.from_distribution(project.cost_per_staff_year),
            conclusions_require_updating=DistributionSpec.from_distribution(project.conclusions_require_updating),
            target_updating=DistributionSpec.from_distribution(project.target_updating),
            money_in_area_millions=DistributionSpec.from_distribution(project.money_in_area_millions),
            percent_money_influenceable=DistributionSpec.from_distribution(project.percent_money_influenceable),
            years_credit=DistributionSpec.from_distribution(project.years_credit),
        )


InterventionID: TypeAlias = str


def lookup_intervention(intervention_id: InterventionID) -> SomeIntervention:
    try:
        result = next(iter(filter(lambda interv: interv.name == intervention_id, ALL_INTERVENTIONS)))
    except StopIteration as e:
        raise ValueError(f"Unknown Intervention name: {intervention_id}") from e
    return result


class ResearchProjectModel(BaseModel):
    """
    An intermediary model for serializing and deserializing research projects.

    TODO(agucova): Finish merging with the ResearchProject model from ccm_api/models.py
    """

    id: str
    name: str
    description: str
    attributes: ResearchProjectAttributesModel
    source_intervention: SomeIntervention | InterventionID
    target_intervention: SomeIntervention | InterventionID

    @classmethod
    def from_project(cls, project: ResearchProject):
        funding_pool: dict[FundingPool, float] = project.funding_profile.intervention_funding_sources
        current_intervention = next(iter(funding_pool)).get_counterfactual_intervention()
        assert current_intervention is not None

        return cls(
            id=project.short_name,
            name=project.name,
            description=project.description,
            attributes=ResearchProjectAttributesModel.from_project(project),
            source_intervention=current_intervention,
            target_intervention=project.target_intervention,
        )

    def to_project(self) -> ResearchProject:
        attrs = self.attributes
        if isinstance(self.source_intervention, str):
            source_intervention = lookup_intervention(self.source_intervention)
        else:
            source_intervention = self.source_intervention
        if isinstance(self.target_intervention, str):
            target_intervention = lookup_intervention(self.target_intervention)
        else:
            target_intervention = self.target_intervention

        funding_pool = SpecifiedInterventionFundingPool(source_intervention)

        return ResearchProject(
            short_name=self.id,
            name=self.name,
            description=self.description,
            cause="Unknown",  # TODO: map cause/subcause?
            sub_cause="Unknown",
            fte_years=attrs.fte_years.to_sq(),
            conclusions_require_updating=attrs.conclusions_require_updating.to_sq(),
            target_updating=attrs.target_updating.to_sq(),
            money_in_area_millions=attrs.money_in_area_millions.to_sq(),
            percent_money_influenceable=attrs.percent_money_influenceable.to_sq(),
            years_credit=attrs.years_credit.to_sq(),
            target_intervention=target_intervention,
            funding_profile=FundingProfile("Unknown Funding Profile", {funding_pool: 1.0}, {funding_pool: 1.0}),
            cost_per_staff_year=attrs.cost_per_staff_year.to_sq(),
        )


class SparseSamples(BaseModel):
    samples: list[float]
    num_zeros: int

    @classmethod
    def from_coo_array(cls, coo_array: coo_array):
        stored_samples = coo_array.data.tolist()
        size_with_zeros = coo_array.shape[0] * coo_array.shape[1]
        zeros = size_with_zeros - coo_array.nnz
        return SparseSamples(samples=stored_samples, num_zeros=zeros)


class ProjectAssessmentModel(BaseModel):
    id: str
    cost: list[float]
    years_credit: list[float]
    gross_impact: SparseSamples
    net_impact: SparseSamples
    net_dalys_per_staff_year: SparseSamples

    @classmethod
    def from_project_assessment(cls, project_asmnt: ProjectAssessment):
        return cls(
            id=project_asmnt.short_name,
            cost=project_asmnt.cost.tolist(),
            years_credit=project_asmnt.years_credit.tolist(),
            gross_impact=SparseSamples.from_coo_array(project_asmnt.gross_impact_DALYs),
            net_impact=SparseSamples.from_coo_array(project_asmnt.net_impact_DALYs),
            net_dalys_per_staff_year=SparseSamples.from_coo_array(project_asmnt.net_DALYs_per_staff_year),
        )
