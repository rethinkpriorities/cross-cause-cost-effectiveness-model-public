import "@quri/squiggle-components/common.css";
import { UniformDistributionSpec } from "../../../client";

import { useEffect, useState } from "react";

import { useDebounce } from "usehooks-ts";
import { FormatType } from "../../../utils/formatting";
import RangeInput from "./RangeInput";

interface ConfidenceDistributionProps {
  distribution: UniformDistributionSpec;
  setDistribution: (distribution: UniformDistributionSpec) => void;
  type?: FormatType;
  unit?: string;
}

export function UniformDistributionInput({
  distribution,
  setDistribution,
  type = "decimal",
  unit,
}: ConfidenceDistributionProps) {
  const [range, setRange] = useState<[number, number]>([
    distribution.range[0],
    distribution.range[1],
  ]);
  const debouncedRange = useDebounce(range, 300);
  const [lowerBound, upperBound] = range;

  useEffect(() => {
    if (debouncedRange[0] < debouncedRange[1]) {
      setDistribution({
        type: "uniform",
        distribution: "uniform",
        range: debouncedRange,
      });
    }
  }, [debouncedRange, setDistribution]);

  // Check if lower bound is higher than or equal to upper bound
  const rangeError = lowerBound >= upperBound;

  return (
    <div>
      <p className="text-sm md:block lt-md:hidden">
        A distribution with uniform probability between the lower and upper
        bound.
      </p>
      <div className="mx-auto mb-2 mt-4 h-8 flex items-center justify-center gap-4">
        <RangeInput
          className="w-30 border-2 border-slate-6 border-rounded"
          boundIndex={0}
          range={range}
          setRange={setRange}
          type={type}
          unit={unit}
        />
        <RangeInput
          className="w-30 border-2 border-slate-6 border-rounded"
          boundIndex={1}
          range={range}
          setRange={setRange}
          type={type}
          unit={unit}
        />
      </div>
      {rangeError && (
        <div className="mb-0 mt-4 text-center text-sm text-red-500">
          Lower bound must be less than upper bound
        </div>
      )}
    </div>
  );
}
