import { useQuery } from "@tanstack/react-query";
import { ReloadIcon } from "@radix-ui/react-icons";
import { useAtomValue } from "jotai";
import { Suspense } from "react";
import { DefaultService } from "../../client";
import { paramsAtom } from "../../stores/atoms";
import { interventionAtom } from "../../stores/report";

import { sort as d3Sort } from "d3";
import { Section } from "../../components/wrappers/Section";
import { ErrorBoundary } from "../../components/support/ErrorHandling";
import { LoadingFallback } from "../../components/support/LoadingFallback";
import { DALYsPer1000 } from "../interventions/DALYsPer1000";
import { ResultSummary } from "../interventions/ResultSummary";
import { InterventionDescription } from "../interventions/InterventionDescription";
import { Endnotes } from "../../components/Endnotes";
import { InterventionConfiguration } from "../report/Interventions";
import { AlternativesComparison } from "../../components/plots/AlternativesComparison";

export const InterventionBody = () => {
  return (
    <div>
      <Section title="Description">
        <InterventionDescription />
      </Section>
      <Section title="Customize Intervention">
        <InterventionConfiguration />
      </Section>
      <InterventionAssessment />
      <Endnotes />
    </div>
  );
};

export const InterventionAssessment = () => {
  const parameters = useAtomValue(paramsAtom);
  const intervention = useAtomValue(interventionAtom)!;

  const { data, isRefetching, refetch } = useQuery({
    queryKey: ["interventionAssesment", intervention, parameters],
    queryFn: () =>
      DefaultService.estimateInterventionDalys(intervention.name, {
        intervention: intervention,
        parameters: parameters,
      }),
  });

  if (data) {
    data.samples = d3Sort(data.samples);
  }
  if (isRefetching || !data) return <LoadingFallback />;
  return (
    <Section
      title={
        <>
          Simulation Results
          <ReloadIcon
            height="1em"
            width="1em"
            className="ml-2 cursor-pointer align-middle"
            onClick={() => {
              void refetch();
            }}
          />
        </>
      }
    >
      <Suspense fallback={<LoadingFallback />}>
        <ErrorBoundary>
          <ResultSummary results={data} includeWaffleChart={true} />
          <DALYsPer1000 interventionSamples={data} />
          <AlternativesComparison values={data} unit="DALYs per $1000" />
        </ErrorBoundary>
      </Suspense>
    </Section>
  );
};
