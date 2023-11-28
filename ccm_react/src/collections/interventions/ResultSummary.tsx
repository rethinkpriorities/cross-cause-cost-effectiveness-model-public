import React from "react";
import { mean as d3Mean } from "d3";
import type { SparseSamples } from "../../client/models/SparseSamples";
import { useWindowDimensions } from "../../hooks/useWindowDimensions";
import {
  numberAsDollars,
  numberAsIntegerString,
  numberAsDecimalString,
} from "../../utils/formatting";
import { sparseMean, sparseMedian, sparseNth } from "../../utils/sparseSamples";
import { Figure } from "../../components/wrappers/Figure.tsx";
import { WaffleChart } from "../../components/plots/WaffleChart";
import { ResultValue } from "../../components/elements/ResultValue";
import { SparseSampleExplainer } from "../../components/SparseSampleExplainer";

const DescribeConfidence = ({
  confidenceImpact,
}: {
  confidenceImpact: [number, number];
}) => {
  if (
    isFinite(confidenceImpact[0]) &&
    isFinite(confidenceImpact[1]) &&
    confidenceImpact[0] === confidenceImpact[1]
  ) {
    return (
      <>
        90% of simulations equal{" "}
        <ResultValue>{confidenceImpact[0]}</ResultValue>
      </>
    );
  } else if (isFinite(confidenceImpact[0]) && isFinite(confidenceImpact[1])) {
    return (
      <>
        90% of simulations fall between{" "}
        <ResultValue>{numberAsDollars(confidenceImpact[0])}</ResultValue> and{" "}
        <ResultValue>{numberAsDollars(confidenceImpact[1])}</ResultValue>
      </>
    );
  } else if (isFinite(confidenceImpact[0])) {
    return (
      <>
        95% of simulations are less effective than{" "}
        <ResultValue>{numberAsDollars(confidenceImpact[0])}</ResultValue> per
        DALY averted
      </>
    );
  } else {
    return (
      <>
        95% of simulations are more effective than{" "}
        <ResultValue>{numberAsDollars(confidenceImpact[1])}</ResultValue> per
        DALY averted
      </>
    );
  }
};

export const ResultSummary = React.memo(function ResultSummary({
  results,
  includeWaffleChart = false,
}: {
  results: SparseSamples;
  includeWaffleChart: boolean;
}) {
  const windowDimensions = useWindowDimensions();
  const numNonZeroSamples = results.samples.filter((s) => s !== 0).length;

  const numDenseSamples = results.samples.length;
  const numZeros = results.num_zeros;
  const numSimulations = numDenseSamples + numZeros;
  const medianImpact = sparseMedian(results);
  const significantResults = results.samples.filter((r) => r !== 0);
  const averageSignificantImpact = d3Mean(significantResults) ?? 0;
  const numSignificantResults =
    1 -
    (numZeros + (numDenseSamples - significantResults.length)) / numSimulations;
  const averageImpact = sparseMean(results);
  const confidenceImpact: [number, number] = [
    sparseNth(results, numSimulations / 20),
    sparseNth(results, (numSimulations * 19) / 20),
  ];
  const numWaffleBins = 1000;
  const samplesPerBin = numSimulations / numWaffleBins;
  const zeroIndex =
    results.samples.findIndex((i) => i >= 0) ?? results.samples.length - 1;
  const simulationValue = (idx: number) => {
    if (idx < zeroIndex) {
      return results.samples[idx];
    } else if (idx > zeroIndex + numZeros) {
      return results.samples[idx - numZeros];
    } else {
      return 0;
    }
  };
  // Split simulations into a number of bins, record the start and end signs of the values in each bin.
  const waffleBins: [number, number][] = Array(numWaffleBins)
    .fill(0)
    .map((_, idx) => [
      Math.sign(simulationValue(idx * samplesPerBin)),
      Math.sign(
        simulationValue(
          Math.min((idx + 1) * samplesPerBin, numSimulations - 1),
        ),
      ),
    ]);

  if (!results) return null;
  if (numNonZeroSamples === 0) {
    return (
      <>
        The intervention had no effect in any of the{" "}
        {numberAsIntegerString(numSimulations)} samples. Consider changing the
        parameter settings or trying again.
      </>
    );
  }
  return (
    <>
      <p>
        Over {numberAsIntegerString(numSimulations)} simulations
        <SparseSampleExplainer samples={results} />, this intervention was found
        to produce on average the equivalent of{" "}
        <ResultValue>{numberAsIntegerString(averageImpact)}</ResultValue> DALYs
        averted in value per $1000. It produced{" "}
        <ResultValue>
          {numberAsIntegerString(averageSignificantImpact)}
        </ResultValue>{" "}
        DALYs on average in the cases where it had an effect, which is{" "}
        <ResultValue>
          {numberAsDecimalString(numSignificantResults * 100)}%
        </ResultValue>{" "}
        of all simulations.
      </p>
      <h4 className="text-center">
        <ResultValue className="text-4xl">
          <span className="bold">{numberAsIntegerString(averageImpact)}</span>
        </ResultValue>{" "}
        DALYs / $1000
      </h4>{" "}
      <p>
        This gives it an average cost per DALY averted of{" "}
        <ResultValue>{numberAsDollars(1000 / averageImpact)}</ResultValue>
        {medianImpact != 0 ? (
          <>
            {" "}
            with a median cost per DALY averted of{" "}
            <ResultValue>{numberAsDollars(1000 / medianImpact)}</ResultValue>
          </>
        ) : (
          <>. </>
        )}
        {(isFinite(confidenceImpact[0]) || isFinite(confidenceImpact[1])) && (
          <>
            <DescribeConfidence confidenceImpact={confidenceImpact} />
          </>
        )}
        .
      </p>
      {includeWaffleChart && (
        <Figure
          name="Result Breakdown"
          caption={
            <>
              This chart depicts positive and negative values among simulation
              results. Each square represents {numDenseSamples / numWaffleBins}{" "}
              outcomes. Squares that represent multiple kinds of results are
              shaded accordingly.
            </>
          }
        >
          <WaffleChart
            bins={waffleBins}
            rows={windowDimensions.width > 720 ? 25 : 40}
            labels={["Negative", "No Effect", "Positive"]}
          />
        </Figure>
      )}
    </>
  );
});
