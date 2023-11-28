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
import { Histogram } from "../../../components/plots/Histogram/Histogram";
import { PlotContainer } from "../../../components/plots/PlotContainer";
import { ResultValue } from "../../../components/elements/ResultValue";

export function DALYsPer1000() {
  const projectAssessment = useAtomValue(projectAssessmentAtom);
  if (!projectAssessment) return null;

  const numSimulations = sparseLength(projectAssessment.gross_impact);
  const averageImpact = sparseMean(projectAssessment.gross_impact);
  const averageCost =
    projectAssessment.cost.reduce((accum, i) => accum + i, 0) /
    projectAssessment.cost.length;
  {
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(averageCost / averageImpact);
  }
  const impactPerDollar = {
    samples: projectAssessment.gross_impact.samples
      .map((gI, i) => (1000 * gI) / projectAssessment.cost[i])
      .sort((a, b) => (a < b ? -1 : 1)),
    num_zeros: projectAssessment.gross_impact.num_zeros,
  };
  const mean = sparseMean(impactPerDollar);
  const median = sparseMedian(impactPerDollar);
  const twoPointFive = sparseNth(
    impactPerDollar,
    Math.ceil(sparseLength(impactPerDollar) * 0.025),
  );
  const ninetySevenPointFive = sparseNth(
    impactPerDollar,
    Math.floor(sparseLength(impactPerDollar) * 0.975),
  );

  let comparisonText = "";
  if (mean > 100) {
    comparisonText = `This puts it well above (~${Math.floor(
      mean / 18,
    )}x) the estimated cost effectiveness of GiveWell's top charities.`;
  } else if (mean > 23) {
    comparisonText = `This puts it somewhat above (~${Math.floor(
      mean / 18,
    )}x) the estimated cost effectiveness of GiveWell's top charities.`;
  } else if (mean > 13) {
    comparisonText =
      "This puts it around the estimated cost effectiveness of GiveWell's top charities.";
  } else if (mean > 5) {
    comparisonText =
      "This puts it a little below the estimated cost effectiveness of GiveWell's top charities.";
  } else {
    comparisonText =
      "This puts it below the estimated cost effectiveness of GiveWell's top charities.";
  }
  return (
    <>
      <h4>Gross DALYs Averted per $1000</h4>
      <p>
        The <i>DALYs averted per $1000</i> of a project is a measure of its
        impact in the number of equivalent Disability Adjusted Life Years
        averted per $1000 U.S. spent on it. The value takes into account the
        counterfactual costs of the project but does not take into account the
        costs of paying the researchers. Instead, those costs are reflected in
        number of DALYs averted per $1k.
      </p>
      <p>
        In the {numberAsIntegerString(numSimulations)} simulations in this run,
        the intervention averted a{" "}
        <ResultValue>mean of {numberAsIntegerString(mean)}</ResultValue> DALYs
        per $1000. {comparisonText} The{" "}
        <ResultValue>median is {numberAsIntegerString(median)}</ResultValue>{" "}
        DALYs averted per $1000 and{" "}
        <ResultValue>
          95% of results fall between {numberAsIntegerString(twoPointFive)} and{" "}
          {numberAsIntegerString(ninetySevenPointFive)}
        </ResultValue>
        .
      </p>
      <Figure
        name="DALYs per $1k"
        caption={
          <>
            This histogram displays the distribution of outcome values across
            the simulation in terms of the value returned per $1,000 spent.
          </>
        }
      >
        <PlotContainer>
          <Histogram
            title="DALYs per $1k"
            data={projectAssessment.gross_impact}
            unit="DALYs averted"
          />
        </PlotContainer>
      </Figure>
    </>
  );
}
