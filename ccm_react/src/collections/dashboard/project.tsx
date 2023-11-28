import { Callout, Flex } from "@radix-ui/themes";
import { useAtom, useAtomValue, useSetAtom } from "jotai";
import { isEqual } from "lodash-es";
import { Suspense } from "react";
import { useProject } from "../../hooks/useProject";
import { Section } from "../../components/wrappers/Section";
import {
  availableInterventionsAtom,
  baseProjectAtom,
  baseProjectIdAtom,
  customAttributesAtom,
  customSourceInterventionAtom,
  customTargetInterventionAtom,
  projectGroupAtom,
} from "../../stores/atoms";
import { LoadingFallback } from "../../components/support/LoadingFallback";
import { ConfigurableAttribute } from "../projects/ConfigurableAttribute";
import { ResultSummary } from "../projects/ResultSummary";
import { DALYsPer1000 } from "../projects/plots/DALYsPer1000";
import { NetImpact } from "../projects/plots/NetImpact";
import { Endnotes } from "../../components/Endnotes";
import { ConfigurableIntervention } from "../../components/ConfigurableIntervention";

export function ProjectBody() {
  return (
    <div>
      <ProjectModified />
      <Section title="Selected Research Project">
        <ProjectDescription />
      </Section>
      <Section title="Simulation Results">
        <ProjectAssessment />
      </Section>
      <Endnotes />
    </div>
  );
}

export function ProjectModified() {
  const selectedProject = useProject();
  const setSourceIntervention = useSetAtom(customSourceInterventionAtom);
  const setTargetIntervention = useSetAtom(customTargetInterventionAtom);
  const setCustomAttributes = useSetAtom(customAttributesAtom);

  return (
    <div>
      {selectedProject && selectedProject.isCustomized && (
        <Section title="Note">
          <Flex align="center">
            <Callout.Text>
              You&apos;ve modified the attributes for this project. The project
              assesment now reflects your changes.
            </Callout.Text>
            <button
              onClick={() => {
                setSourceIntervention(undefined);
                setTargetIntervention(undefined);
                setCustomAttributes({});
              }}
              className="ml-2 rounded-md bg-red-500 px-2 py-1 text-white dark:bg-red-600 hover:bg-red-600 dark:text-white dark:hover:bg-red-500"
            >
              Reset to default project
            </button>
          </Flex>
        </Section>
      )}
    </div>
  );
}

export function ProjectDescription() {
  const [existingProjectGroup, setProjectGroup] = useAtom(projectGroupAtom);
  if ("all" !== existingProjectGroup) setProjectGroup("all");

  const selectedProject = useProject();
  const baseProject = useAtomValue(baseProjectAtom);

  const availableInterventions = useAtomValue(availableInterventionsAtom);

  const [sourceIntervention, setSourceIntervention] = useAtom(
    customSourceInterventionAtom,
  );
  const [targetIntervention, setTargetIntervention] = useAtom(
    customTargetInterventionAtom,
  );

  if (baseProject === undefined || selectedProject === undefined) {
    return null;
  }

  return (
    <div>
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

export function ProjectAssessment() {
  const project = useAtomValue(baseProjectIdAtom);
  if (!project) return null;

  return (
    <div>
      <Suspense fallback={<LoadingFallback />}>
        <ResultSummary />
        <DALYsPer1000 />
        <NetImpact />
      </Suspense>
    </div>
  );
}
