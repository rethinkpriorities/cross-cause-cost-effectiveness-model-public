import { Animal } from "../client";
import { useMoralWeightParams } from "./useMoralWeightParams";
import { DistributionSpec } from "../utils/distributions";

// Returns customized moralWeight, or base if it isn't defined.
export const useMoralWeight = (
  species: Animal | "unknown",
): DistributionSpec | undefined => {
  const moralWeightParams = useMoralWeightParams();
  const moralWeight = moralWeightParams?.moral_weights_override?.[species];
  return moralWeight;
};
