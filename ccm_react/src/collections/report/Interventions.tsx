import { ReloadIcon } from "@radix-ui/react-icons";
import { useQuery } from "@tanstack/react-query";
import { useAtom, useAtomValue } from "jotai";
import { isEmpty, isEqual } from "lodash-es";
import React, { Suspense } from "react";
import { match } from "ts-pattern";
import { DefaultService } from "../../client";
import { availableInterventionsAtom, paramsAtom } from "../../stores/atoms";
import {
  baseInterventionAtom,
  customInterventionAtom,
  interventionAtom,
} from "../../stores/report";
import { groupInterventions } from "../../utils/interventionAreas";
import Markdown from "../../components/Markdown";

import { sort } from "d3";
import { ErrorBoundary } from "../../components/support/ErrorHandling";
import { LoadingFallback } from "../../components/support/LoadingFallback";
import { CustomizationNote } from "../interventions/CustomizationNote";
import { DALYsPer1000 } from "../interventions/DALYsPer1000";
import { ResultSummary } from "../interventions/ResultSummary";
import { InterventionConfiguration as AnimalInterventionConfiguration } from "../interventions/animalWelfare/InterventionConfiguration";
import { InterventionConfiguration as GhdInterventionConfiguration } from "../interventions/ghd/InterventionConfiguration";
import { InterventionConfiguration as XRiskInterventionConfiguration } from "../interventions/xRisk/InterventionConfiguration";
import { AlternativesComparison } from "../../components/plots/AlternativesComparison";
import { ConfigurabilityMessage } from "../../components/ConfigurabilityMessage";

export function Interventions() {
  return (
    <section>
      <h2 id="interventions">Interventions</h2>
      <p>
        Interventions are projects that directly aim to make the world a better
        place, and they form the most important abstraction in CCM. The CCM
        assesses intervention cost-effectiveness in the amount of{" "}
        <a href="https://en.wikipedia.org/wiki/Disability-adjusted_life_year">
          Disability Adjusted Life Years (DALYs)
        </a>{" "}
        averted per $1000 invested in the intervention.
      </p>
      <p>
        A DALY is a unit of value tied to a degree of human misfortune, which is
        widely used in global health and development research. We expand the
        traditional definition of a DALY by valuing animals and lost future
        lives by performing customizable conversions to their equivalent in
        human DALYs.
      </p>
      <p>
        The CCM provides preset interventions: template models for interventions
        in different cause areas. Each preset comes with some default
        assumptions. Real-world projects inspire some of these default
        assumptions, while others are arbitrary or represent our best guesses.
        We expect users to customize these assumptions as needed.
      </p>
      <p>
        Once you select an intervention, the CCM will take the assumptions,
        which are encoded as probability distributions, and sample them
        thousands of times to provide the final distribution of results.
        It&apos;s important to note that this only provides a rough probability
        assessment, and this can also lead to highly erratic results for
        interventions that are highly sensitive to long-shot outcomes (like
        existential risk interventions).
      </p>
      <p>Select a preset intervention to get started:</p>
      <ErrorBoundary>
        <SelectIntervention />
        <Intervention />
      </ErrorBoundary>
    </section>
  );
}

function SelectIntervention() {
  // Available interventions
  const availableInterventions = useAtomValue(
    availableInterventionsAtom,
  ).filter((intervention) => intervention.area != "not-an-intervention");

  const [baseIntervention, setBaseIntervention] = useAtom(baseInterventionAtom);
  const [customIntervention, setCustomIntervention] = useAtom(
    customInterventionAtom,
  );
  const intervention = customIntervention ?? baseIntervention;

  const interventionsByArea = groupInterventions(availableInterventions);
  return (
    <div>
      <select
        className="mb-4 block w-full rounded select select-bordered"
        name="intervention-preset"
        onChange={(e) => {
          const newIntervention = availableInterventions.find(
            (intervention) => intervention.name == e.target.value,
          );
          setBaseIntervention(newIntervention);
          setCustomIntervention(newIntervention);
        }}
        value={intervention?.name}
      >
        <option>Select an intervention</option>
        {interventionsByArea.map(
          ({ area: group, interventions: interventions }) => {
            if (group === "Utility") return null;
            return (
              <optgroup key={group} label={group}>
                {interventions.map((intervention) => (
                  <option key={intervention.name} value={intervention.name}>
                    {intervention.name}
                  </option>
                ))}
              </optgroup>
            );
          },
        )}
      </select>
    </div>
  );
}

export function Intervention() {
  const baseIntervention = useAtomValue(baseInterventionAtom);
  const [customIntervention, setCustomIntervention] = useAtom(
    customInterventionAtom,
  );
  const [allParams, setAllParams] = useAtom(paramsAtom);

  const isCustomized =
    !isEqual(customIntervention, baseIntervention) ||
    !Object.values(allParams).every((areaParams) => isEmpty(areaParams));

  const resetSettings = () => {
    setAllParams({});
    setCustomIntervention(baseIntervention);
  };

  return (
    <>
      {baseIntervention && (
        <div>
          <Suspense fallback={<LoadingFallback />}>
            {isCustomized && <CustomizationNote triggerReset={resetSettings} />}
            {!isCustomized && <ConfigurabilityMessage />}
            <InterventionDescription />
            <InterventionConfiguration />
          </Suspense>
          <Suspense fallback={<LoadingFallback />}>
            <InterventionAssessment />
          </Suspense>
        </div>
      )}
    </>
  );
}

function InterventionDescription() {
  const intervention = useAtomValue(interventionAtom);
  if (!intervention) return null;

  return (
    <div>
      <h3>{intervention.name}</h3>
      <Markdown>{intervention.description}</Markdown>
    </div>
  );
}

export function InterventionConfiguration() {
  const intervention = useAtomValue(interventionAtom);
  if (!intervention) return null;

  return (
    <Suspense fallback={<LoadingFallback />}>
      {match(intervention.area)
        .returnType<React.ReactNode>()
        .with("ghd", () => <GhdInterventionConfiguration />)
        .with("animal-welfare", () => <AnimalInterventionConfiguration />)
        .with("xrisk", () => <XRiskInterventionConfiguration />)
        .otherwise(() => (
          <div></div>
        ))}
    </Suspense>
  );
}

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

  const orderedSamples = {
    samples: sort(data?.samples ?? []),
    num_zeros: data?.num_zeros ?? 0,
  };

  if (isRefetching) return <LoadingFallback />;
  return (
    <Suspense fallback={<LoadingFallback />}>
      <ErrorBoundary>
        <h3 className="mt-[2em]" id="simulation-results">
          Simulation Results
          <ReloadIcon
            height="1em"
            width="1em"
            className="ml-2 cursor-pointer align-middle"
            onClick={() => {
              void refetch();
            }}
          />
        </h3>
        <ResultSummary results={orderedSamples} includeWaffleChart={true} />
        <DALYsPer1000 interventionSamples={orderedSamples} />
        <AlternativesComparison
          values={orderedSamples}
          unit="DALYs per $1000"
        />
      </ErrorBoundary>
    </Suspense>
  );
};
