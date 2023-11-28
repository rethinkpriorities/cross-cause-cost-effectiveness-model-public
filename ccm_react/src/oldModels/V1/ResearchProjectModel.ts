/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AnimalIntervention } from './AnimalIntervention';
import type { GhdIntervention } from './GhdIntervention';
import type { ResearchProjectAttributesModel } from './ResearchProjectAttributesModel';
import type { ResultIntervention } from './ResultIntervention';
import type { XRiskIntervention } from './XRiskIntervention';

/**
 * An intermediary model for serializing and deserializing research projects.
 *
 * TODO(agucova): Finish merging with the ResearchProject model from ccm_api/models.py
 */
export type ResearchProjectModel = {
  id: string;
  name: string;
  description: string;
  attributes: ResearchProjectAttributesModel;
  source_intervention: ((ResultIntervention | AnimalIntervention | GhdIntervention | XRiskIntervention) | string);
  target_intervention: ((ResultIntervention | AnimalIntervention | GhdIntervention | XRiskIntervention) | string);
};

