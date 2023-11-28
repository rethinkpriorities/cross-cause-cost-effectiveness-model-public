import { sort as d3sort } from "d3";
import { SparseSamples } from "../../client/models/SparseSamples";

type Samples = number[] | SparseSamples;

const sum = (arr: number[]) => arr.reduce((acc, v) => acc + v, 0);

const sort = (values: Samples): SparseSamples => {
  if ("samples" in values) {
    return {
      samples: d3sort(values.samples),
      num_zeros: values.num_zeros,
    };
  } else {
    return {
      samples: d3sort(values),
      num_zeros: 0,
    };
  }
};

/*
 * Expected Value Variants
 */
export const calculateEVWithBounds = (
  values: Samples,
  lowerProportion?: number,
  upperProportion?: number,
): number => {
  const sortedValues = sort(values);
  let lower;
  let upper;
  let boundedSize;
  if (sortedValues.num_zeros > 0) {
    const totalSize = sortedValues.samples.length + sortedValues.num_zeros;
    let zeroIndex = sortedValues.samples.findIndex((v) => v > 0);
    lower = Math.ceil((lowerProportion ?? 0) * totalSize);
    upper = Math.floor((upperProportion ?? 1) * totalSize);
    boundedSize = upper - lower;

    if (zeroIndex == -1) {
      zeroIndex = sortedValues.samples.length;
    }
    if (lower >= zeroIndex + sortedValues.num_zeros) {
      lower -= sortedValues.num_zeros;
    } else if (lower >= zeroIndex) {
      lower = zeroIndex;
    }
    if (upper >= zeroIndex + sortedValues.num_zeros) {
      upper -= sortedValues.num_zeros;
    } else if (upper >= zeroIndex) {
      upper = zeroIndex;
    }
  } else {
    lower = Math.ceil((lowerProportion ?? 0) * sortedValues.samples.length);
    upper = Math.floor((upperProportion ?? 1) * sortedValues.samples.length);
    boundedSize = upper - lower;
  }

  const relevantResults = sortedValues.samples.slice(lower, upper);
  return sum(relevantResults) / boundedSize;
};

export const calculateEV = (values: Samples) => calculateEVWithBounds(values);

export const calculateEV99 = (values: Samples) =>
  calculateEVWithBounds(values, 0.005, 0.995);

export const calculateEV99_9 = (values: Samples) =>
  calculateEVWithBounds(values, 0.0005, 0.9995);

/*
 * REU
 *
 */
// Returns the REU of a dataset, assuming each point is a utility with equal probability.
export const calculateREU = (
  values: Samples,
  riskFunc: (arg0: number) => number,
) => {
  const sortedValues = sort(values);
  let zeroIndex: number | undefined = undefined;
  if (sortedValues.num_zeros > 0) {
    zeroIndex = sortedValues.samples.findIndex((v) => v > 0);
    if (zeroIndex == -1) zeroIndex = sortedValues.samples.length;
    // Insert a single 0 to represent the sparse zeros. And since we just
    // inserted a true zero, subtract one from num_zeros.
    sortedValues.samples.splice(zeroIndex, 0, 0);
    sortedValues.num_zeros -= 1;
  }
  return sortedValues.samples.reduce(
    (acc, _d, idx) =>
      acc + getREUWeightedValue(sortedValues, idx, riskFunc, zeroIndex),
    0,
  );
};

// Gets the direct contribution to REU of an index from a dataset.
// Datapoints also have an indirect contribution by changing the probabilities of other values.
const getREUWeightedValue = (
  values: SparseSamples,
  idx: number,
  riskFunc: (arg0: number) => number,
  zeroIndex?: number,
) => {
  const numSamples = values.samples.length + values.num_zeros;
  if (idx === 0) return values.samples[0];
  const diff = values.samples[idx] - values.samples[idx - 1];
  const trueIndex =
    zeroIndex != undefined && idx > zeroIndex ? idx + values.num_zeros : idx;
  const probAtLeastAsGood = 1 - trueIndex / numSamples;
  return diff * riskFunc(probAtLeastAsGood);
};

// The risk function to use to discount.
const rEUWeight03 = -2 / Math.log10(0.03);
const rEUWeight05 = -2 / Math.log10(0.05);
const rEUWeight10 = -2 / Math.log10(0.1);
const p03RiskFunc = (prob: number) => prob ** rEUWeight03;
const p05RiskFunc = (prob: number) => prob ** rEUWeight05;
const p10RiskFunc = (prob: number) => prob ** rEUWeight10;

/* Specific version */
export const calculateREU03 = (values: Samples) =>
  calculateREU(values, p03RiskFunc);

export const calculateREU05 = (values: Samples) =>
  calculateREU(values, p05RiskFunc);

export const calculateREU10 = (values: Samples) =>
  calculateREU(values, p10RiskFunc);

/*
 * WLU
 */
const calculateWLU = (
  values: Samples,
  weightFunc: (arg0: number) => number,
) => {
  if ("samples" in values) {
    const numSamples = values.samples.length + values.num_zeros;
    const sortedDenseValues = d3sort(values.samples);
    const denseWeights = sortedDenseValues.map(weightFunc);
    const zeroWeight = weightFunc(0);
    const averageWeight =
      (sum(denseWeights) + zeroWeight * values.num_zeros) / numSamples;
    const weightingFactors = denseWeights.map((r) => r / averageWeight);
    return (
      sortedDenseValues.reduce(
        (acc, r, idx) => acc + r * weightingFactors[idx],
        0,
      ) / numSamples
    );
  } else {
    const sortedValues = d3sort(values);
    const weights = sortedValues.map(weightFunc);
    const averageWeight = sum(weights) / weights.length;
    const weightingFactors = weights.map((r) => r / averageWeight);
    return (
      sortedValues.reduce((acc, r, idx) => acc + r * weightingFactors[idx], 0) /
      sortedValues.length
    );
  }
};
const w03WeightFunc = (value: number) => {
  if (value < 0) {
    return 2 - 1 / (1 + Math.abs(value) ** 0.1);
  } else {
    return 1 / (1 + value ** 0.1);
  }
};
const w05WeightFunc = (value: number) => {
  if (value < 0) {
    return 2 - 1 / (1 + Math.abs(value) ** 0.21);
  } else {
    return 1 / (1 + value ** 0.21);
  }
};
const w10WeightFunc = (value: number) => {
  if (value < 0) {
    return 2 - 1 / (1 + Math.abs(value) ** 0.33);
  } else {
    return 1 / (1 + value ** 0.33);
  }
};

/* Specific version */
export const calculateWLU03 = (values: Samples) => {
  return calculateWLU(values, w03WeightFunc);
};
export const calculateWLU05 = (values: Samples) => {
  return calculateWLU(values, w05WeightFunc);
};
export const calculateWLU10 = (values: Samples) => {
  return calculateWLU(values, w10WeightFunc);
};
