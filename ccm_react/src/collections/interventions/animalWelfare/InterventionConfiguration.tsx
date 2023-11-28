import { useAtomValue } from "jotai";
import { Animal } from "../../../client";
import {
  baseAnimalInterventionAtom,
  customAnimalInterventionAtom,
} from "../../../stores/atoms";
import { useMoralWeightParams } from "../../../hooks/useMoralWeightParams";
import {
  ConfigurableAnimalParam,
  ConfigurableMoralWeightParam,
  ConfigurableSpeciesSpecificParam,
} from "../ConfigurableParam";
import { useNumAnimalsBornPerYear } from "../../../hooks/useNumAnimalsBornPerYear";
import { numberAsIntegerString } from "../../../utils/formatting";
import { ResultValue } from "../../../components/elements/ResultValue";

type numberRange = [number, number];

const speciesPluralForms: { [species in Animal | "unknown"]: string } = {
  human: "humans",
  chicken: "chickens",
  carp: "carp",
  bsf: "black soldier flies",
  shrimp: "shrimp",
  unknown: "unknown",
};

const speciesSingularForms: { [species in Animal | "unknown"]: string } = {
  human: "human",
  chicken: "chicken",
  carp: "carp",
  bsf: "black soldier fly",
  shrimp: "shrimp",
  unknown: "unknown",
};

export const InterventionConfiguration = () => {
  const customIntervention = useAtomValue(customAnimalInterventionAtom);

  const baseIntervention = useAtomValue(baseAnimalInterventionAtom);
  const intervention = customIntervention ?? baseIntervention;
  const isInterventionSelected = baseIntervention !== undefined;

  const useOverride = intervention?.use_override;

  const species = intervention?.animal ?? "unknown";
  const speciesPlural = speciesPluralForms[species] ?? species;
  const speciesSingle = speciesSingularForms[species] ?? species;
  const moralWeightParams = useMoralWeightParams();
  let welfareRange;
  if (moralWeightParams.welfare_capacities_override) {
    const welfareOverride =
      moralWeightParams.welfare_capacities_override[species];
    if ("range" in welfareOverride) {
      welfareRange = welfareOverride.range as numberRange;
    }
  }

  const numAnimalsBornPerYear = useNumAnimalsBornPerYear(species);
  let hoursSpentSufferingRange;
  let animalsBornPerYearRange;
  let proportionAffectedRange;
  if (intervention) {
    if ("range" in intervention.hours_spent_suffering!) {
      hoursSpentSufferingRange = intervention.hours_spent_suffering
        .range as numberRange;
    }
    if ("range" in intervention.prop_affected!) {
      proportionAffectedRange = intervention.prop_affected.range as numberRange;
    }
  }
  if (numAnimalsBornPerYear) {
    if ("range" in numAnimalsBornPerYear) {
      animalsBornPerYearRange = numAnimalsBornPerYear.range as numberRange;
    }
  }

  return (
    <div style={{ display: isInterventionSelected ? "inline" : "none" }}>
      <p>
        This evaulates a {speciesSingle} intervention as an{" "}
        <a
          href="https://docs.google.com/document/d/1M60ShtBBQEdoTWcGlVtRWSrredP9cZQxSzJXdbAztHI"
          rel="noreferrer"
          target="_blank"
        >
          animal welfare intervention
        </a>{" "}
        using{" "}
        <ConfigurableAnimalParam
          name="use_override"
          displayOnFalse="a model of the suffering reduction within the target population."
          displayOnTrue="an estimation of suffering-years per dollar."
        />{" "}
      </p>
      {useOverride && (
        <p>
          The intervention is assumed to produce{" "}
          <ConfigurableAnimalParam name="suffering_years_per_dollar_override" />{" "}
          suffering-years per dollar (unweighted) condition on {speciesPlural}{" "}
          being sentient.
        </p>
      )}
      {!useOverride && (
        <>
          <p>
            The intervention targets a population of {speciesPlural} containing{" "}
            <ConfigurableSpeciesSpecificParam name="num_animals_born_per_year" />{" "}
            new individuals born every year. The intervention addresses a form
            of suffering which lasts for{" "}
            <ConfigurableAnimalParam
              name="hours_spent_suffering"
              type="unit"
              unit="hour"
            />
            {hoursSpentSufferingRange && hoursSpentSufferingRange[0] > 24 && (
              <ResultValue>
                {" "}
                ({numberAsIntegerString(hoursSpentSufferingRange[0] / 24)}-
                {numberAsIntegerString(hoursSpentSufferingRange[1] / 24)} days)
              </ResultValue>
            )}
            {hoursSpentSufferingRange && hoursSpentSufferingRange[0] < 1 && (
              <ResultValue>
                {" "}
                ({numberAsIntegerString(hoursSpentSufferingRange[0] * 60)}-
                {numberAsIntegerString(hoursSpentSufferingRange[1] * 60)}{" "}
                minutes)
              </ResultValue>
            )}{" "}
            of each affected {speciesSingle}&#39;s life. (Since interventions
            may address multiple sources of suffering, we aggregate suffering
            time and weight it by severity. Three days of suffering represented
            here is the equivalent of three days of such suffering as to render
            life not worth living. It might really stand in for twenty days of
            moderate suffering.) This intervention will reduce suffering by{" "}
            <ConfigurableAnimalParam
              name="prop_suffering_reduced"
              type="percent"
            />{" "}
            for individuals constituting{" "}
            <ConfigurableAnimalParam name="prop_affected" type="percent" />
            {animalsBornPerYearRange && proportionAffectedRange && (
              <ResultValue>
                {" "}
                (
                {numberAsIntegerString(
                  animalsBornPerYearRange[0] * proportionAffectedRange[0],
                )}
                -
                {numberAsIntegerString(
                  animalsBornPerYearRange[1] * proportionAffectedRange[1],
                )}{" "}
                individuals){" "}
              </ResultValue>
            )}
            of the targeted population, if it is successful.{" "}
          </p>
          <p>
            The intervention costs{" "}
            <ConfigurableAnimalParam
              type="currency"
              name="cost_of_intervention"
            />{" "}
            and has a probability of success{" "}
            <ConfigurableAnimalParam name="prob_success" type="percent" />. If
            it is unsuccessful it will have no effect at all. If it is
            successful, its impacts will continue to be felt for{" "}
            <ConfigurableAnimalParam
              name="persistence"
              type="unit"
              unit="year"
            />{" "}
            before it is rendered obsolete or otherwise ineffectual.
          </p>
        </>
      )}
      {species !== "unknown" && (
        <p>
          The probability of sentience in {speciesPlural} is assumed to be{" "}
          <ConfigurableMoralWeightParam name="sentience_ranges" />. It is
          assumed that {speciesPlural} have a capacity for welfare of{" "}
          <ConfigurableMoralWeightParam name="welfare_capacities_override" />{" "}
          times the capacity in humans
          {welfareRange && (
            <>
              , meaning that, conditional on sentience, an episode of suffering
              lasting 1 hour in humans counts for as much as an equivalently
              intense episode in {speciesPlural} lasting between{" "}
              <ResultValue>
                {60 / welfareRange[1] < 119
                  ? `${(60 / welfareRange[1]).toFixed(1)} minutes `
                  : `${numberAsIntegerString(1 / welfareRange[1], {
                      precision: 1,
                    })} hours `}
              </ResultValue>
              and{" "}
              <ResultValue>
                {60 / welfareRange[0] < 119
                  ? `${(60 / welfareRange[0]).toFixed(1)} minutes`
                  : `${numberAsIntegerString(1 / welfareRange[0], {
                      precision: 1,
                    })} hours`}
              </ResultValue>
            </>
          )}
          .
        </p>
      )}
    </div>
  );
};
