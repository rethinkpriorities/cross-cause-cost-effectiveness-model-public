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

export type GhdIntervention = {
  type?: 'ghd';
  /**
   * The name of the intervention. Acts as an ID.
   */
  name: string;
  area?: 'ghd';
  /**
   * A longer description for the Global Health and Development intervention.
   */
  description?: (string | null);
  /**
   * A distribution to be used as the cost-effectiveness bar instead of the preset ones (GiveDirectly, GiveWell, OpenPhilantropy).
   */
  cost_per_daly?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * Adjusts the cost-effectiveness of this intervention downward, based on the cumulative x-risk over this many years.
   */
  years_until_intervention_has_effect?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
};

