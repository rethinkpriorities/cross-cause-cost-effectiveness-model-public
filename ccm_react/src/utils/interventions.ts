import {
  AnimalIntervention,
  GhdIntervention,
  ResultIntervention,
  XRiskIntervention,
} from "../client";

export type Intervention =
  | ResultIntervention
  | AnimalIntervention
  | XRiskIntervention
  | GhdIntervention;
