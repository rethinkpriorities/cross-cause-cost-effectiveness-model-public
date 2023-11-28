import { cumsum } from "d3";
import React from "react";
import type { SparseSamples } from "../../client/models/SparseSamples";
import { numberAsIntegerString } from "../../utils/formatting";
import { Figure } from "../../components/wrappers/Figure.tsx";
import { DotHistogram } from "../../components/plots/DotHistogram";
import { Histogram } from "../../components/plots/Histogram/Histogram";
import { PlotContainer } from "../../components/plots/PlotContainer";

export const DALYsPer1000 = ({
  interventionSamples,
}: {
  interventionSamples: SparseSamples;
}) => {
  const numNonZeroSamples = React.useMemo(
    () => interventionSamples.samples.filter((s) => s !== 0).length,
    [interventionSamples],
  );

  const numSimulations = React.useMemo(
    () => interventionSamples.samples.length + interventionSamples.num_zeros,
    [interventionSamples],
  );
  const totalValue = React.useMemo(
    () => interventionSamples.samples.reduce((acc, s) => acc + s, 0),
    [interventionSamples],
  );

  if (numNonZeroSamples === 0) return null;
  const numZeroSamples = numSimulations - numNonZeroSamples;
  const zeroIndex = interventionSamples.samples.findIndex((a) => a >= 0) ?? 0;
  const cumulativeCount = interventionSamples.samples.map((_d, idx) =>
    idx < zeroIndex ? idx : idx + numZeroSamples,
  );
  const absSamplesWithZero = interventionSamples.samples.map((d) =>
    Math.abs(d),
  );
  if (interventionSamples.samples[zeroIndex] !== 0) {
    cumulativeCount.splice(zeroIndex, 0, numZeroSamples);
    absSamplesWithZero.splice(zeroIndex, 0, 0);
  } else {
    cumulativeCount[zeroIndex] =
      (cumulativeCount[zeroIndex - 1] ?? 0) + numZeroSamples;
  }
  return (
    <>
      <h4 id="cost-effectiveness">Cost-effectiveness</h4>
      <p>
        The DALYs averted per $1000 of an intervention is a measure of its
        impact in value in the equivalent number of Disability-adjusted Life
        Years averted per $1000 U.S. spent on it.
      </p>
      <Figure
        name="DALYs per $1k"
        caption={
          <>
            This histogram displays the distribution of outcome values across{" "}
            {numberAsIntegerString(numSimulations)} simulations in terms of the
            value returned per $1,000 spent.
          </>
        }
      >
        <PlotContainer>
          <Histogram
            title="DALYs per $1k"
            data={interventionSamples}
            unit="DALYs averted"
          />
        </PlotContainer>
      </Figure>
      {numNonZeroSamples > 10 && (
        <Figure
          name="Contributions to Expected Value"
          caption={
            <>
              This chart shows how simulation results are distributed along a
              log scale of expected impact values. The radius of a circle
              indicates the magnitude of the values at that point: either the
              total number of results or sum of their contributions to the
              expected value. A single result&apos;s contribution to the
              expected value equals the result&apos;s absolute value weighted by
              its probability.
            </>
          }
        >
          <PlotContainer>
            <DotHistogram
              rawData={interventionSamples}
              dataPlots={[
                {
                  rCalc: (length, lo, hi) =>
                    (length * Math.abs((lo + hi) / 2)) / totalValue,
                  cumData: [...cumsum(absSamplesWithZero)],
                  colorTransparent: "rgba(69, 119, 178,0.2)",
                  colorSolid: "rgba(69, 119, 178,1)",
                  label: "contributions to expected value",
                },
                {
                  rCalc: (length, _0, _1) => length / numSimulations,
                  cumData: cumulativeCount,
                  colorTransparent: "rgba(69, 119, 178,0.2)",
                  colorSolid: "rgba(69, 119, 178,1)",
                  label: "total number of results",
                },
              ]}
            />
          </PlotContainer>
        </Figure>
      )}
    </>
  );
};
