/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AnimalIntervention } from './AnimalIntervention';
import type { GhdIntervention } from './GhdIntervention';
import type { Parameters } from './Parameters';
import type { ResultIntervention } from './ResultIntervention';
import type { XRiskIntervention } from './XRiskIntervention';

export type EstimateInterventionDALYsParams = {
  intervention: (ResultIntervention | AnimalIntervention | GhdIntervention | XRiskIntervention);
  parameters: Parameters;
};

