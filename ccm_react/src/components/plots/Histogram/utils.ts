import { sort } from "d3";
import { sortedIndex } from "lodash";
import { HIGHLIGHT_RED, NON_HIGHLIGHT_SALMON } from "./constants";

export const filterOutNearZeros = (sortedData: number[]): number[] => {
  // Sort data by absolute value so we can find the 90% and 99% centered around
  // zero.
  const dataAbsValues = sort(sortedData.map((d) => Math.abs(d)));

  const middleDomainLength = Math.floor(dataAbsValues.length * 0.9);
  const wideDomainLength = Math.floor(dataAbsValues.length * 0.99);
  const middleData = dataAbsValues.slice(0, middleDomainLength);
  const middleDomainEV = expectedValue(middleData, middleData.length);
  const wideDomainEV = expectedValue(
    dataAbsValues.slice(0, wideDomainLength),
    wideDomainLength,
  );

  const areMiddleValuesSmall = 10 * middleDomainEV < wideDomainEV;

  // If the values in the middle 90% of the distribution are small, filter out
  // all the values that have a smaller absolute value than the average value in
  // the middle 90%.
  const proximityToCountAsZero = areMiddleValuesSmall ? middleDomainEV : 0;
  const filteredForNearZeros = sortedData.filter(
    (d) => d > 0 + proximityToCountAsZero || d < 0 - proximityToCountAsZero,
  );
  return filteredForNearZeros;
};

// Return a function that takes a bin and returns a color for that bin based on
// the percentile of the middle value of the bin.
export const getColorScale =
  (sortedData: number[], highlightedValues: [number, number, number, number]) =>
  (d: [number]) => {
    // Find the percentile bucket that the middle member of each group falls into.
    const numberLessThan = sortedIndex(sortedData, d[0]) - 1;
    const numberGreaterThan = sortedIndex(sortedData, d[d.length - 1]) + 1;
    const value = (numberGreaterThan + numberLessThan) / 2 / sortedData.length;
    if (
      (value > highlightedValues[0] && value < highlightedValues[1]) ||
      (value > highlightedValues[2] && value <= highlightedValues[3])
    ) {
      return HIGHLIGHT_RED;
    } else {
      return NON_HIGHLIGHT_SALMON;
    }
  };

// Returns the expected value of a subset of samples from an array,
// assuming each sample has an equal probability.
const expectedValue = (array: number[], length: number) =>
  array.reduce((a, i) => a + Math.abs(i), 0) / length;

// Given data and a domain, computes the portion of the absolute expected value
// contributed by each.
export const getExpectedValueMasses = (
  data: number[],
  domain: [number, number],
): { below: number; included: number; above: number } => {
  const lowestIncludedIdx = data.findIndex((i) => i >= domain[0]);
  const highestIncludedIdx =
    data[data.length - 1] <= domain[1]
      ? data.length - 1
      : data.findIndex((i) => i > domain[1]) - 1;
  const values = {
    below:
      lowestIncludedIdx <= 0
        ? 0
        : expectedValue(data.slice(0, lowestIncludedIdx - 1), data.length),
    included: expectedValue(
      data.slice(lowestIncludedIdx, highestIncludedIdx),
      data.length,
    ),
    above:
      highestIncludedIdx >= data.length - 1
        ? 0
        : expectedValue(
            data.slice(highestIncludedIdx + 1, data.length),
            data.length,
          ),
  };
  const totalMass = Object.values(values).reduce((a, b) => a + b, 0);
  const normalizedMasses = {
    below: (100 * values.below) / totalMass,
    included: (100 * values.included) / totalMass,
    above: (100 * values.above) / totalMass,
  };
  return normalizedMasses;
};

export const getPercentageEVNegative = (data: number[]): number => {
  const negSum = data.filter((d) => d < 0).reduce((acc, d) => acc - d, 0);
  const posSum = data.filter((d) => d > 0).reduce((acc, d) => acc + d, 0);

  return (100 * negSum) / (negSum + posSum);
};
