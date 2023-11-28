import { useAtomValue } from "jotai";
import { Suspense } from "react";
import { baseProjectIdAtom } from "../../stores/atoms";
import { LoadingFallback } from "../../components/support/LoadingFallback";
import { ResultSummary } from "./ResultSummary";
import { DALYsPer1000 } from "./plots/DALYsPer1000";
import { NetImpact } from "./plots/NetImpact";

export function ProjectAssessment() {
  const project = useAtomValue(baseProjectIdAtom);
  if (!project) return null;

  return (
    <div>
      <h3 id="projects-simulation-results" className="mt-[3em]">
        Simulation Results
      </h3>
      <Suspense fallback={<LoadingFallback />}>
        <ResultSummary />
        <DALYsPer1000 />
        <NetImpact />
      </Suspense>
    </div>
  );
}
