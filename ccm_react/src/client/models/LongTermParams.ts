/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BetaDistributionSpec } from './BetaDistributionSpec';
import type { CategoricalDistributionSpec } from './CategoricalDistributionSpec';
import type { ConfidenceDistributionSpec } from './ConfidenceDistributionSpec';
import type { ConstantDistributionSpec } from './ConstantDistributionSpec';
import type { Era } from './Era';
import type { GammaDistributionSpec } from './GammaDistributionSpec';
import type { UniformDistributionSpec } from './UniformDistributionSpec';

/**
 * Parameters for the estimation of existential and non-existential risks.
 */
export type LongTermParams = {
  type?: 'Long Term Parameters';
  version?: '2';
  /**
   * Definition of each 'risk era', in terms of its length (in years), the annual extinction risk for its duration, an how the risks are distributed between various risk types.
   */
  risk_eras?: Array<Era>;
  /**
   * The maximum creditable year to take into account in the risk calculations.
   */
  max_creditable_year?: number;
  /**
   * Density of stars in the galaxy, in stars per cubic light year.
   */
  galactic_density?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * Density of stars in a supercluster, in stars per cubic light year
   */
  supercluster_density?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The average human population per star
   */
  stellar_population_capacity?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The median speed at which humanity will expand, in light years per year.
   */
  expansion_speed?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * How much more likely a disaster is to be a non-extinction catastrophe than an extinction level event.
   */
  catastrophe_extinction_risk_ratios?: Record<string, number>;
  /**
   * The proportion of the population that would die in a non-extinction catastrophe
   */
  catastrophe_intensities?: Record<string, (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec)>;
  /**
   * Fractions of total risk belonging to risk type by year
   */
  fractions_of_near_term_total_risk?: Record<string, number>;
};

