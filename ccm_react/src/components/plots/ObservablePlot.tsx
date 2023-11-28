import * as Plot from "@observablehq/plot";
import { Suspense, useEffect, useRef } from "react";
import { LoadingFallback } from "../support/LoadingFallback";

interface PlotProps {
  options: Plot.PlotOptions;
}

export function ObservablePlot({ options }: PlotProps) {
  // Convenience component for creating a Plot (without handling the container)
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const plot = Plot.plot(options);

    if (containerRef.current) {
      containerRef.current.append(plot);
    }
    return () => plot.remove();
  }, [options]);

  return (
    <Suspense fallback={<LoadingFallback />}>
      <div ref={containerRef} />
    </Suspense>
  );
}
