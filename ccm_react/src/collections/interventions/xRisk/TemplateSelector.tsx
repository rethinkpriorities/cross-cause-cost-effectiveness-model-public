import { useAtom, useAtomValue } from "jotai";
import { XRiskIntervention } from "../../../client";
import { TemplateSelector as GenericTemplateSelector } from "../TemplateSelector";
import {
  availableInterventionsAtom,
  baseXRiskInterventionAtom,
  customXRiskInterventionAtom,
} from "../../../stores/atoms";

export const TemplateSelector = () => {
  const availableInterventions = useAtomValue(
    availableInterventionsAtom,
  ).filter((intervention) => intervention.area == "xrisk");
  const [baseIntervention, setBaseIntervention] = useAtom(
    baseXRiskInterventionAtom,
  );
  const [customIntervention, setCustomIntervention] = useAtom(
    customXRiskInterventionAtom,
  );
  const intervention = customIntervention ?? baseIntervention;
  return GenericTemplateSelector({
    availableInterventions: availableInterventions,
    intervention: intervention,
    setBaseIntervention: (value) =>
      setBaseIntervention(value as XRiskIntervention),
    setCustomIntervention: (value) =>
      setCustomIntervention(value as XRiskIntervention),
  });
};
