import { ComponentPropsWithoutRef, forwardRef, useId } from "react";
import { NumericFormat } from "react-number-format";
import { focusOnNextFocusable } from "../../../utils/focus";
import { getFormat, FormatType } from "../../../utils/formatting";

type SetBounds = (bounds: [number, number]) => void;
type SetNullableBounds = (bounds: [number | null, number | null]) => void;

interface NumericBoundProps extends ComponentPropsWithoutRef<"input"> {
  boundIndex: 0 | 1;
  range: [number | null, number | null];
  setRange: SetBounds | SetNullableBounds;
  allowNull?: boolean;
  type: FormatType;
  unit?: string;
  // This is for prop compatibility with react-number-format
  defaultValue?: string;
}

const NumericBound = forwardRef<HTMLDivElement, NumericBoundProps>(
  (
    {
      boundIndex,
      range: bounds,
      setRange: setBounds,
      allowNull,
      type,
      unit,
      ...rest
    },
    ref,
  ) => {
    allowNull = allowNull ?? false;
    const id = useId() + (boundIndex === 0 ? "lower-bound" : "upper-bound");
    return (
      // Input for setting one of the bounds of a confidence interval
      <div ref={ref} className="relative">
        <NumericFormat
          id={id}
          {...rest}
          value={
            bounds[boundIndex] === null
              ? ""
              : type === "percent"
                ? getFormat(type, unit).format(bounds[boundIndex]!)
                : bounds[boundIndex]!
          }
          valueIsNumericString={true}
          onValueChange={(e) => {
            const otherIndex = boundIndex === 0 ? 1 : 0;
            if (allowNull) {
              const floatValue =
                e.floatValue == undefined
                  ? null
                  : type === "percent"
                    ? e.floatValue / 100
                    : e.floatValue;
              const newBounds: [number | null, number | null] =
                boundIndex === 0
                  ? [floatValue, bounds[otherIndex]]
                  : [bounds[otherIndex], floatValue];
              (setBounds as SetNullableBounds)(newBounds);
            } else if (e.floatValue !== undefined) {
              const floatValue =
                type === "percent" ? e.floatValue / 100 : e.floatValue;
              const newBounds: [number, number] =
                boundIndex === 0
                  ? [floatValue, bounds[otherIndex]!]
                  : [bounds[otherIndex]!, floatValue];
              (setBounds as SetBounds)(newBounds);
            }
          }}
          onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
            let dynamicModifierSize = 1;
            if (bounds[0] !== null && bounds[1] !== null) {
              dynamicModifierSize = Math.abs(
                10 ** (Math.ceil(Math.log10((bounds[0] + bounds[1]) / 2)) - 2),
              );
              // Handle numbers between 0 and 10 as special case.
              if (dynamicModifierSize < 1 && bounds[boundIndex]! >= 1)
                dynamicModifierSize = 1;
            }
            // Go up or down by 1 point if percent, 1% of value (rounded) otherwise
            const boundModifier =
              type === "percent" ? 0.01 : dynamicModifierSize;
            if (
              ["ArrowUp", "ArrowDown"].includes(e.key) &&
              bounds[boundIndex] !== null
            ) {
              // If the field contains non-null, arrow keys go up and down by one step
              let newBound = bounds[boundIndex]!;
              const modifierSign = e.key === "ArrowUp" ? 1 : -1;
              newBound = newBound + modifierSign * boundModifier;
              // Round if above 1.
              if (Math.abs(newBound) > 1) newBound = Math.round(newBound);
              const newBounds = [...bounds];
              newBounds[boundIndex] = newBound;
              if (allowNull) {
                (setBounds as SetNullableBounds)(
                  newBounds as [number | null, number | null],
                );
              } else {
                setBounds(newBounds as [number, number]);
              }
            } else if (["Tab", "Enter"].includes(e.key)) {
              focusOnNextFocusable();
            }
          }}
          prefix={type === "currency" ? "$" : undefined}
          suffix={
            type === "percent" ? "%" : type === "unit" ? ` ${unit}s` : undefined
          }
          thousandSeparator={type === "currency" || type === "decimal"}
          min={type === "percent" || type === "currency" ? 0 : undefined}
          allowNegative={!(type === "percent" || type === "currency")}
        />
        <label
          htmlFor={id}
          className="absolute left-2 bg-white px-1 text-xs text-gray-500 -top-2"
        >
          {boundIndex === 0 ? "Lower" : "Upper"}
        </label>
      </div>
    );
  },
);

NumericBound.displayName = "NumericBound";

export default NumericBound;
