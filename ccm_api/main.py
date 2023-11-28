import logging
import os
from typing import Annotated, Literal

import sentry_sdk
import uvicorn
from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse

import ccm.interventions.intervention_definitions.all_interventions as interventions
from ccm.contexts import using_parameters
from ccm.interventions.animal.animal_intervention_params import AnimalInterventionParams
from ccm.interventions.animal.animal_interventions import AnimalIntervention
from ccm.interventions.ghd.ghd_intervention_params import GhdInterventionParams
from ccm.interventions.ghd.ghd_interventions import GhdIntervention
from ccm.interventions.xrisk.impact.impact_method_params import ImpactMethodParams
from ccm.interventions.xrisk.xrisk_interventions import XRiskIntervention
from ccm.parameters import Parameters
from ccm.research_projects.projects.project_definitions.all_projects import get_all_projects
from ccm.research_projects.projects.project_definitions.animal_welfare_projects import get_animal_projects
from ccm.research_projects.projects.project_definitions.ghd_projects import get_ghd_projects
from ccm.research_projects.projects.project_definitions.xrisk_projects import get_xrisk_projects
from ccm.world.longterm_params import LongTermParams
from ccm.world.moral_weight_params import MoralWeightsParams
from ccm_api.models import (
    AttributeModel,
    ProjectAssessmentModel,
    ResearchProjectAttributesModel,
    ResearchProjectModel,
    SparseSamples,
)

FRONT_END_URL = os.getenv("FRONT_END_URL", "")

logging.basicConfig(level=logging.INFO)

if os.getenv("PYTHON_ENV") in ("staging", "production"):
    sentry_sdk.init(
        # (This is not a secret)
        dsn="https://1879bc961158c20e7481f1b140c29d9d@o4505964725796864.ingest.sentry.io/4505965370671104",
        traces_sample_rate=0.5,
        profiles_sample_rate=0.2,
    )
    logging.info("Sentry initialized")


# Set up operation IDs for the OpenAPI codegen
# see https://fastapi.tiangolo.com/advanced/generate-clients/
def generate_unique_id(route: APIRoute):
    if not route.tags:
        return f"{route.name}"
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title="Cross-Cause Model API", generate_unique_id_function=generate_unique_id, separate_input_output_schemas=False
)

app.add_middleware(BrotliMiddleware)
app.add_middleware(
    CORSMiddleware,
    # CORS attacks aren't really an issue
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    FastAPICache.init(backend=InMemoryBackend())


ANIMAL_PROJECTS = get_animal_projects()
GHD_PROJECTS = get_ghd_projects()
XRISK_PROJECTS = get_xrisk_projects()
ALL_PROJECTS = get_all_projects(False)


#  Legacy support
@app.get("/projects/ghd")
def redirect_to_front_end_ghd():
    # redirect to same path
    return RedirectResponse(url=f"{FRONT_END_URL}/projects/ghd")


@app.get("/projects/animal-welfare")
def redirect_to_front_end_animal_welfare():
    # redirect to same path
    return RedirectResponse(url=f"{FRONT_END_URL}/projects/animal-welfare")


@app.get("/")
def redirect_to_front_end():
    return RedirectResponse(url=FRONT_END_URL)


class ProjectsPerGroup(BaseModel):
    animal_welfare: Annotated[list[ResearchProjectModel], Field(alias="animal-welfare")]
    ghd: list[ResearchProjectModel]
    xrisk: list[ResearchProjectModel]
    others: list[ResearchProjectModel]


@app.get("/project-groups/")
@cache()
async def get_projects() -> ProjectsPerGroup:
    with using_parameters(Parameters()):
        ungrouped_projects = set(ALL_PROJECTS) - set(ANIMAL_PROJECTS) - set(GHD_PROJECTS) - set(XRISK_PROJECTS)

        projects_per_group = ProjectsPerGroup.model_validate(
            {
                "animal-welfare": [ResearchProjectModel.from_project(project) for project in ANIMAL_PROJECTS],
                "ghd": [ResearchProjectModel.from_project(project) for project in GHD_PROJECTS],
                "xrisk": [ResearchProjectModel.from_project(project) for project in XRISK_PROJECTS],
                "others": [ResearchProjectModel.from_project(project) for project in ungrouped_projects],
            }
        )
    return projects_per_group


@app.get("/project-groups/{project_group}")
@cache()
async def get_projects_by_group(
    project_group: Literal["animal-welfare", "ghd", "xrisk", "all"]
) -> list[ResearchProjectModel]:
    with using_parameters(Parameters()):
        if project_group == "animal-welfare":
            projects = ANIMAL_PROJECTS
        elif project_group == "ghd":
            projects = GHD_PROJECTS
        elif project_group == "xrisk":
            projects = XRISK_PROJECTS
        else:
            projects = ALL_PROJECTS
    return [ResearchProjectModel.from_project(project) for project in projects]


@app.post("/projects/{project_id}/assess")
async def assess_project_with_params(project_id: str, parameters: Parameters) -> ProjectAssessmentModel:
    # Get project by ID
    with using_parameters(parameters):
        try:
            project = next(filter(lambda proj: proj.short_name == project_id, ALL_PROJECTS))
        except StopIteration as e:
            raise HTTPException(status_code=404, detail="Project not found") from e
        return ProjectAssessmentModel.from_project_assessment(project.assess_project())


# (Multiple arguments necessitates a model for OpenAPI codegen)
class AssessCustomProjectParams(BaseModel):
    project: ResearchProjectModel
    parameters: Parameters


@app.post("/custom-projects/assess")
def assess_custom_project_with_params(
    params: AssessCustomProjectParams,
) -> ProjectAssessmentModel:
    # Construct ResearchProject from ResearchProjectModel
    project = params.project.to_project()

    # Run assessment on the ResearchProject
    with using_parameters(params.parameters):
        return ProjectAssessmentModel.from_project_assessment(project.assess_project())


@app.get("/projects/attributes")
def get_project_attributes() -> dict[str, AttributeModel]:
    # Returns a list of the available attributes for projects
    # along with the metadata from their model schema

    base_attributes = ResearchProjectAttributesModel.model_json_schema()["properties"]

    attributes = {}
    for name, attribute in base_attributes.items():
        attributes[name] = {
            "title": attribute["title"],
            "description": attribute["description"],
        }
    return attributes


@app.get("/parameters/attributes")
def get_parameter_attributes() -> dict[str, AttributeModel]:
    # Returns a list of the available attributes for projects
    # along with the metadata from their model schema

    params_classes = [
        GhdInterventionParams,
        AnimalInterventionParams,
        LongTermParams,
        ImpactMethodParams,
        GhdIntervention,
        AnimalIntervention,
        XRiskIntervention,
        MoralWeightsParams,
    ]

    attributes = {}
    for params_class in params_classes:
        base_attributes = params_class.model_json_schema()["properties"]

        for name, attribute in base_attributes.items():
            attributes[name] = {
                "title": attribute["title"],
                "description": attribute.get("description", "unknown"),
            }

    return attributes


@app.get("/interventions")
def get_interventions() -> list[interventions.SomeIntervention]:
    with using_parameters(Parameters()):
        return interventions.get_unscaled_interventions()


class EstimateInterventionDALYsParams(BaseModel):
    intervention: interventions.SomeIntervention
    parameters: Parameters


@app.post("/interventions/{intervention_id}/estimate")
def estimate_intervention_dalys(
    intervention_id: str,
    params: EstimateInterventionDALYsParams,
) -> SparseSamples:
    with using_parameters(params.parameters):
        samples, zeros = params.intervention.estimate_dalys_per_1000()
        return SparseSamples(samples=samples.tolist(), num_zeros=zeros)


@app.get("/params/default")
def get_default_params() -> Parameters:
    return Parameters()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
