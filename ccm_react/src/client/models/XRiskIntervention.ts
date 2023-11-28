/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BetaDistributionSpec } from './BetaDistributionSpec';
import type { CategoricalDistributionSpec } from './CategoricalDistributionSpec';
import type { ConfidenceDistributionSpec } from './ConfidenceDistributionSpec';
import type { ConstantDistributionSpec } from './ConstantDistributionSpec';
import type { GammaDistributionSpec } from './GammaDistributionSpec';
import type { RiskTypeAI } from './RiskTypeAI';
import type { RiskTypeGLT } from './RiskTypeGLT';
import type { UniformDistributionSpec } from './UniformDistributionSpec';

export type XRiskIntervention = {
  type?: 'xrisk';
  /**
   * The name of the intervention. Acts as an ID.
   */
  name: string;
  area?: 'xrisk';
  /**
   * A longer description for the x-risk intervention.
   */
  description?: (string | null);
  version?: '1';
  /**
   * Which type of existential/catastrophic risk the intervention deals with.
   */
  risk_type: (RiskTypeAI | RiskTypeGLT);
  /**
   * The cost of the intervention, as a range (in US dollars). If not provided, a reasonable default is estimated based in the impact magnitude, with a mean of USD ~12M for 0.5% relative risk reduced and ~6B for 20% of relative risk reduced.
   */
  cost?: ((UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec) | null);
  /**
   * How long the intervention's effects will last, in years.
   */
  persistence?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * How probable it is that the intervention will lead to a net positive result.
   */
  prob_good?: number;
  /**
   * How probable it is that the intervention has no effect at all.
   */
  prob_no_effect?: number;
  /**
   * Estimated net bad effect that can be caused by the intervention (e.g., through dual-use research), expressed as a proportion of the intervention's intended effect.
   */
  intensity_bad?: number;
  /**
   * The proportional effect of the intervention on reducing existential risks.
   */
  effect_on_xrisk?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
  /**
   * The proportional effect of the intervention on reducing catastrophic risks.
   */
  effect_on_catastrophic_risk?: (UniformDistributionSpec | ConstantDistributionSpec | ConfidenceDistributionSpec | GammaDistributionSpec | BetaDistributionSpec | CategoricalDistributionSpec);
};

