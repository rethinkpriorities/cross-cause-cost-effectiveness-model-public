import { interpolateReds, scaleSequential } from "d3";
import { Era } from "../../../client";
import { numberAsIntegerString } from "../../../utils/formatting";

const colorScale = scaleSequential()
  .domain([0, 5])
  .interpolator(interpolateReds);

interface RiskEraDisplayProps {
  riskEras: Era[];
  selectedEraIdx: number | undefined;
  setSelectedEraIdx: (arg0: number | undefined) => void;
  addRiskEra: (arg0: number) => void;
  maxCreditableYear: number;
}

export const RiskEraDisplay = ({
  riskEras,
  selectedEraIdx,
  setSelectedEraIdx,
  addRiskEra,
  maxCreditableYear,
}: RiskEraDisplayProps) => {
  const maxYear = maxCreditableYear;
  const markedPoints = [];
  for (let i = 1; i <= Math.log10(maxYear); i++) {
    markedPoints.push(Math.pow(10, i));
  }
  let lastEraEnd = 1;
  return (
    <svg
      width="100%"
      viewBox="0 -20 520 100"
      className="m-auto block fill-slate-700 stroke-slate-700 dark:fill-slate-200 dark:stroke-slate-200"
    >
      {markedPoints.map((p) => {
        const logP = (Math.log10(p) / Math.log10(maxYear)) * 500;
        return <line key={logP} x1={logP} x2={logP} y1="50" y2="55" />;
      })}
      {markedPoints.map((p) => {
        const logP = (Math.log10(p) / Math.log10(maxYear)) * 500;
        return (
          <text
            key={logP}
            x={logP}
            y="70"
            textAnchor="middle"
            style={{
              fontSize: "10px",
            }}
          >
            {numberAsIntegerString(2023 + p, { seperator: false })}
          </text>
        );
      })}
      {riskEras.map((era, idx) => {
        const eraStart = lastEraEnd;
        if (eraStart >= maxYear) return null;
        let eraEnd = Math.min(eraStart + era.length, maxYear);
        if (idx === riskEras.length - 1) {
          eraEnd = maxYear;
        }

        lastEraEnd = eraEnd;
        const logEraStart = (Math.log10(eraStart) / Math.log10(maxYear)) * 500;
        const logEraEnd = (Math.log10(eraEnd) / Math.log10(maxYear)) * 500;
        const totalRisk = Object.values(era.absolute_risks_by_type!).reduce(
          (acc, x) => acc + x,
          0,
        );
        const midPoint = logEraStart + (logEraEnd - logEraStart) / 2;

        return (
          <g
            key={"era" + idx}
            onClick={() =>
              setSelectedEraIdx(idx === selectedEraIdx ? undefined : idx)
            }
            className="cursor-pointer"
          >
            <line
              key={eraStart + "line"}
              // Leave a littles space between lines.
              x1={logEraStart + (idx === 0 ? 0 : 1)}
              x2={logEraEnd - (idx === riskEras.length - 1 ? 0 : 1)}
              y1="47"
              y2="47"
              style={{
                stroke: colorScale(
                  6 - Math.log10(1 / totalRisk),
                ) as unknown as string,
                strokeWidth: "8px",
              }}
            />
            {idx !== riskEras.length - 1 && (
              <text
                key={eraEnd + "line"}
                x={logEraEnd - 5}
                y="32"
                style={{ fontSize: "1.5em" }}
                onClick={(e) => {
                  addRiskEra(idx + 1);
                  e.stopPropagation();
                }}
              >
                +
              </text>
            )}
            {selectedEraIdx === idx && (
              <line
                key={eraStart + "ml"}
                x1={logEraStart}
                x2={logEraEnd}
                y1="41"
                y2="41"
                style={{
                  strokeWidth: "3px",
                }}
              />
            )}
            <line
              key={eraStart + "m"}
              x1={midPoint}
              x2={midPoint}
              y1="32"
              y2="41"
              style={{
                strokeWidth: selectedEraIdx === idx ? "3px" : "1.5px",
              }}
            />
            <line
              key={eraStart + "m2"}
              x1={midPoint - 0.2}
              x2={midPoint + 4}
              y1="32.5"
              y2="25"
              style={{
                strokeWidth: selectedEraIdx === idx ? "3px" : "1.5px",
              }}
            />
            <text
              key={eraStart + "text"}
              textAnchor="start"
              alignmentBaseline="middle"
              transform={`rotate(-52 ${midPoint} 45)`}
              x={midPoint + 22}
              y="37"
              style={{ fontWeight: selectedEraIdx === idx ? "bold" : "400" }}
            >
              Era {idx + 1}
            </text>
          </g>
        );
      })}
      {typeof selectedEraIdx === "undefined" && (
        <text x="260" y="90" textAnchor="middle" fontSize="11px">
          (Click on an era to configure)
        </text>
      )}
    </svg>
  );
};
