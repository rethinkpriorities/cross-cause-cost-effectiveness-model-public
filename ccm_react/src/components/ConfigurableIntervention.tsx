import * as BaseDialog from "@radix-ui/react-dialog";
import { Button, Dialog, Tabs } from "@radix-ui/themes";
import { isEqual } from "lodash-es";
import { useEffect, useState } from "react";
import { ResultIntervention } from "../client";
import { DistributionSpec } from "../utils/distributions";
import { FormatType } from "../utils/formatting";
import { groupInterventions } from "../utils/interventionAreas";
import { Intervention } from "../utils/interventions";
import Markdown from "./Markdown";
import { DistributionPicker } from "./configurableDistribution/distributionPicker/DistributionPicker";
import { InlineButton } from "./elements/InlineButton";

type InterventionID = string;

interface ConfigurableInterventionProps {
  intervention: ResultIntervention | InterventionID | undefined;
  setIntervention: (
    intervention: ResultIntervention | InterventionID | undefined,
  ) => void;
  baseIntervention: Intervention | InterventionID;
  availableInterventions: Intervention[];
  type: string;
  formatType?: FormatType;
  formatUnit?: string;
  isModified?: boolean;
  allowCustom?: boolean;
}

interface ConfigurableInterventionState {
  preset: Intervention;
  custom: Intervention;
}

function resolveIntervention(
  intervention: Intervention | InterventionID | undefined,
  interventions: Intervention[],
) {
  if (typeof intervention === "string") {
    return interventions.find((i) => i.name === intervention);
  } else {
    return intervention;
  }
}

export function ConfigurableIntervention({
  intervention,
  setIntervention,
  baseIntervention,
  availableInterventions,
  type = "",
  formatType = "decimal",
  formatUnit,
  isModified = false,
  allowCustom = true,
}: ConfigurableInterventionProps) {
  const rawOuterIntervention = intervention ?? baseIntervention;
  const outerIntervention =
    resolveIntervention(intervention, availableInterventions) ??
    resolveIntervention(baseIntervention, availableInterventions)!;
  const resolvedBaseIntervention = resolveIntervention(
    baseIntervention,
    availableInterventions,
  ) as ResultIntervention;

  // Internal state of the component,
  // which keeps track of both tabs (preset and custom)
  // independently of the outer state
  const [innerInterventions, setInnerInterventions] =
    useState<ConfigurableInterventionState>({
      preset:
        resolveIntervention(intervention, availableInterventions) ??
        resolveIntervention(baseIntervention, availableInterventions)!,
      custom:
        resolveIntervention(intervention, availableInterventions) ??
        resolveIntervention(baseIntervention, availableInterventions)!,
    });

  // TODO(agucova): Connect with the contents of the distribution
  // when a custom intervention is selected
  const outerInterventionName =
    "name" in outerIntervention
      ? outerIntervention.name
      : "Custom intervention";

  const isCustom =
    typeof rawOuterIntervention !== "string" &&
    "name" in outerIntervention &&
    outerIntervention.name?.includes("Custom");

  const [tab, setTab] = useState<"preset" | "custom">(
    isCustom ? "custom" : "preset",
  );

  const [innerIntervention, setInnerIntervention] = useState<Intervention>(
    innerInterventions[tab],
  );

  useEffect(() => {
    setInnerInterventions({
      preset:
        resolveIntervention(intervention, availableInterventions) ??
        resolveIntervention(baseIntervention, availableInterventions)!,
      custom:
        resolveIntervention(intervention, availableInterventions) ??
        resolveIntervention(baseIntervention, availableInterventions)!,
    });
  }, [intervention, baseIntervention, availableInterventions]);

  useEffect(() => {
    setInnerIntervention(innerInterventions[tab]);
  }, [innerInterventions, tab]);

  // This does the same thing as `isCustom` in DistributionPicker, but here
  // "custom" is a type of intervention so `isCustom` means something else.
  const isSavedInterventionModified =
    intervention !== undefined && !isEqual(intervention, baseIntervention);

  const isChanged = !isEqual(outerIntervention, innerIntervention);

  const setInterventionFromDistribution = (
    distribution: DistributionSpec | undefined,
  ) => {
    // Updates the state when the distribution is changed
    if (distribution === undefined) {
      setIntervention(undefined);
    } else {
      const intervention: ResultIntervention = {
        name: "Custom intervention",
        area: "utility",
        type: "result",
        result_distribution: distribution,
      };
      setIntervention(intervention);
      setInnerInterventions((prev) => ({
        ...prev,
        custom: intervention,
      }));
    }
  };

  const interventionsByArea = groupInterventions(availableInterventions);

  return (
    <Dialog.Root>
      {/* We use the primitive trigger component so as to use asChild */}
      <BaseDialog.Trigger asChild>
        <InlineButton isHighlighted={isModified}>
          {outerInterventionName}
        </InlineButton>
      </BaseDialog.Trigger>
      <Dialog.Content>
        <Dialog.Title>Change {type} intervention</Dialog.Title>
        <Tabs.Root
          value={tab}
          onValueChange={(tab) => setTab(tab as "preset" | "custom")}
          className="mt-4"
        >
          <Tabs.List>
            <Tabs.Trigger value="preset">Preset intervention</Tabs.Trigger>
            {allowCustom && (
              <Tabs.Trigger value="custom">Distribution</Tabs.Trigger>
            )}
          </Tabs.List>
          <div className="px-4 pb-2 pt-3">
            <Tabs.Content value="preset">
              {tab == "preset" && (
                <div>
                  <p>
                    This is the currently selected {type} intervention for this
                    project:
                  </p>
                  <select
                    className="mb-4 block w-full rounded select select-bordered"
                    value={innerIntervention.name}
                    onChange={(e) => {
                      setInnerInterventions((prev) => ({
                        ...prev,
                        preset:
                          availableInterventions.find(
                            (intervention) =>
                              intervention.name == e.target.value,
                          ) ?? prev.preset,
                      }));
                    }}
                  >
                    <option value="Custom intervention">
                      Select an intervention
                    </option>
                    {interventionsByArea.map(
                      ({ area: group, interventions: interventions }) => (
                        <optgroup key={group} label={group}>
                          {interventions.map((intervention) => (
                            <option
                              key={intervention.name}
                              value={intervention.name}
                            >
                              {intervention.name}
                            </option>
                          ))}
                        </optgroup>
                      ),
                    )}
                  </select>
                  {innerIntervention?.name != "Custom intervention" &&
                    innerIntervention?.description && (
                      <Markdown>{innerIntervention.description}</Markdown>
                    )}
                  <div className="mt-8 flex justify-center space-x-2">
                    <Button
                      onClick={() =>
                        setIntervention(
                          "result_distribution" in innerIntervention
                            ? innerIntervention
                            : innerIntervention.name,
                        )
                      }
                      className="cursor-pointer"
                      variant="soft"
                      disabled={!isChanged}
                    >
                      Save changes
                    </Button>
                    <Button
                      onClick={() => setIntervention(undefined)}
                      className="cursor-pointer"
                      variant="soft"
                      color="crimson"
                      disabled={!isChanged && !isSavedInterventionModified}
                    >
                      Reset
                    </Button>
                  </div>
                </div>
              )}
            </Tabs.Content>
            {allowCustom && (
              <Tabs.Content value="custom">
                {tab == "custom" && (
                  <div>
                    <p>
                      You&apos;re overriding the {type} intervention for this
                      project to an arbitrary distribution:
                    </p>
                    <DistributionPicker
                      distribution={
                        ("result_distribution" in innerIntervention &&
                          innerIntervention.result_distribution) ||
                        undefined
                      }
                      setDistribution={setInterventionFromDistribution}
                      baseDistribution={
                        resolvedBaseIntervention.result_distribution
                      }
                      forceEnableSave={
                        outerIntervention.name != "Custom intervention"
                      }
                      forceEnableReset={
                        outerIntervention.name == "Custom intervention"
                      }
                      type={formatType}
                      unit={formatUnit}
                    />
                  </div>
                )}
              </Tabs.Content>
            )}
            <div className="mt-8 flex justify-center space-x-2"></div>
          </div>
        </Tabs.Root>
      </Dialog.Content>
    </Dialog.Root>
  );
}
