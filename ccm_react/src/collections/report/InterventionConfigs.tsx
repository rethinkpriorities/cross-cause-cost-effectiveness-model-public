import {
  baseInterventionAtom,
  customInterventionAtom,
} from "../../stores/report";
import { FormatType } from "../../utils/formatting";
import { ConfigurablePathParam } from "../interventions/ConfigurableParam";

export function InterventionAttribute({
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
    valueAtom: customInterventionAtom,
    defaultValueAtom: baseInterventionAtom,
    path: path,
    type: type,
    unit: unit,
    displayOnTrue: displayOnTrue,
    displayOnFalse: displayOnFalse,
    literalOptions: literalOptions,
  });
}
