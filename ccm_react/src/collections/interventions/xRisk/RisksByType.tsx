import { useAtomValue } from "jotai";
import { Era } from "../../../client";
import { ConfigurableParam } from "../ConfigurableParam";
import { ResultValue } from "../../../components/elements/ResultValue";
import { getFormat } from "../../../utils/formatting";
import { ConfigurableLongTermRiskTypeParam } from "../ConfigurableParam";
import { RiskTypeAI } from "../../../client/models/RiskTypeAI";
import { RiskTypeGLT } from "../../../client/models/RiskTypeGLT";

type RiskType = RiskTypeAI | RiskTypeGLT;

import {
  baseXRiskInterventionAtom,
  defaultParamsAtom,
  paramsAtom,
} from "../../../stores/atoms";

const PRETTY_RISK_NAMES: Record<RiskType, string> = {
  ai: "AI",
  "ai misalignment": "AI Misalignment",
  "ai misuse": "AI Misuse",
  nukes: "Nuclear War",
  bio: "Biological Risks",
  nano: "Runaway Nanotechnology",
  natural: "Natural Disasters",
  unknown: "Uncategorized",
};

export const RisksByType = ({
  updateCustomRiskEras,
  customRiskEra,
  isWithinCatastropheRange,
  index,
}: {
  updateCustomRiskEras: () => void;
  customRiskEra: Era;
  isWithinCatastropheRange: boolean;
  index: number;
}) => {
  const defaultParams = useAtomValue(defaultParamsAtom);
  const allParams = useAtomValue(paramsAtom);
  const baseIntervention = useAtomValue(baseXRiskInterventionAtom);
  const baseRiskEras = defaultParams.longterm_params!.risk_eras!;
  const baseRisksByType =
    index < baseRiskEras.length
      ? baseRiskEras[index].absolute_risks_by_type
      : undefined;
  const customRisksByType = customRiskEra.absolute_risks_by_type!;
  const catastropheRatios = (allParams?.longterm_params
    ?.catastrophe_extinction_risk_ratios ??
    defaultParams?.longterm_params?.catastrophe_extinction_risk_ratios)!;

  return (
    <table className="col-2-r col-3-r">
      <thead>
        <tr>
          <th>Category</th>
          {isWithinCatastropheRange && <th />}
          <th>Yearly Probability</th>
        </tr>
        <tr>
          <th />
          <th>Extinction</th>
          {isWithinCatastropheRange && (
            <>
              <th className="hidden lg:table-cell" />
              <th className="hidden lg:table-cell">Catastrophe</th>
            </>
          )}
        </tr>
      </thead>
      <tbody>
        {(Object.keys(customRisksByType) as RiskType[]).map((k: RiskType) => {
          return (
            <tr
              key={"tr-risk-era-" + (index + 1).toString() + "-" + k}
              className={
                k === baseIntervention?.risk_type
                  ? "bg-slate-200 dark:bg-slate-500"
                  : ""
              }
            >
              <td>{PRETTY_RISK_NAMES[k]}</td>
              <td>
                <ConfigurableParam
                  customValue={customRisksByType[k]}
                  baseValue={
                    baseRisksByType?.[k] ??
                    customRisksByType[
                      k
                    ] /* if this risk era doesn't exist on the base, don't let the user reset it */
                  }
                  setValue={(value) => {
                    customRisksByType[k] = (value ??
                      baseRisksByType![k]) as number;
                    updateCustomRiskEras();
                  }}
                  name={"risk-era-" + (index + 1).toString() + "-" + k}
                  type="percent"
                />
              </td>
              {isWithinCatastropheRange && (
                <>
                  <td className="hidden lg:table-cell">
                    {k === baseIntervention?.risk_type && (
                      <>
                        x
                        <ConfigurableLongTermRiskTypeParam name="catastrophe_extinction_risk_ratios" />
                      </>
                    )}
                  </td>
                  <td className="hidden lg:table-cell">
                    {k === baseIntervention?.risk_type && (
                      <ResultValue>
                        {getFormat("percent").format(
                          catastropheRatios?.[k] * customRisksByType?.[k],
                        )}
                      </ResultValue>
                    )}
                  </td>
                </>
              )}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};
