import "@quri/squiggle-components/common.css";
import { GearIcon } from "@radix-ui/react-icons";
import * as Popover from "@radix-ui/react-popover";
import { IconButton, Tooltip } from "@radix-ui/themes";
import { isEqual } from "lodash-es";
import { ConfidenceDistributionSpec } from "../../../client";

import { useEffect, useState } from "react";

import { rangeToConfidenceModel } from "../../../utils/distributions";
import {
  BaseSelect,
  Select,
  SelectItem,
  SelectLabel,
} from "../../elements/Select";
import RangeInput from "./RangeInput";

import { useDebounce } from "usehooks-ts";
import { FormatType } from "../../../utils/formatting";

interface ConfidenceDistributionProps {
  distribution: ConfidenceDistributionSpec;
  setDistribution: (distribution: ConfidenceDistributionSpec) => void;
  baseDistribution: ConfidenceDistributionSpec;
  type?: FormatType;
  unit?: string;
}

/* Check if clip is defined on at least one side */
function isClipDefined(clip: (number | null)[] | undefined) {
  return typeof clip?.[0] == "number" || typeof clip?.[1] == "number";
}

function isClipRangeValid(clip: [number | null, number | null] | undefined) {
  return (
    clip == undefined ||
    typeof clip[0] != "number" ||
    typeof clip[1] != "number" ||
    clip[0] < clip[1]
  );
}

export function ConfidenceDistribution({
  distribution,
  setDistribution,
  baseDistribution,
  type = "decimal",
  unit,
}: ConfidenceDistributionProps) {
  const [range, setRange] = useState<[number, number]>([
    distribution.range[0] as number,
    distribution.range[1] as number,
  ]);
  const [clip, setClip] = useState<[number | null, number | null]>(
    (distribution.clip ?? [null, null]) as [number | null, number | null],
  );
  const [credibility, setCredibility] = useState<90 | 80 | 50>(
    distribution.credibility!,
  );

  const isClipModified = !isEqual(clip, baseDistribution.clip);

  const debouncedRange = useDebounce(range, 300);
  const debouncedClip = useDebounce(clip, 300);

  const [showClipInputs, setShowClipInputs] = useState(
    isClipDefined(distribution.clip),
  );

  const handleCheckboxChange = () => {
    if (!showClipInputs) {
      setClip(baseDistribution.clip as [number | null, number | null]);
      setShowClipInputs(true);
    } else {
      setClip([null, null]);
      setShowClipInputs(false);
    }
  };

  // Update range and clip when the distribution changes
  useEffect(() => {
    setRange(distribution.range as [number, number]);
    setClip(
      (distribution.clip ?? [null, null]) as [number | null, number | null],
    );
    setShowClipInputs(isClipDefined(distribution.clip));
  }, [distribution]);

  useEffect(() => {
    if (
      debouncedRange[0] < debouncedRange[1] &&
      isClipRangeValid(debouncedClip)
    ) {
      setDistribution(
        rangeToConfidenceModel(
          debouncedRange,
          credibility,
          debouncedClip as [number | undefined, number | undefined] | undefined,
          distribution.distribution,
        ),
      );
    }
  }, [
    credibility,
    debouncedClip,
    debouncedRange,
    distribution.distribution,
    setDistribution,
  ]);

  // Check if lower bound is higher than or equal to upper bound
  const rangeError = range[0] >= range[1];
  const clipRangeError = !isClipRangeValid(clip);

  const clipTooltip = clipRangeError
    ? "Invalid clip range"
    : isClipModified
      ? "Clip range of the distribution (modified)"
      : "Clip range of the distribution";

  return (
    <div>
      <p className="text-sm md:block lt-md:hidden">
        Confidence distribution. By default, uses a lognormal distribution for
        positive-everywhere ranges and a normal distribution for ranges that
        cross zero.
      </p>
      <div className="mx-auto mb-2 mt-4 flex flex-wrap items-center justify-center gap-4">
        <RangeInput
          className="w-20 border-2 border-slate-6 border-rounded md:w-30"
          boundIndex={0}
          range={range}
          setRange={setRange}
          type={type}
          unit={unit}
        />
        <RangeInput
          className="w-20 border-2 border-slate-6 border-rounded md:w-30"
          boundIndex={1}
          range={range}
          setRange={setRange}
          type={type}
          unit={unit}
        />
        <Select
          placeholder="CI"
          value={credibility.toString()}
          setValue={(value) => setCredibility(parseInt(value) as 50 | 80 | 90)}
        >
          <BaseSelect.Group>
            <SelectLabel>Confidence Interval</SelectLabel>
            <SelectItem value="50">50%</SelectItem>
            <SelectItem value="80">80%</SelectItem>
            <SelectItem value="90">90%</SelectItem>
          </BaseSelect.Group>
        </Select>
        <Popover.Root>
          <Tooltip content={clipTooltip} sideOffset={12}>
            <Popover.Trigger asChild>
              <IconButton
                color={
                  clipRangeError ? "red" : isClipModified ? "orange" : undefined
                }
                variant={clipRangeError ? "solid" : "surface"}
                highContrast={!clipRangeError}
              >
                <GearIcon />
              </IconButton>
            </Popover.Trigger>
          </Tooltip>
          <Popover.Content
            className="w-auto flex flex-col gap-4 rounded-lg bg-white p-6 shadow-lg outline-1 outline-gray-200 outline space-y-2"
            sideOffset={10}
          >
            <div className="flex justify-center gap-2">
              <input
                id="clip-checkbox"
                type="checkbox"
                checked={showClipInputs}
                onChange={handleCheckboxChange}
                style={{ border: "2px solid #e1e1e1" }}
              />
              <label htmlFor="clip-checkbox">
                Clip the tails of this distribution
              </label>
            </div>
            {showClipInputs && (
              <div style={{ display: "flex", gap: "10px" }}>
                <div style={{ display: "flex", gap: "10px" }}>
                  <RangeInput
                    className="w-20 border-2 border-slate-6 border-rounded md:w-30"
                    boundIndex={0}
                    range={clip}
                    setRange={setClip}
                    allowNull={true}
                    type={type}
                    unit={unit}
                  />
                  <RangeInput
                    className="w-20 border-2 border-slate-6 border-rounded md:w-30"
                    boundIndex={1}
                    range={clip}
                    setRange={setClip}
                    allowNull={true}
                    type={type}
                    unit={unit}
                  />
                </div>
              </div>
            )}
            {clipRangeError && (
              <div className="mb-0 mt-4 text-center text-sm text-red-500">
                Lower clip must be less than upper clip
              </div>
            )}
          </Popover.Content>
        </Popover.Root>
      </div>
      {rangeError && (
        <div className="mb-0 mt-4 text-center text-sm text-red-500">
          Lower bound must be less than upper bound
        </div>
      )}
    </div>
  );
}
