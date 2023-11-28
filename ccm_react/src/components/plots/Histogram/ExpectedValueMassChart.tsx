import { useState, useContext, useEffect } from "react";
import { CaptionTextContext } from "../../../contexts/contexts";
import { numberAsIntegerString } from "../../../utils/formatting";
import { UNDISPLAYED_BLUE, DISPLAYED_BLUE } from "./constants";

interface ExpectedValueMassChartProps {
  expectedValueMasses: { below: number; included: number; above: number };
  totalResults: number;
  percentageDisplayed: number;
  percentageNegative: number;
  nearZerosHidden: number;
}

export function ExpectedValueMassChart({
  expectedValueMasses,
  totalResults,
  percentageDisplayed,
  nearZerosHidden,
  percentageNegative,
}: ExpectedValueMassChartProps) {
  const valueMassColors = {
    below: UNDISPLAYED_BLUE,
    included: DISPLAYED_BLUE,
    above: UNDISPLAYED_BLUE,
  };
  const [ref, setRef] = useState<SVGSVGElement | null>(null);
  const addToCaption = useContext(CaptionTextContext);

  const svgWidth = ref ? ref.getBoundingClientRect().width : null;
  const isLopsided = expectedValueMasses.included - percentageDisplayed < -0.1;
  useEffect(() => {
    addToCaption(
      <>
        {" "}
        The results include some extreme values that could not be displayed.
        {isLopsided && (
          <>
            {" "}
            While {percentageDisplayed.toFixed(2)}% of the{" "}
            {nearZerosHidden > 0 ? "significant positive and negative " : ""}
            results are included
            {nearZerosHidden == 0
              ? ""
              : nearZerosHidden / totalResults < 0.9
                ? ` (${numberAsIntegerString(
                    nearZerosHidden,
                  )} values are excluded for being close to 0)`
                : ` (all but ${numberAsIntegerString(
                    totalResults - nearZerosHidden,
                  )} values are excluded for being close to 0)`}
            , only
          </>
        )}{" "}
        {!isLopsided && (
          <>
            {" "}
            {percentageDisplayed.toFixed(2)}% of the{" "}
            {nearZerosHidden > 0
              ? "significant positive and negative "
              : "total "}
            results and{" "}
          </>
        )}
        {expectedValueMasses.included.toFixed(2)}% of the absolute expected
        value is reflected in this interval.
      </>,
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [expectedValueMasses]);
  return (
    <>
      {expectedValueMasses.included < 95 && (
        <div className="mt-3">
          <svg
            className="flex stroke-slate-700 dark:fill-slate-200 dark:stroke-slate-200"
            width="100%"
            height="32"
            ref={(newRef) => setRef(newRef)}
          >
            {expectedValueMasses.below > 0.5 && (
              <rect
                key="undisplayed - small"
                x="0%"
                y={4}
                width={expectedValueMasses.below - 0.5 + "%"}
                height="18"
                fill={valueMassColors.below}
              >
                <title>
                  {expectedValueMasses.below.toFixed(2)}% of absolute expected
                  value comes from samples smaller than any displayed.
                </title>
              </rect>
            )}
            {expectedValueMasses.included > 0.5 && (
              <rect
                key="displayed"
                x={expectedValueMasses.below + "%"}
                y={4}
                width={expectedValueMasses.included - 0.5 + "%"}
                height="18"
                fill={valueMassColors.included}
              >
                <title>
                  {expectedValueMasses.included.toFixed(2)}% of absolute
                  expected value comes from samples that are displayed.
                </title>
              </rect>
            )}
            {expectedValueMasses.above > 0.5 && (
              <rect
                key="undisplayed - large"
                x={
                  expectedValueMasses.below + expectedValueMasses.included + "%"
                }
                y={4}
                width={expectedValueMasses.above - 0.5 + "%"}
                height="18"
                fill={valueMassColors.above}
              >
                <title>
                  {expectedValueMasses.above.toFixed(2)}% of absolute expected
                  value comes from samples larger thant any displayed.
                </title>
              </rect>
            )}
            {svgWidth && (
              <g>
                <polygon
                  points={`${(percentageNegative * svgWidth) / 100},3 ${
                    (percentageNegative * svgWidth) / 100 - 3
                  },0 ${(percentageNegative * svgWidth) / 100 + 3},0`}
                />
                <text
                  x={Math.min(
                    Math.max(3, (percentageNegative * svgWidth) / 100),
                    svgWidth - 3,
                  )}
                  y="28"
                  dominantBaseline="middle"
                  textAnchor="middle"
                  className="fill-black text-sm text-size-[11px]"
                >
                  0
                </text>
                <title>
                  All expected values to the left are negative and to the right
                  are positive.
                </title>
              </g>
            )}
            {expectedValueMasses.included >= 10 && (
              <text
                x={`${
                  expectedValueMasses.below + expectedValueMasses.included / 2
                }%`}
                y="15"
                dominantBaseline="middle"
                textAnchor="middle"
                className="fill-white text-sm"
              >
                {expectedValueMasses.included.toFixed(2)}%
              </text>
            )}
            {expectedValueMasses.included < 10 &&
              expectedValueMasses.below >= 10 && (
                <text
                  x={`${expectedValueMasses.below / 2}%`}
                  y="15"
                  dominantBaseline="middle"
                  textAnchor="middle"
                  className="fill-white text-sm"
                >
                  {expectedValueMasses.below.toFixed(2)}%
                </text>
              )}
            {expectedValueMasses.included < 10 &&
              expectedValueMasses.above >= 10 && (
                <text
                  x={`${
                    expectedValueMasses.below +
                    expectedValueMasses.included +
                    expectedValueMasses.above / 2
                  }%`}
                  y="15"
                  dominantBaseline="middle"
                  textAnchor="middle"
                  className="fill-white text-sm"
                >
                  {expectedValueMasses.above.toFixed(2)}%
                </text>
              )}
          </svg>
        </div>
      )}
    </>
  );
}
