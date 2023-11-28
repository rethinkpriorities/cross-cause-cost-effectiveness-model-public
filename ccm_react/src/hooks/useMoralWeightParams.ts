import { useAtomValue } from "jotai";
import { clone } from "lodash-es";
import { MoralWeightsParams } from "../client";
import { defaultParamsAtom, paramsAtom } from "../stores/atoms";

// Returns customized moralWeight, or base if it isn't defined.
export const useMoralWeightParams = (): MoralWeightsParams => {
  const defaultParams = useAtomValue(defaultParamsAtom);
  const allParams = useAtomValue(paramsAtom);
  // This always exists, as Parameters are initialized with default values.
  const baseObj =
    defaultParams.animal_intervention_params!.moral_weight_params!;

  const customObj = {
    override_type: baseObj.override_type,
    moral_weights_override: clone(baseObj.moral_weights_override),
    welfare_capacities_override: clone(baseObj.welfare_capacities_override),
    ...allParams.animal_intervention_params?.moral_weight_params,
  };
  return customObj ?? baseObj;
};
