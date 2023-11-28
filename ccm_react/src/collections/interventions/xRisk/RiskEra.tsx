import { Era } from "../../../client";
import {
  TrashIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
} from "@radix-ui/react-icons";
import { useAtomValue } from "jotai";
import { defaultParamsAtom } from "../../../stores/atoms";
import { XRiskIntervention } from "../../../client";
import { ConfigurableParam } from "../ConfigurableParam";
import { RisksByType } from "./RisksByType";
import { ResultValue } from "../../../components/elements/ResultValue";
import { customInterventionAtom } from "../../../stores/report";
import { distributionBulk } from "../../../utils/distributions";
import {
  numberAsDecimalString,
  numberAsIntegerString,
} from "../../../utils/formatting";

export const RiskEra = ({
  customRiskEra,
  setSelectedRiskEraIdx,
  deleteRiskEra,
  updateCustomRiskEras,
  riskEras,
  i,
}: {
  customRiskEra: Era;
  setSelectedRiskEraIdx: (arg0: number) => void;
  deleteRiskEra: (arg0: number) => void;
  resetRiskEra: (arg0: number) => void;
  updateCustomRiskEras: () => void;
  riskEras: Era[];
  i: number;
}) => {
  const defaultParams = useAtomValue(defaultParamsAtom);
  const baseRiskEras = defaultParams.longterm_params!.risk_eras!;
  const baseRiskEra = i < baseRiskEras.length ? baseRiskEras[i] : undefined;
  const customIntervention = useAtomValue(
    customInterventionAtom,
  ) as XRiskIntervention;
  const totalRisk = Object.values(customRiskEra.absolute_risks_by_type!).reduce(
    (acc, x) => acc + x,
    0,
  );
  const startDate =
    riskEras.slice(0, i).reduce((acc, era) => acc + era.length, 0) + 2023;
  const endDate = startDate + customRiskEra.length;
  let expectedPersistence = 0;
  if (customIntervention?.persistence) {
    expectedPersistence =
      distributionBulk(customIntervention.persistence) ?? expectedPersistence;
  }
  return (
    <div key={"risk-era-" + (i + 1).toString()}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          {i > 0 && (
            <ChevronLeftIcon
              className="cursor-pointer"
              onClick={() => setSelectedRiskEraIdx(i - 1)}
            />
          )}
          <strong>Era {i + 1}</strong>
          {i < riskEras.length - 1 && (
            <ChevronRightIcon
              className="cursor-pointer"
              onClick={() => setSelectedRiskEraIdx(i + 1)}
            />
          )}
        </div>
        <div>
          <TrashIcon
            height="1.5em"
            width="1.5em"
            className="min-h-10 cursor-pointer"
            onClick={() => deleteRiskEra(i)}
          />
        </div>
      </div>
      Era {i + 1} will last for{" "}
      <ConfigurableParam
        customValue={customRiskEra.length}
        baseValue={
          baseRiskEra?.length ??
          customRiskEra.length /* if this risk era doesn't exist on the base, don't let the user reset it */
        }
        setValue={(value) => {
          customRiskEra.length = (value ?? baseRiskEra!.length) as number;
          updateCustomRiskEras();
        }}
        name="length"
      />{" "}
      years, from {numberAsIntegerString(startDate, { seperator: false })} to{" "}
      {numberAsIntegerString(endDate, { seperator: false })}, with a total
      annual extinction risk of about{" "}
      <ResultValue>{numberAsDecimalString(totalRisk * 100)}%</ResultValue>{" "}
      (which implies a per-century extinction risk of about{" "}
      <ResultValue>
        {numberAsDecimalString((1 - (1 - totalRisk) ** 100) * 100)}%
      </ResultValue>
      ). Overall risks are the sum of annual risks in the following categories.
      <RisksByType
        customRiskEra={customRiskEra}
        index={i}
        isWithinCatastropheRange={
          riskEras.reduce((acc, r, j) => (j < i ? acc + r.length : acc), 0) <
          expectedPersistence
        }
        updateCustomRiskEras={updateCustomRiskEras}
      />
    </div>
  );
};
