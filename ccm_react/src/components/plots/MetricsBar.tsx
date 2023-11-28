import { format as d3Format } from "d3";

interface MetricsBarProps {
  mean: number;
  median: number;
  format?: string;
  annotation?: string;
}

export function MetricsBar({
  mean,
  median,
  format,
  annotation,
}: MetricsBarProps) {
  const formatNumber = d3Format(format ?? "s");

  return (
    <>
      <div className="flex justify-between gap-4">
        <div className="text-gray-500">
          <span className="text-sm">{annotation}</span>
        </div>
        <div className="flex flex-row gap-4">
          <div className="text-blue-500">
            <span className="font-semibold">Mean:</span> {formatNumber(mean)}
          </div>
          <div className="text-green-500">
            <span className="font-semibold">Median:</span>{" "}
            {formatNumber(median)}
          </div>
        </div>
      </div>
    </>
  );
}
