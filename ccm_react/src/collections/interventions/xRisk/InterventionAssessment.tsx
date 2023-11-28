import { ReloadIcon } from "@radix-ui/react-icons";
import { sort } from "d3";
import { useAtom, useAtomValue } from "jotai";
import { Suspense } from "react";
import { XRiskIntervention } from "../../../client";
import {
  customXRiskInterventionAtom,
  xRiskInterventionAssessmentAtom,
} from "../../../stores/atoms";
import { LoadingFallback } from "../../../components/support/LoadingFallback";
import { AlternativesComparison } from "../../../components/plots/AlternativesComparison";
import { DALYsPer1000 } from "../DALYsPer1000";
import { ResultSummary } from "../ResultSummary";

export function InterventionAssessment() {
  const [customIntervention, setCustomIntervention] = useAtom(
    customXRiskInterventionAtom,
  );
  const results = useAtomValue(xRiskInterventionAssessmentAtom) ?? {
    samples: [],
    num_zeros: 0,
  };
  results.samples = sort(results.samples);

  // Note better approach to retrying in report.
  const retry = () =>
    setCustomIntervention({
      ...customIntervention,
      key: Math.random(),
    } as XRiskIntervention);

  return (
    <>
      <h3 className="mt-[2em]">
        Simulation Results
        <ReloadIcon
          height="1em"
          width="1em"
          className="ml-2 cursor-pointer align-middle"
          onClick={() => retry()}
        />
      </h3>
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
}
