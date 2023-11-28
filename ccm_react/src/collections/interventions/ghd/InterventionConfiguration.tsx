import { ConfigurableGhdParam } from "../ConfigurableParam";

export const InterventionConfiguration = () => {
  return (
    <>
      <p>
        For interventions in global health and development we don&apos;t model
        impact internally, but instead stipulate the range of possible values.
        This intervention is assumed to cost{" "}
        <ConfigurableGhdParam name="cost_per_daly" type="currency" /> per DALY
        averted.
      </p>
    </>
  );
};
