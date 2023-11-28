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

export type ResearchProjectAttributesModel = {
  /**
   * The number of full-time-equivalent years of work required to complete the research project.
   */
  fte_years: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The cost of one full-time-equivalent year of work on the research project.
   */
  cost_per_staff_year: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The probability that the research projects find a new intervention (the target intervention). It can also be seen as the probability that the project's conclusions cause an update regarding the best available intervention.
   */
  conclusions_require_updating: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The probability that the funder will alter their views in light of the research project, moving money to the target intervention.
   */
  target_updating: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The amount of money in the area relevant to the research project, in millions of US dollars.
   */
  money_in_area_millions: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The percentage of money in the area relevant to the research project that is influenceable.
   */
  percent_money_influenceable: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The number of years until the discovery would have been made counterfactually, if not for the research project.
   */
  years_credit: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
};

