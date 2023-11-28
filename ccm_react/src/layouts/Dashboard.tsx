import * as TabsPrimitive from "@radix-ui/react-tabs";
import { useAtom, useAtomValue, useSetAtom } from "jotai";
import { ProjectsPerGroup } from "../client";
import { InterventionBody } from "../collections/dashboard/intervention";
import { ProjectBody } from "../collections/dashboard/project";
import { TagGroup } from "../components/TagGroup";
import {
  availableInterventionsAtom,
  availableProjectsPerGroupAtom,
  baseProjectIdAtom,
  customAttributesAtom,
  customSourceInterventionAtom,
  selectedDashboardTabAtom,
} from "../stores/atoms";
import { baseInterventionAtom, customInterventionAtom } from "../stores/report";
import { useDarkModeBg } from "../utils/darkMode";
import {
  formatAreaOrGroup,
  groupInterventionsToObject,
} from "../utils/interventionAreas";
import { Intervention } from "../utils/interventions";

const Tab = TabsPrimitive.Root;
const TabList = TabsPrimitive.List;
const TabTrigger = TabsPrimitive.Trigger;
const TabContent = TabsPrimitive.Content;

const Header = () => (
  <header className="mb-8 max-w-2xl">
    <h1 className="mb-4 text-6xl font-bold">
      Cross-Cause Cost-Effectiveness Model
    </h1>
    <p className="mb-2">
      The CCM is a tool by Rethink Priorities that helps assess the
      cost-effectiveness of interventions and research projects by interacting
      with ready-made mathematical models with flexible assumptions.{" "}
      <a
        href="https://forum.effectivealtruism.org/posts/pniDWyjc9vY5sjGre/rethink-priorities-cross-cause-cost-effectiveness-model"
        className="font-semibold text-current-color underline"
      >
        Read more.
      </a>
    </p>
  </header>
);

const DashboardLayout = () => {
  const [selectedTab, setSelectedTab] = useAtom(selectedDashboardTabAtom);

  const setSelectedTabGeneric = (tab: string) => {
    if (tab !== "intervention" && tab !== "research") {
      throw new Error(`Invalid tab: ${tab}`);
    }
    setSelectedTab(tab);
  };

  // Fetch interventions and group them for the tags
  const availableInterventions = useAtomValue(availableInterventionsAtom);
  const interventionsByArea: Record<string, Intervention[]> =
    groupInterventionsToObject(availableInterventions);

  // Currently selected intervention
  const [baseIntervention, setBaseIntervention] = useAtom(baseInterventionAtom);
  const setCustomIntervention = useSetAtom(customInterventionAtom);

  // Fetch research projects (no grouping is needed)
  const availableProjectsByGroup = useAtomValue(availableProjectsPerGroupAtom);

  // Currently selected research project
  const [baseProjectId, setBaseProjectId] = useAtom(baseProjectIdAtom);
  const setSourceIntervention = useSetAtom(customSourceInterventionAtom);
  const setTargetIntervention = useSetAtom(customInterventionAtom);
  const setCustomAttributes = useSetAtom(customAttributesAtom);

  // Current tag (depending on the selected tab)
  const selectedTag = (
    selectedTab === "intervention" ? baseIntervention?.name : baseProjectId
  ) as string | null;

  // Sets the body bg color if needed
  useDarkModeBg();

  const handleTagClick = (tagId: string) => {
    if (selectedTab === "intervention") {
      // Find the intervention with the given name
      const newIntervention = availableInterventions.find(
        (intervention) => intervention.name === tagId,
      );
      // Set the base and custom interventions to the new intervention
      setBaseIntervention(newIntervention);
      setCustomIntervention(newIntervention);
    } else {
      setBaseProjectId(tagId);
      // Reset customized interventions and attributes for the project
      setSourceIntervention(undefined);
      setTargetIntervention(undefined);
      setCustomAttributes({});
    }
  };

  return (
    <div className="bg-dashboard-light px-20 pb-6 pt-10 text-gray-900 dark:bg-dashboard-dark dark:text-gray-200">
      <Header />
      <main>
        <Tab
          defaultValue="intervention"
          className="flex flex-col"
          onValueChange={setSelectedTabGeneric}
          value={selectedTab}
        >
          <TabList className="mb-4 text-xl font-semibold">
            <TabTrigger
              value="intervention"
              className={`px-6 py-3 focus:outline-none ${
                selectedTab === "intervention"
                  ? "border-b-2 dark:border-white "
                  : "border-b-2 border-transparent"
              } dark:text-white`}
            >
              Direct Intervention
            </TabTrigger>
            <TabTrigger
              value="research"
              className={`px-6 py-3 focus:outline-none ${
                selectedTab === "research"
                  ? "border-b-2 dark:border-white"
                  : "border-b-2 border-transparent"
              } dark:text-white`}
            >
              Research Project
            </TabTrigger>
          </TabList>
          <TabContent value="intervention" className="p-4">
            <div className="grid grid-cols-1 gap-4 2xl:grid-cols-4 lg:grid-cols-3 sm:grid-cols-2">
              {Object.entries(interventionsByArea).map(
                ([area, interventions]) =>
                  [
                    "Global Health and Development",
                    "Animal Welfare",
                    "Existential Risk",
                  ].includes(area) ? (
                    <TagGroup
                      key={`${area}-interventions`}
                      title={area}
                      tags={interventions.map((intervention) => ({
                        name: intervention.name,
                        id: intervention.name,
                      }))}
                      selectedTagId={selectedTag}
                      onTagClick={handleTagClick}
                      inTwoLines={false}
                    />
                  ) : undefined,
              )}
            </div>
            {selectedTag !== undefined && <InterventionBody />}
          </TabContent>
          <TabContent value="research" className="p-4">
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3 sm:grid-cols-2">
              {Object.entries(availableProjectsByGroup).map(
                ([area, projects]) => (
                  <TagGroup
                    key={`${area}-projects`}
                    title={formatAreaOrGroup(area as keyof ProjectsPerGroup)}
                    tags={projects.map((project) => ({
                      name: project.name,
                      id: project.id,
                    }))}
                    selectedTagId={selectedTag}
                    onTagClick={handleTagClick}
                    inTwoLines={true}
                  />
                ),
              )}
            </div>
            {selectedTag !== undefined && <ProjectBody />}
          </TabContent>
        </Tab>
      </main>
    </div>
  );
};

export default DashboardLayout;
