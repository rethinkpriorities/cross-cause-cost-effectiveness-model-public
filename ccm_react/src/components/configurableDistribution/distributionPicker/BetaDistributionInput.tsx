import { useEffect, useState } from "react";
import { useDebounce } from "usehooks-ts";
import { BetaDistributionSpec } from "../../../client";
import { predefinedFormats } from "../../../utils/formatting";
import NumberInput from "./NumberInput";
predefinedFormats;

interface BetaDistributionInputProps {
  distribution: BetaDistributionSpec;
  setDistribution: (distribution: BetaDistributionSpec) => void;
}

interface BetaDistributionInputState {
  alpha: number;
  beta: number;
}

export function BetaDistributionInput({
  distribution,
  setDistribution,
}: BetaDistributionInputProps) {
  const [params, setParams] = useState<BetaDistributionInputState>({
    alpha: distribution.alpha,
    beta: distribution.beta,
  });

  const debouncedParams = useDebounce(params, 300);

  useEffect(() => {
    setDistribution({
      type: "beta",
      distribution: "beta",
      alpha: debouncedParams.alpha,
      beta: debouncedParams.beta,
    });
  }, [debouncedParams, setDistribution]);

  return (
    <>
      <p className="text-sm md:block lt-md:hidden">
        Beta distribution, most often used to model probabilities. You can think
        of it as your subjective probability of a binary event where you&apos;ve
        observed <code>alpha</code> successes and <code>beta</code> failures so
        far.
      </p>
      <div className="mx-auto mb-2 mt-4 h-8 flex items-center justify-center gap-4">
        <NumberInput
          className="w-30 border-2 border-slate-6 border-rounded"
          value={distribution.alpha}
          setValue={(alpha) =>
            setParams({
              ...params,
              alpha,
            })
          }
          id="alpha"
          label="Alpha"
          type="decimal"
        />
        <NumberInput
          className="w-30 border-2 border-slate-6 border-rounded"
          value={distribution.beta}
          setValue={(beta) =>
            setParams({
              ...params,
              beta,
            })
          }
          id="beta"
          label="Beta"
          type="decimal"
        />
      </div>
    </>
  );
}
