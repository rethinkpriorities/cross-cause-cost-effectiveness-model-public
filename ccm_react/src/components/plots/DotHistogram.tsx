import * as Plot from "@observablehq/plot";
import { SparseSamples } from "../../client/models/SparseSamples";
import { numberAsIntegerString } from "../../utils/formatting";
import { symLog, symPow } from "../../utils/scaling";
import { ObservablePlot } from "./ObservablePlot";

interface DataPlot {
  cumData: number[];
  rCalc: (length: number, lo: number, hi: number) => number;
  colorTransparent: string;
  colorSolid: string;
  label: string;
}

// Plots a number of dot lines and cumulative line charts on a log scale.
// Takes 'dot plot' data to indicate what should go in each dot/line pair.
export const DotHistogram = ({
  rawData,
  dataPlots,
}: {
  rawData: SparseSamples;
  dataPlots: DataPlot[];
}) => {
  const dataMin = rawData.samples[0];
  const dataMax = rawData.samples[rawData.samples.length - 1];
  const midPoint = symLog(dataMin) + (symLog(dataMax) - symLog(dataMin)) / 2;
  const markBy = dataMin < -10000 || dataMax > 10000 ? 2 : 1;
  const numZeroSamples =
    rawData.num_zeros + rawData.samples.filter((x) => x == 0).length;
  const samplesWithZero = rawData.samples;
  const zeroIndex =
    samplesWithZero.findIndex((a) => a >= 0) ?? samplesWithZero.length - 1;
  // Add 0 if not present to account for extra sparse 0s.
  if (samplesWithZero[zeroIndex] !== 0) {
    samplesWithZero.splice(zeroIndex, 0, 0);
  }

  const options: Plot.PlotOptions = {
    x: {
      label: "Value per result",
      ticks: [
        0,
        // Mark off every log 10 values.
        // If markBy is 2, skip every other value.
        // Handles both positive and negative powers of 10.
        ...Array(40)
          .fill(1)
          .map(
            (_, i) =>
              (-1) ** Math.floor(i / 2) * 10 ** (markBy * Math.ceil(i / 2)),
          )
          // filter all irrelevant ones
          .filter((v: number) => v > dataMin && v < dataMax)
          // Map to scale of the chart
          .map(symLog),
      ],
      tickFormat: (d: number) =>
        d == 0 ? 0 : numberAsIntegerString(symPow(d)),
    },
    y: { axis: null, domain: [0, 1 + dataPlots.length * 4] },
    height: 20 + dataPlots.length * 150,
    // The range of radii of the dots.
    r: { range: [1, 30] },
    marks: [
      // shade background rectangles to set line charts apart from dots and convey the total percentage covered.
      ...dataPlots.map((_, idx) => {
        return Plot.rect(
          [
            {
              x1: symLog(rawData.samples[0]),
              x2: symLog(rawData.samples[rawData.samples.length - 1]),
              y1: idx * 4 + 1,
              y2: idx * 4 + 2,
            },
          ],
          {
            x1: "x1",
            x2: "x2",
            y1: "y1",
            y2: "y2",
            fill: "rgba(0,0,0,.05)",
          },
        );
      }),
      // Plot each dot chart, excluding zeros because we will add those separately.
      ...dataPlots.map((nextDataPlot, idx) => {
        return Plot.dot(
          rawData.samples,
          Plot.binX(
            {
              y: (_: number[]) => 3 + idx * 4,
              r: (d: number[]) => {
                if (d.includes(0) || (d[0] < 0 && d[d.length - 1] > 0)) {
                  return nextDataPlot.rCalc(
                    // Include 0s for relevant bin
                    d.length + rawData.num_zeros,
                    d[0],
                    d[d.length - 1],
                  );
                }
                return nextDataPlot.rCalc(d.length, d[0], d[d.length - 1]);
              },
            },
            {
              x: (d: number) => {
                return symLog(d);
              },
              // eslint-disable-next-line
              // @ts-ignore
              stroke: "rgba(0,0,0,0)",
              fill: nextDataPlot.colorTransparent,
            },
          ),
        );
      }),
      // Add the zeros to each dot chart.
      ...dataPlots.map((nextDataPlot, idx) => {
        return Plot.dot([0], {
          x: (d: number) => d,
          y: (_) => 3 + idx * 4,
          r: (_) =>
            nextDataPlot.rCalc(
              // include 0s for relevant dot
              numZeroSamples,
              0,
              0,
            ),
          stroke: "rgba(0,0,0,0)",
          fill: nextDataPlot.colorTransparent,
        });
      }),
      // Plot each line chart.
      ...dataPlots.map((nextDataPlot, idx) => {
        let points = [...nextDataPlot.cumData].map((d, id) => {
          return [
            symLog(samplesWithZero[id]),
            d / nextDataPlot.cumData[nextDataPlot.cumData.length - 1] +
              idx * 4 +
              1,
          ];
        });
        points = points.filter((p, idx) => {
          return (
            p[0] || points[idx - 1]?.[0] !== 0 || points[idx + 1]?.[0] !== 0
          );
        });
        return Plot.line(points, {
          stroke: nextDataPlot.colorSolid,
          curve: "step-after",
        });
      }),
      // Label each chart
      Plot.text(
        dataPlots.map((_, idx) => [midPoint, idx * 4 + 4]),
        { text: dataPlots.map((p) => p.label) },
      ),
      // Add 0s and 1s to line chart y axis.
      Plot.text(
        dataPlots.reduce(
          (acc: [number, number][], _: DataPlot, idx: number) => [
            ...acc,
            [
              symLog(rawData.samples[rawData.samples.length - 1]),
              idx * 4 + 1,
            ] as [number, number],
            [
              symLog(rawData.samples[rawData.samples.length - 1]) * 1.0031,
              idx * 4 + 2,
            ] as [number, number],
          ],
          [] as [number, number][],
        ),
        {
          text: dataPlots.reduce(
            (acc, _) => [...acc, "0", "1"],
            [] as string[],
          ),
          textAnchor: "start",
          fontSize: "7",
        },
      ),
    ],
  };

  return <ObservablePlot options={options} />;
};
