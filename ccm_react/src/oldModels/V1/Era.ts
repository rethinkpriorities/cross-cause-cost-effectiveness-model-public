/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Instances of Era describe eras of risk
 */
export type Era = {
  length: number;
  annual_extinction_risk?: (number | null);
  absolute_risks_by_type?: (Record<string, number> | null);
  proportional_risks_by_type?: (Record<string, number> | null);
};

