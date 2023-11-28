import { useAtom, useAtomValue } from "jotai";
import { isEqual, omit } from "lodash-es";
import { Suspense } from "react";
import {
  baseXRiskInterventionAtom,
  customXRiskInterventionAtom,
  paramsAtom,
} from "../../../stores/atoms";
import { ErrorBoundary } from "../../../components/support/ErrorHandling";
import { LoadingFallback } from "../../../components/support/LoadingFallback";
import { ConfigurabilityMessage } from "../../../components/ConfigurabilityMessage";
import { CustomizationNote } from "../CustomizationNote";
import { InterventionAssessment } from "./InterventionAssessment";
import { InterventionConfiguration } from "./InterventionConfiguration";
import { TemplateSelector } from "./TemplateSelector";

export function XRiskInterventionLayout() {
  const [customIntervention, setCustomIntervention] = useAtom(
    customXRiskInterventionAtom,
  );
  const baseIntervention = useAtomValue(baseXRiskInterventionAtom);

  const [allParams, setAllParams] = useAtom(paramsAtom);

  const isCustomized =
    !isEqual(customIntervention, baseIntervention) ||
    Object.keys(allParams.longterm_params ?? {}).length > 0 ||
    Object.keys(allParams.impact_method ?? {}).length > 0;

  const reset = () => {
    setAllParams(omit(allParams, ["longterm_params", "impact_method"]));
    setCustomIntervention(baseIntervention);
  };

  return (
    <section>
      <h2>Existential Risk Interventions</h2>
      <h3>Settings</h3>
      <h4>Templates</h4>
      <TemplateSelector />
      {baseIntervention && (
        <ErrorBoundary>
          <Suspense fallback={<LoadingFallback />}>
            <ConfigurabilityMessage />
            <h4>Existential risk parameters</h4>
            {isCustomized && <CustomizationNote triggerReset={reset} />}
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
