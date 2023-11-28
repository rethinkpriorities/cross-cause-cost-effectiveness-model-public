import { CheckIcon, ChevronDownIcon } from "@radix-ui/react-icons";
import * as BaseSelect from "@radix-ui/react-select";
import React, { forwardRef } from "react";

interface SelectProps extends React.ComponentPropsWithoutRef<"div"> {
  placeholder: string;
  value: string;
  setValue: (value: string) => void;
}
export function Select({
  placeholder,
  value,
  setValue,
  children,
  ...rest
}: SelectProps) {
  return (
    <div className="relative text-base font-sans prose" {...rest}>
      <BaseSelect.Root value={value} onValueChange={setValue}>
        <BaseSelect.Trigger
          className="h-[43px] inline-flex items-center justify-center gap-[5px] border-2 border-slate-6 border-rounded rounded bg-white px-[15px] text-base font-normal leading-none font-sans accent-blue-5 focus:border-3 focus:border-blue-6 data-[placeholder]:text-accent focus:outline-none"
          aria-label={placeholder}
        >
          <BaseSelect.Value placeholder={placeholder} />
          <BaseSelect.Icon>
            <ChevronDownIcon />
          </BaseSelect.Icon>
        </BaseSelect.Trigger>
        <BaseSelect.Portal>
          <BaseSelect.Content className="overflow-hidden rounded-md bg-white text-base font-sans shadow">
            {/* TODO: Improve styling here */}
            <BaseSelect.Viewport className="px-3 py-2">
              {children}
            </BaseSelect.Viewport>
          </BaseSelect.Content>
        </BaseSelect.Portal>
      </BaseSelect.Root>
      <label className="absolute left-2 bg-white px-1 text-xs text-gray-500 -top-2">
        {placeholder}
      </label>
    </div>
  );
}

export const SelectItem = forwardRef<
  HTMLDivElement,
  BaseSelect.SelectItemProps
>(({ children, ...rest }: BaseSelect.SelectItemProps, forwardedRef) => (
  <BaseSelect.Item
    {...rest}
    ref={forwardedRef}
    className="relative h-[25px] flex items-center rounded-[3px] pl-[25px] pr-[35px] text-sm leading-none font-sans data-[disabled]:pointer-events-none data-[highlighted]:bg-blue-6 data-[highlighted]:text-white data-[highlighted]:outline-none"
  >
    <BaseSelect.ItemText>{children}</BaseSelect.ItemText>
    <BaseSelect.ItemIndicator className="absolute left-0 w-[25px] inline-flex items-center justify-center">
      <CheckIcon />
    </BaseSelect.ItemIndicator>
  </BaseSelect.Item>
));

SelectItem.displayName = "SelectItem";

export const SelectLabel = forwardRef<
  HTMLDivElement,
  BaseSelect.SelectLabelProps
>((props: BaseSelect.SelectLabelProps, forwardedRef) => (
  <BaseSelect.Label
    {...props}
    ref={forwardedRef}
    className="x-[25px] pb-2 text-sm leading-[25px] text-slate-6"
  />
));

SelectLabel.displayName = "SelectLabel";

// re-export BaseSelect
// eslint-disable-next-line react-refresh/only-export-components
export * as BaseSelect from "@radix-ui/react-select";
export type { SelectItemProps } from "@radix-ui/react-select";
