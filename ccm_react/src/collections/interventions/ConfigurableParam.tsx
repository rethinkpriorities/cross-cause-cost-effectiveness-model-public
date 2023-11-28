import * as BaseDialog from "@radix-ui/react-dialog";
import { Button, Checkbox, Dialog } from "@radix-ui/themes";
import { produce, setAutoFreeze } from "immer";
import { Atom, WritableAtom, useAtom, useAtomValue } from "jotai";
import { clone, get, isEqual, omit, set } from "lodash-es";
import { useEffect, useState } from "react";
import {
  Animal,
  AnimalIntervention,
  AnimalInterventionParams,
  GhdIntervention,
  GhdInterventionParams,
  LongTermParams,
  MoralWeightsParams,
  XRiskIntervention,
} from "../../client";
import {
  baseAnimalInterventionAtom,
  baseGhdInterventionAtom,
  baseXRiskInterventionAtom,
  customAnimalInterventionAtom,
  customGhdInterventionAtom,
  customXRiskInterventionAtom,
  defaultParamsAtom,
  interventionSpeciesAtom,
  paramAttributesAtom,
  paramsAtom,
} from "../../stores/atoms";
import { DistributionSpec } from "../../utils/distributions";
import { FormatType, getFormat } from "../../utils/formatting";
import Markdown from "../../components/Markdown";
import NumberInput from "../../components/configurableDistribution/distributionPicker/NumberInput";
import { ConfigurableDistribution } from "../../components/configurableDistribution/ConfigurableDistribution";
import { InlineButton } from "../../components/elements/InlineButton";

type ParamType = DistributionSpec | string | number | boolean;

function SaveAndResetButtons<Value extends ParamType>({
  baseValue,
  paramValue,
  inputValue,
  setInputValue,
  setValue,
  isModified,
}: {
  baseValue: Value;
  paramValue: Value;
  inputValue: Value;
  setInputValue: (value: Value) => void;
  setValue: (value: Value | undefined) => void;
  isModified: boolean;
}) {
  const isInputChanged = inputValue !== paramValue;

  return (
    <div className="mt-8 flex justify-center space-x-2">
      <Button
        onClick={() => {
          if (inputValue === baseValue) {
            setValue(undefined);
          } else {
            setValue(inputValue);
          }
        }}
        className="cursor-pointer"
        variant="soft"
        disabled={!isInputChanged}
      >
        Save changes
      </Button>
      <Button
        onClick={() => {
          setInputValue(baseValue);
          setValue(undefined);
        }}
        className="cursor-pointer"
        variant="soft"
        color="crimson"
        disabled={!isModified}
      >
        Reset
      </Button>
    </div>
  );
}

function ConfigurableDistributionParam({
  customDistribution,
  baseDistribution,
  setDistribution,
  name,
  type = "decimal",
  unit,
}: {
  customDistribution: DistributionSpec | undefined;
  baseDistribution: DistributionSpec;
  setDistribution: (dist: DistributionSpec | undefined) => void;
  name: string;
  type?: FormatType;
  unit?: string;
}) {
  const isModified =
    customDistribution !== undefined &&
    !isEqual(customDistribution, baseDistribution);
  const paramAttributes = useAtomValue(paramAttributesAtom);

  const metadata = paramAttributes[name];

  // Create key out of custom params to force re-render when they change.
  const key = Object.values(customDistribution ?? {}).join(",");

  return ConfigurableDistribution({
    metadata: metadata,
    customDistribution: customDistribution,
    baseDistribution: baseDistribution,
    setDistribution: setDistribution,
    isModified: isModified,
    key: key,
    type: type,
    unit: unit,
  });
}

function ConfigurableBooleanParam({
  customValue,
  baseValue,
  setValue,
  name,
  displayOnTrue,
  displayOnFalse,
}: {
  customValue: boolean | undefined;
  baseValue: boolean;
  setValue: (value: ParamType | undefined) => void;
  name: string;
  displayOnTrue: string;
  displayOnFalse: string;
}) {
  const isModified = customValue !== undefined && customValue != baseValue;
  const paramAttributes = useAtomValue(paramAttributesAtom);
  const metadata = paramAttributes[name];
  const paramValue = customValue ?? baseValue;
  const [inputValue, setInputValue] = useState<boolean>(paramValue);

  // Ensure that `inputValue` updates whenever `paramValue` changes
  useEffect(() => setInputValue(paramValue), [paramValue]);

  const checkboxID = `checkbox-${name.replace(" ", "-").toLowerCase()}`;

  return (
    <Dialog.Root>
      {/* We use the primitive trigger component so as to use asChild */}
      <BaseDialog.Trigger asChild>
        <InlineButton isHighlighted={isModified}>
          {paramValue ? displayOnTrue : displayOnFalse}
        </InlineButton>
      </BaseDialog.Trigger>
      <Dialog.Content>
        <Dialog.Title>
          Modifying attribute: {metadata?.title ?? name}
        </Dialog.Title>
        <div className="my-4 flex items-start gap-2">
          <div className="flex items-center">
            <Checkbox
              id={checkboxID}
              checked={inputValue}
              onCheckedChange={(checked) => {
                if (checked !== "indeterminate") {
                  setInputValue(checked);
                }
              }}
            />
          </div>
          <label htmlFor={checkboxID}>
            <Markdown unwrapDisallowed={true} disallowedElements={["p"]}>
              {metadata.description}
            </Markdown>
          </label>
        </div>
        {SaveAndResetButtons({
          baseValue: baseValue,
          paramValue: paramValue,
          inputValue: inputValue,
          setInputValue: setInputValue,
          setValue: setValue,
          isModified: isModified,
        })}
      </Dialog.Content>
    </Dialog.Root>
  );
}

function ConfigurableLiteralParam({
  customValue,
  baseValue,
  setValue,
  name,
  optionMap,
  literalOptions,
}: {
  customValue: string | undefined;
  baseValue: string;
  optionMap?: Record<string, string>;
  setValue: (value: ParamType | undefined) => void;
  name: string;
  literalOptions: string[];
}) {
  const isModified = customValue !== undefined && customValue != baseValue;
  const paramAttributes = useAtomValue(paramAttributesAtom);
  const metadata = paramAttributes[name];
  const paramValue = customValue ?? baseValue;
  const [inputValue, setInputValue] = useState<string>(paramValue);

  // Ensure that `inputValue` updates whenever `paramValue` changes
  useEffect(() => setInputValue(paramValue), [paramValue]);

  const dropdownID = `dropdown-${name.replace(" ", "-").toLowerCase()}}`;

  return (
    <Dialog.Root>
      {/* We use the primitive trigger component so as to use asChild */}
      <BaseDialog.Trigger asChild>
        <InlineButton isHighlighted={isModified}>
          {optionMap ? optionMap[paramValue] ?? paramValue : paramValue}
        </InlineButton>
      </BaseDialog.Trigger>
      <Dialog.Content>
        <Dialog.Title>
          Modifying attribute: {metadata?.title ?? name}
        </Dialog.Title>
        <div>
          <p>This is the currently selected option:</p>
          <select
            id={dropdownID}
            name={name}
            onChange={(e) => {
              setInputValue(e.target.value);
            }}
            value={inputValue}
            className="mb-4 block w-full rounded select select-bordered"
          >
            {literalOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <label htmlFor={dropdownID}>
            <Markdown>{metadata.description}</Markdown>
          </label>
        </div>
        {SaveAndResetButtons({
          baseValue: baseValue,
          paramValue: paramValue,
          inputValue: inputValue,
          setInputValue: setInputValue,
          setValue: setValue,
          isModified: isModified,
        })}
      </Dialog.Content>
    </Dialog.Root>
  );
}

/* Note: This function behaves somewhat unusually to work with moral weight params.
   Namely, instead of treating `customValue == undefined` as the default, it treats
   `customValue == baseValue` as the default, and it requires `customValue` to be
   defined or else it raises validation errors.
 */
function ConfigurableNumericParam({
  customValue,
  baseValue,
  setValue,
  name,
  type = "decimal",
  unit,
}: {
  customValue: number | undefined;
  baseValue: number;
  setValue: (value: number | undefined) => void;
  name: string;
  type?: FormatType;
  unit?: string;
}) {
  const isModified = customValue !== undefined && customValue !== baseValue;
  const paramAttributes = useAtomValue(paramAttributesAtom);
  const metadata = paramAttributes[name];
  const description = metadata?.description ?? "";
  const paramValue = customValue ?? baseValue;
  const [inputValue, setInputValue] = useState<number>(paramValue);
  const formatter = getFormat(type, unit);

  // Ensure that `inputValue` updates whenever `paramValue` changes
  useEffect(() => setInputValue(paramValue), [paramValue]);

  return (
    <Dialog.Root>
      {/* We use the primitive trigger component so as to use asChild */}
      <BaseDialog.Trigger asChild>
        <InlineButton isHighlighted={isModified}>
          {formatter.format(paramValue)}
        </InlineButton>
      </BaseDialog.Trigger>
      <Dialog.Content>
        <Dialog.Title>
          Modifying attribute: {metadata?.title ?? name}
        </Dialog.Title>
        <div className="my-4 flex items-start gap-2">
          <div className="flex items-center">
            <NumberInput
              id={name}
              label={name}
              value={inputValue ?? paramValue}
              setValue={setInputValue}
              type={type}
            />
          </div>
          <label htmlFor={name}>{description}</label>
        </div>
        {SaveAndResetButtons({
          baseValue: baseValue,
          paramValue: paramValue,
          inputValue: inputValue,
          setInputValue: setInputValue,
          setValue: setValue,
          isModified: isModified,
        })}
      </Dialog.Content>
    </Dialog.Root>
  );
}

/* Generic function to configure a named parameter on an object. Takes in a
`valueAtom` object holding the custom value, a constant `defaultValueAtom`
object holding the default value, and a `path` to the parameter on the object,
of the form "field_name.subfield_name".

 In some cases, we want to set a sub-field *within* a parameter where the
 parameter has type Record<string, ParamType>. Use the `keyName` parameter to
 specify the name of the sub-field under the parameter. If a sub-field is
 modified, the parameter record will copy its values from the default value,
 only modifying the one sub-field. If the sub-field is set to the default value
 and all other sub-fields equal their default values, the parameter will be
 removed from the params object. */
export function ConfigurablePathParam<
  O extends Record<string, unknown> | (Record<string, unknown> | undefined),
>({
  valueAtom,
  defaultValueAtom,
  path,
  type = "decimal",
  unit,
  keyName,
  displayOnTrue = "",
  displayOnFalse = "",
  literalOptions = [],
}: {
  valueAtom: WritableAtom<O | Promise<O>, O[], unknown>;
  defaultValueAtom: Atom<O | Promise<O>>;
  path: string;
  type?: FormatType;
  unit?: string;
  keyName?: string;
  displayOnTrue?: string;
  displayOnFalse?: string;
  literalOptions?: string[];
}) {
  let baseValue: ParamType;
  let customValue: ParamType | undefined;
  let setCustomValue: (value: ParamType | undefined) => void;

  // Default
  const defaultParams = useAtomValue(defaultValueAtom);

  // Custom
  const [customParams, setCustomParams] = useAtom(valueAtom);
  if (keyName == undefined) {
    baseValue = get(defaultParams, path) as ParamType;
    customValue = get(customParams, path) as ParamType | undefined;
    setCustomValue = (value) => {
      setAutoFreeze(false);
      setCustomParams(
        produce(customParams ?? ({} as Exclude<O, undefined>), (draft) => {
          set(draft, path, value);
        }),
      );
    };
  } else {
    const baseRecord = get(defaultParams, path) as Record<string, ParamType>;
    const customRecord = get(customParams, path) as
      | Record<string, ParamType>
      | undefined;
    baseValue = baseRecord[keyName]!;
    customValue = customRecord?.[keyName];
    setCustomValue = (value) => {
      setAutoFreeze(false);
      let newRecord = {
        ...(customRecord ?? baseRecord),
        [keyName]: value ?? baseValue,
      } as Record<string, ParamType> | undefined;
      if (isEqual(newRecord, baseRecord)) {
        newRecord = undefined;
      }
      setCustomParams(
        produce(customParams ?? ({} as Exclude<O, undefined>), (draft) => {
          set(draft, path, newRecord);
        }),
      );
    };
  }

  // extract name from path
  const name = path.split(".")?.slice(-1)[0];

  return ConfigurableParam({
    baseValue: baseValue,
    customValue: customValue,
    setValue: setCustomValue,
    name: name,
    type: type,
    unit: unit,
    displayOnTrue: displayOnTrue,
    displayOnFalse: displayOnFalse,
    literalOptions: literalOptions,
  });
}

export function GlobalParam({
  path,
  type = "decimal",
  unit,
  literalOptions,
  displayOnTrue = "",
  displayOnFalse = "",
}: {
  path: string;
  type?: FormatType;
  unit?: string;
  displayOnTrue?: string;
  displayOnFalse?: string;
  literalOptions?: string[];
}) {
  return ConfigurablePathParam({
    valueAtom: paramsAtom,
    defaultValueAtom: defaultParamsAtom,
    path: path,
    type: type,
    unit: unit,
    displayOnTrue: displayOnTrue,
    displayOnFalse: displayOnFalse,
    literalOptions: literalOptions,
  });
}

export function ConfigurableParam({
  customValue,
  baseValue,
  setValue,
  name,
  type = "decimal",
  unit,
  displayOnTrue,
  displayOnFalse,
  literalOptions = [],
  optionMap,
}: {
  customValue: ParamType | undefined;
  baseValue: ParamType;
  setValue: (value: ParamType | undefined) => void;
  optionMap?: Record<string, string>;
  name: string;
  type?: FormatType;
  unit?: string;
  displayOnTrue?: string;
  displayOnFalse?: string;
  literalOptions?: string[];
}) {
  if (baseValue === undefined) {
    throw new Error(
      "The base value must be defined. Perhaps you used the wrong path to the param?",
    );
  }
  if (typeof baseValue == "boolean") {
    return (
      <ConfigurableBooleanParam
        customValue={customValue as boolean | undefined}
        baseValue={baseValue}
        setValue={setValue}
        name={name}
        displayOnTrue={displayOnTrue!}
        displayOnFalse={displayOnFalse!}
      />
    );
  } else if (typeof baseValue == "string") {
    return (
      <ConfigurableLiteralParam
        customValue={customValue as string | undefined}
        baseValue={baseValue}
        setValue={setValue}
        optionMap={optionMap}
        name={name}
        literalOptions={literalOptions}
      />
    );
  } else if (typeof baseValue == "number") {
    return (
      <ConfigurableNumericParam
        customValue={customValue as number | undefined}
        baseValue={baseValue}
        setValue={setValue}
        name={name}
        type={type}
        unit={unit}
      />
    );
  } else {
    return (
      <ConfigurableDistributionParam
        customDistribution={customValue as DistributionSpec | undefined}
        baseDistribution={baseValue}
        setDistribution={setValue}
        name={name}
        type={type}
        unit={unit}
      />
    );
  }
}

export function ConfigurableGlobalGhdParam({
  name,
  type = "decimal",
  unit,
  displayOnTrue = "",
  displayOnFalse = "",
}: {
  name: keyof GhdInterventionParams;
  type?: FormatType;
  unit?: string;
  displayOnTrue?: string;
  displayOnFalse?: string;
}) {
  return (
    <ConfigurablePathParam
      valueAtom={paramsAtom}
      defaultValueAtom={defaultParamsAtom}
      path={`ghd_intervention_params.${name}`}
      type={type}
      unit={unit}
      displayOnTrue={displayOnTrue}
      displayOnFalse={displayOnFalse}
    />
  );
}

export function ConfigurableGhdParam({
  name,
  type = "decimal",
  unit,
  displayOnTrue = "",
  displayOnFalse = "",
  literalOptions = [],
}: {
  name: keyof GhdIntervention;
  type?: FormatType;
  unit?: string;
  displayOnTrue?: string;
  displayOnFalse?: string;
  literalOptions?: string[];
}) {
  return (
    <ConfigurablePathParam
      valueAtom={customGhdInterventionAtom}
      defaultValueAtom={baseGhdInterventionAtom}
      path={name}
      type={type}
      unit={unit}
      displayOnTrue={displayOnTrue}
      displayOnFalse={displayOnFalse}
      literalOptions={literalOptions}
    />
  );
}

export function ConfigurableAnimalParam({
  name,
  type = "decimal",
  unit,
  displayOnTrue = "",
  displayOnFalse = "",
  literalOptions = [],
}: {
  name: keyof AnimalIntervention;
  type?: FormatType;
  unit?: string;
  displayOnTrue?: string;
  displayOnFalse?: string;
  literalOptions?: string[];
}) {
  return (
    <ConfigurablePathParam
      valueAtom={customAnimalInterventionAtom}
      defaultValueAtom={baseAnimalInterventionAtom}
      path={name}
      type={type}
      unit={unit}
      displayOnTrue={displayOnTrue}
      displayOnFalse={displayOnFalse}
      literalOptions={literalOptions}
    />
  );
}

/*
 * Configuration for a param containing a dict from animal species to
 * DistributionSpec.
 */
export function ConfigurableSpeciesSpecificParam({
  name,
  type = "decimal",
  unit,
}: {
  name: keyof AnimalInterventionParams;
  type?: FormatType;
  unit?: string;
}) {
  const species = useAtomValue(interventionSpeciesAtom);
  if (species == undefined) {
    // User hasn't selected a base intervention yet.
    return <span>unknown, please select an intervention</span>;
  }

  return (
    <ConfigurablePathParam
      valueAtom={paramsAtom}
      defaultValueAtom={defaultParamsAtom}
      path={`animal_intervention_params.${name}`}
      keyName={species}
      type={type}
      unit={unit}
    />
  );
}

/*
 * Special function for moral weights because they're stored in a weird format.
 */

type OverrideType = MoralWeightsParams["override_type"];
export function ConfigurableMoralWeightParam({
  name,
  optionMap,
}: {
  name: keyof MoralWeightsParams;
  optionMap?: Record<string, string>;
}) {
  const defaultParams = useAtomValue(defaultParamsAtom);
  const [allParams, setAllParams] = useAtom(paramsAtom);

  // This always exists, as Parameters are initialized with default values.
  const baseObj =
    defaultParams.animal_intervention_params!.moral_weight_params!;

  const customObj = {
    override_type: baseObj.override_type,
    sentience_ranges: clone(baseObj.sentience_ranges),
    moral_weights_override: clone(baseObj.moral_weights_override),
    welfare_capacities_override: clone(baseObj.welfare_capacities_override),
    ...(allParams.animal_intervention_params?.moral_weight_params ?? {}),
  };

  const species = useAtomValue(interventionSpeciesAtom);
  if (species === undefined) {
    return <span>unknown</span>;
  }

  type Valueof<T> = T[keyof T];
  const accessBySpeciesAsRelevant =
    name === "override_type"
      ? (v: Valueof<MoralWeightsParams>) => v
      : (v: Valueof<MoralWeightsParams>) => v?.[species as keyof typeof v];

  const baseMoralWeight = accessBySpeciesAsRelevant(baseObj[name]);
  const customMoralWeight = accessBySpeciesAsRelevant(customObj[name]);

  const setMoralWeight = (
    value: OverrideType | DistributionSpec | undefined,
  ) => {
    // Note: If `value` is undefined, we set the moral weight to
    //`baseMoralWeight` instead of omitting it because the backend expects the
    // `moral_weights` dict to have populated values for every species. Our
    // standard logic to merge defaultParamsAtom with paramsAtom doesn't work
    // because the `moral_weights` dict is a sub-field on a param, not the param
    // itself.
    if (name === "override_type") {
      customObj.override_type = (value ?? baseMoralWeight) as OverrideType;
    } else {
      const objUnderName = customObj[name]! as Record<Animal, DistributionSpec>;
      objUnderName[species] = (value ?? baseMoralWeight) as DistributionSpec;
    }

    // If the moral weights dict has no custom values, the moral weights object
    // is removed from animal intervention params.
    let newAnimalParams: AnimalInterventionParams | undefined;
    if (
      typeof value !== "undefined" &&
      !isEqual(customObj?.[name], baseObj[name])
    ) {
      newAnimalParams = {
        ...allParams.animal_intervention_params,
        moral_weight_params: customObj,
      };
    } else {
      const newMoralWeightParams = omit(
        allParams?.animal_intervention_params?.moral_weight_params,
        name,
      );
      newAnimalParams = {
        ...allParams.animal_intervention_params,
        moral_weight_params: newMoralWeightParams,
      };
    }

    // If this resulted in an empty animal params object, the animal params
    // object is removed from the params atom.
    if (Object.keys(newAnimalParams).length != 0) {
      setAllParams({
        ...allParams,
        animal_intervention_params: newAnimalParams,
      });
    } else {
      setAllParams(omit(allParams, "animal_intervention_params"));
    }
  };

  if (name === "override_type") {
    return (
      <ConfigurableParam
        customValue={customMoralWeight as ParamType}
        baseValue={baseMoralWeight as string}
        setValue={setMoralWeight as (value: ParamType | undefined) => void}
        optionMap={optionMap}
        name={name}
        literalOptions={optionMap ? Object.keys(optionMap) : []}
      />
    );
  }
  return (
    <ConfigurableDistributionParam
      customDistribution={customMoralWeight as DistributionSpec}
      baseDistribution={baseMoralWeight as DistributionSpec}
      setDistribution={setMoralWeight}
      name="moral_weight_params"
    />
  );
}

export function ConfigurableLongTermParam({
  name,
  type = "decimal",
  unit,
}: {
  name: keyof LongTermParams;
  type?: FormatType;
  unit?: string;
}) {
  return (
    <ConfigurablePathParam
      valueAtom={paramsAtom}
      defaultValueAtom={defaultParamsAtom}
      path={`longterm_params.${name}`}
      type={type}
      unit={unit}
    />
  );
}

export function ConfigurableLongTermRiskTypeParam({
  name,
  type = "decimal",
}: {
  name:
    | "catastrophe_extinction_risk_ratios"
    | "catastrophe_intensities"
    | "fractions_of_near_term_total_risk";
  type?: FormatType;
}) {
  const baseIntervention = useAtomValue(baseXRiskInterventionAtom);
  if (baseIntervention == undefined) {
    return <span>unknown, please select an intervention</span>;
  }
  const riskType = baseIntervention.risk_type;

  return (
    <ConfigurablePathParam
      valueAtom={paramsAtom}
      defaultValueAtom={defaultParamsAtom}
      path={`longterm_params.${name}`}
      keyName={riskType}
      type={type}
    />
  );
}

export function ConfigurableXRiskParam({
  name,
  type = "decimal",
  unit,
  displayOnTrue = "",
  displayOnFalse = "",
  literalOptions = [],
}: {
  name: keyof XRiskIntervention;
  type?: FormatType;
  unit?: string;
  displayOnTrue?: string;
  displayOnFalse?: string;
  literalOptions?: string[];
}) {
  return (
    <ConfigurablePathParam
      valueAtom={customXRiskInterventionAtom}
      defaultValueAtom={baseXRiskInterventionAtom}
      path={name}
      type={type}
      unit={unit}
      displayOnTrue={displayOnTrue}
      displayOnFalse={displayOnFalse}
      literalOptions={literalOptions}
    />
  );
}
