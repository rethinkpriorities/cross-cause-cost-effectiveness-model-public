import { useAtom } from "jotai";
import { isEqual, omit } from "lodash-es";
import { Suspense } from "react";
import {
  baseGhdInterventionAtom,
  customGhdInterventionAtom,
  paramsAtom,
} from "../../../stores/atoms";
import { ErrorBoundary } from "../../../components/support/ErrorHandling";
import { LoadingFallback } from "../../../components/support/LoadingFallback";
import { ConfigurabilityMessage } from "../../../components/ConfigurabilityMessage";
import { CustomizationNote } from "../CustomizationNote";
import { InterventionOverview } from "../InterventionOverview";
import { InterventionAssessment } from "./InterventionAssessment";
import { InterventionConfiguration } from "./InterventionConfiguration";
import { InterventionDescription } from "../InterventionDescription";
import { TemplateSelector } from "./TemplateSelector";

export function GhdInterventionLayout() {
  const [customIntervention, setCustomIntervention] = useAtom(
    customGhdInterventionAtom,
  );
  const [baseIntervention] = useAtom(baseGhdInterventionAtom);

  const [allParams, setAllParams] = useAtom(paramsAtom);
  const isCustomized =
    !isEqual(customIntervention, baseIntervention) ||
    Object.keys(allParams.ghd_intervention_params ?? {}).length > 0;

  const reset = () => {
    setAllParams(omit(allParams, "ghd_intervention_params"));
    setCustomIntervention(baseIntervention);
  };
  return (
    <section>
      <h2>Global Health and Development Interventions</h2>
      <InterventionOverview interventionType="ghd" />
      <h3>Settings</h3>
      <h4>Templates</h4>
      <TemplateSelector />
      {baseIntervention && (
        <ErrorBoundary>
          <Suspense fallback={<LoadingFallback />}>
            <ConfigurabilityMessage />
            <h4>Intervention Parameters</h4>
            {isCustomized && <CustomizationNote triggerReset={reset} />}
            <InterventionDescription />
            <InterventionConfiguration />
          </Suspense>
          <Suspense fallback={<LoadingFallback />}>
            <InterventionAssessment />
          </Suspense>
        </ErrorBoundary>
      )}
    </section>
  );
}
