import { SquiggleChart } from "@quri/squiggle-components";
import "@quri/squiggle-components/common.css";

import { forwardRef } from "react";

interface SquiggleChartWrapperProps {
  code: string;
  className?: string;
}

// This wrapper enables compatibility with Radix UI
// by forwarding refs and accessibility props to an enclosing div.
const SquiggleChartWrapper = forwardRef<
  HTMLDivElement,
  SquiggleChartWrapperProps
>(({ code, className, ...rest }, ref) => {
  return (
    <div className={`squiggledisplay ${className ?? ""}`} ref={ref} {...rest}>
      <SquiggleChart code={code} />
    </div>
  );
});

SquiggleChartWrapper.displayName = "SquiggleChartWrapper";

export default SquiggleChartWrapper;
