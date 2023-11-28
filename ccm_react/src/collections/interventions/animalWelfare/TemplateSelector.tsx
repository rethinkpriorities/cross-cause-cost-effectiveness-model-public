import { useAtom, useAtomValue } from "jotai";
import { AnimalIntervention } from "../../../client";
import {
  availableInterventionsAtom,
  baseAnimalInterventionAtom,
  customAnimalInterventionAtom,
} from "../../../stores/atoms";
import { TemplateSelector as GenericTemplateSelector } from "../TemplateSelector";

export const TemplateSelector = () => {
  const availableInterventions = useAtomValue(
    availableInterventionsAtom,
  ).filter((intervention) => intervention.area == "animal-welfare");
  const [baseIntervention, setBaseIntervention] = useAtom(
    baseAnimalInterventionAtom,
  );
  const [customIntervention, setCustomIntervention] = useAtom(
    customAnimalInterventionAtom,
  );
  const intervention = customIntervention ?? baseIntervention;
  return GenericTemplateSelector({
    availableInterventions: availableInterventions,
    intervention: intervention,
    setBaseIntervention: (value) =>
      setBaseIntervention(value as AnimalIntervention),
    setCustomIntervention: (value) =>
      setCustomIntervention(value as AnimalIntervention),
  });
};
