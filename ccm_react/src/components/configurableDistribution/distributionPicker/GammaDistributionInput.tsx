import { useEffect, useState } from "react";
import { useDebounce } from "usehooks-ts";
import { GammaDistributionSpec } from "../../../client";
import { predefinedFormats } from "../../../utils/formatting";
import NumberInput from "./NumberInput";
predefinedFormats;

interface GammaDistributionInputProps {
  distribution: GammaDistributionSpec;
  setDistribution: (distribution: GammaDistributionSpec) => void;
}

interface GammaDistributionInputState {
  shape: number;
  scale: number;
}

export function GammaDistributionInput({
  distribution,
  setDistribution,
}: GammaDistributionInputProps) {
  const [params, setParams] = useState<GammaDistributionInputState>({
    shape: distribution.shape,
    scale: distribution.scale,
  });

  const debouncedParams = useDebounce(params, 300);

  useEffect(() => {
    setDistribution({
      type: "gamma",
      distribution: "gamma",
      shape: debouncedParams.shape,
      scale: debouncedParams.scale,
    });
  }, [debouncedParams, setDistribution]);

  return (
    <>
      <p className="text-sm md:block lt-md:hidden">
        Gamma distribution. Gives the probability of a certain waiting time
        until <code>shape</code> events are observed, where each individual
        event has an average waiting time of <code>scale</code>.
      </p>
      <div className="mx-auto mb-2 mt-4 h-8 flex items-center justify-center gap-4">
        <NumberInput
          className="w-30 border-2 border-slate-6 border-rounded"
          value={distribution.shape}
          setValue={(shape) =>
            setParams({
              ...params,
              shape,
            })
          }
          id="shape"
          label="Shape"
          type="decimal"
        />
        <NumberInput
          className="w-30 border-2 border-slate-6 border-rounded"
          value={distribution.scale}
          setValue={(scale) =>
            setParams({
              ...params,
              scale,
            })
          }
          id="scale"
          label="Scale"
          type="decimal"
        />
      </div>
    </>
  );
}
