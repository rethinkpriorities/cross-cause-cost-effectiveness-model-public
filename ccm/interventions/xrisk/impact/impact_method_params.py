from typing import Annotated, Literal

from pydantic import Field

from ccm.base_parameters import BaseParameters
from ccm.interventions.xrisk.impact.expected_years_saved import ExpectedYearsSaved
from ccm.interventions.xrisk.impact.impact_method import ImpactMethod
from ccm.interventions.xrisk.impact.thousand_year_impact import ThousandYearImpact
from ccm.interventions.xrisk.impact.time_of_perils_impact import TimeOfPerils

expected_years_saved = ExpectedYearsSaved()
thousand_year_impact = ThousandYearImpact()
time_of_perils = TimeOfPerils()

ALL_IMPACT_METHODS: dict[str, ImpactMethod] = {
    expected_years_saved.get_name(): expected_years_saved,
    thousand_year_impact.get_name(): thousand_year_impact,
    time_of_perils.get_name(): time_of_perils,
}

DEFAULT_IMPACT_METHOD = expected_years_saved


class ImpactMethodParams(BaseParameters, frozen=True):
    type: Annotated[
        Literal["Impact Method Parameters"],
        Field(
            title="Type",
            description="A string representation of the parameter type",
        ),
    ] = "Impact Method Parameters"
    version: Annotated[
        Literal["1"],
        Field(
            title="Version",
            description="The version of parameter class",
        ),
    ] = "1"
    impact_method: Annotated[
        # Note: Remember to update this Literal when adding a new ImpactMethod
        Literal["expected years saved", "thousand year impact", "time of perils"],
        Field(description="Which ImpactMethod to use for evaluating value of a given X-risk reduction."),
    ] = DEFAULT_IMPACT_METHOD.get_name()  # type: ignore

    def get_impact_method(self) -> ImpactMethod:
        return ALL_IMPACT_METHODS[self.impact_method]

    @staticmethod
    def get_default_impact_method() -> ImpactMethod:
        return DEFAULT_IMPACT_METHOD

    @staticmethod
    def get_all_impact_methods() -> list[ImpactMethod]:
        return list(ALL_IMPACT_METHODS.values())
