import { useAtomValue } from "jotai";
import { defaultParamsAtom, paramsAtom } from "../stores/atoms";

// Returns customized animalInterventionParams, or base if it isn't defined.
export const useNumAnimalsBornPerYear = (species: string) => {
  const defaultParams = useAtomValue(defaultParamsAtom);
  const allParams = useAtomValue(paramsAtom);
  // This always exists, as Parameters are initialized with default values.
  const baseObj =
    defaultParams.animal_intervention_params?.num_animals_born_per_year?.[
      species
    ];

  const customObj =
    allParams.animal_intervention_params?.num_animals_born_per_year?.[species];
  return customObj ?? baseObj;
};
