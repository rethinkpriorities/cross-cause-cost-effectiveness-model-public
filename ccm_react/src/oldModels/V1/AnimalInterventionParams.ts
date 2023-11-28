/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BetaDistributionSpec } from './BetaDistributionSpec';
import type { CategoricalDistributionSpec } from './CategoricalDistributionSpec';
import type { ConfidenceDistributionSpec } from './ConfidenceDistributionSpec';
import type { ConstantDistributionSpec } from './ConstantDistributionSpec';
import type { GammaDistributionSpec } from './GammaDistributionSpec';
import type { MoralWeightsParams } from './MoralWeightsParams';
import type { UniformDistributionSpec } from './UniformDistributionSpec';

export type AnimalInterventionParams = {
  /**
   * Moral weights for each species.
   */
  moral_weight_params?: MoralWeightsParams;
  /**
   * A mapping expressing, for each species, how many new individuals are born each year.
   */
  num_animals_born_per_year?: Record<string, (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec)>;
};

