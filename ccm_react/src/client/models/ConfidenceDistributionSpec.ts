/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * A way to specify a distribution by giving a confidence interval.
 */
export type ConfidenceDistributionSpec = {
  type: 'confidence';
  /**
   * If not given, lognormal will be preferred for positive ranges and normal for negative ranges.
   */
  distribution: ('normal' | 'lognormal' | null);
  range: any[];
  clip?: any[];
  credibility?: 90 | 80 | 50;
};

