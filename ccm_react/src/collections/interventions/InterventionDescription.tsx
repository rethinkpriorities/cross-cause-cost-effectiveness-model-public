import { useAtomValue } from "jotai";
import { interventionAtom } from "../../stores/report";
import Markdown from "../../components/Markdown";

export const InterventionDescription = () => {
  const intervention = useAtomValue(interventionAtom);

  if (intervention === undefined) {
    return <></>;
  }

  return <Markdown>{intervention.description}</Markdown>;
};
