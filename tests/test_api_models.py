"""
Perform serialization tests on all existing models for projects,
project attributes and assessments, and interventions.
"""

import pytest
from fastapi.encoders import jsonable_encoder

import ccm.world.risk_types as risk_types
from ccm.contexts import using_parameters
from ccm.interventions.animal.animal_intervention_params import (
    DEFAULT_ANIMALS_BORN_PER_YEAR,
    AnimalInterventionParams,
)
from ccm.interventions.animal.animal_interventions import DEFAULT_ANIMAL_PARAMS, AnimalIntervention
from ccm.interventions.ghd.ghd_interventions import GhdIntervention
from ccm.interventions.intervention_definitions.all_interventions import ALL_INTERVENTIONS
from ccm.interventions.xrisk.xrisk_interventions import XRiskIntervention
from ccm.parameters import Parameters
from ccm.research_projects.projects.project_definitions.all_projects import get_all_projects
from ccm.world.moral_weight_params import MoralWeightsParams
from ccm_api.models import (
    ProjectAssessmentModel,
    ResearchProjectAttributesModel,
    ResearchProjectModel,
)

ALL_PROJECTS = set(get_all_projects(equal_money_for_causes=False)).union(get_all_projects(equal_money_for_causes=True))
ALL_RISK_TYPES = risk_types.get_glt_risk_types()


@pytest.mark.parametrize("project", ALL_PROJECTS)
def test_research_project_attributes_model(project):
    dummy_model = ResearchProjectAttributesModel.from_project(project)
    assert dummy_model.model_json_schema(), (
        f"Project '{project.short_name}' attributes model is not JSON serializable "
        "with pydantic method `.model_json_schema()`."
    )
    assert dummy_model.model_dump_json(), (
        f"Project '{project.short_name}' attributes model is not JSON serializable "
        "with pydantic method `.model_json_schema()`."
    )
    assert jsonable_encoder(dummy_model), (
        f"Project '{project.short_name}' attributes model is not JSON serializable "
        "with FastAPI `jsonable_encoder()` function."
    )


@pytest.mark.parametrize("project", ALL_PROJECTS)
def test_research_project_model(project):
    dummy_model = ResearchProjectModel.from_project(project)
    assert dummy_model.model_json_schema(), (
        f"Project '{project.short_name}' model is not JSON serializable " "with pydantic method `.model_json_schema()`."
    )
    assert dummy_model.model_dump_json(), (
        f"Project '{project.short_name}' model is not JSON serializable " "with pydantic method `.model_dump_json()`."
    )
    assert jsonable_encoder(dummy_model), (
        f"Project '{project.short_name}' model is not JSON serializable "
        "with with FastAPI `jsonable_encoder()` function."
    )


@pytest.mark.parametrize("intervention", ALL_INTERVENTIONS)
def test_intervention_spec(intervention):
    assert intervention.model_json_schema(), (
        f"Intervention '{intervention.name}' assessment model is not JSON serializable "
        "with pydantic method `.model_json_schema()`."
    )
    assert intervention.model_dump_json(), (
        f"Intervention '{intervention.name}' assessment model is not JSON serializable "
        "with pydantic method `.model_dump_json()`."
    )
    assert jsonable_encoder(intervention), (
        f"Intervention '{intervention.name}' assessment model is not JSON serializable "
        "with FastAPI `jsonable_encoder()` function."
    )


@pytest.mark.parametrize("project", ALL_PROJECTS)
def test_project_assessment_model(project):
    project_assessment = project.assess_project()
    dummy_model = ProjectAssessmentModel.from_project_assessment(project_assessment)
    assert dummy_model.model_json_schema(), (
        f"Project '{project.short_name}' assessment model is not JSON serializable "
        "with pydantic method `.model_json_schema()`."
    )
    assert dummy_model.model_dump_json(), (
        f"Project '{project.short_name}' assessment model is not JSON serializable "
        "with pydantic method `.model_dump_json()`."
    )
    assert jsonable_encoder(dummy_model), (
        f"Project '{project.short_name}' assessment model is not JSON serializable "
        "with FastAPI `jsonable_encoder()` function."
    )


def test_animal_intervention_model():
    with using_parameters(
        Parameters(
            animal_intervention_params=AnimalInterventionParams(
                moral_weight_params=MoralWeightsParams(),
                num_animals_born_per_year=DEFAULT_ANIMALS_BORN_PER_YEAR,
            )
        )
    ):
        for animal, default_params in DEFAULT_ANIMAL_PARAMS.items():
            intervention = AnimalIntervention(animal=animal, **default_params)
            assert intervention.model_json_schema(), (
                f"Serializing AnimalIntervention model failed for {animal.value.title()} with pydantic method "
                + "`.model_json_schema()`."
            )
            assert intervention.model_dump_json(), (
                f"Serializing AnimalIntervention model failed for {animal.value.title()} with pydantic method "
                + "`.model_dump_json()`."
            )
            assert jsonable_encoder(intervention), (
                f"Serializing AnimalIntervention model failed for {animal.value.title()} with FastAPI "
                + "`jsonable_encoder()` function."
            )


def test_ghd_intervention_model():
    with using_parameters(Parameters()):
        intervention = GhdIntervention(name="a")
        assert (
            intervention.model_json_schema()
        ), "Serializing GhdIntervention model failed with pydantic method `.model_json_schema()`."
        assert (
            intervention.model_dump_json()
        ), "Serializing GhdIntervention model failed with pydantic method `.model_dump_json()`."
        assert jsonable_encoder(
            intervention
        ), "Serializing GhdIntervention model failed with FastAPI `jsonable_encoder()` function."


@pytest.mark.parametrize("risk_type", ALL_RISK_TYPES)
def test_xrisk_intervention_model(risk_type):
    with using_parameters(Parameters()):
        intervention = XRiskIntervention(risk_type=risk_type)
        assert intervention.model_json_schema(), (
            f"Serializing XRiskIntervention model failed for {risk_type.value.title()} with pydantic method "
            + "`.model_json_schema()`."
        )
        assert intervention.model_dump_json(), (
            f"Serializing XRiskIntervention model failed for {risk_type.value.title()} with pydantic method "
            + "`.model_dump_json()`."
        )
        assert jsonable_encoder(intervention), (
            f"Serializing XRiskIntervention model failed for {risk_type.value.title()} with FastAPI "
            + "`jsonable_encoder()` function."
        )
