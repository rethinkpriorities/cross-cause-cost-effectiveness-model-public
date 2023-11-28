import { Suspense } from "react";
import { ErrorBoundary } from "../support/ErrorHandling";
import { LoadingFallback } from "../support/LoadingFallback";

export function PlotContainer({ children }: { children: React.ReactNode }) {
  // TODO: Change to useTransition?
  return (
    <div className="w-full lg:w-[640px]">
      <ErrorBoundary>
        <Suspense fallback={<LoadingFallback />}>{children}</Suspense>
      </ErrorBoundary>
    </div>
  );
}
