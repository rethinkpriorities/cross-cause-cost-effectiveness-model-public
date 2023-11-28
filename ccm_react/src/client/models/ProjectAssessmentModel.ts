/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SparseSamples } from './SparseSamples';

export type ProjectAssessmentModel = {
  id: string;
  cost: Array<number>;
  years_credit: Array<number>;
  gross_impact: SparseSamples;
  net_impact: SparseSamples;
  net_dalys_per_staff_year: SparseSamples;
};

