import { Button, Dialog, Tabs } from "@radix-ui/themes";
import { cloneDeep, isEqual } from "lodash";
import { Suspense, lazy, useCallback, useEffect, useState } from "react";

import {
  distDefaults,
  distributionMean,
  distributionStdev,
  distributionToSquiggle,
  setDistributionFromMoments,
} from "../../../utils/distributions";
// import SquiggleChartWrapper from "../plots/SquiggleChart";
import { ConfidenceDistribution } from "./ConfidenceDistributionInput";
import { UniformDistributionInput } from "./UniformDistributionInput";
import { ConfidenceDistributionSpec } from "../../../client";
import type { DistributionSpec } from "../../../utils/distributions";
import { rangeToConfidenceModel } from "../../../utils/distributions";
import { FormatType } from "../../../utils/formatting";
import { LoadingFallback } from "../../support/LoadingFallback";
import { BetaDistributionInput } from "./BetaDistributionInput";
import { ConstantDistributionInput } from "./ConstantDistributionInput";
import { GammaDistributionInput } from "./GammaDistributionInput";

const SquiggleChartWrapper = lazy(() => import("../../plots/SquiggleChart"));

const AbbreviateOnMobile = ({ children }: { children: React.ReactNode }) => {
  return (
    <>
      <span className="display-none md:inline">{children}</span>
      <span className="inline md:display-none">.</span>
    </>
  );
};

interface DistributionPickerProps {
  // The current value of the distribution
  distribution: DistributionSpec | undefined;
  // The function to call when the distribution is changed
  setDistribution: (distribution: DistributionSpec | undefined) => void;
  // The default distribution (to be used when the user resets the distribution)
  baseDistribution: DistributionSpec;
  // If true, always enable the Save button
  forceEnableSave?: boolean;
  // If true, always enable the Reset button
  forceEnableReset?: boolean;
  // The type of the random variable
  type?: FormatType;
  unit?: string;
}

/* Generates the default values for each possible distribution type that show up
  whenever the user opens the picker. If the current distribution uses a range
  and the user switches to a confidence distribution model, the default range
  values will be copied over from the range of the initial distribution.
  Otherwise, the distribution will be set to have the same mean and standard
  deviation as the current distribution (when converting from a constant
  distribution, the standard deviation is scaled based on the mean). */
function generateDistributionDefaults(
  distribution: DistributionSpec,
): Record<DistributionSpec["type"], DistributionSpec> {
  const defaults: Record<DistributionSpec["type"], DistributionSpec> =
    cloneDeep(distDefaults);
  // Override the default with the already set distribution
  defaults[distribution.type] = distribution;
  const mean = distributionMean(distribution);
  const stdev = distributionStdev(distribution);

  if (mean === null || stdev === null) {
    return defaults;
  }

  let key: DistributionSpec["type"];
  for (key in defaults) {
    if (key == distribution.type) {
      continue;
    }
    if ("clip" in distribution && "clip" in defaults[key]) {
      // copy over clip if it exists
      (defaults[key] as { clip: typeof distribution.clip }).clip =
        distribution.clip;
    }
    if ("range" in distribution && defaults[key].type == "confidence") {
      defaults[key] = rangeToConfidenceModel(
        distribution.range as [number, number],
        90,
        undefined,
        undefined,
      );
    } else {
      setDistributionFromMoments({
        dist: defaults[key],
        mean: mean,
        stdev: stdev,
        positiveEverywhere:
          ["lognormal", "beta", "gamma"].includes(distribution.type) ||
          ("range" in distribution && distribution.range[0] >= 0) ||
          (distribution.type == "constant" && distribution.value > 0),
      });
    }
  }
  return defaults;
}

/*
 * This component is used to pick an arbitrary distribution.
 */
export function DistributionPicker({
  distribution,
  setDistribution,
  baseDistribution,
  forceEnableSave = false,
  forceEnableReset = false,
  type = "decimal",
  unit,
}: DistributionPickerProps) {
  // TODO(agucova): Add support for passing a unit and displaying it.
  if (baseDistribution === undefined) {
    throw new Error("baseDistribution must be defined");
  }
  const defaultSpecType =
    distribution?.type ?? baseDistribution?.type ?? "confidence";
  const defaultDistributions = generateDistributionDefaults(
    distribution ?? baseDistribution,
  );
  const [innerDistributions, setInnerDistributions] =
    useState<Record<DistributionSpec["type"], DistributionSpec>>(
      defaultDistributions,
    );

  const [specType, setSpecType] =
    useState<DistributionSpec["type"]>(defaultSpecType);

  const innerDistribution = innerDistributions[specType];
  const setInnerDistribution = useCallback(
    (distribution: DistributionSpec) => {
      setInnerDistributions((prev) => {
        return {
          ...prev,
          [specType]: distribution,
        };
      });
    },
    [specType],
  );

  const isCustom =
    distribution !== undefined && !isEqual(distribution, baseDistribution);

  // The display is considered changed if the user has switched tabs or if an
  // input value in any tab has changed.
  const isTabChanged = specType !== defaultSpecType;
  const isInputChanged = (
    Object.keys(defaultDistributions) as (
      | "beta"
      | "confidence"
      | "constant"
      | "gamma"
      | "uniform"
      | "categorical"
    )[]
  ).some(
    (distType) =>
      !isEqual(innerDistributions[distType], defaultDistributions[distType]),
  );
  const isChanged = isTabChanged || isInputChanged;

  useEffect(() => {
    // Reset inner distribution when the state outside changes
    setInnerDistributions(
      generateDistributionDefaults(distribution ?? baseDistribution),
    );
    setSpecType(distribution?.type ?? baseDistribution?.type ?? "confidence");
  }, [distribution, baseDistribution]);

  const editKey = JSON.stringify(innerDistribution?.type);
  const squiggleCode = distributionToSquiggle(innerDistribution);

  return (
    <Tabs.Root
      value={specType}
      onValueChange={(specType) =>
        setSpecType(specType as DistributionSpec["type"])
      }
    >
      <Tabs.List>
        <Tabs.Trigger value="confidence">CI</Tabs.Trigger>
        <Tabs.Trigger value="uniform">
          Uni<AbbreviateOnMobile>form</AbbreviateOnMobile>
        </Tabs.Trigger>
        <Tabs.Trigger value="beta">Beta</Tabs.Trigger>
        <Tabs.Trigger value="gamma">Gamma</Tabs.Trigger>
        <Tabs.Trigger value="constant">
          Const<AbbreviateOnMobile>ant</AbbreviateOnMobile>
        </Tabs.Trigger>
      </Tabs.List>
      <div className="px-4 py-2 pt-3">
        {innerDistribution.type !== "constant" && (
          // TODO(agucova): Replace with the internal chart
          // (or replace with another chart)
          <Suspense fallback={<LoadingFallback />}>
            <SquiggleChartWrapper code={squiggleCode} />
          </Suspense>
        )}
        <Tabs.Content value="confidence">
          {innerDistribution.type == "confidence" && (
            <ConfidenceDistribution
              distribution={innerDistribution}
              setDistribution={setInnerDistribution}
              baseDistribution={baseDistribution as ConfidenceDistributionSpec}
              type={type}
              unit={unit}
              key={editKey}
            />
          )}
        </Tabs.Content>
        <Tabs.Content value="uniform">
          {innerDistribution.type == "uniform" && (
            <UniformDistributionInput
              distribution={innerDistribution}
              setDistribution={setInnerDistribution}
              type={type}
              unit={unit}
              key={editKey}
            />
          )}
        </Tabs.Content>
        <Tabs.Content value="beta">
          {innerDistribution.type == "beta" && (
            <BetaDistributionInput
              distribution={innerDistribution}
              setDistribution={setInnerDistribution}
              key={editKey}
            />
          )}
        </Tabs.Content>
        <Tabs.Content value="gamma">
          {innerDistribution.type == "gamma" && (
            <GammaDistributionInput
              distribution={innerDistribution}
              setDistribution={setInnerDistribution}
              key={editKey}
            />
          )}
        </Tabs.Content>
        <Tabs.Content value="constant">
          {innerDistribution.type == "constant" && (
            <ConstantDistributionInput
              distribution={innerDistribution}
              setDistribution={setInnerDistribution}
              type={type}
              unit={unit}
              key={editKey}
            />
          )}
        </Tabs.Content>
        <div className="mt-8 flex justify-center space-x-2">
          <Dialog.Close>
            <Button
              onClick={() => setDistribution(innerDistribution)}
              className="cursor-pointer"
              variant="soft"
              disabled={!isChanged && !forceEnableSave}
            >
              Save changes
            </Button>
          </Dialog.Close>
          <Button
            onClick={() => {
              setDistribution(undefined);
              setInnerDistributions(
                generateDistributionDefaults(baseDistribution),
              );
            }}
            className="cursor-pointer"
            variant="soft"
            color="crimson"
            disabled={!isInputChanged && !isCustom && !forceEnableReset}
          >
            Reset
          </Button>
        </div>
      </div>
    </Tabs.Root>
  );
}
