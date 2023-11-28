import { useAtomValue } from "jotai";
import { baseProjectAtom, fullSelectedProjectAtom } from "../stores/atoms";

import { ResearchProjectModel } from "../client";

interface CustomizableResearchProjectModel extends ResearchProjectModel {
  isCustomized?: boolean;
}

// Returns project based on location and storage params, and makes sure they agree.
export const useProject = () => {
  const baseProject: CustomizableResearchProjectModel | undefined =
    useAtomValue(baseProjectAtom);
  const fullProject: CustomizableResearchProjectModel | undefined =
    useAtomValue(fullSelectedProjectAtom);
  if (baseProject) baseProject.isCustomized = false;
  if (fullProject) fullProject.isCustomized = true;

  const selectedProject = fullProject ?? baseProject;

  return selectedProject;
};
