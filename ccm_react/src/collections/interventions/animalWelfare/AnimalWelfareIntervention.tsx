import { useAtom, useAtomValue } from "jotai";
import { isEqual, omit } from "lodash-es";
import { Suspense } from "react";
import { LoadingFallback } from "../../../components/support/LoadingFallback";
import { ConfigurabilityMessage } from "../../../components/ConfigurabilityMessage";
import { CustomizationNote } from "../CustomizationNote";
import { InterventionOverview } from "../InterventionOverview";
import { InterventionAssessment } from "./InterventionAssessment";
import { InterventionConfiguration } from "./InterventionConfiguration";
import { TemplateSelector } from "./TemplateSelector";

import {
  baseAnimalInterventionAtom,
  customAnimalInterventionAtom,
  paramsAtom,
} from "../../../stores/atoms";

export function AnimalWelfareInterventionLayout() {
  const [allParams, setAllParams] = useAtom(paramsAtom);
  const baseIntervention = useAtomValue(baseAnimalInterventionAtom);
  const [customIntervention, setCustomIntervention] = useAtom(
    customAnimalInterventionAtom,
  );

  const isCustomized =
    !isEqual(customIntervention, baseIntervention) ||
    Object.keys(allParams.animal_intervention_params ?? {}).length > 0;

  const reset = () => {
    setAllParams(omit(allParams, "animal_intervention_params"));
    setCustomIntervention(baseIntervention);
  };
  return (
    <section>
      <h2>Animal Welfare Interventions</h2>
      <InterventionOverview interventionType="animal welfare" />
      <h3>Settings</h3>
      <h4>Templates</h4>
      <TemplateSelector />
      {baseIntervention && (
        <>
          <Suspense fallback={<LoadingFallback />}>
            <ConfigurabilityMessage />
            <h4>{baseIntervention?.name} Parameters</h4>
            {isCustomized && <CustomizationNote triggerReset={reset} />}
            <InterventionConfiguration />
          </Suspense>
          <Suspense fallback={<LoadingFallback />}>
            <InterventionAssessment />
          </Suspense>
        </>
      )}
    </section>
  );
}
