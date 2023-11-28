import { Suspense } from "react";
import { ErrorBoundary } from "../support/ErrorHandling";
import { LoadingFallback } from "../support/LoadingFallback";

export const Section = ({
  title,
  children,
}: {
  title: React.ReactNode;
  children: React.ReactNode;
}) => (
  <section className="mt-6">
    <h2 className="mb-4 text-xl font-bold">{title}</h2>
    <div className="max-w-2xl rounded-lg bg-white px-4 py-0.5 shadow-sm prose dark:bg-dashboard-gray dark:prose-invert">
      <Suspense fallback={<LoadingFallback />}>
        <ErrorBoundary>{children}</ErrorBoundary>
      </Suspense>
    </div>
  </section>
);
