import { Parameters, LongTermParams } from "../../client";
import {
  Parameters as Parameters_V1,
  LongTermParams as LongTermParams_V1,
} from "../../oldModels/V1";
import {
  UniformDistributionSpec,
  ConstantDistributionSpec,
  ConfidenceDistributionSpec,
  GammaDistributionSpec,
  BetaDistributionSpec,
  CategoricalDistributionSpec,
} from "../../client";

const isLongtermV1 = (data: LongTermParams | LongTermParams_V1) => {
  if (!("version" in data)) {
    return true;
  }
  return false;
};

export const updateParamsToLatestVersion = (
  oldData: Parameters_V1 | Parameters,
): Parameters => {
  const newData = { ...oldData } as Parameters | Parameters_V1;
  try {
    if (
      "longterm_params" in oldData &&
      isLongtermV1(oldData.longterm_params!)
    ) {
      convertFromLongTermV1ToV2(newData as Parameters_V1);
    }
  } catch (e) {
    console.log(e);
  }
  // In case of error, just return old version.
  return newData as Parameters;
};

const applyConversions = (
  obj: object,
  conversionList: ((v: object) => object)[],
) => {
  let newObj = { ...obj };
  for (const conversion of conversionList) {
    newObj = conversion(newObj);
  }
  return newObj;
};

const convertConstantToDistribution = (keyName: string) => {
  return (obj: object) => {
    const definedKeyName = keyName as keyof typeof obj;
    const newObj = {
      ...obj,
      [definedKeyName]: obj[definedKeyName] as
        | number
        | (
            | UniformDistributionSpec
            | ConstantDistributionSpec
            | ConfidenceDistributionSpec
            | GammaDistributionSpec
            | BetaDistributionSpec
            | CategoricalDistributionSpec
          ),
    };
    if (keyName in newObj) {
      if (typeof newObj[definedKeyName] === "number") {
        newObj[definedKeyName] = {
          type: "constant",
          distribution: "constant",
          value: newObj[definedKeyName] as number,
        };
      }
    }
    return newObj;
  };
};

const convertFromLongTermV1ToV2 = (newData: Parameters_V1 | Parameters) => {
  // Convert from constant params
  newData.longterm_params = applyConversions(
    newData.longterm_params as LongTermParams_V1,
    [
      convertConstantToDistribution("stellar_population_capacity"),
      convertConstantToDistribution("galactic_density"),
      convertConstantToDistribution("supercluster_density"),
      convertConstantToDistribution("expansion_speed"),
    ],
  ) as LongTermParams;
  newData.longterm_params.version = "2";
};
