import * as Plot from "@observablehq/plot";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { bin as d3bin, histogram as d3histogram, range, sort } from "d3";
import { Suspense, useEffect, useMemo, useState } from "react";
import type { SparseSamples } from "../../../client/models/SparseSamples";
import { symLog, symPow } from "../../../utils/scaling";
import { sparseMean, sparseMedian } from "../../../utils/sparseSamples";
import { ObservablePlot } from "../ObservablePlot";
import { ExpectedValueMassChart } from "./ExpectedValueMassChart";
import { HighlightSelect } from "./HighlightSelect";
import { MeanLegend } from "./MeanLegend";
import { LoadingFallback } from "../../support/LoadingFallback";
import {
  filterOutNearZeros,
  getColorScale,
  getExpectedValueMasses,
  getPercentageEVNegative,
} from "./utils";

interface HistogramProps {
  data: SparseSamples;
  title: string;
  unit?: string;
  xTickFormat?: string;
  yTickFormat?: string;
  marginLeft?: number;
}

/*
 * Create ticks for the x-axis of a graph where the ticks are evenly distributed
 * on a sym-log scale.
 */
function symLogTicksForDomain(
  domain: [number, number],
  tickCount: number,
): number[] {
  const logDomain = domain.map(symLog);
  const logTicks = range(
    logDomain[0] - 1,
    logDomain[1] + 1,
    (logDomain[1] - logDomain[0]) / (tickCount - 1),
  );
  const ticks = logTicks.map(symPow);
  return ticks;
}

export function Histogram({
  data,
  title,
  unit,
  xTickFormat,
  // This can be used when yTicks are too long and get cut off
  marginLeft,
}: HistogramProps) {
  const [loading, setLoading] = useState<boolean>(true);
  // Sort data to make future computations more efficient
  const sortedDenseData: number[] = useMemo(
    () => sort(data.samples || []),
    [data],
  );
  const [highlightedValues, setHighlightedValues] = useState<
    [number, number, number, number]
  >([0, 0.1, 0.9, 1]);

  const filteredForNearZeros = useMemo(
    () => filterOutNearZeros(sortedDenseData),
    [sortedDenseData],
  );

  const numSamples = useMemo(
    () => data.samples.length + data.num_zeros,
    [data],
  );
  const denseRatio = useMemo(
    () => data.samples.length / numSamples,
    [data, numSamples],
  );

  const [hideZeros, setHideZeros] = useState<boolean | null>(
    data.samples.length == 0
      ? null
      : filteredForNearZeros.length / numSamples < 0.1,
  );

  // On initial page load, this function is called with an empty `data` array.
  // We don't want to set the initial value of `hideZeros` when that happens. So
  // instead we set it to null and then set it to a numeric value the first time
  // this function is called with a non-empty `data` array.
  useEffect(() => {
    if (hideZeros == null && data.samples.length > 0) {
      setHideZeros(filteredForNearZeros.length / numSamples < 0.1);
    }
  }, [filteredForNearZeros, data, numSamples, hideZeros]);

  const [useLogScale, setUseLogScale] = useState<boolean>(false);

  const colorScale = useMemo(
    () => getColorScale(sortedDenseData, highlightedValues),
    [sortedDenseData, highlightedValues],
  );

  const mean = useMemo(() => sparseMean(data), [data]);
  const median = useMemo(
    () =>
      sparseMedian({
        samples: sortedDenseData,
        num_zeros: data.num_zeros,
      }),
    [sortedDenseData, data],
  )!;

  const filteredData = hideZeros ? filteredForNearZeros : data.samples;
  const countNearZerosHidden = numSamples - filteredData.length;
  // Display any data no more than twice as far from the median as max of 1% and 99%.
  const firstPercentile =
    sortedDenseData[Math.floor(sortedDenseData.length * 0.01)];
  const ninetyNinthPercentile =
    sortedDenseData[Math.floor(sortedDenseData.length * 0.99)];
  const denseMedian = sortedDenseData[Math.floor(sortedDenseData.length * 0.5)];
  const maxDistanceFromMedian = Math.max(
    Math.abs(median - firstPercentile),
    Math.abs(ninetyNinthPercentile - median),
  );
  const minValue = sortedDenseData[0];
  const maxValue = sortedDenseData[sortedDenseData.length - 1];

  const showLogScaleCheckbox =
    denseMedian == 0 || ninetyNinthPercentile / denseMedian > 100;
  const showHighlightSelect = !showLogScaleCheckbox;

  // memoize to avoid expectedValueMass rememoizing dependent functions
  const domain = useMemo(
    () =>
      (maxDistanceFromMedian > 0
        ? [
            median - 2 * maxDistanceFromMedian,
            median + 2 * maxDistanceFromMedian,
          ]
        : [minValue, maxValue]) as [number, number],
    [maxDistanceFromMedian, median, minValue, maxValue],
  );

  const expectedValueMasses = useMemo(
    () =>
      typeof domain === "undefined"
        ? { below: 0, included: 100, above: 0 }
        : getExpectedValueMasses(sortedDenseData, domain),
    [sortedDenseData, domain],
  );

  const percentageNegative = useMemo(
    () => getPercentageEVNegative(sortedDenseData),
    [sortedDenseData],
  );

  // Percentage of "significant" (not close to zero) outcomes that are displayed.
  // This measures how many results were too extreme to fit on the histogram.
  const percentageDisplayed = useMemo(
    () =>
      typeof domain === "undefined"
        ? 100
        : ((sortedDenseData.findIndex((d) => d > domain[1]) -
            sortedDenseData.findIndex((d) => d > domain[0])) *
            100) /
          sortedDenseData.length,
    [sortedDenseData, domain],
  );

  // Create 100 bins from displayed data.
  const bins = useMemo(() => {
    const binCount = 100;
    let histogram = d3histogram().thresholds(binCount);
    if (useLogScale) {
      histogram = d3histogram().thresholds(
        symLogTicksForDomain(domain, binCount),
      );
    }
    const displayedData = filteredData.filter(
      (d) => d >= domain[0] && d <= domain[1],
    );
    const bins = histogram(displayedData);

    // Scale down all the bins so we can fit the zeros in a bin without using
    // too much memory. The total number of values in the scaled-down bins will
    // approximately equal the number of values in data.samples.
    if (data.num_zeros > 0 && !hideZeros) {
      const scaledNumZeros = Math.floor(
        (data.num_zeros * data.samples.length) / numSamples,
      );
      let foundZeroBin = false;
      for (const bin of bins) {
        if (bin.x0! < 0 && bin.x1! > 0) {
          const len = Math.round(bin.length * denseRatio);
          foundZeroBin = true;
          bin.splice(
            len,
            bin.length - len,
            ...(Array(scaledNumZeros).fill(0) as number[]),
          );
        }
      }

      // If there is no bin containing zero, insert a new bin
      if (!foundZeroBin) {
        const binSize = bins[0].x1! - bins[0].x0!;
        const bin = d3bin().domain([-binSize / 2, binSize / 2])(
          Array(scaledNumZeros).fill(0),
        )[0];
        bins.push(bin);
      }
    }
    return bins;
  }, [
    domain,
    filteredData,
    useLogScale,
    data,
    numSamples,
    hideZeros,
    denseRatio,
  ]);

  useEffect(() => {
    setLoading(false);
  }, [bins]);

  const options: Plot.PlotOptions = {
    marginLeft: marginLeft ?? 50,
    x: useLogScale
      ? {
          type: "symlog",
          base: 10,
          domain: domain,
          label: `${title} ${unit ? `(${unit})` : ""}`,
          tickFormat: ".0e",
          ticks: symLogTicksForDomain(domain, 7),
          grid: true,
        }
      : {
          label: `${title} ${unit ? `(${unit})` : ""}`,
          tickFormat: xTickFormat ?? "s",
          domain: domain,
        },
    y: {
      tickFormat: () => "",
      tickSize: 40,
      label: "Number of results",
      grid: true,
    },
    marks: [
      Plot.rectY(bins, {
        fill: colorScale,
        x1: "x0",
        x2: "x1",
        y: "length",
      }),
      Plot.ruleY([0]),
      Plot.ruleX([mean], {
        stroke: "currentColor",
        strokeWidth: 2.5,
        tip: false,
      }),
      Plot.ruleX([median], {
        stroke: "currentColor",
        strokeWidth: 4.5,
        strokeDasharray: "5,5",
        tip: false,
      }),
    ],
  };

  if (data === undefined) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-center font-semibold">No data provided.</p>
      </div>
    );
  }

  return (
    <>
      <div className="relative">
        <style>
          [aria-label={'"'}y-axis tick{'"'}] path:not(:first-child) {"{"}
          stroke: rgba(0,0,0,.1)!important;
          {"}"}
        </style>
        <Suspense>
          {loading ? <LoadingFallback /> : <ObservablePlot options={options} />}
        </Suspense>
        <div className="bottom-[-0.5rem] left-[1em] flex flex-col md:absolute md:flex-row">
          <MeanLegend />
          <div className="flex flex-row">
            {showHighlightSelect && (
              <HighlightSelect
                highlightedValues={highlightedValues}
                setHighlightedValues={setHighlightedValues}
              />
            )}
            {showLogScaleCheckbox && (
              <label className="mt-[3px] text-xs">
                <input
                  type="checkbox"
                  checked={useLogScale}
                  onChange={() => {
                    setLoading(true);
                    setUseLogScale(!useLogScale);
                  }}
                  className="cursor-pointer border-1 border-black border-solid color-red-500"
                />
                Log scale
              </label>
            )}
            {filteredForNearZeros.length < numSamples && (
              <label className="mt-[3px] text-xs">
                <input
                  type="checkbox"
                  checked={hideZeros ?? false}
                  onChange={() => {
                    setLoading(true);
                    setHideZeros(!(hideZeros ?? false));
                  }}
                  className="cursor-pointer border-1 border-black border-solid color-red-500"
                />
                Hide near 0s
              </label>
            )}
          </div>
        </div>
      </div>
      <ExpectedValueMassChart
        totalResults={numSamples}
        percentageDisplayed={percentageDisplayed}
        nearZerosHidden={countNearZerosHidden}
        expectedValueMasses={expectedValueMasses}
        percentageNegative={percentageNegative}
      />
      <p className="text-sm color-red-500 dark:color-red-300">
        {(hideZeros! || useLogScale) && (
          <ExclamationTriangleIcon
            height="1em"
            width="1em"
            className="align-middle"
          />
        )}{" "}
        {hideZeros && (
          <>
            Values near 0 have been removed from the above chart to provide a
            fine-grained view of the remaining data.{" "}
          </>
        )}
        {useLogScale && (
          <>
            This chart is {hideZeros && "also"} displayed on a log scale.
            Results near the far left and right may have very large absolute
            values.
          </>
        )}
      </p>
    </>
  );
}
