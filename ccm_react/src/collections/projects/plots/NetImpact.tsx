import { cumsum } from "d3";
import { useAtomValue } from "jotai";
import { projectAssessmentAtom } from "../../../stores/atoms";
import { numberAsIntegerString } from "../../../utils/formatting";
import {
  sparseLength,
  sparseMean,
  sparseMedian,
  sparseNth,
} from "../../../utils/sparseSamples";
import { Figure } from "../../../components/wrappers/Figure.tsx";
import { DotHistogram } from "../../../components/plots/DotHistogram";
import { Histogram } from "../../../components/plots/Histogram/Histogram";
import { PlotContainer } from "../../../components/plots/PlotContainer";
import { ResultValue } from "../../../components/elements/ResultValue";

export function NetImpact() {
  const projectAssessment = useAtomValue(projectAssessmentAtom);
  if (!projectAssessment) return null;
  projectAssessment.net_impact.samples =
    projectAssessment.net_impact.samples.sort((a, b) => (a < b ? -1 : 1));
  const numSimulations = sparseLength(projectAssessment.net_impact);
  const mean = sparseMean(projectAssessment.net_impact);
  const median = sparseMedian(projectAssessment.net_impact);
  const twoPointFive = sparseNth(
    projectAssessment.net_impact,
    Math.ceil(sparseLength(projectAssessment.net_impact) * 0.025),
  );
  const ninetySevenPointFive = sparseNth(
    projectAssessment.net_impact,
    Math.floor(sparseLength(projectAssessment.net_impact) * 0.975),
  );

  const totalValue = projectAssessment.net_impact.samples.reduce(
    (acc, d) => acc + Math.abs(d),
    0,
  );

  return (
    <>
      <h4>Total Net Impact (DALYs)</h4>
      <p>
        The <i>net impact</i> of a project is a measure of its impact in
        DALY-averted equivalent units. It takes into account both the
        counterfactual costs of the change in the intervention and the costs of
        staff time. (Counterfactual research projects are not included in the
        estimated value, just the dollar cost of staff employment.)
      </p>
      <p>
        In the {numberAsIntegerString(numSimulations)} simulations in this run,
        the intervention averted a{" "}
        <ResultValue>mean of {numberAsIntegerString(mean)}</ResultValue> net
        DALYs. The{" "}
        <ResultValue>median is {numberAsIntegerString(median)}</ResultValue> net
        DALYs averted and{" "}
        <ResultValue>
          95% of results fall between {numberAsIntegerString(twoPointFive)} and{" "}
          {numberAsIntegerString(ninetySevenPointFive)}
        </ResultValue>
        .
      </p>
      <Figure
        name="Net Impact"
        caption={
          <>
            This histogram displays the distribution of outcome values across
            the simulation in terms of the value returned per $1,000 spent.{" "}
          </>
        }
      >
        <PlotContainer>
          <Histogram
            title="Net impact"
            data={projectAssessment.net_impact}
            unit="DALYs averted"
          />
        </PlotContainer>
      </Figure>
      <Figure
        name="Contributions to Expected Value"
        caption={
          <>
            This chart shows how simulation results are distributed along a log
            scale of expected impact values. The radius of a circle indicates
            the magnitude of the values at that point: either the total number
            of results or sum of their contributions to the expected value. A
            single result&apos;s contribution to the expected value equals the
            result&apos;s absolute value weighted by its probability.
          </>
        }
      >
        <PlotContainer>
          <DotHistogram
            rawData={projectAssessment.net_impact}
            dataPlots={[
              {
                rCalc: (length, lo, hi) =>
                  (length * Math.abs((lo + hi) / 2)) / totalValue,
                cumData: [
                  ...cumsum(
                    projectAssessment.net_impact.samples.map((d) =>
                      Math.abs(d),
                    ),
                  ),
                ],
                colorTransparent: "rgba(69, 119, 178,0.2)",
                colorSolid: "rgba(69, 119, 178,1)",
                label: "contributions to expected value",
              },
              {
                rCalc: (length, _0, _1) =>
                  length / sparseLength(projectAssessment.net_impact),
                cumData: projectAssessment.net_impact.samples.map(
                  (_d, idx) => idx,
                ),
                colorTransparent: "rgba(69, 119, 178,0.2)",
                colorSolid: "rgba(69, 119, 178,1)",
                label: "total number of results",
              },
            ]}
          />
        </PlotContainer>
      </Figure>
    </>
  );
}
