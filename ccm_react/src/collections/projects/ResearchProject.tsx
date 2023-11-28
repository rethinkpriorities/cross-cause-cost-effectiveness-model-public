import { Button, Callout, Flex } from "@radix-ui/themes";
import { useAtom, useAtomValue, useSetAtom } from "jotai";
import { isEqual } from "lodash-es";
import { Suspense } from "react";
import { ProjectsPerGroup } from "../../client";
import { useProject } from "../../hooks/useProject";
import {
  availableInterventionsAtom,
  availableProjectsAtom,
  availableProjectsPerGroupAtom,
  baseProjectAtom,
  baseProjectIdAtom,
  customAttributesAtom,
  customSourceInterventionAtom,
  customTargetInterventionAtom,
  projectGroupAtom,
} from "../../stores/atoms";
import { formatAreaOrGroup } from "../../utils/interventionAreas";
import { ProjectGroupLiteral } from "../../utils/projectGroups";
import { ErrorBoundary } from "../../components/support/ErrorHandling";
import { LoadingFallback } from "../../components/support/LoadingFallback";
import { ConfigurableIntervention } from "../../components/ConfigurableIntervention";
import { ConfigurableAttribute } from "./ConfigurableAttribute";
import { ProjectAssessment } from "./ProjectAssessment";

export function ResearchProject({
  group: group,
}: {
  group: ProjectGroupLiteral;
}) {
  return (
    <section>
      <h2>Introduction</h2>
      <p>
        This tool allows you to assess the impact of a research project based on
        predefined templates you can tweak.
      </p>
      <h2 id="atoms">Research Project Assessment</h2>
      <ResearchProjectInteractive group={group} />
    </section>
  );
}

export function ResearchProjectInteractive({
  group: group,
}: {
  group: ProjectGroupLiteral;
}) {
  return (
    <div>
      <ErrorBoundary>
        <Suspense fallback={<LoadingFallback />}>
          <SelectResearchProject group={group} />
        </Suspense>
      </ErrorBoundary>
      <ErrorBoundary>
        <Suspense fallback={<LoadingFallback />}>
          <ProjectDescription group={group} />
        </Suspense>
      </ErrorBoundary>
      <ErrorBoundary>
        <Suspense fallback={<LoadingFallback />}>
          <ProjectAssessment />
        </Suspense>
      </ErrorBoundary>
    </div>
  );
}
export function ProjectDescription({
  group: group,
}: {
  group: ProjectGroupLiteral;
}) {
  const [existingProjectGroup, setProjectGroup] = useAtom(projectGroupAtom);
  if (group !== existingProjectGroup) setProjectGroup(group);

  const selectedProject = useProject();
  const baseProject = useAtomValue(baseProjectAtom);

  const availableInterventions = useAtomValue(
    availableInterventionsAtom,
  ).filter((intervention) => {
    if (group === "all") return true;
    return intervention.area && [group, "utility"].includes(intervention.area);
  });

  const [sourceIntervention, setSourceIntervention] = useAtom(
    customSourceInterventionAtom,
  );
  const [targetIntervention, setTargetIntervention] = useAtom(
    customTargetInterventionAtom,
  );

  const setCustomAttributes = useSetAtom(customAttributesAtom);

  if (baseProject === undefined || selectedProject === undefined) {
    return null;
  }

  return (
    <div>
      <h3>{selectedProject.name}</h3>
      {selectedProject.isCustomized && (
        <Callout.Root>
          <Flex align="center">
            <Callout.Text>
              You&apos;ve modified the attributes for this project. The project
              assesment now reflects your changes.
            </Callout.Text>
            <Button
              variant="soft"
              color="crimson"
              className="min-h-10 cursor-pointer"
              onClick={() => {
                setSourceIntervention(undefined);
                setTargetIntervention(undefined);
                setCustomAttributes({});
              }}
            >
              Reset to default project
            </Button>
          </Flex>
        </Callout.Root>
      )}
      <p>
        This project simulates a research project that potentially results in
        moving money from{" "}
        <ConfigurableIntervention
          type="source"
          intervention={sourceIntervention}
          baseIntervention={baseProject.source_intervention}
          setIntervention={setSourceIntervention}
          availableInterventions={availableInterventions}
          isModified={
            sourceIntervention !== undefined &&
            !isEqual(sourceIntervention, baseProject.source_intervention)
          }
        />{" "}
        to{" "}
        <ConfigurableIntervention
          type="target"
          intervention={targetIntervention}
          baseIntervention={baseProject.target_intervention}
          setIntervention={setTargetIntervention}
          availableInterventions={availableInterventions}
          isModified={
            targetIntervention !== undefined &&
            !isEqual(targetIntervention, baseProject.target_intervention)
          }
        />
        . The project has a chance of{" "}
        <ConfigurableAttribute
          name="conclusions_require_updating"
          type="percent"
        />{" "}
        of finding the new target intervention. If the intervention is
        discovered, then the project only takes{" "}
        <ConfigurableAttribute name="years_credit" type="unit" unit="year" /> of
        credit for the results, considering that it would have been discovered
        eventually anyway.
      </p>
      <p>
        This project is based on the assumption that the cause area has{" "}
        <ConfigurableAttribute name="money_in_area_millions" /> million dollars
        in funding available for interventions, of which{" "}
        <ConfigurableAttribute
          name="percent_money_influenceable"
          type="percent"
        />{" "}
        could potentially be retargeted to the new intervention if the funder is
        swayed by the result, which happens{" "}
        <ConfigurableAttribute name="target_updating" type="percent" /> of the
        time.{" "}
      </p>
      <p>
        Whether succesful or not, this research project would spend{" "}
        <ConfigurableAttribute name="fte_years" /> Full Time Equivalent (FTE)
        years of work on the research project, with every FTE year costing{" "}
        <ConfigurableAttribute name="cost_per_staff_year" type="currency" /> .{" "}
      </p>
    </div>
  );
}

export function SelectResearchProject({
  group: group,
}: {
  group: ProjectGroupLiteral;
}) {
  if (group === "all") return <SelectResearchProjectAllGroups />;
  return <SelectResearchProjectInGroup group={group} />;
}

export function SelectResearchProjectInGroup({
  group: group,
}: {
  group: ProjectGroupLiteral;
}) {
  const [existingProjectGroup, setProjectGroup] = useAtom(projectGroupAtom);
  if (group !== existingProjectGroup) setProjectGroup(group);

  const selectedProject = useAtomValue(baseProjectIdAtom);
  const setBaseResearchProject = useSetAtom(baseProjectIdAtom);
  const setSourceIntervention = useSetAtom(customSourceInterventionAtom);
  const setTargetIntervention = useSetAtom(customTargetInterventionAtom);
  const setCustomAttributes = useSetAtom(customAttributesAtom);

  const availableResearchProjects = useAtomValue(availableProjectsAtom);

  return (
    <select
      className="mb-4 block w-full rounded select select-bordered"
      name="research-project"
      onChange={(e) => {
        setBaseResearchProject(
          e.target.value === "" ? undefined : e.target.value,
        );
        setSourceIntervention(undefined);
        setTargetIntervention(undefined);
        setCustomAttributes({});
      }}
      value={selectedProject}
    >
      <option value="">Select a research project</option>

      {availableResearchProjects.map((researchProject) => (
        <option key={researchProject.id} value={researchProject.id}>
          {researchProject.name}
        </option>
      ))}
    </select>
  );
}

export function SelectResearchProjectAllGroups() {
  const selectedProject = useAtomValue(baseProjectIdAtom);
  const setBaseResearchProject = useSetAtom(baseProjectIdAtom);
  const setSourceIntervention = useSetAtom(customSourceInterventionAtom);
  const setTargetIntervention = useSetAtom(customTargetInterventionAtom);
  const setCustomAttributes = useSetAtom(customAttributesAtom);

  const projectsByGroup = useAtomValue(availableProjectsPerGroupAtom);

  return (
    <select
      className="mb-4 block w-full rounded select select-bordered"
      name="research-project"
      onChange={(e) => {
        setBaseResearchProject(
          e.target.value === "" ? undefined : e.target.value,
        );
        setSourceIntervention(undefined);
        setTargetIntervention(undefined);
        setCustomAttributes({});
      }}
      value={selectedProject}
    >
      <option value="">Select a research project</option>

      {Object.entries(projectsByGroup).map(([group, projects]) => (
        <optgroup
          key={group}
          label={formatAreaOrGroup(group as keyof ProjectsPerGroup)}
        >
          {projects.map((researchProject) => (
            <option key={researchProject.id} value={researchProject.id}>
              {researchProject.name}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  );
}
