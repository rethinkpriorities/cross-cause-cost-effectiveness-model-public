import { useAtom, useAtomValue } from "jotai";
import { GhdIntervention } from "../../../client";
import { TemplateSelector as GenericTemplateSelector } from "../TemplateSelector";
import {
  availableInterventionsAtom,
  baseGhdInterventionAtom,
  customGhdInterventionAtom,
} from "../../../stores/atoms";

export const TemplateSelector = () => {
  const availableInterventions = useAtomValue(
    availableInterventionsAtom,
  ).filter((intervention) => intervention.area == "ghd");
  const [baseIntervention, setBaseIntervention] = useAtom(
    baseGhdInterventionAtom,
  );
  const [customIntervention, setCustomIntervention] = useAtom(
    customGhdInterventionAtom,
  );
  const intervention = customIntervention ?? baseIntervention;
  return GenericTemplateSelector({
    availableInterventions: availableInterventions,
    intervention: intervention,
    setBaseIntervention: (value) =>
      setBaseIntervention(value as GhdIntervention),
    setCustomIntervention: (value) =>
      setCustomIntervention(value as GhdIntervention),
  });
};
