import { ConstantDistributionSpec } from "../../../client";
import { FormatType } from "../../../utils/formatting";
import NumberInput from "./NumberInput";

interface ConstantDistributionInputProps {
  distribution: ConstantDistributionSpec;
  setDistribution: (distribution: ConstantDistributionSpec) => void;
  type: FormatType;
  unit?: string;
}

export function ConstantDistributionInput({
  distribution,
  setDistribution,
  type = "decimal",
}: ConstantDistributionInputProps) {
  return (
    <div className="mx-auto mb-2 mt-4 h-60 flex flex-col items-center justify-around">
      <p className="text-sm md:block lt-md:hidden">
        Fixes a constant value. Note that this makes the model effectively
        certain about this attribute.
      </p>
      {/* TODO(agucova): When used for a preset intervention, use a slider instead. */}
      <NumberInput
        className="border-2 border-slate-6 border-rounded"
        value={distribution.value}
        setValue={(value) =>
          setDistribution({
            ...distribution,
            value,
          })
        }
        id="value"
        label="Value"
        type={type}
      />
    </div>
  );
}
