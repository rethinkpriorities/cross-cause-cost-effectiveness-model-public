/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Animal } from './Animal';
import type { BetaDistributionSpec } from './BetaDistributionSpec';
import type { CategoricalDistributionSpec } from './CategoricalDistributionSpec';
import type { ConfidenceDistributionSpec } from './ConfidenceDistributionSpec';
import type { ConstantDistributionSpec } from './ConstantDistributionSpec';
import type { GammaDistributionSpec } from './GammaDistributionSpec';
import type { UniformDistributionSpec } from './UniformDistributionSpec';

export type AnimalIntervention = {
  type?: 'animal-welfare';
  /**
   * The name of the intervention. Acts as an ID.
   */
  name: string;
  area?: 'animal-welfare';
  description?: (string | null);
  /**
   * Which species the intervention is tailored for.
   */
  animal?: Animal;
  /**
   * Directly specify a distribution of the years of suffering averted per $1000 rather than model that impact through other parameter choices.
   */
  use_override?: boolean;
  /**
   * Proportion of animals affected by intervention
   */
  prop_affected?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * A confidence interval estimate for the absolute amount of hours an average individual of the target species will spend in pain during its lifetime. This should be restricted *only* to the type of suffering that is addressable through the intervention.
   */
  hours_spent_suffering?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The proportion of an animal's suffering that is reduced by the intervention.
   */
  prop_suffering_reduced?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The probability that the animal welfare intervention succeeds.
   */
  prob_success?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * How many US dollars does it cost to implement the intervention.
   */
  cost_of_intervention?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * How long the intervention's effects will last, in years.
   */
  persistence?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * If set, this value determines suffering-years averted per dollar, overriding other calculations.
   */
  suffering_years_per_dollar_override?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
};

