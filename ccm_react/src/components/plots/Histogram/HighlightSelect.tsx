import { HIGHLIGHT_RED } from "./constants";

interface HighlightSelectProps {
  highlightedValues: [number, number, number, number];
  setHighlightedValues: (arg0: [number, number, number, number]) => void;
}

export const HighlightSelect = ({
  highlightedValues,
  setHighlightedValues,
}: HighlightSelectProps) => {
  return (
    <div>
      <svg width="10" height="10">
        <rect width="10" height="10" fill={HIGHLIGHT_RED} />
      </svg>
      <select
        value={JSON.stringify(highlightedValues)}
        onChange={(e) =>
          setHighlightedValues(
            JSON.parse(e.target.value) as [number, number, number, number],
          )
        }
        className="border-none px-1 py-0 pr-5 text-xs shadow-none outline-none"
      >
        <option value="[0,0.25,0.75,1]">Top and bottom 25%</option>
        <option value="[0,0.1,0.9,1]">Top and bottom 10%</option>
        <option value="[0,0.025,0.975,1]">Top and bottom 2.5%</option>
        <option value="[0,0.001,0.999,1]">Top and bottom 0.1%</option>
      </select>
    </div>
  );
};
