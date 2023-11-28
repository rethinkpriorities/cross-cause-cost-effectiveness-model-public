import { atom, Getter, Setter } from "jotai";
import { atomWithLocation } from "jotai-location";
import { atomsWithQuery } from "jotai-tanstack-query";
import {
  AnimalIntervention,
  DefaultService,
  GhdIntervention,
  Parameters,
  ResearchProjectAttributesModel,
  ResearchProjectModel,
  ResultIntervention,
  XRiskIntervention,
} from "../client";
import { Parameters as Parameters_V1 } from "../oldModels/V1/Parameters";
import { Animal } from "../client/models/Animal";
import { DistributionSpec } from "../utils/distributions";

import { updateParamsToLatestVersion } from "../utils/updaters/updaters";
/*
 * Generic atoms
 */

export interface AtomLocationType {
  pathname?: string | undefined;
  searchParams?: URLSearchParams | undefined;
}

export const locationAtom = atomWithLocation();

/*
 * Full lists of predefined project-relavant models
 */

import { ProjectGroupLiteral } from "../utils/projectGroups";
import { getQueryClient } from "../utils/query-client";

import { atomWithStoredHash } from "../utils/state";

export const projectGroupAtom = atom<ProjectGroupLiteral>("ghd");

export const [availableProjectsAtom] = atomsWithQuery(
  (get: Getter) => ({
    queryKey: ["availableProjects", get(projectGroupAtom)],
    queryFn: async ({ queryKey: [, group] }) => {
      return await DefaultService.getProjectsByGroup(
        group as ProjectGroupLiteral,
      );
    },
  }),
  getQueryClient,
);

availableProjectsAtom.debugLabel = "availableProjects";

export const [availableProjectsPerGroupAtom] = atomsWithQuery(
  (_get: Getter) => ({
    queryKey: ["availableProjectsPerGroup"],
    queryFn: async () => {
      return await DefaultService.getProjects();
    },
  }),
  getQueryClient,
);

availableProjectsPerGroupAtom.debugLabel = "availableProjectsPerGroup";

export const [availableInterventionsAtom] = atomsWithQuery(
  (_get) => ({
    queryKey: ["availableInterventions"],
    queryFn: async () => {
      return await DefaultService.getInterventions();
    },
  }),
  getQueryClient,
);

availableInterventionsAtom.debugLabel = "availableInterventions";

export const [availableAttributesAtom] = atomsWithQuery(
  (_get) => ({
    queryKey: ["availableAttributes"],
    queryFn: async () => {
      return await DefaultService.getProjectAttributes();
    },
  }),
  getQueryClient,
);

availableAttributesAtom.debugLabel = "availableAttributes";

export const [paramAttributesAtom] = atomsWithQuery(
  (_get) => ({
    queryKey: ["paramAttributes"],
    queryFn: async () => {
      return await DefaultService.getParameterAttributes();
    },
  }),
  getQueryClient,
);

paramAttributesAtom.debugLabel = "paramAttributes";

/*
 * Research Project customization settings
 */

type InterventionID = string;

// Intervention this project would cause money to be moved from.
export const customSourceInterventionAtom = atomWithStoredHash<
  InterventionID | ResultIntervention | undefined
>("sourceIntervention", undefined, { boundToPage: true });

// Intervention this project would cause money to be moved to.
export const customTargetInterventionAtom = atomWithStoredHash<
  InterventionID | ResultIntervention | undefined
>("targetIntervention", undefined, { boundToPage: true });

// Attribute overrides for the project
export const customAttributesAtom = atomWithStoredHash<
  Partial<ResearchProjectAttributesModel>
>("customAttributes", {}, { boundToPage: true });

export const setCustomAttributeAtom = atom(
  null,
  (
    get: Getter,
    set: Setter,
    name: string,
    value: DistributionSpec | undefined,
  ) => {
    const customAttributes = get(customAttributesAtom);
    if (value !== undefined) {
      // Set the attribute
      set(customAttributesAtom, {
        ...customAttributes,
        [name]: value,
      });
    } else {
      // Remove the attribute
      const { [name as keyof ResearchProjectAttributesModel]: _, ...rest } =
        customAttributes;
      set(customAttributesAtom, rest);
    }
  },
);

export const baseProjectIdAtom = atomWithStoredHash<string | undefined>(
  "baseProjectId",
  undefined,
  {
    boundToPage: true,
  },
);

export const baseGhdInterventionAtom = atomWithStoredHash<
  GhdIntervention | undefined
>("baseGhdIntervention", undefined);

export const customGhdInterventionAtom = atomWithStoredHash<
  GhdIntervention | undefined
>("customGhdIntervention", undefined);

export const baseAnimalInterventionAtom = atomWithStoredHash<
  AnimalIntervention | undefined
>("baseAnimalIntervention", undefined);

export const customAnimalInterventionAtom = atomWithStoredHash<
  AnimalIntervention | undefined
>("customAnimalIntervention", undefined);

export const baseXRiskInterventionAtom = atomWithStoredHash<
  XRiskIntervention | undefined
>("baseXRiskIntervention", undefined);

export const customXRiskInterventionAtom = atomWithStoredHash<
  XRiskIntervention | undefined
>("customXRiskIntervention", undefined);

export const interventionSpeciesAtom = atom<Animal | undefined>(
  (get: Getter) => {
    const intervention =
      get(customAnimalInterventionAtom) ?? get(baseAnimalInterventionAtom);
    return intervention?.animal;
  },
);

export class ProjectNotFoundError extends Error {
  id: string;

  constructor(id: string) {
    super(`Project ${id} not found`);
    this.id = id;
  }
}

export const baseProjectAtom = atom(async (get: Getter) => {
  const selectedId = get(baseProjectIdAtom);
  const projects = await Promise.resolve(get(availableProjectsAtom));
  if (selectedId) {
    const selectedProject = projects.find((p) => p.id === selectedId);
    if (!selectedProject) {
      throw new ProjectNotFoundError(selectedId);
    }
    return selectedProject;
  }
});

// This gives you all the attributes, including the modifications
export const combinedAttributesAtom = atom(async (get: Getter) => {
  const baseProject = await get(baseProjectAtom);
  const customAttributes = get(customAttributesAtom);

  if (baseProject) {
    return {
      ...baseProject.attributes,
      ...customAttributes,
    };
  }
  return undefined;
});

// This is the full, modified, project
export const fullSelectedProjectAtom = atom<
  Promise<ResearchProjectModel | undefined>
>(async (get: Getter) => {
  const baseProject = await get(baseProjectAtom);
  const selectedSourceIntervention = get(customSourceInterventionAtom);
  const selectedTargetIntervention = get(customTargetInterventionAtom);
  const customAttributes = get(customAttributesAtom);
  const combinedAttributes = await get(combinedAttributesAtom);

  if (!baseProject) {
    return undefined;
  }

  if (
    selectedSourceIntervention === undefined &&
    selectedTargetIntervention === undefined &&
    Object.keys(customAttributes).length === 0
  ) {
    return undefined;
  }

  const source = selectedSourceIntervention ?? baseProject.source_intervention;
  const target = selectedTargetIntervention ?? baseProject.target_intervention;

  // Override the source and target interventions by extending the ProjectAssessmentModel from the selected project
  return {
    ...baseProject,
    name: `${baseProject?.name} (modified)`,
    source_intervention: source,
    target_intervention: target,
    attributes: combinedAttributes,
  } as ResearchProjectModel;
});

export const [defaultParamsAtom] = atomsWithQuery(
  (_get: Getter) => ({
    queryKey: ["defaultParams"],
    queryFn: async () => {
      return await DefaultService.getDefaultParams();
    },
  }),
  getQueryClient,
);

defaultParamsAtom.debugLabel = "defaultParams";

export const paramsAtomStored = atomWithStoredHash<Parameters | Parameters_V1>(
  "params",
  {},
);

export const paramsAtom = atom<Parameters, [Parameters], void>(
  (get: Getter) => updateParamsToLatestVersion(get(paramsAtomStored)),
  (_get: Getter, set: Setter, newValue: Parameters) =>
    set(paramsAtomStored, newValue),
);

export const [projectAssessmentAtom] = atomsWithQuery(
  (get: Getter) => ({
    queryKey: [
      "projectAssessment",
      get(baseProjectIdAtom),
      get(paramsAtom),
      get(customSourceInterventionAtom),
      get(customTargetInterventionAtom),
      get(customAttributesAtom),
      get(fullSelectedProjectAtom),
    ],
    queryFn: async () => {
      const selectedId = get(baseProjectIdAtom);
      const parameters = get(paramsAtom);
      const project = await get(fullSelectedProjectAtom);

      if (selectedId) {
        if (project !== undefined) {
          // Use a custom project
          const res = await DefaultService.assessCustomProjectWithParams({
            project,
            parameters,
          });
          return res;
        }
        // Use a predefined project
        return await DefaultService.assessProjectWithParams(
          selectedId,
          parameters,
        );
      }
      return null;
    },
  }),
  getQueryClient,
);

projectAssessmentAtom.debugLabel = "projectAssessment";

export async function assessIntervention(
  intervention:
    | GhdIntervention
    | AnimalIntervention
    | XRiskIntervention
    | undefined,
  parameters: Parameters,
) {
  if (intervention == undefined) {
    return Promise.resolve(null);
  }
  const interventionSamples = await DefaultService.estimateInterventionDalys(
    intervention.name,
    {
      intervention: intervention,
      parameters: parameters,
    },
  );
  return interventionSamples;
}

export const [ghdInterventionAssessmentAtom] = atomsWithQuery((get: Getter) => {
  return {
    queryKey: [
      "ghdInterventionAssessment",
      get(customGhdInterventionAtom) ?? get(baseGhdInterventionAtom),
      get(paramsAtom),
    ],
    queryFn: async () => {
      return await assessIntervention(
        get(customGhdInterventionAtom) ?? get(baseGhdInterventionAtom),
        get(paramsAtom),
      );
    },
  };
}, getQueryClient);

ghdInterventionAssessmentAtom.debugLabel = "ghdInterventionAssessment";

export const [animalInterventionAssessmentAtom] = atomsWithQuery(
  (get: Getter) => {
    return {
      queryKey: [
        "animalInterventionAssessment",
        get(customAnimalInterventionAtom) ?? get(baseAnimalInterventionAtom),
        get(paramsAtom),
      ],
      queryFn: async () => {
        return await assessIntervention(
          get(customAnimalInterventionAtom) ?? get(baseAnimalInterventionAtom),
          get(paramsAtom),
        );
      },
    };
  },
  getQueryClient,
);

animalInterventionAssessmentAtom.debugLabel = "animalInterventionAssessment";

export const [xRiskInterventionAssessmentAtom] = atomsWithQuery(
  (get: Getter) => {
    return {
      queryKey: [
        "xRiskInterventionAssessment",
        get(customXRiskInterventionAtom) ?? get(baseXRiskInterventionAtom),
        get(paramsAtom),
      ],
      queryFn: async () => {
        return await assessIntervention(
          get(customXRiskInterventionAtom) ?? get(baseXRiskInterventionAtom),
          get(paramsAtom),
        );
      },
    };
  },
  getQueryClient,
);

xRiskInterventionAssessmentAtom.debugLabel = "xRiskInterventionAssessment";

// Dashboard
export const selectedDashboardTabAtom = atomWithStoredHash<
  "intervention" | "research"
>("selectedDashboardTab", "intervention");
