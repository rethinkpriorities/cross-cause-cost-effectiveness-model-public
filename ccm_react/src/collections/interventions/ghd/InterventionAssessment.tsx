import { sort } from "d3";
import { useAtomValue } from "jotai";
import { Suspense } from "react";
import { ghdInterventionAssessmentAtom } from "../../../stores/atoms";
import { LoadingFallback } from "../../../components/support/LoadingFallback";
import { AlternativesComparison } from "../../../components/plots/AlternativesComparison";
import { DALYsPer1000 } from "../DALYsPer1000";
import { ResultSummary } from "../ResultSummary";

export const InterventionAssessment = () => {
  const results = useAtomValue(ghdInterventionAssessmentAtom) ?? {
    samples: [],
    num_zeros: 0,
  };
  results.samples = sort(results.samples);

  return (
    <>
      <h3 className="mt-[2em]">Simulation Results</h3>
      <Suspense fallback={<LoadingFallback />}>
        <ResultSummary results={results} includeWaffleChart={false} />
      </Suspense>
      <Suspense fallback={<LoadingFallback />}>
        <DALYsPer1000 interventionSamples={results} />
      </Suspense>
      <Suspense fallback={<LoadingFallback />}>
        <AlternativesComparison values={results} unit="DALYs per $1000" />
      </Suspense>
    </>
  );
};
