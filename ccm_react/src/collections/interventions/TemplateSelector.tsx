import { Intervention } from "../../utils/interventions";

export const TemplateSelector = ({
  availableInterventions,
  intervention,
  setBaseIntervention,
  setCustomIntervention,
}: {
  availableInterventions: Intervention[];
  intervention: Intervention | undefined;
  setBaseIntervention: (value: Intervention | undefined) => void;
  setCustomIntervention: (value: Intervention | undefined) => void;
}) => {
  return (
    <>
      <p>Select an intervention preset:</p>
      <select
        className="mb-4 block w-full rounded select select-bordered"
        name="intervention-selector"
        onChange={(e) => {
          const newIntervention = availableInterventions.find(
            (intervention) => intervention.name == e.target.value,
          );
          setBaseIntervention(newIntervention);
          setCustomIntervention(newIntervention);
        }}
        value={intervention?.name}
      >
        <option value={undefined} />

        {availableInterventions.map((intervention) => (
          <option key={intervention.name} value={intervention.name}>
            {intervention.name}
          </option>
        ))}
      </select>
    </>
  );
};
