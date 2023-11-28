const typeDescriptions = {
  xrisk: "existential risk mitigation",
  "animal welfare": "improving animal welfare",
  ghd: "global health and development",
};

export const InterventionOverview = ({
  interventionType,
}: {
  interventionType: "xrisk" | "animal welfare" | "ghd";
}) => {
  return (
    <div className="mb-10">
      <p>
        This page presents results from a Monte Carlo model of the effectiveness
        of interventions focused on {typeDescriptions[interventionType]}. To
        estimate the effectiveness of these interventions, we sample values for
        parameters from input distributions and run them through our model to
        produce distributions of outputs. These results are our estimates of the
        effectiveness of the intervention in light of the the parameter choices.
      </p>
    </div>
  );
};
