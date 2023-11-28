import { ComponentPropsWithoutRef, forwardRef } from "react";
import { NumericFormat } from "react-number-format";
import { focusOnNextFocusable } from "../../../utils/focus";
import { getFormat, FormatType } from "../../../utils/formatting";

interface NumberInputProps extends ComponentPropsWithoutRef<"input"> {
  // ID of the element, used for the label
  id: string;
  // Text shown over the input
  label: string;
  // Value of the input
  value: number;
  setValue: (value: number) => void;
  // Type of the value being set, use unit for annotated decimals
  type: FormatType;
  // Measurable unit of the input, if any
  unit?: string;
  // This is for prop compatibility with react-number-format
  defaultValue?: string;
}

const NumberInput = forwardRef<HTMLDivElement, NumberInputProps>(
  ({ id, value, setValue, label, type, unit, ...rest }, ref) => (
    // Input for setting one of the bounds of a confidence interval
    <div ref={ref} className="relative">
      <NumericFormat
        {...rest}
        id={id}
        value={
          // convert percents to formatted strings so they don't display a long
          // string of digits, but instead only show as many digits as
          // `getFormat` is set to display
          type === "percent" && typeof value === "number"
            ? getFormat(type, unit).format(value).replace("%", "")
            : (value as number | string)
        }
        valueIsNumericString={true}
        onValueChange={(e) => {
          if (e.floatValue !== undefined) {
            const floatValue =
              type === "percent" ? e.floatValue / 100 : e.floatValue;
            setValue(floatValue);
          }
        }}
        onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
          let dynamicModifierSize = Math.abs(
            10 ** (Math.ceil(Math.log10(value / 2)) - 2),
          );
          // Handle numbers between 0 and 10 as special case.
          if (dynamicModifierSize < 1 && value >= 1) dynamicModifierSize = 1;
          // Go up or down by 1 point if percent, 1% of value (rounded) otherwise
          const valueModifier = type === "percent" ? 0.01 : dynamicModifierSize;
          let newValue = value;

          if (["ArrowUp", "ArrowDown"].includes(e.key)) {
            const modifierSign = e.key === "ArrowUp" ? 1 : -1;
            newValue = newValue + modifierSign * valueModifier;
            // Round if above 1.
            if (Math.abs(newValue) > 1) newValue = Math.round(newValue);
            setValue(newValue);
          } else if (["Tab", "Enter"].includes(e.key)) {
            focusOnNextFocusable();
          }
        }}
        prefix={type === "currency" ? "$" : undefined}
        suffix={type === "percent" ? "%" : type === "unit" ? unit : undefined}
        thousandSeparator={
          type === "currency" || type === "decimal" || type === "unit"
        }
        min={type === "percent" || type === "currency" ? 0 : undefined}
        allowNegative={!(type === "percent" || type === "currency")}
      />
      <label
        htmlFor={id}
        className="absolute left-2 bg-white px-1 text-xs text-gray-500 -top-2"
      >
        {label}
      </label>
    </div>
  ),
);

NumberInput.displayName = "NumberInput";

export default NumberInput;
