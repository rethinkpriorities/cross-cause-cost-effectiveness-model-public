import { forwardRef } from "react";
import { MixerHorizontalIcon } from "@radix-ui/react-icons";

interface InlineButtonProps extends React.HTMLAttributes<HTMLSpanElement> {
  isHighlighted?: boolean;
}

const InlineButton = forwardRef<HTMLButtonElement, InlineButtonProps>(
  function InlineButton(
    {
      children,
      onClick,
      onKeyPress = () => undefined,
      isHighlighted = false,
      className,
      ...rest
    },
    ref,
  ) {
    return (
      <span
        role="button"
        className={`inline-button dark:text-black ${
          isHighlighted ? "bg-orange-200" : "bg-sky-200"
        } ${className} cursor-pointer`}
        onClick={onClick}
        onKeyPress={onKeyPress}
        tabIndex={0}
        ref={ref}
        {...rest}
      >
        {children}
        <span style={{ paddingLeft: "1px" }}>
          <MixerHorizontalIcon />
        </span>
      </span>
    );
  },
);

InlineButton.displayName = "InlineButton";

export { InlineButton };
