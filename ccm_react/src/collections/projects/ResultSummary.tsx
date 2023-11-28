import { useAtomValue } from "jotai";
import { useWindowDimensions } from "../../hooks/useWindowDimensions";
import { projectAssessmentAtom } from "../../stores/atoms";
import { numberAsDollars, numberAsIntegerString } from "../../utils/formatting";
import {
  sparseLength,
  sparseMean,
  sparseMedian,
  sparseNth,
} from "../../utils/sparseSamples";
import { Figure } from "../../components/wrappers/Figure.tsx";
import { WaffleChart } from "../../components/plots/WaffleChart";
import { ResultValue } from "../../components/elements/ResultValue";
import { SparseSampleExplainer } from "../../components/SparseSampleExplainer";

const DescribeConfidence = ({
  costPerImpactCI,
}: {
  costPerImpactCI: [number, number];
}) => {
  if (isFinite(costPerImpactCI[0]) && isFinite(costPerImpactCI[1])) {
    return (
      <>
        90% of simulations falling between{" "}
        <ResultValue>{numberAsDollars(costPerImpactCI[0])}</ResultValue> and{" "}
        <ResultValue>{numberAsDollars(costPerImpactCI[1])}</ResultValue>
      </>
    );
  } else if (isFinite(costPerImpactCI[0])) {
    return (
      <>
        95% of simulations falling above{" "}
        <ResultValue>{numberAsDollars(costPerImpactCI[0])}</ResultValue>
      </>
    );
  } else {
    return (
      <>
        95% of simulations falling below{" "}
        <ResultValue>{numberAsDollars(costPerImpactCI[1])}</ResultValue>
      </>
    );
  }
};

export function ResultSummary() {
  const windowDimensions = useWindowDimensions();
  const projectAssessment = useAtomValue(projectAssessmentAtom);
  if (!projectAssessment) return null;

  const averageImpact = sparseMean(projectAssessment.gross_impact);
  const averageCost = sparseMean({
    samples: projectAssessment.cost,
    num_zeros: 0,
  });

  const results = projectAssessment.gross_impact;
  const numSimulations = sparseLength(results);
  const impactPerDollar = {
    samples: projectAssessment.gross_impact.samples
      .map((gI, idx) => gI / projectAssessment.cost[idx])
      .sort((a, b) => (a < b ? -1 : 1)),
    num_zeros: projectAssessment.gross_impact.num_zeros,
  };
  const medianCost = 1 / sparseMedian(impactPerDollar);
  const costPerImpactCI: [number, number] = [
    1 / sparseNth(impactPerDollar, Math.floor(numSimulations / 20)),
    1 / sparseNth(impactPerDollar, Math.floor((numSimulations * 19) / 20)),
  ];

  const numWaffleBins = 1000;
  const samplesPerBin = numSimulations / numWaffleBins;
  const zeroIndex =
    results.samples.findIndex((i) => i >= 0) ?? results.samples.length - 1;
  const simulationValue = (idx: number) => {
    if (idx < zeroIndex) {
      return results.samples[idx];
    } else if (idx > zeroIndex + results.num_zeros) {
      return results.samples[idx - results.num_zeros];
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

  return (
    <>
      Over {numberAsIntegerString(numSimulations)} simulations
      <SparseSampleExplainer samples={projectAssessment.gross_impact} />, this
      project was found to produce on average the equivalent of{" "}
      <ResultValue>{numberAsIntegerString(averageImpact)}</ResultValue> DALYs
      averted in value at a cost of{" "}
      <ResultValue>{numberAsDollars(averageCost)}</ResultValue>. This gives it
      an average cost per DALY averted of{" "}
      <ResultValue>{numberAsDollars(averageCost / averageImpact)}</ResultValue>{" "}
      with{" "}
      {isFinite(medianCost) ? (
        <>
          a median cost per DALY averted of{" "}
          <ResultValue>{numberAsDollars(medianCost)}</ResultValue>
        </>
      ) : (
        <>
          the median result having <ResultValue>no effect</ResultValue>
        </>
      )}
      {(isFinite(costPerImpactCI[0]) || isFinite(costPerImpactCI[1])) && (
        <>
          {" "}
          and <DescribeConfidence costPerImpactCI={costPerImpactCI} />
        </>
      )}
      .{" "}
      <Figure
        name="Result Breakdown"
        caption={
          <>
            This chart depicts positive and negative values among simulation
            results. Each square represents{" "}
            {numberAsIntegerString(numSimulations / numWaffleBins)} outcomes.
            Squares that represent multiple kinds of results are shaded
            accordingly.
          </>
        }
      >
        <WaffleChart
          bins={waffleBins}
          rows={windowDimensions.width > 720 ? 25 : 40}
          labels={["Negative", "No Effect", "Positive"]}
        />
      </Figure>
    </>
  );
}
