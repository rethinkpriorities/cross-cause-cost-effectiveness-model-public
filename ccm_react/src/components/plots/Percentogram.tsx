import * as Plot from "@observablehq/plot";
import { MetricsBar } from "./MetricsBar";
import { ObservablePlot } from "./ObservablePlot";

import { quantileSorted, range, sort } from "d3";
import { chauvenetRange } from "../../utils/dataManipulation";

interface PercentogramProps {
  data: number[];
  title: string;
  unit?: string;
  xTickFormat?: string;
  yTickFormat?: string;
  marginLeft?: number;
  percentileRange?: [number, number];
  chauvenetFilter?: number;
  densityPercentagePerBin?: number;
}

function percentiles(
  numbers: number[],
  densityPercentagePerBin: number,
): number[] {
  const sorted: number[] = sort(numbers);
  return range(0, 101).map(
    (q) => quantileSorted(sorted, (densityPercentagePerBin * q) / 100)!,
  );
}

export function Percentogram({
  data,
  title,
  unit,
  xTickFormat,
  yTickFormat,
  // This can be used when yTicks are too long and get cut off
  marginLeft,
  chauvenetFilter,
  densityPercentagePerBin = 2.5,
}: PercentogramProps) {
  if (data === undefined) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-center font-semibold">No data provided.</p>
      </div>
    );
  }
  // Chauvenet range
  const domain = chauvenetFilter
    ? chauvenetRange(data, chauvenetFilter)
    : undefined;

  // Construction of the percentiles
  const mean = data.reduce((a, b) => a + b, 0) / data.length;
  const sortedData = data.sort((a, b) => a - b);
  const middle = Math.floor(sortedData.length / 2);
  const median =
    sortedData.length % 2 === 0
      ? (sortedData[middle - 1] + sortedData[middle]) / 2
      : sortedData[middle];

  const options: Plot.PlotOptions = {
    x: {
      label: `${title} ${unit ? `(${unit})` : ""}`,
      tickFormat: xTickFormat ?? "s",
      domain: domain,
    },
    y: { tickFormat: yTickFormat },
    marginLeft: marginLeft ?? 50,
    color: {
      legend: true,
      type: "quantize",
      scheme: "spectral",
      n: 10,
      label: "percentile",
    },
    marks: [
      Plot.rectY(data, {
        fill: (_d, i) => i,
        ...Plot.binX({
          y: (
            _bin: unknown,
            {
              x1,
              x2,
            }: {
              x1: number;
              x2: number;
            },
          ) => 1 / (x2 - x1),
          thresholds: (numbers: number[]) =>
            percentiles(numbers, densityPercentagePerBin),
        }),
      }),
      Plot.ruleY([0]),
      Plot.ruleX([mean], {
        stroke: "#3B82F6",
        strokeWidth: 3,
        title: `Mean: ${mean.toFixed(2)}`,
      }),
      Plot.ruleX([median], {
        stroke: "#22c55e",
        strokeWidth: 3,
        title: `Median: ${median.toFixed(2)}`,
      }),
    ],
  };
  return (
    <div>
      <ObservablePlot options={options} />
      <MetricsBar
        mean={mean}
        median={median}
        annotation={`Each bar represents ${densityPercentagePerBin}% of the data`}
      />
    </div>
  );
}
