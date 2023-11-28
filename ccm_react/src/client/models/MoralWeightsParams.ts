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

export type MoralWeightsParams = {
  /**
   * A string representation of the parameter type
   */
  type?: 'Moral Weight Parameters';
  /**
   * The version of parameter class
   */
  version?: '1';
  /**
   * Whether to override part or all of the moral weights calculations. If set to `'No override'`, all the calculations are performed considering the `weights_for_models` parameter, the `sentience_ranges` parameter and the welfare capacities for each model found by Rethink Priorities' Moral Weights  Project (*default*). If set to `'Only welfare capacities'`, the `weights_for_models` parameter is ignored, and the `welfare_capacities_override` is used instead to calculate moral weights by combining them with the `sentience_ranges` parameter. If set to `'All moral weight calculations'`, none of these are used, and instead the `moral_weights_override` parameter is used to set moral weights directly.
   */
  override_type?: 'No override' | 'Only welfare capacities' | 'All moral weight calculations';
  /**
   * Weights for distinct welfare capacity modelling approaches. Must add up to 1.
   */
  weights_for_models?: Record<string, number>;
  /**
   * Sentience range distributions
   */
  sentience_ranges?: Record<string, (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec)>;
  /**
   * Direct input of capacity welfare capacities for various species, *conditional on them being sentient*.
   */
  welfare_capacities_override?: Record<string, (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec)>;
  /**
   * Direct input of moral weights for various species.
   */
  moral_weights_override?: Record<string, (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec)>;
};

