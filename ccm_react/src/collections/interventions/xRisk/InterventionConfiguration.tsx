import { useAtomValue } from "jotai";
import {
  baseXRiskInterventionAtom,
  customXRiskInterventionAtom,
  defaultParamsAtom,
  paramsAtom,
} from "../../../stores/atoms";
import { formatRiskType } from "../../../utils/interventionAreas";
import {
  ConfigurableLongTermParam,
  ConfigurableLongTermRiskTypeParam,
  ConfigurableXRiskParam,
} from "../ConfigurableParam";
import { RiskErasLayout } from "./RiskErasLayout";

export const InterventionConfiguration = () => {
  const customIntervention = useAtomValue(customXRiskInterventionAtom);

  const baseIntervention = useAtomValue(baseXRiskInterventionAtom);
  const isInterventionSelected = baseIntervention !== undefined;

  const intervention = (customIntervention ?? baseIntervention)!;

  const riskType = formatRiskType(intervention?.risk_type);

  const defaultParams = useAtomValue(defaultParamsAtom);
  const allParams = useAtomValue(paramsAtom);

  // This always exists, as Parameters are initialized with default values.
  const maxCreditableYear = (allParams.longterm_params?.max_creditable_year ??
    defaultParams.longterm_params?.max_creditable_year)!;

  return (
    <>
      {" "}
      <div className={isInterventionSelected ? "" : "display-none"}>
        <p>
          This models an intervention targeting {riskType} as an{" "}
          <a
            href="https://docs.google.com/document/d/1hCD3p1qbq9HY360N5Owjt691GmYH44uFY23rCqU2vmk"
            rel="noreferrer"
            target="_blank"
          >
            existential risk mitigation project
          </a>{" "}
          {intervention?.cost && (
            <>
              costing a total of{" "}
              <ConfigurableXRiskParam name="cost" type="currency" />{" "}
            </>
          )}{" "}
          that will change the probability of extinction for{" "}
          <ConfigurableXRiskParam name="persistence" /> years before being made
          obsolete. The intervention may fail: we assume a{" "}
          <ConfigurableXRiskParam name="prob_no_effect" type="percent" /> chance
          of having no effect. If it doesn&apos;t fail, it may also backfire: we
          assume it has a{" "}
          <ConfigurableXRiskParam name="prob_good" type="percent" /> chance of
          having a positive effect, conditional on having any effect.{" "}
        </p>
        <p>
          Assuming that the intervention does succeed, we expect that it reduces
          absolute existential risk by a factor{" "}
          <ConfigurableXRiskParam name="effect_on_xrisk" /> before it is
          rendered obsolete. If the intervention backfires, it will raise the
          probability of extinction by{" "}
          <ConfigurableXRiskParam name="intensity_bad" type="percent" /> of the
          counterfactual positive effect.
        </p>
        <p>
          In addition to reducing existential risk, the intervention will also
          reduce the probability of a non-existential catastrophic risk by{" "}
          <ConfigurableXRiskParam name="effect_on_catastrophic_risk" />.
          Whatever the probability of an extinction event, we estimate that a
          non-extinction catastrophe is{" "}
          <ConfigurableLongTermRiskTypeParam name="catastrophe_extinction_risk_ratios" />{" "}
          times more likely and would cause the deaths of{" "}
          <ConfigurableLongTermRiskTypeParam
            name="catastrophe_intensities"
            type="percent"
          />{" "}
          of the population.
        </p>
        <p>
          Of course, the future is unpredictable and far future scenarios may be
          too hypothetical to take seriously. In light of this, we don&apos;t
          consider future people after the year{" "}
          <ConfigurableLongTermParam
            name="max_creditable_year"
            type="preciseDecimal"
          />
          .
        </p>
        {maxCreditableYear >= 10_000 && (
          <p>
            If our descendents do survive thousands of years, then the number of
            future people spared by existential risk mitigation work depends on
            the future population and the amount of time our descendents would
            last until extinction, assuming the mitigation work does prevent
            extinction in the near-term. The total population depends on the
            rate at which we populate space. We assume that humanity will
            colonize all systems within a sphere that grows at a median speed of{" "}
            <ConfigurableLongTermParam name="expansion_speed" /> light years per
            year. Among colonized systems within this sphere, the average human
            population per star will be{" "}
            <ConfigurableLongTermParam name="stellar_population_capacity" />.
            The number of systems depends on the density of habitable systems.
            We assume that the galaxy has{" "}
            <ConfigurableLongTermParam name="galactic_density" /> stars per
            cubic light year
            {maxCreditableYear >= 1_000_000 && (
              <>
                {" "}
                and outside our galaxy, the galactic supercluster has{" "}
                <ConfigurableLongTermParam name="supercluster_density" /> stars
                per cubic light year
              </>
            )}
            .
          </p>
        )}
        <p>
          How long our descendents will last will depend on the risks we face in
          the future. We group these risks together into eras with a common risk
          profile.
        </p>
        {RiskErasLayout()}{" "}
      </div>
    </>
  );
};
