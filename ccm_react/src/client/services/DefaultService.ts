/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnimalIntervention } from '../models/AnimalIntervention';
import type { AssessCustomProjectParams } from '../models/AssessCustomProjectParams';
import type { AttributeModel } from '../models/AttributeModel';
import type { EstimateInterventionDALYsParams } from '../models/EstimateInterventionDALYsParams';
import type { GhdIntervention } from '../models/GhdIntervention';
import type { Parameters } from '../models/Parameters';
import type { ProjectAssessmentModel } from '../models/ProjectAssessmentModel';
import type { ProjectsPerGroup } from '../models/ProjectsPerGroup';
import type { ResearchProjectModel } from '../models/ResearchProjectModel';
import type { ResultIntervention } from '../models/ResultIntervention';
import type { SparseSamples } from '../models/SparseSamples';
import type { XRiskIntervention } from '../models/XRiskIntervention';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DefaultService {

  /**
   * Redirect To Front End Ghd
   * @returns any Successful Response
   * @throws ApiError
   */
  public static redirectToFrontEndGhd(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/projects/ghd',
    });
  }

  /**
   * Redirect To Front End Animal Welfare
   * @returns any Successful Response
   * @throws ApiError
   */
  public static redirectToFrontEndAnimalWelfare(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/projects/animal-welfare',
    });
  }

  /**
   * Redirect To Front End
   * @returns any Successful Response
   * @throws ApiError
   */
  public static redirectToFrontEnd(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/',
    });
  }

  /**
   * Get Projects
   * @returns ProjectsPerGroup Successful Response
   * @throws ApiError
   */
  public static getProjects(): CancelablePromise<ProjectsPerGroup> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/project-groups/',
    });
  }

  /**
   * Get Projects By Group
   * @param projectGroup
   * @returns ResearchProjectModel Successful Response
   * @throws ApiError
   */
  public static getProjectsByGroup(
    projectGroup: 'animal-welfare' | 'ghd' | 'xrisk' | 'all',
  ): CancelablePromise<Array<ResearchProjectModel>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/project-groups/{project_group}',
      path: {
        'project_group': projectGroup,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Assess Project With Params
   * @param projectId
   * @param requestBody
   * @returns ProjectAssessmentModel Successful Response
   * @throws ApiError
   */
  public static assessProjectWithParams(
    projectId: string,
    requestBody: Parameters,
  ): CancelablePromise<ProjectAssessmentModel> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/projects/{project_id}/assess',
      path: {
        'project_id': projectId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Assess Custom Project With Params
   * @param requestBody
   * @returns ProjectAssessmentModel Successful Response
   * @throws ApiError
   */
  public static assessCustomProjectWithParams(
    requestBody: AssessCustomProjectParams,
  ): CancelablePromise<ProjectAssessmentModel> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/custom-projects/assess',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get Project Attributes
   * @returns AttributeModel Successful Response
   * @throws ApiError
   */
  public static getProjectAttributes(): CancelablePromise<Record<string, AttributeModel>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/projects/attributes',
    });
  }

  /**
   * Get Parameter Attributes
   * @returns AttributeModel Successful Response
   * @throws ApiError
   */
  public static getParameterAttributes(): CancelablePromise<Record<string, AttributeModel>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/parameters/attributes',
    });
  }

  /**
   * Get Interventions
   * @returns any Successful Response
   * @throws ApiError
   */
  public static getInterventions(): CancelablePromise<Array<(ResultIntervention | AnimalIntervention | GhdIntervention | XRiskIntervention)>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/interventions',
    });
  }

  /**
   * Estimate Intervention Dalys
   * @param interventionId
   * @param requestBody
   * @returns SparseSamples Successful Response
   * @throws ApiError
   */
  public static estimateInterventionDalys(
    interventionId: string,
    requestBody: EstimateInterventionDALYsParams,
  ): CancelablePromise<SparseSamples> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/interventions/{intervention_id}/estimate',
      path: {
        'intervention_id': interventionId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get Default Params
   * @returns Parameters Successful Response
   * @throws ApiError
   */
  public static getDefaultParams(): CancelablePromise<Parameters> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/params/default',
    });
  }

}
