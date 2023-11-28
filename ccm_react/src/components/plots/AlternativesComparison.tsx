import {
  calculateEV,
  calculateEV99,
  calculateEV99_9,
  calculateREU03,
  calculateREU05,
  calculateREU10,
  calculateWLU03,
  calculateWLU05,
  calculateWLU10,
} from "../../utils/alternativeWeighting/alternativeWeighting";
import { Table } from "../wrappers/Table";
import { Footnote } from "../elements/Footnote";

import { numberAsIntegerString } from "../../utils/formatting";
import { SparseSamples } from "../../client/models/SparseSamples";

export function AlternativesComparison({
  values,
  unit,
}: {
  values: number[] | SparseSamples;
  unit?: string;
}) {
  const eV = calculateEV(values);
  if (eV === 0) return null;
  const eV99 = calculateEV99(values);
  const eV99_9 = calculateEV99_9(values);
  const rEU03 = calculateREU03(values);
  const rEU05 = calculateREU05(values);
  const rEU10 = calculateREU10(values);
  const wLU03 = calculateWLU03(values);
  const wLU05 = calculateWLU05(values);
  const wLU10 = calculateWLU10(values);

  return (
    <>
      <h4>Alternative Weightings</h4>
      <p>
        In traditional decision theories, the values of prospects is given by
        their expected value: the sum of the value of each outcome weighted by
        its probability. Difference-Making Risk-Weighted Expected Utility
        <Footnote fkey="REU">
          <>
            For more on REU, see Clatterbuck, &quot;Fanaticism, Risk Aversion,
            and Decision Theory&quot;{" "}
            <a
              rel="noreferrer"
              href="https://docs.google.com/document/d/13SCTWfpixNmZbDkmCA6vJGxFU0034-0il9C6grMFkek/edit#heading=h.s2ql6diwoqg6"
              target="blank"
            >
              (2023)
            </a>{" "}
            . For the difference-making varient, see Duffy, &quot;How Can Risk
            Aversion Affect Your Cause Prioritization?&quot;{" "}
            <a
              rel="noreferrer"
              href="https://docs.google.com/document/d/1CZ5S-Eayxr64z5YADYR9M3P2WTp4u2Pgb4N-ynYbbMU/edit#bookmark=id.oikxikjwzz56"
              target="blank"
            >
              (2023)
            </a>
            .
          </>
        </Footnote>{" "}
        applies a weighting function to skew the value of each outcome based on
        the probability of producing at least as good a result. Weighted Linear
        Utility
        <Footnote fkey="WLU">
          <>
            For more on WLU, see Clatterbuck, &quot;Fanaticism, Risk Aversion,
            and Decision Theory&quot;{" "}
            <a
              rel="noreferrer"
              href="https://docs.google.com/document/d/13SCTWfpixNmZbDkmCA6vJGxFU0034-0il9C6grMFkek/edit#heading=h.s2ql6diwoqg6"
              target="blank"
            >
              (2023)
            </a>
            .
          </>
        </Footnote>{" "}
        skews outcomes based on the magnitude of the result.{" "}
        {eV * 0.3 > Math.max(rEU03, rEU05, wLU03, wLU05, wLU10) && (
          <>
            {" "}
            The distribution of results indicates that the prospects should be
            significantly less appealing for the risk averse.{" "}
          </>
        )}
      </p>
      <Table
        name="Alternative Weightings"
        caption={
          <>
            The values of alternative weighting schemes are compared with each
            other. DMREU weights each outcome by the power of the probability of
            an outcome at least as good. Here we use functions of the form W(v)
            = P<sup>a</sup>(o | o ≥ v). WLU weights each outcome by its value.
            Here we use functions of the form: W(v) = 1/(1 + v<sup>a</sup>).
            Low, moderate, and high levels of risk aversion correspond to values
            of <i>a</i> justifying indifference between a 100% chance of
            averting 10 DALYs and a x% chance of averting 1000 DALYs, for x = 3
            (low), 5 (moderate), and 10 (high). WLU is stake sensitive and the
            stated risk aversion levels do not include the counterfactual costs
            of missed opportunities and should not be taken too seriously.
            <Footnote fkey="WLUStake">
              <>
                <a
                  rel="noreferrer"
                  href="https://docs.google.com/document/d/1CZ5S-Eayxr64z5YADYR9M3P2WTp4u2Pgb4N-ynYbbMU/edit#heading=h.m86268ofs7oi"
                  target="_blank"
                >
                  Duffy (2023)
                </a>{" "}
                presents some issues WLU has with stake sensitivity.
              </>
            </Footnote>{" "}
            <br /> <br />
            These numbers are most appropriately used to compare results within
            a scheme, not across schemes as they are displayed there. The
            relative sizes of numbers in different schemes is of unclear
            significance. Nevertheless, each alternative weighting represents an
            intervention averting X DALYs with certainty to have value X.{" "}
            {eV > 0 &&
              Math.min(rEU03, rEU05, rEU10, wLU03, wLU05, wLU10) < 0 && (
                <>
                  Where values are negative, this indicates that under that
                  weighting, the risky prospect is equivalent in some sense to
                  causing harm with certainty, but there may be additional moral
                  reasons that explain why it is better to take a gamble on a
                  positive result than to cause harm with certainty.
                </>
              )}
          </>
        }
      >
        <table className="col-2-r col-3-r">
          <thead>
            <tr>
              <th>Approach</th>
              <th>Weighted {unit ?? "Value"}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={2}>
                <strong>Expected Utility</strong>
              </td>
            </tr>
            <tr>
              <td className="pl-10">Full</td>
              <td>{numberAsIntegerString(eV)}</td>
            </tr>
            <tr>
              <td className="pl-10">Middle 99.9%</td>
              <td>{numberAsIntegerString(eV99_9)}</td>
            </tr>
            <tr>
              <td className="pl-10">Middle 99%</td>
              <td>{numberAsIntegerString(eV99)}</td>
            </tr>
            <tr>
              <td></td>
            </tr>
            <tr>
              <td colSpan={3}>
                <strong>
                  Difference-Making Risk-Weighted Expected Utility
                </strong>
              </td>
            </tr>
            <tr>
              <td className="pl-10">Low risk aversion</td>
              <td>{numberAsIntegerString(rEU03)}</td>
            </tr>
            <tr>
              <td className="pl-10">Moderate risk aversion </td>
              <td>{numberAsIntegerString(rEU05)}</td>
            </tr>
            <tr>
              <td className="pl-10">High risk aversion </td>
              <td>{numberAsIntegerString(rEU10)}</td>
            </tr>
            <tr>
              <td></td>
            </tr>
            <tr>
              <td colSpan={3}>
                <strong>Weighted Linear Utility</strong>
              </td>
            </tr>
            <tr>
              <td className="pl-10">Low risk aversion</td>
              <td>{numberAsIntegerString(wLU03)}</td>
            </tr>
            <tr>
              <td className="pl-10">Moderate risk aversion</td>
              <td>{numberAsIntegerString(wLU05)}</td>
            </tr>
            <tr>
              <td className="pl-10">High risk aversion</td>
              <td>{numberAsIntegerString(wLU10)}</td>
            </tr>
          </tbody>
        </table>
      </Table>
    </>
  );
}
