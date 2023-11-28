/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BetaDistributionSpec } from './BetaDistributionSpec';
import type { CategoricalDistributionSpec } from './CategoricalDistributionSpec';
import type { ConfidenceDistributionSpec } from './ConfidenceDistributionSpec';
import type { ConstantDistributionSpec } from './ConstantDistributionSpec';
import type { GammaDistributionSpec } from './GammaDistributionSpec';
import type { UniformDistributionSpec } from './UniformDistributionSpec';

/**
 * An intervention defined directly by its result distribution.
 */
export type ResultIntervention = {
  type: 'result';
  /**
   * The name of the intervention. Acts as an ID.
   */
  name: string;
  /**
   * The cause area of the intervention.
   */
  area: ('ghd' | 'animal-welfare' | 'xrisk' | 'utility' | 'not-an-intervention' | null);
  description?: (string | null);
  result_distribution: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
};

