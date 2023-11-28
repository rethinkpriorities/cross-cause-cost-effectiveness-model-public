import { match } from "ts-pattern";
import { ResultIntervention, XRiskIntervention } from "../client";
import { Intervention } from "./interventions";
import { ProjectGroupConcrete } from "./projectGroups";

// All possible values of Intervention.area
export type InterventionAreaLiteral = Exclude<ResultIntervention["area"], null>;

export function formatAreaOrGroup(
  area: InterventionAreaLiteral | ProjectGroupConcrete | "others",
) {
  return match(area)
    .returnType<string>()
    .with("ghd", () => "Global Health and Development")
    .with("animal-welfare", () => "Animal Welfare")
    .with("xrisk", () => "Existential Risk")
    .with("utility", () => "Utility")
    .with("others", () => "Miscellaneous")
    .otherwise(() => "Miscellaneous");
}

export function formatRiskType(risk_type: XRiskIntervention["risk_type"]) {
  return match(risk_type)
    .returnType<string>()
    .with("ai misuse", () => "AI misuse")
    .with("ai misalignment", () => "AI misalignment")
    .with("ai", () => "AI")
    .with("bio", () => "biological")
    .with("nano", () => "nanotechnology")
    .with("nukes", () => "nuclear")
    .with("natural", () => "natural disaster")
    .otherwise(() => "unknown");
}

const AREA_ORDER = [
  "ghd",
  "animal-welfare",
  "xrisk",
  "utility",
  "not-an-intervention",
  null,
  undefined,
];

interface InterventionArea {
  area: InterventionAreaLiteral;
  interventions: Intervention[];
}

interface FormattedInterventionArea {
  area: string;
  interventions: Intervention[];
}

export function groupInterventions(
  intervention: Intervention[],
): FormattedInterventionArea[] {
  let grouped: InterventionArea[] = [];
  intervention.forEach((intervention) => {
    const area = intervention.area;
    if (area) {
      const existing = grouped.find((group) => group.area === area);
      if (existing) {
        existing.interventions.push(intervention);
      } else {
        grouped.push({ area, interventions: [intervention] });
      }
    }
  });

  // Sort areas by AREA_ORDER
  grouped = grouped.sort((a, b) => {
    const aIndex = AREA_ORDER.indexOf(a.area);
    const bIndex = AREA_ORDER.indexOf(b.area);
    return aIndex - bIndex;
  });

  // Format area names
  return grouped.map((group) => ({
    ...group,
    area: formatAreaOrGroup(group.area),
  }));
}

export function groupInterventionsToObject(
  interventions: Intervention[],
): Record<string, Intervention[]> {
  const grouped = groupInterventions(interventions);
  const groupedObject: Record<string, Intervention[]> = {};
  grouped.forEach((group) => {
    groupedObject[group.area] = group.interventions;
  });
  return groupedObject;
}

export function groupInterventionNames(
  intervention: Intervention[],
): Record<string, string[]> {
  const grouped = groupInterventions(intervention);
  const groupedObject: Record<string, string[]> = {};
  grouped.forEach((group) => {
    groupedObject[group.area] = group.interventions.map(
      (intervention) => intervention.name,
    );
  });
  return groupedObject;
}
