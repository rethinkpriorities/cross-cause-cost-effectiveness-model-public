import {
  BetaDistributionSpec,
  CategoricalDistributionSpec,
  ConfidenceDistributionSpec,
  ConstantDistributionSpec,
  GammaDistributionSpec,
  UniformDistributionSpec,
} from "../client";

export type DistributionSpec =
  | BetaDistributionSpec
  | ConfidenceDistributionSpec
  | ConstantDistributionSpec
  | GammaDistributionSpec
  | UniformDistributionSpec
  | CategoricalDistributionSpec;

export const distDefaults: Record<DistributionSpec["type"], DistributionSpec> =
  {
    confidence: {
      type: "confidence",
      distribution: null,
      range: [0, 1],
      credibility: 90,
    },
    uniform: {
      type: "uniform",
      distribution: "uniform",
      range: [0, 1],
    },
    constant: {
      type: "constant",
      distribution: "constant",
      value: 1,
    },
    beta: {
      type: "beta",
      distribution: "beta",
      alpha: 1,
      beta: 1,
    },
    gamma: {
      type: "gamma",
      distribution: "gamma",
      shape: 3,
      scale: 5,
    },
    categorical: {
      type: "categorical",
      distribution: "categorical",
      items: [
        [-1, 0.5],
        [1, 0.5],
      ],
    },
  };

export function distributionToSquiggle(model: DistributionSpec): string {
  // Build the inner distribution
  let distribution: string;
  if (model.type === "confidence") {
    const range = model.range as [number, number];
    let distributionName = model.distribution;
    if (distributionName === null) {
      //  This follows the squigglepy "to" logic.
      if (range[0] <= 0) {
        distributionName = "normal";
      } else {
        distributionName = "lognormal";
      }
    }
    if (model.credibility == 90) {
      distribution = `${model.distribution}({p5: ${range[0]}, p95: ${range[1]}})`;
    } else if (model.credibility == 80) {
      distribution = `${model.distribution}({p10: ${range[0]}, p90: ${range[1]}})`;
    } else if (model.credibility == 50) {
      distribution = `${model.distribution}({p25: ${range[0]}, p75: ${range[1]}})`;
    } else {
      throw new Error(`Unsupported credibility: ${model.credibility}`);
    }
  } else if (model.type === "uniform") {
    distribution = `${model.distribution}(${model.range[0]}, ${model.range[1]})`;
  } else if (model.type === "gamma") {
    // TODO: check squiggle parameterization of this dist
    distribution = `${model.distribution}(${model.shape}, ${model.scale})`;
  } else if (model.type === "beta") {
    distribution = `${model.distribution}(${model.alpha}, ${model.beta})`;
  } else if (model.type === "constant") {
    distribution = `${model.value}`;
  } else {
    throw new Error(`Unsupported distribution type: ${JSON.stringify(model)}`);
  }

  // Clip the distribution if necessary.
  if (
    "clip" in model &&
    model.clip &&
    (model.clip[1] !== null || model.clip[0] !== null)
  ) {
    // Compute right, left, or both truncation depending on what is defined.
    const types: Record<string, Record<string, string>> = {
      object: { number: "Right" },
      undefined: { number: "Right" },
      number: { object: "Left", undefined: "Left", number: "" },
    };
    const truncateType = types[typeof model.clip[0]][typeof model.clip[1]];
    distribution = `truncate${truncateType}(${distribution}, ${model.clip
      .filter((v) => typeof v !== "object")
      .join(", ")})`;
  }

  return distribution;
}

export function rangeToConfidenceModel(
  range: [number, number],
  credibility: 90 | 80 | 50,
  clip?: [number | undefined, number | undefined],
  distributionTypeOverride?: "normal" | "lognormal" | null,
): ConfidenceDistributionSpec {
  let distributionType: "normal" | "lognormal";
  // This follows the squigglepy "to" logic.
  if (range[0] <= 0) {
    distributionType = "normal";
  } else {
    distributionType = "lognormal";
  }

  return {
    type: "confidence",
    distribution: distributionTypeOverride ?? distributionType,
    range: range,
    credibility: credibility,
    clip,
  };
}

export function rangeToUniformModel(
  range: [number, number],
): UniformDistributionSpec {
  return {
    type: "uniform",
    distribution: "uniform",
    range: range,
  };
}

/* Calculates the mean of a distribution. Returns null if it cannot be calculated
 * for distributions of the given type.
 */
export function distributionMean(
  distribution: DistributionSpec,
): number | null {
  switch (distribution.type) {
    case "constant":
      return distribution.value;
    case "confidence":
      if (distribution.distribution == "lognormal") {
        return Math.sqrt(distribution.range[0] * distribution.range[1]);
      } else {
        return (distribution.range[0] + distribution.range[1]) / 2;
      }
    case "uniform":
      return (distribution.range[0] + distribution.range[1]) / 2;
    case "beta":
      return distribution.alpha / (distribution.alpha + distribution.beta);
    case "gamma":
      return distribution.shape * distribution.scale;
    default:
      return null;
  }
}

/* Calculates the standard deviation of a distribution. Returns null if it cannot
 * be calculated for distributions of the given type.
 */
export function distributionStdev(
  distribution: DistributionSpec,
): number | null {
  switch (distribution.type) {
    case "constant":
      return 0;
    case "confidence": {
      const numSdtevs = {
        50: 0.674,
        80: 1.282,
        90: 1.645,
      }[distribution.credibility ?? 90];
      if (distribution.distribution == "lognormal") {
        const lo = Math.log(distribution.range[0] as number);
        const hi = Math.log(distribution.range[1] as number);
        const sigma = (hi - lo) / 2 / numSdtevs;
        const mu = (lo + hi) / 2;
        return Math.sqrt(
          (Math.exp(sigma ** 2) - 1) * Math.exp(2 * mu + sigma ** 2),
        );
      } else {
        const lo = distribution.range[0] as number;
        const hi = distribution.range[1] as number;
        const sigma = (hi - lo) / 2 / numSdtevs;
        return sigma;
      }
    }
    case "uniform":
      return (distribution.range[1] - distribution.range[0]) / Math.sqrt(12);
    case "beta": {
      const a = distribution.alpha;
      const b = distribution.beta;
      return Math.sqrt((a * b) / (a + b) ** 2 / (a + b + 1));
    }
    case "gamma":
      return Math.sqrt(distribution.shape) * distribution.scale;
    default:
      return null;
  }
}

export function distributionBulk(
  distribution: DistributionSpec,
): number | null {
  const mean = distributionMean(distribution);
  const stdev = distributionStdev(distribution);
  if (mean && stdev) return mean + 3 * stdev;
  return null;
}

/* Sets the distribution to have the given mean and standard deviation. If the
 * distribution cannot be set from a mean and standard deviation, does nothing.
 */
export function setDistributionFromMoments({
  dist,
  mean,
  stdev,
  positiveEverywhere = false,
  significantFigures = 3,
}: {
  dist: DistributionSpec;
  mean: number;
  stdev: number;
  positiveEverywhere?: boolean;
  significantFigures?: number;
}) {
  const round = (x: number) => {
    if (x == 0) return 0;
    const magnitude = Math.floor(Math.log10(Math.abs(x)));
    const scale = Math.pow(10, significantFigures - magnitude - 1);
    return Math.round(x * scale) / scale;
  };

  const numStdevs = 1.645; // represents a 90% CI for a normal distribution
  if (stdev == 0) {
    // A constant distribution produces a stdev of 0. In that case, set the
    // stdev to be 20% of the mean as a reasonable default.
    stdev = 0.2 * mean;
  }
  switch (dist.type) {
    case "constant":
      dist.value = round(mean);
      break;
    case "confidence":
    case "uniform":
      if (dist.distribution == "lognormal" || positiveEverywhere) {
        // If dist is normal but positiveEverywhere is true, then construct a lognormal
        // distribution instead.
        const mu = Math.log(mean - stdev ** 2 / 2);
        const sigma = Math.sqrt(Math.log(1 + stdev ** 2 / mean ** 2));
        dist.distribution = "lognormal";
        dist.range = [
          Math.exp(mu - numStdevs * sigma),
          Math.exp(mu + numStdevs * sigma),
        ];
      } else {
        dist.range = [
          round(mean - numStdevs * stdev),
          round(mean + numStdevs * stdev),
        ];
      }
      break;
    case "beta":
      if (mean >= 1 || stdev >= 0.25) {
        // This mean/stdev cannot be modeled as a beta distribution
        return;
      }
      dist.alpha = round(mean * ((mean * (1 - mean)) / stdev ** 2 - 1));
      dist.beta = round((dist.alpha * (1 - mean)) / mean);
      break;
    case "gamma":
      dist.shape = round(mean ** 2 / stdev ** 2);
      dist.scale = round(stdev ** 2 / mean);
      break;
    default:
      break;
  }
}
