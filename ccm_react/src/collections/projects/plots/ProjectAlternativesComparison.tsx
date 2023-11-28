import { sort } from "d3";
import { useAtomValue } from "jotai";
import { projectAssessmentAtom } from "../../../stores/atoms";
import { AlternativesComparison } from "../../../components/plots/AlternativesComparison";

export const ProjectAlternativesComparison = () => {
  const projectAssessment = useAtomValue(projectAssessmentAtom);
  if (!projectAssessment) return null;

  return (
    <AlternativesComparison
      values={{
        samples: sort(projectAssessment.net_impact.samples),
        num_zeros: projectAssessment.net_impact.num_zeros,
      }}
    />
  );
};
