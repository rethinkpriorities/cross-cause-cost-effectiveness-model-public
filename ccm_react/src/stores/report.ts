import { atom } from "jotai";
import { match } from "ts-pattern";
import { Intervention } from "../utils/interventions";
import { atomWithStoredHash } from "../utils/state";
import {
  baseAnimalInterventionAtom,
  baseGhdInterventionAtom,
  baseXRiskInterventionAtom,
  customAnimalInterventionAtom,
  customGhdInterventionAtom,
  customXRiskInterventionAtom,
} from "./atoms";
import {
  AnimalIntervention,
  GhdIntervention,
  XRiskIntervention,
} from "../client";
import { ProjectGroupConcrete } from "../utils/projectGroups";

export const baseInterventionAreaAtom = atomWithStoredHash<
  ProjectGroupConcrete | undefined
>("baseInterventionArea", undefined);

export const customInterventionAreaAtom = atomWithStoredHash<
  ProjectGroupConcrete | undefined
>("customInterventionArea", undefined);

export const baseInterventionAtom = atom(
  (get) => {
    const area = get(baseInterventionAreaAtom);
    return match(area)
      .with("ghd", () => get(baseGhdInterventionAtom))
      .with("animal-welfare", () => get(baseAnimalInterventionAtom))
      .with("xrisk", () => get(baseXRiskInterventionAtom))
      .otherwise(() => undefined);
  },
  (_, set, newIntervention: Intervention | undefined) => {
    const area = newIntervention?.area as ProjectGroupConcrete | undefined;
    set(baseInterventionAreaAtom, area);
    match(area)
      .with("ghd", () =>
        set(
          baseGhdInterventionAtom,
          newIntervention as GhdIntervention | undefined,
        ),
      )
      .with("animal-welfare", () =>
        set(
          baseAnimalInterventionAtom,
          newIntervention as AnimalIntervention | undefined,
        ),
      )
      .with("xrisk", () =>
        set(
          baseXRiskInterventionAtom,
          newIntervention as XRiskIntervention | undefined,
        ),
      );
  },
);

export const customInterventionAtom = atom(
  (get) => {
    const area = get(customInterventionAreaAtom);
    return match(area)
      .with("ghd", () => get(customGhdInterventionAtom))
      .with("animal-welfare", () => get(customAnimalInterventionAtom))
      .with("xrisk", () => get(customXRiskInterventionAtom))
      .otherwise(() => undefined);
  },
  (_, set, newIntervention: Intervention | undefined) => {
    const area = newIntervention?.area as ProjectGroupConcrete | undefined;
    set(customInterventionAreaAtom, area);
    match(area)
      .with("ghd", () =>
        set(
          customGhdInterventionAtom,
          newIntervention as GhdIntervention | undefined,
        ),
      )
      .with("animal-welfare", () =>
        set(
          customAnimalInterventionAtom,
          newIntervention as AnimalIntervention | undefined,
        ),
      )
      .with("xrisk", () =>
        set(
          customXRiskInterventionAtom,
          newIntervention as XRiskIntervention | undefined,
        ),
      );
  },
);

export const interventionAtom = atom<Intervention | undefined>((get) => {
  const base = get(baseInterventionAtom);
  const custom = get(customInterventionAtom);
  return custom ?? base;
});
