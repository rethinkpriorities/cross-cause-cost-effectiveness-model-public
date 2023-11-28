import { Button } from "@radix-ui/themes";
import { Era } from "../../../client";
import { useAtom, useAtomValue } from "jotai";
import { cloneDeep, isEqual, omit } from "lodash-es";
import { useState } from "react";
import { defaultParamsAtom, paramsAtom } from "../../../stores/atoms";
import { RiskEra } from "./RiskEra";
import { riskEraSets } from "./riskEraSets";
import { RiskEraDisplay } from "./RiskEraDisplay";

export function RiskErasLayout() {
  const [selectedEraIdx, setSelectedEraIdx] = useState<number | undefined>(0);
  const defaultParams = useAtomValue(defaultParamsAtom);
  const [allParams, setAllParams] = useAtom(paramsAtom);
  const baseRiskEras = defaultParams.longterm_params!.risk_eras!;
  let customRiskEras =
    allParams.longterm_params?.risk_eras ?? cloneDeep(baseRiskEras);
  // This always exists, as Parameters are initialized with default values.
  const maxCreditableYear = (allParams.longterm_params?.max_creditable_year ??
    defaultParams.longterm_params?.max_creditable_year)!;

  const addRiskEra = (index: number) => {
    const previousRiskEra = cloneDeep(
      customRiskEras[index - 1] ?? baseRiskEras[0],
    )!;
    const nextRiskEra =
      customRiskEras[index] ?? baseRiskEras[baseRiskEras.length - 1];

    customRiskEras.splice(index, 0, {
      length: 20 * 10 * index,
      annual_extinction_risk: 0.01,
      // Average two adjacent risk eras
      absolute_risks_by_type: Object.keys(
        previousRiskEra.absolute_risks_by_type!,
      ).reduce(
        (acc, t: string) => ({
          ...acc,
          [t]:
            ((previousRiskEra.absolute_risks_by_type?.[t] ?? 0) +
              (nextRiskEra.absolute_risks_by_type?.[t] ?? 0)) /
            2,
        }),
        {},
      ),
    });
    updateCustomRiskEras();
    setSelectedEraIdx(index);
  };

  const deleteRiskEra = (index: number) => {
    customRiskEras.splice(index, 1);
    updateCustomRiskEras();
  };

  const resetRiskEra = (index: number) => {
    customRiskEras[index] = cloneDeep(baseRiskEras[index]);
    updateCustomRiskEras();
  };

  const setRiskEras = (eraSet: Era[]) => {
    customRiskEras = cloneDeep(eraSet);
    updateCustomRiskEras();
  };

  const updateCustomRiskEras = () => {
    let newLongTermParams;
    if (isEqual(baseRiskEras, customRiskEras)) {
      newLongTermParams = omit(allParams.longterm_params, "risk_eras");
    } else {
      newLongTermParams = {
        ...allParams.longterm_params,
        risk_eras: customRiskEras,
      };
    }
    if (Object.keys(newLongTermParams).length != 0) {
      setAllParams({
        ...allParams,
        longterm_params: newLongTermParams,
      });
    } else {
      setAllParams(omit(allParams, "longterm_params"));
    }
  };

  let nextEraStart = 0;
  const relevantRiskEras = customRiskEras.filter((e) => {
    const isRelevant = nextEraStart < maxCreditableYear;
    nextEraStart += e.length;
    return isRelevant;
  });
  return (
    <>
      <summary>Risk eras</summary>
      <p>
        In this model, civilization will experience a series of &quot;risk
        eras&quot;. We face some fixed annual probability of extinction that
        lasts for the duration of a risk era. Then the next risk era brings a
        different probability of extinction, perhaps due to changing technology
        or international relations.
      </p>
      <RiskEraDisplay
        key={JSON.stringify(customRiskEras)}
        selectedEraIdx={selectedEraIdx}
        setSelectedEraIdx={setSelectedEraIdx}
        riskEras={relevantRiskEras}
        maxCreditableYear={maxCreditableYear}
        addRiskEra={addRiskEra}
      />
      {!isEqual(baseRiskEras, customRiskEras) && (
        <Button
          variant="soft"
          color="crimson"
          className="mr-4 min-h-10 cursor-pointer"
          key="reset-all-risk-eras"
          onClick={() => setRiskEras(baseRiskEras)}
        >
          Reset to default
        </Button>
      )}
      {riskEraSets.map((riskEraSet) => (
        <Button
          variant={isEqual(customRiskEras, riskEraSet.eras) ? "solid" : "soft"}
          color="blue"
          className="mr-2 min-h-10 cursor-pointer"
          key={`set-risk-eras-${riskEraSet.name}`}
          onClick={() => setRiskEras(riskEraSet.eras)}
        >
          {riskEraSet.name}
        </Button>
      ))}
      {typeof selectedEraIdx !== "undefined" &&
        customRiskEras[selectedEraIdx] && (
          <div key={"risk-era-parent"}>
            <RiskEra
              customRiskEra={customRiskEras[selectedEraIdx]}
              deleteRiskEra={deleteRiskEra}
              resetRiskEra={resetRiskEra}
              updateCustomRiskEras={updateCustomRiskEras}
              setSelectedRiskEraIdx={setSelectedEraIdx}
              riskEras={relevantRiskEras}
              i={selectedEraIdx}
            />
          </div>
        )}
    </>
  );
}
